"""Numerical checks of the proofs of the half-moments study.

    python3 proofs.py properties     # plan PL1: hypotheses H1-H9, H17 (proofs/properties.md)
    python3 proofs.py distributions  # plan PL2: hypotheses H10-H16 (proofs/distributions.md)
    python3 proofs.py asymptotics    # plan PL5: hypothesis H18 (proofs/asymptotics.md)

Each mode copies its proof document into $CLAIMSET_RUN_DIR and writes its checks to $CLAIMSET_RESULTS:
- "relative error of the numerical check" for every check, with conditions {hypothesis, check, ...}. For an
  equality it is |computed - stated| / max(|stated|, 1e-300), and for influence-function values, which cross zero,
  |computed - stated| / max(|stated|, 1); for an inequality it is the relative violation,
  max(0, (bound - value) / |bound|), which is 0 when the inequality holds.
- "largest relative error of the numerical checks" for every hypothesis (the diagnostic the plans name).
Other results (growth exponents, simulated standard deviations) are named for what they are.
"""
import json
import os
import shutil
import sys
from pathlib import Path

import mpmath as mp
import numpy as np

mp.mp.dps = int(os.environ.get("HM_DPS", 40))      # 40 digits; lower only in exploratory test runs
HERE = Path(__file__).resolve().parent
RESULTS = []
WORST = {}
HU = 2 * mp.mpf(3) ** mp.mpf(-0.75)                    # Hypotailedness of the uniform distribution
P = mp.log(mp.mpf(0.5)) / mp.log(HU)                    # the Extremity exponent


def put(variable, value, **conditions):
    RESULTS.append({"variable": variable, "value": float(value), "conditions": conditions})


def check(hypothesis, check_name, error, **conditions):
    error = abs(float(error))
    put("relative error of the numerical check", error, hypothesis=hypothesis, check=check_name, **conditions)
    WORST[hypothesis] = max(WORST.get(hypothesis, 0.0), error)


def rel(computed, stated):
    return abs(computed - stated) / max(abs(stated), mp.mpf("1e-300"))


def scaled(computed, stated):
    """|computed - stated| / max(|stated|, 1): the error of an influence-function value, which crosses zero."""
    return abs(computed - stated) / max(abs(stated), mp.mpf(1))


def violation(value, bound):
    """Relative violation of value >= bound (0 when it holds)."""
    return max(mp.mpf(0), (bound - value) / abs(bound))


# ---------- distributions (mpmath densities with their supports) ----------

def _beta_pdf(a, b):
    B = mp.beta(a, b)
    return lambda y: y ** (a - 1) * (1 - y) ** (b - 1) / B


DISTS = {
    "normal": (lambda y: mp.npdf(y), -mp.inf, mp.inf),
    "uniform": (lambda y: mp.mpf(0.5), mp.mpf(-1), mp.mpf(1)),
    "Laplace": (lambda y: mp.exp(-abs(y)) / 2, -mp.inf, mp.inf),
    "t(5)": (lambda y: mp.gamma(3) / (mp.sqrt(5 * mp.pi) * mp.gamma(mp.mpf(2.5))) * (1 + y * y / 5) ** -3, -mp.inf, mp.inf),
    "exponential": (lambda y: mp.exp(-y), mp.mpf(0), mp.inf),
    "gamma(2)": (lambda y: y * mp.exp(-y), mp.mpf(0), mp.inf),
    "lognormal(0,1)": (lambda y: mp.exp(-mp.log(y) ** 2 / 2) / (y * mp.sqrt(2 * mp.pi)), mp.mpf(0), mp.inf),
    "beta(2,5)": (_beta_pdf(2, 5), mp.mpf(0), mp.mpf(1)),
}
SYMMETRIC = ("normal", "uniform", "Laplace", "t(5)")


def integral(fn, lo, hi, points=(), heavy=False):
    """The integral of fn over (lo, hi), split at the points. With heavy=True an infinite end is reached from the
    nearest finite point by the substitution y = a +- exp(u), which keeps slowly decaying (heavy-tailed) integrands
    accurate (Student t with few degrees of freedom, Cauchy)."""
    if not heavy:
        pts = [lo] + sorted(p for p in points if lo < p < hi) + [hi]
        return mp.quad(fn, pts)
    if lo >= hi:
        return mp.mpf(0)
    inner = sorted(p for p in points if lo < p < hi)
    if lo == -mp.inf and hi == mp.inf and not inner:
        inner = [mp.mpf(0)]
    finite = ([lo] if lo != -mp.inf else []) + inner + ([hi] if hi != mp.inf else [])
    total = mp.quad(fn, finite) if len(finite) > 1 else mp.mpf(0)
    upts = [-mp.inf, -20, 0, 5, 20, 60, 200, mp.inf]
    if hi == mp.inf:
        a = finite[-1]
        total += mp.quad(lambda u: fn(a + mp.exp(u)) * mp.exp(u), upts)
    if lo == -mp.inf:
        a = finite[0]
        total += mp.quad(lambda u: fn(a - mp.exp(u)) * mp.exp(u), upts)
    return total


class Law:
    """A distribution given by a density on (lo, hi): its moments, parts and influence functions."""

    def __init__(self, name, pdf, lo, hi):
        self.name, self.pdf, self.lo, self.hi = name, pdf, lo, hi
        self.mean = integral(lambda y: y * pdf(y), lo, hi, (0, 1))
        self.var = integral(lambda y: (y - self.mean) ** 2 * pdf(y), lo, hi, (self.mean,))
        self.R, self.I = self.parts(self.mean)
        self.nu = self.R + self.I

    def parts(self, t):
        R = integral(lambda y: mp.sqrt(y - t) * self.pdf(y), max(t, self.lo), self.hi) if t < self.hi else mp.mpf(0)
        I = integral(lambda y: mp.sqrt(t - y) * self.pdf(y), self.lo, min(t, self.hi)) if t > self.lo else mp.mpf(0)
        return R, I

    def one_sided(self, t, power, side):
        """E[|y - t|^power ; side] and P(side)."""
        if side > 0:
            m = integral(lambda y: (y - t) ** power * self.pdf(y), t, self.hi)
            p = integral(self.pdf, t, self.hi)
        else:
            m = integral(lambda y: (t - y) ** power * self.pdf(y), self.lo, t)
            p = integral(self.pdf, self.lo, t)
        return m, p

    def a(self):
        ap = integral(lambda y: (y - self.mean) ** mp.mpf(-0.5) * self.pdf(y), self.mean, self.hi)
        am = integral(lambda y: (self.mean - y) ** mp.mpf(-0.5) * self.pdf(y), self.lo, self.mean)
        return ap, am


def asym(R, I):
    return 4 / mp.pi * mp.atan((R - I) / (R + I))


def hypo(R, I, var):
    return (R + I) / var ** mp.mpf(0.25)


def extr(h):
    return 2 * h ** P - 1


LAWS = {}


def law(name):
    if name not in LAWS:
        LAWS[name] = Law(name, *DISTS[name])
    return LAWS[name]


# ---------- PL1: properties ----------

def _h4(names):
    # H4: identity (A) and the range, strictly inside (-1, 1); mirror images too
    for n in names:
        L = law(n)
        for mirror in (False, True):
            R, I = (L.I, L.R) if mirror else (L.R, L.I)
            phi = mp.atan2(I, R)
            a1 = 1 - phi / (mp.pi / 4)
            cond = {"distribution": n + (" mirrored" if mirror else "")}
            check("H4", "1 - phi/(pi/4) against (4/pi) arctan((R - I)/nu)", rel(a1, asym(R, I)) if a1 else a1 - asym(R, I), **cond)
            check("H4", "Asymmetry within [-1, 1]", max(mp.mpf(0), abs(a1) - 1), **cond)
            check("H4", "Asymmetry strictly inside (-1, 1): the parts are both positive", 0 if (R > 0 and I > 0 and abs(a1) < 1) else 1, **cond)
            check("H4", "sign of Asymmetry against the larger part", 0 if (a1 < 0) == (I > R) or abs(R - I) < mp.mpf("1e-30") else 1, **cond)



def _g(v):
    return (3 + v) / 4 - v ** mp.mpf(0.25)


def _h20(names):
    # H20: 1 - H = E[g(V)], E = 2(1 - E[g(V)])^p - 1, kappa - 1 = E[(V - 1)^2]; the properties of g
    for n in names:
        L = law(n)
        s2 = L.var
        Eg = integral(lambda y: _g((y - L.mean) ** 2 / s2) * L.pdf(y), L.lo, L.hi, (L.mean,))
        H = hypo(L.R, L.I, s2)
        cond = {"distribution": n}
        check("H20", "1 - Hypotailedness against E[g(V)]", rel(1 - H, Eg), **cond)
        check("H20", "Extremity against 2(1 - E[g(V)])^p - 1", rel(extr(H), 2 * (1 - Eg) ** P - 1), **cond)
        m4 = integral(lambda y: (y - L.mean) ** 4 * L.pdf(y), L.lo, L.hi, (L.mean,))
        EV1 = integral(lambda y: ((y - L.mean) ** 2 / s2 - 1) ** 2 * L.pdf(y), L.lo, L.hi, (L.mean,))
        check("H20", "kurtosis - 1 against E[(V - 1)^2]", rel(m4 / s2 ** 2 - 1, EV1), **cond)
        put("1 - Hypotailedness", 1 - H, hypothesis="H20", **cond)
        put("kurtosis - 1", m4 / s2 ** 2 - 1, hypothesis="H20", **cond)
    grid = [mp.mpf(k) / 64 for k in range(0, 64 * 8 + 1)] + [mp.mpf(10) ** k for k in range(1, 13)]
    check("H20", "g positive away from 1", max([0] + [1 for v in grid if v != 1 and not _g(v) > 0]), function="g")
    check("H20", "g zero at 1", _g(mp.mpf(1)), function="g")
    check("H20", "g second derivative positive", max([0] + [1 for v in grid if v > 0 and not mp.diff(_g, v, 2) > 0]),
          function="g")
    check("H20", "g(0) against 3/4", rel(_g(mp.mpf(0)), mp.mpf(3) / 4), function="g")
    check("H20", "g(0) against 8 times (3/32)(0 - 1)^2", rel(_g(mp.mpf(0)), 8 * mp.mpf(3) / 32), function="g")
    for d in (mp.mpf("1e-6"), mp.mpf("-1e-6"), mp.mpf("1e-10"), mp.mpf("-1e-10")):
        ratio = _g(1 + d) / (mp.mpf(3) / 32 * d ** 2)
        # Taylor: ratio - 1 = O(|v - 1|), the remainder over |v - 1| tends to a third-derivative constant (7/12)
        check("H20", "Taylor remainder (g(v)/((3/32)(v - 1)^2) - 1)/|v - 1| within 1", max(mp.mpf(0), abs(ratio - 1) / abs(d) - 1),
              function="g", v_minus_1=float(d))
    for v in (mp.mpf(10) ** 4, mp.mpf(10) ** 8, mp.mpf(10) ** 12):
        check("H20", "g(v) - v/4 against 3/4 - v^(1/4)", rel(_g(v) - v / 4, mp.mpf(3) / 4 - v ** mp.mpf(0.25)), function="g", v=float(v))



def properties():
    names = list(DISTS)
    only = os.environ.get("HM_ONLY")                    # e.g. "H4": check one hypothesis (a re-decided wording)
    if only == "H4":
        _h4(names)
        return
    if only == "H20":
        _h20(names)
        return

    # H1: symmetry gives equal parts
    for n in SYMMETRIC:
        L = law(n)
        check("H1", "real minus imaginary part over HAM", (L.R - L.I) / L.nu, distribution=n)

    # H2: the family of the proof (piecewise uniform, c = 1/b, delta0 = b(1-b)/2) has equal parts and is asymmetric
    for b in (mp.mpf("0.1"), mp.mpf("0.25"), mp.mpf("0.5"), mp.mpf("0.75")):
        c, d0 = 1 / b, b * (1 - b) / 2

        def g(x):
            return ((x + d0) ** mp.mpf(1.5) - (x - d0) ** mp.mpf(1.5)) / (3 * d0)
        w2 = mp.mpf(1)
        w3 = (g(b) - b * g(1)) / (c * g(1) - g(c))
        w1 = w2 * b + w3 * c
        tot = w1 + w2 + w3
        w1, w2, w3 = w1 / tot, w2 / tot, w3 / tot
        pdf = lambda y, w1=w1, w2=w2, w3=w3, b=b, c=c, d0=d0: (
            (w1 if abs(y + 1) <= d0 else 0) + (w2 if abs(y - b) <= d0 else 0) + (w3 if abs(y - c) <= d0 else 0)) / (2 * d0)
        pts = [-1 - d0, -1 + d0, b - d0, b + d0, c - d0, c + d0]
        mean = sum(mp.quad(lambda y: y * pdf(y), [pts[2 * i], pts[2 * i + 1]]) for i in range(3))
        R = sum(mp.quad(lambda y: mp.sqrt(y - mean) * pdf(y), [pts[2 * i], pts[2 * i + 1]]) for i in (1, 2))
        I = mp.quad(lambda y: mp.sqrt(mean - y) * pdf(y), [pts[0], pts[1]])
        m2 = sum(mp.quad(lambda y: (y - mean) ** 2 * pdf(y), [pts[2 * i], pts[2 * i + 1]]) for i in range(3))
        m3 = sum(mp.quad(lambda y: (y - mean) ** 3 * pdf(y), [pts[2 * i], pts[2 * i + 1]]) for i in range(3))
        cond = {"b": float(b)}
        check("H2", "mean of the constructed law", mean, **cond)
        check("H2", "masses positive", max(mp.mpf(0), -min(w1, w2, w3)), **cond)
        check("H2", "real minus imaginary part over HAM", (R - I) / (R + I), **cond)
        put("skewness of the constructed law", m3 / m2 ** mp.mpf(1.5), hypothesis="H2", **cond)
    # the three-point law of RN1
    x = [mp.mpf(-1), mp.mpf("0.36"), mp.mpf("2.25")]
    w = [mp.mpf("0.45"), mp.mpf(5) / 12, mp.mpf(2) / 15]
    mean = sum(wi * xi for wi, xi in zip(w, x))
    R = sum(wi * mp.sqrt(xi - mean) for wi, xi in zip(w, x) if xi > mean)
    I = sum(wi * mp.sqrt(mean - xi) for wi, xi in zip(w, x) if xi < mean)
    check("H2", "real minus imaginary part over HAM", (R - I) / (R + I), distribution="three-point law of RN1")

    # H3: location, scale, sign (transformed densities, integrated afresh)
    for n in ("exponential", "gamma(2)", "lognormal(0,1)", "beta(2,5)"):
        L = law(n)
        for c in (mp.mpf(2), mp.mpf("0.5"), mp.mpf(-2)):
            a = mp.mpf("3.7")
            pdf = lambda y, c=c, a=a, L=L: L.pdf((y - a) / c) / abs(c)
            lo, hi = sorted([a + c * L.lo, a + c * L.hi])
            T = Law(f"{n} x {c} + 3.7", pdf, lo, hi)
            if c > 0:
                err = max(rel(T.R, mp.sqrt(c) * L.R), rel(T.I, mp.sqrt(c) * L.I))
            else:
                err = max(rel(T.R, mp.sqrt(-c) * L.I), rel(T.I, mp.sqrt(-c) * L.R))
            check("H3", "parts of a + c y against the stated transform", err, distribution=n, c=float(c))

    _h4(names)

    # H5: decomposition
    for n in names:
        L = law(n)
        m_p, p_p = L.one_sided(L.mean, mp.mpf(0.5), +1)
        m_m, p_m = L.one_sided(L.mean, mp.mpf(0.5), -1)
        d_p, _ = L.one_sided(L.mean, 1, +1)
        d_m, _ = L.one_sided(L.mean, 1, -1)
        h_p = (m_p / p_p) / mp.sqrt(d_p / p_p)
        h_m = (m_m / p_m) / mp.sqrt(d_m / p_m)
        check("H5", "R/I against (p+/p-)^0.5 h+/h-", rel(L.R / L.I, mp.sqrt(p_p / p_m) * h_p / h_m), distribution=n)
        check("H5", "h+ and h- at most 1", max(mp.mpf(0), h_p - 1, h_m - 1), distribution=n)
        check("H5", "balance of the mean", rel(d_p, d_m), distribution=n)

    # H6: the mean is the L_{3/2}-quantile at tau* = I/nu (golden-section minimisation of the loss)
    for n in names:
        L = law(n)
        tau = L.I / L.nu

        def psi(theta, L=L, tau=tau):
            up = integral(lambda y: (y - theta) ** mp.mpf(1.5) * L.pdf(y), max(theta, L.lo), L.hi) if theta < L.hi else 0
            dn = integral(lambda y: (theta - y) ** mp.mpf(1.5) * L.pdf(y), L.lo, min(theta, L.hi)) if theta > L.lo else 0
            return tau * up + (1 - tau) * dn
        sd = mp.sqrt(L.var)
        lo, hi = L.mean - sd, L.mean + sd
        gr = (mp.sqrt(5) - 1) / 2
        x1, x2 = hi - gr * (hi - lo), lo + gr * (hi - lo)
        f1, f2 = psi(x1), psi(x2)
        while hi - lo > sd * mp.mpf("1e-14"):
            if f1 < f2:
                hi, x2, f2 = x2, x1, f1
                x1 = hi - gr * (hi - lo)
                f1 = psi(x1)
            else:
                lo, x1, f1 = x1, x2, f2
                x2 = lo + gr * (hi - lo)
                f2 = psi(x2)
        theta = (lo + hi) / 2
        # a minimiser found to 1e-14 sd; the check is the distance in sd, against the bracket's own width
        check("H6", "minimiser of the L_{3/2} loss minus the mean, in standard deviations (bracket 1e-14)",
              max(mp.mpf(0), abs(theta - L.mean) / sd - mp.mpf("1e-14")), distribution=n)
        check("H6", "Asymmetry against (4/pi) arctan(1 - 2 tau*)", rel(asym(L.R, L.I), 4 / mp.pi * mp.atan(1 - 2 * tau)) if asym(L.R, L.I) else 0, distribution=n)

    # H7: Hypotailedness in (0, 1]; equality for the symmetric two-point law; Extremity at the uniform
    for n in names:
        L = law(n)
        h = hypo(L.R, L.I, L.var)
        check("H7", "Hypotailedness at most 1", max(mp.mpf(0), h - 1), distribution=n)
        check("H7", "Hypotailedness positive", 0 if h > 0 else 1, distribution=n)
    check("H7", "Hypotailedness of the two-point law at +-1 equals 1", rel(hypo(mp.mpf(0.5), mp.mpf(0.5), mp.mpf(1)), 1))
    U = law("uniform")
    check("H7", "Extremity of the uniform distribution", extr(hypo(U.R, U.I, U.var)))

    # H8: the sharp sample bound
    rng = np.random.default_rng(20261123)
    for n in (2, 3, 5, 10, 30, 100):
        bound = 2 ** 0.75 * n ** -0.75
        worst = np.inf
        for gen in (lambda s: rng.standard_normal(s), lambda s: rng.exponential(1, s), lambda s: rng.standard_t(1, s)):
            y = gen((10000, n))
            e = y - y.mean(axis=1, keepdims=True)
            h = np.mean(np.abs(e) ** 0.5, axis=1) / np.mean(e ** 2, axis=1) ** 0.25
            worst = min(worst, float(np.min(h / bound)))
        check("H8", "sample Hypotailedness below the bound, relative", max(0.0, 1 - worst), n=n)
        put("smallest ratio of sample Hypotailedness to the bound over 30000 samples", worst, hypothesis="H8", n=n)
        ext = [mp.mpf(0)] * n
        ext[0], ext[1] = mp.mpf(1), mp.mpf(-1)
        m = sum(ext) / n
        e = [v - m for v in ext]
        hx = (sum(abs(v) ** mp.mpf(0.5) for v in e) / n) / (sum(v * v for v in e) / n) ** mp.mpf(0.25)
        check("H8", "extremal sample attains the bound", rel(hx, 2 ** mp.mpf(0.75) * mp.mpf(n) ** mp.mpf(-0.75)), n=n)

    # H9: one-sided Hypotailedness
    for n in names:
        L = law(n)
        hs = []
        for side in (+1, -1):
            m_half, p = L.one_sided(L.mean, mp.mpf(0.5), side)
            m_two, _ = L.one_sided(L.mean, 2, side)
            hs.append((m_half / p) / (m_two / p) ** mp.mpf(0.25))
        check("H9", "one-sided Hypotailedness at most 1", max(mp.mpf(0), hs[0] - 1, hs[1] - 1), distribution=n)
        if n == "uniform":
            check("H9", "one-sided Hypotailedness of the uniform equals 2 x 3^-0.75", max(rel(hs[0], HU), rel(hs[1], HU)))
        if n in SYMMETRIC:
            h = hypo(L.R, L.I, L.var)
            check("H9", "one-sided Hypotailedness equals Hypotailedness under symmetry", max(rel(hs[0], h), rel(hs[1], h)), distribution=n)

    # H17: influence functions, by the central difference of T((1-e)F + e delta_x) in e, with e = 1e-6/(1 + k^2)
    # (a one-sided difference has truncation error of order e; a fixed e = 1e-6 makes the signed mixture at
    # e < 0 degenerate for large k, as e (k sigma)^2 approaches the variance)
    ks = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    for n in names:
        L = law(n)
        sd = mp.sqrt(L.var)
        ap, am = L.a()

        def T_mix(eps, x, L=L):
            mean = L.mean + eps * (x - L.mean)
            R0, I0 = L.parts(mean)
            R = (1 - eps) * R0 + eps * (mp.sqrt(x - mean) if x > mean else 0)
            I = (1 - eps) * I0 + eps * (mp.sqrt(mean - x) if x < mean else 0)
            m2 = (1 - eps) * (L.var + (L.mean - mean) ** 2) + eps * (x - mean) ** 2
            return asym(R, I), hypo(R, I, m2)

        def IF(x, L=L, ap=ap, am=am):
            d = x - L.mean
            ifR = (mp.sqrt(d) if d > 0 else 0) - L.R - ap / 2 * d
            ifI = (mp.sqrt(-d) if d < 0 else 0) - L.I + am / 2 * d
            ifA = 4 / mp.pi * (L.I * ifR - L.R * ifI) / (L.R ** 2 + L.I ** 2)
            ifnu = ifR + ifI
            ifH = ifnu / L.var ** mp.mpf(0.25) - L.nu / (4 * L.var ** mp.mpf(1.25)) * (d * d - L.var)
            return ifA, ifH
        logs = {("A", 1): [], ("A", -1): [], ("H", 1): [], ("H", -1): []}
        for k in ks:
            for side in (1, -1):
                x = L.mean + side * k * sd
                if not (L.lo <= x <= L.hi) and k < 2:
                    pass
                e = mp.mpf("1e-6") / (1 + k * k)
                Ap, Hp = T_mix(e, x)
                Am, Hm = T_mix(-e, x)
                gA, gH = (Ap - Am) / (2 * e), (Hp - Hm) / (2 * e)
                iA, iH = IF(x)
                cond = {"distribution": n, "k": k, "side": "above" if side > 0 else "below"}
                check("H17", "Asymmetry: central difference against the derived influence function", scaled(gA, iA), **cond)
                check("H17", "Hypotailedness: central difference against the derived influence function", scaled(gH, iH), **cond)
                logs[("A", side)].append((k, iA))
                logs[("H", side)].append((k, iH))
                if k >= 10:
                    sA = 0 if (side > 0) == (iA < 0) else 1
                    check("H17", "Asymmetry decreases for large positive x and increases for large negative x", sA, **cond)
                    check("H17", "Hypotailedness influence negative for large |x|", 0 if iH < 0 else 1, **cond)
        for (coef, side), pts in logs.items():
            big = [(k, v) for k, v in pts if k >= 10]
            xs = [mp.log(k) for k, _ in big]
            ys = [mp.log(abs(v)) for _, v in big]
            xm, ym = sum(xs) / len(xs), sum(ys) / len(ys)
            slope = sum((a - xm) * (b - ym) for a, b in zip(xs, ys)) / sum((a - xm) ** 2 for a in xs)
            put("growth exponent of the influence function", slope, hypothesis="H17", distribution=n,
                coefficient="Asymmetry" if coef == "A" else "Hypotailedness", side="above" if side > 0 else "below")


# ---------- PL2: closed forms ----------

def distributions():
    def num_parts(pdf, lo, hi, centre, pts=(), heavy=False):
        R = integral(lambda y: mp.sqrt(y - centre) * pdf(y), centre, hi, pts, heavy)
        I = integral(lambda y: mp.sqrt(centre - y) * pdf(y), lo, centre, pts, heavy)
        return R, I

    def var_of(pdf, lo, hi, centre):
        return integral(lambda y: (y - centre) ** 2 * pdf(y), lo, hi, (centre,))

    # H10 uniform
    for b, c in ((0, 1), (-2, 5)):
        b, c = mp.mpf(b), mp.mpf(c)
        pdf = lambda y, b=b, c=c: 1 / (c - b)
        m = (b + c) / 2
        R, I = num_parts(pdf, b, c, m)
        v = var_of(pdf, b, c, m)
        cond = {"b": float(b), "c": float(c)}
        check("H10", "real part", rel(R, mp.sqrt((c - b) / 2) / 3), **cond)
        check("H10", "imaginary part", rel(I, mp.sqrt((c - b) / 2) / 3), **cond)
        check("H10", "Asymmetry", asym(R, I), **cond)
        check("H10", "Hypotailedness", rel(hypo(R, I, v), HU), **cond)
        check("H10", "Extremity", extr(hypo(R, I, v)), **cond)
    # H11 normal
    for s in (1, 3):
        s = mp.mpf(s)
        pdf = lambda y, s=s: mp.npdf(y, 0, s)
        R, I = num_parts(pdf, -mp.inf, mp.inf, 0)
        v = var_of(pdf, -mp.inf, mp.inf, 0)
        part = mp.gamma(0.75) * mp.pi ** -0.5 * 2 ** mp.mpf(-0.75) * mp.sqrt(s)
        cond = {"sigma": float(s)}
        check("H11", "real part", rel(R, part), **cond)
        check("H11", "imaginary part", rel(I, part), **cond)
        check("H11", "Asymmetry", asym(R, I), **cond)
        check("H11", "Hypotailedness", rel(hypo(R, I, v), mp.gamma(0.75) * mp.pi ** -0.5 * 2 ** mp.mpf(0.25)), **cond)
    # H12 Laplace
    for bb in ("1", "2.5"):
        bb = mp.mpf(bb)
        pdf = lambda y, bb=bb: mp.exp(-abs(y) / bb) / (2 * bb)
        R, I = num_parts(pdf, -mp.inf, mp.inf, 0)
        v = var_of(pdf, -mp.inf, mp.inf, 0)
        cond = {"b": float(bb)}
        check("H12", "real part", rel(R, mp.sqrt(mp.pi) / 4 * mp.sqrt(bb)), **cond)
        check("H12", "imaginary part", rel(I, mp.sqrt(mp.pi) / 4 * mp.sqrt(bb)), **cond)
        check("H12", "Hypotailedness", rel(hypo(R, I, v), mp.sqrt(mp.pi) / 2 * 2 ** mp.mpf(-0.25)), **cond)
    # H13 generalised normal (alpha = 1.7)
    al = mp.mpf("1.7")
    for s in ("0.5", "1", "1.5", "2", "4"):
        s = mp.mpf(s)
        pdf = lambda y, s=s: s / (2 * al * mp.gamma(1 / s)) * mp.exp(-abs(y / al) ** s)
        R, I = num_parts(pdf, -mp.inf, mp.inf, 0, (al, 10 * al))
        v = var_of(pdf, -mp.inf, mp.inf, 0)
        part = mp.sqrt(al) / 2 * mp.gamma(mp.mpf(1.5) / s) / mp.gamma(1 / s)
        cond = {"shape": float(s), "scale": float(al)}
        check("H13", "real part", rel(R, part), **cond)
        check("H13", "imaginary part", rel(I, part), **cond)
        check("H13", "Hypotailedness", rel(hypo(R, I, v), mp.gamma(mp.mpf(1.5) / s) * mp.gamma(1 / s) ** mp.mpf(-0.75) * mp.gamma(3 / s) ** mp.mpf(-0.25)), **cond)
    # H14 Student t
    for nu in ("0.75", "1", "1.5", "3", "5", "30"):
        nu = mp.mpf(nu)
        pdf = lambda y, nu=nu: mp.gamma((nu + 1) / 2) / (mp.sqrt(nu * mp.pi) * mp.gamma(nu / 2)) * (1 + y * y / nu) ** (-(nu + 1) / 2)
        R, I = num_parts(pdf, -mp.inf, mp.inf, 0, (1, 10, 100), heavy=True)
        part = mp.gamma(0.75) * mp.gamma((nu - mp.mpf(0.5)) / 2) * nu ** mp.mpf(0.25) / (2 * mp.sqrt(mp.pi) * mp.gamma(nu / 2))
        cond = {"nu": float(nu)}
        check("H14", "real part about 0", rel(R, part), **cond)
        check("H14", "imaginary part about 0", rel(I, part), **cond)
        if nu > 2:
            v = nu / (nu - 2)
            check("H14", "Hypotailedness", rel(hypo(R, I, v), mp.gamma(0.75) * mp.gamma((nu - mp.mpf(0.5)) / 2) * (nu - 2) ** mp.mpf(0.25) / (mp.sqrt(mp.pi) * mp.gamma(nu / 2))), **cond)
    # H15 Cauchy
    for g in (1, 2):
        g = mp.mpf(g)
        pdf = lambda y, g=g: g / (mp.pi * (y * y + g * g))
        R, I = num_parts(pdf, -mp.inf, mp.inf, 0, (g, 100 * g), heavy=True)
        part = mp.sqrt(g) / 2 * mp.sec(mp.pi / 4)
        cond = {"gamma": float(g)}
        check("H15", "real part about 0", rel(R, part), **cond)
        check("H15", "imaginary part about 0", rel(I, part), **cond)
    # H16 gamma
    for a in ("0.5", "1", "2", "5", "20"):
        for lam in (1, 3):
            a, lam = mp.mpf(a), mp.mpf(lam)
            pdf = lambda y, a=a, lam=lam: lam ** a / mp.gamma(a) * y ** (a - 1) * mp.exp(-lam * y)
            m = a / lam
            R, I = num_parts(pdf, mp.mpf(0), mp.inf, m)
            Rc = mp.gamma(mp.mpf(1.5)) * a ** (a + mp.mpf(0.5)) * mp.exp(-a) / (mp.gamma(a) * mp.sqrt(lam)) * mp.hyperu(mp.mpf(1.5), a + mp.mpf(1.5), a)
            Ic = mp.beta(a, mp.mpf(1.5)) * a ** (a + mp.mpf(0.5)) / (mp.gamma(a) * mp.sqrt(lam)) * mp.hyp1f1(a, a + mp.mpf(1.5), -a)
            cond = {"shape": float(a), "rate": float(lam)}
            check("H16", "real part", rel(R, Rc), **cond)
            check("H16", "imaginary part", rel(I, Ic), **cond)
            if a == 1:
                check("H16", "exponential real part", rel(R, mp.sqrt(mp.pi) / (2 * mp.e * mp.sqrt(lam))), **cond)
                check("H16", "exponential imaginary part", rel(I, (2 * mp.e - mp.sqrt(mp.pi) * mp.erfi(1)) / (2 * mp.e * mp.sqrt(lam))), **cond)
        # Asymmetry does not depend on the rate
        A1 = asym(*num_parts(lambda y, a=a: a ** 0 / mp.gamma(a) * y ** (a - 1) * mp.exp(-y), mp.mpf(0), mp.inf, a))
        A3 = asym(*num_parts(lambda y, a=a: 3 ** a / mp.gamma(a) * y ** (a - 1) * mp.exp(-3 * y), mp.mpf(0), mp.inf, a / 3))
        check("H16", "Asymmetry at rates 1 and 3", rel(A3, A1), shape=float(a))


# ---------- PL5: asymptotics ----------

def asymptotics():
    rng_seed = 20261121
    n, reps, chunk = 20000, 20000, 100
    if os.environ.get("HM_SMOKE"):                     # a crash test only; never set in a recorded run
        n, reps, chunk = 200, 200, 100
    gens = {"normal": lambda r, s: r.standard_normal(s),
            "t(5)": lambda r, s: r.standard_t(5, s),
            "exponential": lambda r, s: r.exponential(1, s)}
    for k, (name, gen) in enumerate(gens.items()):
        L = law(name)
        ap, am = L.a()

        def IFs(x, L=L, ap=ap, am=am):
            d = x - L.mean
            ifR = (mp.sqrt(d) if d > 0 else 0) - L.R - ap / 2 * d
            ifI = (mp.sqrt(-d) if d < 0 else 0) - L.I + am / 2 * d
            ifA = 4 / mp.pi * (L.I * ifR - L.R * ifI) / (L.R ** 2 + L.I ** 2)
            ifH = (ifR + ifI) / L.var ** mp.mpf(0.25) - L.nu / (4 * L.var ** mp.mpf(1.25)) * (d * d - L.var)
            h = hypo(L.R, L.I, L.var)
            ifE = 2 * P * h ** (P - 1) * ifH
            return ifA, ifH, ifE
        asy = []
        for j in range(3):
            asy.append(mp.sqrt(integral(lambda x, j=j: IFs(x)[j] ** 2 * L.pdf(x), L.lo, L.hi, (L.mean,))))
        rng = np.random.default_rng(rng_seed + k)
        stats = []
        for _ in range(reps // chunk):
            y = gen(rng, (chunk, n))
            e = y - y.mean(axis=1, keepdims=True)
            R = np.mean(np.sqrt(np.clip(e, 0, None)), axis=1)
            I = np.mean(np.sqrt(np.clip(-e, 0, None)), axis=1)
            v = np.mean(e ** 2, axis=1)
            A = 4 / np.pi * np.arctan((R - I) / (R + I))
            H = (R + I) / v ** 0.25
            E = 2 * H ** float(P) - 1
            stats.append(np.column_stack([A, H, E]))
        stats = np.vstack(stats)
        for j, coef in enumerate(("Asymmetry", "Hypotailedness", "Extremity")):
            s = stats[:, j]
            sd = float(np.std(s, ddof=1))
            z = (s - s.mean()) / sd
            kurt = float(np.mean(z ** 4))
            se_sd = sd * np.sqrt((kurt - 1) / (4 * len(s)))
            target = float(asy[j]) / np.sqrt(n)
            ratio = sd / target
            cond = {"distribution": name, "coefficient": coef, "n": n, "replications": reps}
            put("simulated standard deviation", sd, hypothesis="H18", **cond)
            put("asymptotic standard deviation sqrt(E[IF^2]/n)", target, hypothesis="H18", **cond)
            put("ratio of simulated to asymptotic standard deviation", ratio, hypothesis="H18", **cond)
            put("Monte Carlo standard error of the ratio", se_sd / target, hypothesis="H18", **cond)
            put("Monte Carlo standard error of the simulated standard deviation", se_sd, hypothesis="H18", **cond)
            put("distance of the ratio from 1 in Monte Carlo standard errors", abs(ratio - 1) / (se_sd / target), hypothesis="H18", **cond)


MODES = {"properties": (properties, "properties.md"), "distributions": (distributions, "distributions.md"),
         "asymptotics": (asymptotics, "asymptotics.md")}

if __name__ == "__main__":
    mode = sys.argv[1]
    fn, doc = MODES[mode]
    run_dir = os.environ.get("CLAIMSET_RUN_DIR")
    if run_dir:
        shutil.copy(HERE / "proofs" / doc, Path(run_dir) / doc)
    fn()
    for h, w in sorted(WORST.items(), key=lambda kv: int(kv[0][1:])):
        put("largest relative error of the numerical checks", w, hypothesis=h)
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as fh:
            json.dump(RESULTS, fh)
    else:
        for r in RESULTS:
            if r["variable"] == "largest relative error of the numerical checks":
                print(r)
