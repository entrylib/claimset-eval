"""Reference analysis for the lab-weak-models experiment (never shown to the agents under test).

Simulates the design of ../study/brief.md, fits every series with three arms and writes
  estimates.csv  one row per (DGP, T, replicate, arm, parameter): estimate, truth, error flag, bound flag
  summary.csv    bias, Monte Carlo SE of the bias, RMSE, MAE, failures per (DGP, T, arm, parameter)
  consistency.csv  RMSE by T and the slope of log RMSE on log T per (DGP, arm, parameter)
Usage: python simulate.py [--reps 300] [--workers 4] [--out .]
"""
import argparse, csv, math, os, sys, time, warnings
from concurrent.futures import ProcessPoolExecutor
import numpy as np

BASE_SEED = 20261111
TS = [50, 100, 250, 500]
SEASON = 12
L0, B0 = 100.0, 1.0
S0 = [10 * math.sin(2 * math.pi * j / SEASON) for j in range(SEASON)]
DGPS = [  # id, form, true parameters
    ("ANN-a0.1", "ANN", {"alpha": 0.1}),
    ("ANN-a0.5", "ANN", {"alpha": 0.5}),
    ("AAN-a0.3-b0.05", "AAN", {"alpha": 0.3, "beta": 0.05}),
    ("AAN-a0.5-b0.2", "AAN", {"alpha": 0.5, "beta": 0.2}),
    ("ANA-a0.2-g0.1", "ANA", {"alpha": 0.2, "gamma": 0.1}),
]
ARMS = ["smooth_optimal", "statsforecast", "smooth_backcasting"]
TOL = 1e-3  # an estimate within TOL of one of its implementation's bounds counts as on a bound


def simulate(form, par, n, rng):
    e = rng.normal(0.0, 1.0, n)
    l, b, s = L0, B0, list(S0)
    y = np.empty(n)
    for t in range(n):
        trend = b if form == "AAN" else 0.0
        seas = s[t % SEASON] if form == "ANA" else 0.0
        y[t] = l + trend + seas + e[t]
        l = l + trend + par["alpha"] * e[t]
        if form == "AAN":
            b = b + par["beta"] * e[t]
        if form == "ANA":
            s[t % SEASON] = seas + par["gamma"] * e[t]
    return y


def bounds(arm, name, est):
    """(lower, upper) of a parameter in the arm's own usual bounds, given the other estimates."""
    if arm == "statsforecast":
        lo, hi = 1e-4, 0.9999
    else:
        lo, hi = 0.0, 1.0
    if name == "beta":
        hi = min(hi, est["alpha"])
    if name == "gamma":
        hi = min(hi, 1 - est["alpha"])
    return lo, hi


def fit(arm, form, y):
    warnings.filterwarnings("ignore")
    seasonal = form == "ANA"
    info = {}
    if arm.startswith("smooth"):
        from smooth import ES
        m = ES(model=form, lags=[SEASON] if seasonal else None,
               initial="optimal" if arm == "smooth_optimal" else "backcasting")
        m.fit(y)
        est = {"alpha": float(m.persistence_level_)}
        if form == "AAN":
            est["beta"] = float(m.persistence_trend_)
        if seasonal:
            g = m.persistence_seasonal_
            est["gamma"] = float(np.ravel(g)[0])
    else:
        from statsforecast.models import AutoETS
        f = AutoETS(model=form, season_length=SEASON if seasonal else 1, damped=False).fit(y)
        p = f.model_["par"]
        if f.model_["method"] != f"ETS({form[0]},{form[1]},{form[2]})":
            raise RuntimeError("statsforecast fitted " + f.model_["method"])
        est = {"alpha": float(p[0])}
        if form == "AAN":
            est["beta"] = float(p[1])
        if seasonal:
            est["gamma"] = float(p[2])
        info["nit"] = int(f.model_["fit"].nit)
    return est, info


def cell(args):
    di, ti, reps = args
    dgp, form, par = DGPS[di]
    n = TS[ti]
    rows = []
    for r in range(reps):
        seed = [BASE_SEED, di, n, r]
        y = simulate(form, par, n, np.random.default_rng(seed))
        for arm in ARMS:
            try:
                est, info = fit(arm, form, y)
                err = ""
            except Exception as ex:  # counted, never dropped silently
                est, info, err = {}, {}, f"{type(ex).__name__}: {ex}"[:200]
            for name, truth in par.items():
                v = est.get(name, float("nan"))
                on = ""
                if not err:
                    lo, hi = bounds(arm, name, est)
                    on = "lower" if v - lo < TOL else ("upper" if hi - v < TOL else "")
                rows.append({"dgp": dgp, "form": form, "T": n, "rep": r, "seed": "-".join(map(str, seed)),
                             "arm": arm, "parameter": name, "truth": truth, "estimate": v,
                             "error": err, "on_bound": on, "nit": info.get("nit", "")})
    return rows


def summarise(rows):
    out = []
    keys = sorted({(r["dgp"], r["T"], r["arm"], r["parameter"]) for r in rows},
                  key=lambda k: ([d[0] for d in DGPS].index(k[0]), k[1], ARMS.index(k[2]), k[3]))
    groups = {}
    for r in rows:
        groups.setdefault((r["dgp"], r["T"], r["arm"], r["parameter"]), []).append(r)
    for k in keys:
        g = groups[k]
        ok = [r for r in g if not r["error"]]
        d = np.array([r["estimate"] - r["truth"] for r in ok])
        out.append({"dgp": k[0], "T": k[1], "arm": k[2], "parameter": k[3], "truth": g[0]["truth"],
                    "n_reps": len(g), "n_errors": len(g) - len(ok),
                    "n_lower_bound": sum(r["on_bound"] == "lower" for r in ok),
                    "n_upper_bound": sum(r["on_bound"] == "upper" for r in ok),
                    "mean_estimate": float(np.mean(d) + g[0]["truth"]),
                    "median_estimate": float(np.median(d) + g[0]["truth"]),
                    "bias": float(np.mean(d)), "bias_se": float(np.std(d, ddof=1) / math.sqrt(len(d))),
                    "rmse": float(np.sqrt(np.mean(d ** 2))), "mae": float(np.mean(np.abs(d)))})
    return out


def consistency(summary):
    out = []
    groups = {}
    for s in summary:
        groups.setdefault((s["dgp"], s["arm"], s["parameter"]), []).append(s)
    for (dgp, arm, p), g in groups.items():
        g = sorted(g, key=lambda s: s["T"])
        x = np.log([s["T"] for s in g]); yv = np.log([s["rmse"] for s in g])
        slope = float(np.polyfit(x, yv, 1)[0])
        row = {"dgp": dgp, "arm": arm, "parameter": p, "loglog_slope": slope,
               "rmse_ratio_500_50": g[-1]["rmse"] / g[0]["rmse"],
               "monotone_decreasing": all(a["rmse"] > b["rmse"] for a, b in zip(g, g[1:]))}
        for s in g:
            row[f"rmse_T{s['T']}"] = s["rmse"]
        out.append(row)
    return out


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    t0 = time.time()
    jobs = [(di, ti, a.reps) for di in range(len(DGPS)) for ti in range(len(TS))]
    with ProcessPoolExecutor(a.workers) as ex:
        rows = [r for part in ex.map(cell, jobs) for r in part]
    write(os.path.join(a.out, "estimates.csv"), rows)
    s = summarise(rows)
    write(os.path.join(a.out, "summary.csv"), s)
    write(os.path.join(a.out, "consistency.csv"), consistency(s))
    print(f"{len(rows)} rows, {time.time() - t0:.0f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
