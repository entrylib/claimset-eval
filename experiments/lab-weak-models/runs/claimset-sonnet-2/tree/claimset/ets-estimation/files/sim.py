"""Simulation: smooth ES vs statsforecast AutoETS, estimates of ETS smoothing parameters.

Usage: python3 sim.py --seed 20261111 --R 300 --T 50 100 250 500
Writes a JSON array of results to $CLAIMSET_RESULTS and raw estimates to $CLAIMSET_RUN_DIR/estimates.csv.
"""
import argparse, json, os, time, warnings, csv
import numpy as np

M = 12
L0, B0 = 100.0, 1.0
S0 = 10 * np.sin(2 * np.pi * np.arange(M) / M)
TOL = 1e-3  # an estimate within TOL of a bound counts as on the bound

SETTINGS = [  # (process label, form, true parameters)
    ("ETS(A,N,N) alpha=0.1", "ANN", dict(alpha=0.1)),
    ("ETS(A,N,N) alpha=0.5", "ANN", dict(alpha=0.5)),
    ("ETS(A,A,N) alpha=0.3 beta=0.05", "AAN", dict(alpha=0.3, beta=0.05)),
    ("ETS(A,A,N) alpha=0.5 beta=0.2", "AAN", dict(alpha=0.5, beta=0.2)),
    ("ETS(A,N,A) alpha=0.2 gamma=0.1", "ANA", dict(alpha=0.2, gamma=0.1)),
]
METHODS = ["smooth ES, optimised initials", "smooth ES, backcasting", "statsforecast AutoETS"]


def simulate(form, par, T, rng):
    e = rng.normal(0.0, 1.0, T)
    y = np.empty(T)
    l, b, s = L0, B0, S0.copy()
    a = par["alpha"]
    for t in range(T):
        et = e[t]
        if form == "ANN":
            y[t] = l + et
            l = l + a * et
        elif form == "AAN":
            y[t] = l + b + et
            l, b = l + b + a * et, b + par["beta"] * et
        else:
            k = t % M
            y[t] = l + s[k] + et
            l = l + a * et
            s[k] = s[k] + par["gamma"] * et
    return y


def fit_smooth(y, form, initial):
    from smooth import ES
    kw = dict(lags=[M]) if form == "ANA" else {}
    m = ES(model=form, initial=initial, loss="likelihood", bounds="usual", **kw)
    m.fit(y)
    out = {"alpha": float(m.persistence_level_)}
    if form == "AAN":
        out["beta"] = float(m.persistence_trend_)
    if form == "ANA":
        out["gamma"] = float(np.ravel(m.persistence_seasonal_)[0])
    return out


def fit_sf(y, form):
    from statsforecast.models import AutoETS
    a = AutoETS(season_length=M if form == "ANA" else 1, model=form, damped=False).fit(y)
    p = a.model_["par"]
    out = {"alpha": float(p[0])}
    if form == "AAN":
        out["beta"] = float(p[1])
    if form == "ANA":
        out["gamma"] = float(p[2])
    return out


def on_bound(name, est):
    a = est["alpha"]
    if name == "alpha":
        return a <= TOL or a >= 1 - TOL
    if name == "beta":
        return est["beta"] <= TOL or est["beta"] >= a - TOL
    return est["gamma"] <= TOL or est["gamma"] >= 1 - a - TOL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--T", type=int, nargs="+", default=[50, 100, 250, 500])
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    run_dir = os.environ.get("CLAIMSET_RUN_DIR", ".")
    rows = []  # method, process, T, rep, param, truth, estimate
    nfail, secs = {}, {m: 0.0 for m in METHODS}
    t_start = time.time()
    for pi, (label, form, truth) in enumerate(SETTINGS):
        for T in a.T:
            rng = np.random.default_rng(np.random.SeedSequence([a.seed, pi, T]))
            for r in range(a.R):
                y = simulate(form, truth, T, rng)
                fits = [lambda: fit_smooth(y, form, "optimal"), lambda: fit_smooth(y, form, "backcasting"),
                        lambda: fit_sf(y, form)]
                for meth, f in zip(METHODS, fits):
                    t0 = time.time()
                    try:
                        est = f()
                        ok = all(np.isfinite(v) for v in est.values())
                    except Exception:
                        est, ok = None, False
                    secs[meth] += time.time() - t0
                    if not ok:
                        nfail[(meth, label, T)] = nfail.get((meth, label, T), 0) + 1
                        continue
                    for name, tv in truth.items():
                        rows.append((meth, label, T, r, name, tv, est[name], int(on_bound(name, est))))
    with open(os.path.join(run_dir, "estimates.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["method", "process", "T", "rep", "parameter", "truth", "estimate", "on_bound"])
        w.writerows(rows)

    res = []
    stat = {}
    for meth, label, T, r, name, tv, ev, ob in rows:
        stat.setdefault((meth, label, T, name), []).append((ev - tv, ob))
    for (meth, label, T, name), v in sorted(stat.items()):
        d = np.array([x[0] for x in v])
        cond = {"method": meth, "process": label, "parameter": name, "sample size": T}
        bias, rmse = float(d.mean()), float(np.sqrt((d ** 2).mean()))
        res += [{"variable": "bias", "value": bias, "conditions": cond},
                {"variable": "RMSE", "value": rmse, "conditions": cond},
                {"variable": "MAE", "value": float(np.abs(d).mean()), "conditions": cond},
                {"variable": "estimates on a bound", "value": float(sum(x[1] for x in v)), "conditions": cond},
                {"variable": "successful fits", "value": float(len(v)), "conditions": cond}]
    for meth in METHODS:
        for label, form, truth in SETTINGS:
            for T in a.T:
                res.append({"variable": "failed fits", "value": float(nfail.get((meth, label, T), 0)),
                            "conditions": {"method": meth, "process": label, "sample size": T}})
    res.append({"variable": "failed fits excluded", "value": float(sum(nfail.values())), "conditions": {}})

    rm = {k: float(np.sqrt(np.mean([x[0] ** 2 for x in v]))) for k, v in stat.items()}
    ratios = [rm[(METHODS[0], l, T, n)] / rm[(METHODS[2], l, T, n)]
              for (m_, l, T, n) in rm if m_ == METHODS[0] and (METHODS[2], l, T, n) in rm]
    res.append({"variable": "minimum RMSE ratio, smooth ES optimised initials over statsforecast AutoETS",
                "value": min(ratios), "conditions": {"cells": len(ratios)}})
    res.append({"variable": "maximum RMSE ratio, smooth ES optimised initials over statsforecast AutoETS",
                "value": max(ratios), "conditions": {"cells": len(ratios)}})
    if 50 in a.T:
        n = sum(rm[(METHODS[1], l, 50, nm)] < rm[(METHODS[0], l, 50, nm)]
                for (m_, l, T, nm) in rm if m_ == METHODS[0] and T == 50)
        res.append({"variable": "cells at T=50 with lower RMSE for smooth ES backcasting than optimised initials",
                    "value": float(n), "conditions": {"cells": 8}})
    if 50 in a.T and 500 in a.T:
        for meth in METHODS:
            n = sum(rm[(meth, l, 500, nm)] >= rm[(meth, l, 50, nm)]
                    for (m_, l, T, nm) in rm if m_ == meth and T == 50)
            res.append({"variable": "cells with RMSE at T=500 not below RMSE at T=50",
                        "value": float(n), "conditions": {"method": meth, "cells": 8}})
    for meth in METHODS:
        res.append({"variable": "computing seconds", "value": secs[meth], "unit": "s",
                    "conditions": {"method": meth, "R": a.R}})
    res.append({"variable": "computing seconds", "value": time.time() - t_start, "unit": "s",
                "conditions": {"method": "all, including simulation", "R": a.R}})
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as fh:
            json.dump(res, fh)


if __name__ == "__main__":
    main()
