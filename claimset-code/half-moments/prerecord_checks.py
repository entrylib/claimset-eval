"""Re-runs, inside the lab record, the checks the agent made in scratch work before the record began
(19 November 2026): the manuscript's closed forms against numerical integration, the exact values behind its
figure captions, a counterexample to the converse of Theorem 1, the smallest sample Hypotailedness found by
optimisation against the bound n^-0.75, and the coefficients of further distributions.

Writes every number as a result to $CLAIMSET_RESULTS (or prints them outside the lab)."""
import json
import os

import mpmath as mp
import numpy as np
from scipy import integrate, optimize, stats

mp.mp.dps = 40
P = float(mp.log(0.5) / mp.log(2 * mp.mpf(3) ** -0.75))          # the Extremity exponent
results = []


def put(variable, value, **conditions):
    results.append({"variable": variable, "value": float(value), "conditions": conditions})


def coefficients(upper, lower, var):
    """Upper part (real), lower part (imaginary) and variance -> the manuscript's coefficients."""
    nu = upper + lower
    asym = 1 - np.arctan2(lower, upper) / (np.pi / 4)
    hyp = nu / var ** 0.25
    ext = 2 * hyp ** P - 1
    ce_re = 2 * (2 * upper / var ** 0.25) ** P - 1
    ce_im = 2 * (2 * lower / var ** 0.25) ** P - 1
    return asym, hyp, ext, ce_re, ce_im


def parts(dist, lo, hi):
    mu = dist.mean()
    lower = integrate.quad(lambda y: (mu - y) ** 0.5 * dist.pdf(y), lo, mu, limit=500)[0]
    upper = integrate.quad(lambda y: (y - mu) ** 0.5 * dist.pdf(y), mu, hi, limit=500)[0]
    return upper, lower, dist.var()


# 1. the manuscript's closed forms against numerical integration
g = float(mp.gamma(0.75) * mp.pi ** -0.5 * 2 ** -0.75)
up, lo, var = parts(stats.norm(), -np.inf, np.inf)
put("HCM real part", g, distribution="normal(0,1)", source="closed form (eq. 29)")
put("HCM real part", up, distribution="normal(0,1)", source="numerical integration")
up, lo, var = parts(stats.uniform(-1, 2), -1, 1)
put("HCM real part", 1 / 3, distribution="uniform(-1,1)", source="closed form (eq. 21)")
put("HCM real part", up, distribution="uniform(-1,1)", source="numerical integration")
R = float(mp.sqrt(mp.pi) / (2 * mp.e))
I = float((2 * mp.e - mp.sqrt(mp.pi) * mp.erfi(1)) / (2 * mp.e))
up, lo, var = parts(stats.expon(), 0, np.inf)
for name, closed, num in (("HCM real part", R, up), ("HCM imaginary part", I, lo)):
    put(name, closed, distribution="exponential(1)", source="closed form (eq. 36)")
    put(name, num, distribution="exponential(1)", source="numerical integration")
for nu in (0.75, 1.0, 1.5, 3.0, 5.0, 30.0):
    ham = float(mp.gamma(0.75) * mp.gamma((nu - 0.5) / 2) * nu ** 0.25 / (mp.sqrt(mp.pi) * mp.gamma(nu / 2)))
    num = 2 * integrate.quad(lambda y: y ** 0.5 * stats.t.pdf(y, nu), 0, np.inf, limit=500)[0]
    put("HAM about 0", ham, distribution=f"t({nu:g})", source="closed form (eq. 35)")
    put("HAM about 0", num, distribution=f"t({nu:g})", source="numerical integration")
num = 2 * integrate.quad(lambda y: y ** 0.5 * stats.cauchy.pdf(y, scale=2.0), 0, np.inf, limit=500)[0]
put("HAM about 0", 2.0 ** 0.5 * 2 ** 0.5, distribution="Cauchy(0,2)", source="closed form (Section 4.4)")
put("HAM about 0", num, distribution="Cauchy(0,2)", source="numerical integration")

# 2. coefficients of the manuscript's distributions, exactly
for name, (u, l, v) in {"normal": (g, g, 1.0), "uniform": (1 / 3, 1 / 3, 1 / 3),
                        "exponential": (R, I, 1.0)}.items():
    for var_name, value in zip(("Asymmetry", "Hypotailedness", "Extremity", "CE real part", "CE imaginary part"),
                               coefficients(u, l, v)):
        put(var_name, value, distribution=name, source="exact")


# 3. the figure captions' distributions, exactly (substitutions that remove the endpoint singularities)
def clamp(x):
    return mp.sqrt(max(mp.mpf(0), x))


b = mp.mpf("1e-5")
d = b / (1 + b)
up = mp.quad(lambda s: clamp(d - s ** (1 / b)), [0, d ** b])
lo = mp.quad(lambda s: clamp(s ** (1 / b) - d), [d ** b, 1])
asym = 1 - mp.atan2(lo, up) / (mp.pi / 4)
put("Asymmetry", asym, distribution="beta(1,1e-5)", source="exact")
a = mp.mpf("0.001")
half = 1 / (a * mp.beta(a, a)) * mp.quad(lambda s: clamp(mp.mpf(0.5) - s ** (1 / a)) * (1 - s ** (1 / a)) ** (a - 1),
                                         [0, mp.mpf(0.5) ** a])
var = a * a / ((2 * a) ** 2 * (2 * a + 1))
put("Extremity", 2 * (2 * half / var ** 0.25) ** P - 1, distribution="beta(0.001,0.001)", source="exact")
s = mp.mpf("0.1")
ham = mp.gamma(1.5 / s) / mp.gamma(1 / s)
var = mp.gamma(3 / s) / mp.gamma(1 / s)
put("Extremity", 2 * (ham / var ** 0.25) ** P - 1, distribution="generalised normal(shape 0.1)", source="exact")

# 4. a distribution with equal parts that is not symmetric (support -1, 0.36, 2.25)
x = np.array([-1.0, 0.36, 2.25])
w = np.array([0.45, 5 / 12, 2 / 15])
mean = float(w @ x)
dev = x - mean
put("mean", mean, distribution="three-point counterexample", source="exact")
put("HCM real part", float(w @ (np.abs(dev) ** 0.5 * (dev > 0))), distribution="three-point counterexample", source="exact")
put("HCM imaginary part", float(w @ (np.abs(dev) ** 0.5 * (dev < 0))), distribution="three-point counterexample", source="exact")
put("skewness", float(w @ dev ** 3 / (w @ dev ** 2) ** 1.5), distribution="three-point counterexample", source="exact")


# 5. smallest sample Hypotailedness: optimisation against n^-0.75 and the two-outlier sample
def hyp(y):
    e = y - y.mean()
    return np.mean(np.abs(e) ** 0.5) / np.mean(e ** 2) ** 0.25


rng = np.random.default_rng(20261119)
for n in (3, 5, 10):
    best = 1.0
    for _ in range(25):
        start = rng.standard_normal(n) * rng.exponential(1, n) ** 3
        r = optimize.minimize(hyp, start, method="Nelder-Mead", options={"maxiter": 20000, "xatol": 1e-10, "fatol": 1e-12})
        best = min(best, r.fun)
    two = np.zeros(n)
    two[0], two[1] = 1.0, -1.0
    put("smallest sample Hypotailedness found", best, n=n, source="Nelder-Mead, 25 random starts")
    put("sample Hypotailedness", hyp(two), n=n, source="two values at +-1, the rest at the mean")
    put("bound n^-0.75", n ** -0.75, n=n, source="Theorem 2")

# 6. further distributions
for name, dist, a_, b_ in (("Laplace", stats.laplace(), -np.inf, np.inf), ("logistic", stats.logistic(), -np.inf, np.inf),
                           ("t(5)", stats.t(5), -np.inf, np.inf), ("gamma(2)", stats.gamma(2), 0, np.inf),
                           ("gamma(5)", stats.gamma(5), 0, np.inf), ("lognormal(0.5)", stats.lognorm(0.5), 0, np.inf),
                           ("lognormal(1)", stats.lognorm(1), 0, np.inf), ("beta(2,5)", stats.beta(2, 5), 0, 1),
                           ("beta(0.5,0.5)", stats.beta(0.5, 0.5), 0, 1), ("chi-squared(3)", stats.chi2(3), 0, np.inf)):
    u, l, v = parts(dist, a_, b_)
    put("skewness", dist.stats(moments="s"), distribution=name, source="exact")
    for var_name, value in zip(("Asymmetry", "Hypotailedness", "Extremity", "CE real part", "CE imaginary part"),
                               coefficients(u, l, v)):
        put(var_name, value, distribution=name, source="numerical integration")

path = os.environ.get("CLAIMSET_RESULTS")
if path:
    with open(path, "w") as fh:
        json.dump(results, fh)
else:
    for r in results:
        print(r)
