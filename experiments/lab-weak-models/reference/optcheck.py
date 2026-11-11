"""Optimisation check for the reference: is a difference between arms the estimator's or the optimiser's?

For every fit in estimates.csv, computes the sum of squared one-step errors (SSE) at the arm's estimated
smoothing parameters with the initial states chosen by least squares (for fixed smoothing parameters the
errors are affine in the initial states, so this is exact). This is the concentrated Gaussian likelihood
criterion that both smooth (loss="likelihood") and statsforecast (opt_crit="lik") minimise when initial states
are optimised. Writes optcheck.csv: per DGP, T and arm, the mean SSE, and how often the arm's SSE exceeds the
lowest SSE of the three arms on the same series by more than 1e-6 and 0.1% relative, and the mean relative excess.
"""
import csv, os
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import simulate as S


def errors(form, y, par, x0):
    m = S.SEASON
    l = x0[0]
    b = x0[1] if form == "AAN" else 0.0
    s = list(x0[1:]) if form == "ANA" else None
    e = np.empty(len(y))
    for t in range(len(y)):
        st = s[t % m] if s is not None else 0.0
        e[t] = y[t] - l - b - st
        l = l + b + par["alpha"] * e[t]
        if form == "AAN":
            b = b + par["beta"] * e[t]
        if s is not None:
            s[t % m] = st + par["gamma"] * e[t]
    return e


def sse(form, y, par):
    k = {"ANN": 1, "AAN": 2, "ANA": 1 + S.SEASON}[form]
    c = errors(form, y, par, np.zeros(k))
    X = np.column_stack([c - errors(form, y, par, np.eye(k)[i]) for i in range(k)])
    x, *_ = np.linalg.lstsq(X, c, rcond=None)
    r = c - X @ x
    return float(r @ r)


def job(args):
    di, ti, ests = args
    dgp, form, par = S.DGPS[di]
    n = S.TS[ti]
    out = []
    for rep, byarm in sorted(ests.items()):
        y = S.simulate(form, par, n, np.random.default_rng([S.BASE_SEED, di, n, rep]))
        vals = {arm: sse(form, y, p) for arm, p in byarm.items()}
        best = min(vals.values())
        for arm, v in vals.items():
            out.append((dgp, n, arm, v, v > best * (1 + 1e-6), v > best * (1 + 1e-3), v / best - 1))
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ests = {}
    with open(os.path.join(here, "estimates.csv")) as f:
        for r in csv.DictReader(f):
            if r["error"]:
                continue
            di = [d[0] for d in S.DGPS].index(r["dgp"])
            ti = S.TS.index(int(r["T"]))
            ests.setdefault((di, ti), {}).setdefault(int(r["rep"]), {}).setdefault(r["arm"], {})[r["parameter"]] = float(r["estimate"])
    with ProcessPoolExecutor(4) as ex:
        rows = [x for part in ex.map(job, [(di, ti, e) for (di, ti), e in sorted(ests.items())]) for x in part]
    agg = {}
    for dgp, n, arm, v, worse, worse3, rel in rows:
        a = agg.setdefault((dgp, n, arm), [0.0, 0, 0, 0, 0.0])
        a[0] += v; a[1] += 1; a[2] += worse; a[3] += worse3; a[4] += rel
    with open(os.path.join(here, "optcheck.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dgp", "T", "arm", "mean_sse_ls_initials", "n", "n_sse_above_best_arm_1e-6",
                    "n_sse_above_best_arm_0.1pct", "mean_relative_sse_excess"])
        for (dgp, n, arm), (s, c, k, k3, rel) in agg.items():
            w.writerow([dgp, n, arm, s / c, c, k, k3, rel / c])


if __name__ == "__main__":
    main()
