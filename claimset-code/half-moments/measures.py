"""Sample measures of skewness and tail weight, vectorised over the rows of a 2-D array (one sample per row).

Half-moment coefficients (study half-moments, terms TM1-TM8):
    hcm_parts      real part (values above the sample mean) and imaginary part (below it)
    asymmetry      (4/pi) arctan((R - I) / (R + I))
    hypotailedness (R + I) / (mean squared deviation)^(1/4)
    extremity      2 H^p - 1, p = log 0.5 / log(2 * 3^-0.75)
    complex_extremity  (2 H+^p - 1, 2 H-^p - 1) from the one-sided Hypotailedness above and below the mean
Comparison measures (TM9-TM19): moment skewness and excess kurtosis (1/n moments), L- and TL(1,1)-moment ratios
(unbiased estimators of Hosking 1990 and Elamir & Seheult 2003), quartile skewness and octile kurtosis (quantiles
by linear interpolation, R type 7), the medcouple (Brys, Hubert & Struyf 2004; exact, by its kernel over all pairs),
the mean-based skewness 2 F_n(mean) - 1, and Geary's ratio (mean absolute deviation / standard deviation).
"""
from math import comb, log

import numpy as np

P = log(0.5) / log(2 * 3 ** -0.75)


def hcm_parts(y):
    e = y - y.mean(axis=1, keepdims=True)
    return np.mean(np.sqrt(np.clip(e, 0, None)), axis=1), np.mean(np.sqrt(np.clip(-e, 0, None)), axis=1)


def asymmetry(y):
    R, I = hcm_parts(y)
    return 4 / np.pi * np.arctan((R - I) / (R + I))


def hypotailedness(y):
    R, I = hcm_parts(y)
    e = y - y.mean(axis=1, keepdims=True)
    return (R + I) / np.mean(e ** 2, axis=1) ** 0.25


def extremity(y):
    return 2 * hypotailedness(y) ** P - 1


def one_sided(y):
    """H+ and H-: the one-sided Hypotailedness over the values above and below the sample mean."""
    e = y - y.mean(axis=1, keepdims=True)
    up, dn = e > 0, e < 0
    n_up, n_dn = up.sum(axis=1), dn.sum(axis=1)
    half_up = np.where(up, np.sqrt(np.abs(e)), 0).sum(axis=1) / n_up
    two_up = np.where(up, e ** 2, 0).sum(axis=1) / n_up
    half_dn = np.where(dn, np.sqrt(np.abs(e)), 0).sum(axis=1) / n_dn
    two_dn = np.where(dn, e ** 2, 0).sum(axis=1) / n_dn
    return half_up / two_up ** 0.25, half_dn / two_dn ** 0.25


def complex_extremity(y):
    hp, hm = one_sided(y)
    return 2 * hp ** P - 1, 2 * hm ** P - 1


def moment_skewness(y):
    e = y - y.mean(axis=1, keepdims=True)
    return np.mean(e ** 3, axis=1) / np.mean(e ** 2, axis=1) ** 1.5


def excess_kurtosis(y):
    e = y - y.mean(axis=1, keepdims=True)
    return np.mean(e ** 4, axis=1) / np.mean(e ** 2, axis=1) ** 2 - 3


_WEIGHTS = {}


def _tl_weights(n, r, t):
    """Weights w_i (i = 1..n, sorted sample) of the unbiased sample TL-moment lambda_r^(t) (Elamir & Seheult 2003,
    eq. 4.1); t = 0 gives Hosking's sample L-moments."""
    key = (n, r, t)
    if key not in _WEIGHTS:
        w = np.zeros(n)
        denom = comb(n, r + 2 * t)
        for i in range(1, n + 1):
            s = 0
            for k in range(r):
                s += (-1) ** k * comb(r - 1, k) * comb(i - 1, r + t - 1 - k) * comb(n - i, t + k)
            w[i - 1] = s / (r * denom)
        _WEIGHTS[key] = w
    return _WEIGHTS[key]


def _tl_ratios(y, t):
    ys = np.sort(y, axis=1)
    n = y.shape[1]
    l2, l3, l4 = (ys @ _tl_weights(n, r, t) for r in (2, 3, 4))
    return l3 / l2, l4 / l2


def l_skewness(y):
    return _tl_ratios(y, 0)[0]


def l_kurtosis(y):
    return _tl_ratios(y, 0)[1]


def tl_skewness(y):
    return _tl_ratios(y, 1)[0]


def tl_kurtosis(y):
    return _tl_ratios(y, 1)[1]


def quartile_skewness(y):
    q1, q2, q3 = np.quantile(y, [0.25, 0.5, 0.75], axis=1)
    return (q3 + q1 - 2 * q2) / (q3 - q1)


def octile_kurtosis(y):
    e = np.quantile(y, [k / 8 for k in range(1, 8)], axis=1)
    return ((e[6] - e[4]) + (e[2] - e[0])) / (e[5] - e[1])


def medcouple(y):
    """The medcouple of each row, from its kernel over all pairs x_i <= m <= x_j (Brys, Hubert & Struyf 2004).
    Values equal to the median (k of them) form k x k tie pairs, whose kernel is sign(i + j - 1 - k) for the
    i-th and j-th of them (Brys et al. 2004, the special kernel for ties at the median)."""
    out = np.empty(y.shape[0])
    for r, row in enumerate(y):
        z = np.sort(row) - np.median(row)
        zp = z[z > 0]
        zm = z[z < 0]
        k = int(np.sum(z == 0))
        a = np.concatenate([zp, np.zeros(k)])[:, None]
        b = np.concatenate([np.zeros(k), zm])[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            h = (a + b) / (a - b)
        if k:
            i = np.arange(1, k + 1)
            h[len(zp):, :k] = np.sign(i[:, None] + i[None, :] - 1 - k)
        out[r] = np.median(h)
    return out


def mean_skewness(y):
    """2 F_n(mean) - 1, the share of values at or below the sample mean, rescaled."""
    m = y.mean(axis=1, keepdims=True)
    return 2 * np.mean(y <= m, axis=1) - 1


def geary_ratio(y):
    e = y - y.mean(axis=1, keepdims=True)
    return np.mean(np.abs(e), axis=1) / np.sqrt(np.mean(e ** 2, axis=1))


HALF_MOMENT = {
    "Asymmetry": asymmetry,
    "Hypotailedness": hypotailedness,
    "Extremity": extremity,
    "Complex Extremity, real part": lambda y: complex_extremity(y)[0],
    "Complex Extremity, imaginary part": lambda y: complex_extremity(y)[1],
}
COMPARISON = {
    "moment skewness": moment_skewness,
    "L-skewness": l_skewness,
    "TL-skewness": tl_skewness,
    "quartile skewness": quartile_skewness,
    "medcouple": medcouple,
    "mean-based skewness 2F(mean) - 1": mean_skewness,
    "excess kurtosis": excess_kurtosis,
    "L-kurtosis": l_kurtosis,
    "TL-kurtosis": tl_kurtosis,
    "octile kurtosis": octile_kurtosis,
    "Geary ratio": geary_ratio,
}
ALL = {**HALF_MOMENT, **COMPARISON}
