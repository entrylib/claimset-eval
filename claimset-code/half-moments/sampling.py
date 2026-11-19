"""Plan PL6 (question Q5): bias, spread and interval coverage of the sample half-moment coefficients.

Samples from normal(0,1), Student t(5) and exponential(1); n = 20, 50, 100, 200, 500, 1000, 2000; 10000
replications for each distribution and n (seed 20261122, incremented for each next one). On each sample: the
sample Asymmetry, Hypotailedness, Extremity and both parts of the Complex Extremity; 95% intervals by (a) the normal
approximation with a jackknife standard error, (b) the percentile bootstrap with 999 resamples, the bootstrap on the
first 2000 replications only. True values by numerical integration at 40 digits (for the normal and exponential
distributions they equal the closed forms of Q2).

Results ($CLAIMSET_RESULTS), conditions {coefficient, distribution, n} (and {interval} for coverage):
"bias", "standard deviation", "root mean squared error", "sqrt(n) times the standard deviation", each with
"Monte Carlo standard error of the <variable>"; "coverage of the 95% interval" with
"Monte Carlo standard error of the coverage"; "true value".
Usage: python3 sampling.py [--replications R] [--bootstrap-replications B] [--sizes ...]  (defaults: the plan's)
"""
import argparse
import json
import os

import mpmath as mp
import numpy as np

from measures import P

COEFS = ["Asymmetry", "Hypotailedness", "Extremity", "Complex Extremity, real part",
         "Complex Extremity, imaginary part"]
BASES = [("normal(0,1)", lambda r, s: r.standard_normal(s), lambda y: mp.npdf(y), -mp.inf, mp.inf),
         ("t(5)", lambda r, s: r.standard_t(5, s),
          lambda y: mp.gamma(3) / (mp.sqrt(5 * mp.pi) * mp.gamma(mp.mpf(2.5))) * (1 + y * y / 5) ** -3, -mp.inf, mp.inf),
         ("exponential(1)", lambda r, s: r.exponential(1.0, s), lambda y: mp.exp(-y), mp.mpf(0), mp.inf)]


def true_values(pdf, lo, hi):
    mp.mp.dps = 40
    q = lambda f, a, b: mp.quad(f, [a, b])
    mean = q(lambda y: y * pdf(y), lo, hi)
    var = q(lambda y: (y - mean) ** 2 * pdf(y), lo, hi)
    R = q(lambda y: mp.sqrt(y - mean) * pdf(y), mean, hi)
    I = q(lambda y: mp.sqrt(mean - y) * pdf(y), lo, mean)
    pp = q(pdf, mean, hi)
    pm = q(pdf, lo, mean)
    up2 = q(lambda y: (y - mean) ** 2 * pdf(y), mean, hi)
    dn2 = q(lambda y: (mean - y) ** 2 * pdf(y), lo, mean)
    hp = (R / pp) / (up2 / pp) ** mp.mpf(0.25)
    hm = (I / pm) / (dn2 / pm) ** mp.mpf(0.25)
    H = (R + I) / var ** mp.mpf(0.25)
    return {"Asymmetry": float(4 / mp.pi * mp.atan((R - I) / (R + I))), "Hypotailedness": float(H),
            "Extremity": float(2 * H ** P - 1), "Complex Extremity, real part": float(2 * hp ** P - 1),
            "Complex Extremity, imaginary part": float(2 * hm ** P - 1)}


def coefficients(e, keep=None):
    """The five coefficients from deviations e (rows: samples) over the entries where keep is True."""
    if keep is None:
        keep = np.ones_like(e, dtype=bool)
    cnt = keep.sum(axis=1)
    pos, neg = (e > 0) & keep, (e < 0) & keep
    ae = np.abs(e)
    sq = np.sqrt(ae)
    R = np.where(pos, sq, 0).sum(axis=1) / cnt
    I = np.where(neg, sq, 0).sum(axis=1) / cnt
    v = np.where(keep, e * e, 0).sum(axis=1) / cnt
    H = (R + I) / v ** 0.25
    npos, nneg = pos.sum(axis=1), neg.sum(axis=1)
    hp = (np.where(pos, sq, 0).sum(axis=1) / npos) / (np.where(pos, e * e, 0).sum(axis=1) / npos) ** 0.25
    hm = (np.where(neg, sq, 0).sum(axis=1) / nneg) / (np.where(neg, e * e, 0).sum(axis=1) / nneg) ** 0.25
    return np.column_stack([4 / np.pi * np.arctan((R - I) / (R + I)), H, 2 * H ** P - 1, 2 * hp ** P - 1,
                            2 * hm ** P - 1])


def sample_coefs(y):
    return coefficients(y - y.mean(axis=1, keepdims=True))


def jackknife_se(y):
    """Jackknife standard errors (rows: samples) of the five coefficients. For leave-one-out sample i the
    deviations are e_ij = y_j - m_(i), m_(i) the mean without y_i; each sum over j != i is the full sum over j
    minus the term j = i, so no mask is needed."""
    n = y.shape[1]
    out = np.empty((y.shape[0], len(COEFS)))
    for r, row in enumerate(y):
        m = (row.sum() - row) / (n - 1)                 # leave-one-out means
        e = row[None, :] - m[:, None]                   # e[i, j]
        d = row - m                                     # the left-out terms e[i, i]
        pos = e > 0
        sq = np.sqrt(np.abs(e))
        e2 = e * e
        sp = (sq * pos).sum(axis=1) - np.sqrt(abs(d)) * (d > 0)
        sn = (sq * (e < 0)).sum(axis=1) - np.sqrt(abs(d)) * (d < 0)
        np_ = pos.sum(axis=1) - (d > 0)
        nn = (e < 0).sum(axis=1) - (d < 0)
        e2p = (e2 * pos).sum(axis=1) - d * d * (d > 0)
        e2n = (e2 * (e < 0)).sum(axis=1) - d * d * (d < 0)
        R, I, v = sp / (n - 1), sn / (n - 1), (e2p + e2n) / (n - 1)
        H = (R + I) / v ** 0.25
        hp = (sp / np_) / (e2p / np_) ** 0.25
        hm = (sn / nn) / (e2n / nn) ** 0.25
        t = np.column_stack([4 / np.pi * np.arctan((R - I) / (R + I)), H, 2 * H ** P - 1, 2 * hp ** P - 1,
                             2 * hm ** P - 1])
        out[r] = np.sqrt((n - 1) / n * np.sum((t - t.mean(axis=0)) ** 2, axis=0))
    return out


def bootstrap_ci(row, rng, B):
    n = len(row)
    idx = rng.integers(0, n, size=(B, n))
    t = sample_coefs(row[idx])
    return np.quantile(t, 0.025, axis=0), np.quantile(t, 0.975, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replications", type=int, default=10000)
    ap.add_argument("--bootstrap-replications", type=int, default=2000)
    ap.add_argument("--resamples", type=int, default=999)
    ap.add_argument("--sizes", default="20,50,100,200,500,1000,2000")
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    results = []

    def put(var, value, **cond):
        results.append({"variable": var, "value": float(value), "conditions": cond})
    seed = 20261122
    for name, gen, pdf, lo, hi in BASES:
        truth = true_values(pdf, lo, hi)
        for c in COEFS:
            put("true value", truth[c], coefficient=c, distribution=name)
        for n in sizes:
            rng = np.random.default_rng(seed)
            seed += 1
            y = gen(rng, (args.replications, n))
            est = sample_coefs(y)
            se = jackknife_se(y)
            boot_lo, boot_hi = [], []
            for r in range(min(args.bootstrap_replications, args.replications)):
                l, h = bootstrap_ci(y[r], rng, args.resamples)
                boot_lo.append(l)
                boot_hi.append(h)
            boot_lo, boot_hi = np.array(boot_lo), np.array(boot_hi)
            R = len(est)
            for j, c in enumerate(COEFS):
                t = est[:, j]
                tv = truth[c]
                cond = {"coefficient": c, "distribution": name, "n": n}
                bias, sd = t.mean() - tv, t.std(ddof=1)
                rmse = np.sqrt(np.mean((t - tv) ** 2))
                kurt = np.mean(((t - t.mean()) / sd) ** 4)
                put("bias", bias, **cond)
                put("Monte Carlo standard error of the bias", sd / np.sqrt(R), **cond)
                put("standard deviation", sd, **cond)
                put("Monte Carlo standard error of the standard deviation", sd * np.sqrt((kurt - 1) / (4 * R)), **cond)
                put("root mean squared error", rmse, **cond)
                sq = (t - tv) ** 2
                put("Monte Carlo standard error of the root mean squared error", sq.std(ddof=1) / np.sqrt(R) / (2 * rmse), **cond)
                put("sqrt(n) times the standard deviation", np.sqrt(n) * sd, **cond)
                cover_j = np.mean((t - 1.959964 * se[:, j] <= tv) & (tv <= t + 1.959964 * se[:, j]))
                put("coverage of the 95% interval", cover_j, interval="normal approximation, jackknife standard error", **cond)
                put("Monte Carlo standard error of the coverage", np.sqrt(cover_j * (1 - cover_j) / R),
                    interval="normal approximation, jackknife standard error", **cond)
                Rb = len(boot_lo)
                cover_b = np.mean((boot_lo[:, j] <= tv) & (tv <= boot_hi[:, j]))
                put("coverage of the 95% interval", cover_b, interval="percentile bootstrap, 999 resamples", **cond)
                put("Monte Carlo standard error of the coverage", np.sqrt(cover_b * (1 - cover_b) / Rb),
                    interval="percentile bootstrap, 999 resamples", **cond)
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as fh:
            json.dump(results, fh)
    else:
        print(len(results), "results")


if __name__ == "__main__":
    main()
