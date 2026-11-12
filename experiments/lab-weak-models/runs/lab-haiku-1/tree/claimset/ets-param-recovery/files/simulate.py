"""Monte Carlo comparison of smooth and statsforecast estimates of ETS smoothing parameters.

Data: innovations-form ETS with additive N(0,1) errors, state initialisation as in the study brief.
Arms (same simulated series for all arms, common random numbers):
  smooth_opt   smooth ES, initial='optimal'          (primary)
  smooth_bc    smooth ES, initial='backcasting'      (smooth's default, reported separately)
  sf           statsforecast ets_f, optimised initial states (primary)

Writes per-replicate rows to $CLAIMSET_RUN_DIR/replicates.csv and aggregated results to $CLAIMSET_RESULTS.
Failures (exceptions or non-finite estimates) and estimates on a bound are counted, not dropped.

Usage: python3 simulate.py --seed 2026 --reps 300
"""
import csv
import json
import math
import os
import sys
import time

import numpy as np
from smooth import ES
from statsforecast.ets import ets_f

M = 12
LEVEL0, TREND0 = 100.0, 1.0
SEASON0 = 10.0 * np.sin(2 * np.pi * np.arange(M) / M)
LENGTHS = [50, 100, 250, 500]

# (label, model code, alpha, beta, gamma)
PROCESSES = [
    ("ETS(A,N,N) alpha=0.1", "ANN", 0.1, None, None),
    ("ETS(A,N,N) alpha=0.5", "ANN", 0.5, None, None),
    ("ETS(A,A,N) alpha=0.3 beta=0.05", "AAN", 0.3, 0.05, None),
    ("ETS(A,A,N) alpha=0.5 beta=0.2", "AAN", 0.5, 0.2, None),
    ("ETS(A,N,A) m=12 alpha=0.2 gamma=0.1", "ANA", 0.2, None, 0.1),
]
ARMS = ["smooth_opt", "smooth_bc", "sf"]
ARM_LABEL = {
    "smooth_opt": "smooth ES, optimised initial states",
    "smooth_bc": "smooth ES, backcasting initial states (default)",
    "sf": "statsforecast ets_f, optimised initial states",
}
PARAMS = {"ANN": ["alpha"], "AAN": ["alpha", "beta"], "ANA": ["alpha", "gamma"]}
# Bounds of each implementation used for the 'on a bound' count.
SM_BOX = (0.0, 1.0)
SF_BOX = (0.0001, 0.9999)
SF_BETA_CAP = 0.0001 + 0.2 * (0.9999 - 0.0001) / 1  # starting alpha for m=1 (initparam)
TOL = 1e-3


def simulate(code, T, rng, alpha, beta, gamma):
    e = rng.standard_normal(T)
    y = np.empty(T)
    if code == "ANN":
        lev = LEVEL0
        for t in range(T):
            y[t] = lev + e[t]
            lev = lev + alpha * e[t]
    elif code == "AAN":
        lev, tr = LEVEL0, TREND0
        for t in range(T):
            y[t] = lev + tr + e[t]
            lev, tr = lev + tr + alpha * e[t], tr + beta * e[t]
    else:  # ANA
        lev = LEVEL0
        seas = SEASON0.copy()
        for t in range(T):
            s = seas[t % M]
            y[t] = lev + s + e[t]
            lev = lev + alpha * e[t]
            seas[t % M] = s + gamma * e[t]
    return y


def on_bound(value, box, tol=TOL):
    lo, hi = box
    return value <= lo + tol or value >= hi - tol


def fit(arm, code, y):
    """Return dict of parameter estimates (nan where not estimated) and flags."""
    out = {"alpha": math.nan, "beta": math.nan, "gamma": math.nan}
    flags = {"alpha": False, "beta": False, "gamma": False}
    if arm == "sf":
        r = ets_f(y, m=M if code == "ANA" else 1, model=code)
        par = np.asarray(r["par"], dtype=float)
        out["alpha"] = float(par[0])
        if code == "AAN":
            out["beta"] = float(par[1])
        if code == "ANA":
            out["gamma"] = float(par[2])
        box = SF_BOX
        flags["alpha"] = on_bound(out["alpha"], box)
        if code == "AAN":
            flags["beta"] = on_bound(out["beta"], box) or out["beta"] >= SF_BETA_CAP - TOL
        if code == "ANA":
            flags["gamma"] = on_bound(out["gamma"], box)
    else:
        init = "optimal" if arm == "smooth_opt" else "backcasting"
        lags = [M] if code == "ANA" else None
        m = ES(model=code, lags=lags, initial=init).fit(y)
        out["alpha"] = float(m.persistence_level_)
        if code == "AAN":
            out["beta"] = float(m.persistence_trend_)
        if code == "ANA":
            out["gamma"] = float(np.ravel(m.persistence_seasonal_)[0])
        flags["alpha"] = on_bound(out["alpha"], SM_BOX)
        if code == "AAN":
            flags["beta"] = on_bound(out["beta"], SM_BOX) or out["beta"] >= out["alpha"] - TOL
        if code == "ANA":
            flags["gamma"] = on_bound(out["gamma"], SM_BOX)
    return out, flags


def main():
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 2026
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 300
    run_dir = os.environ.get("CLAIMSET_RUN_DIR", ".")
    rows = []
    t0 = time.time()
    for p_idx, (label, code, alpha, beta, gamma) in enumerate(PROCESSES):
        true = {"alpha": alpha, "beta": beta, "gamma": gamma}
        for T_idx, T in enumerate(LENGTHS):
            for rep in range(reps):
                # one seed per (process, length, replicate), shared by all arms
                s = seed * 10_000_000 + p_idx * 1_000_000 + T_idx * 100_000 + rep
                y = simulate(code, T, np.random.default_rng(s), alpha, beta, gamma)
                for arm in ARMS:
                    try:
                        est, flags = fit(arm, code, y)
                        status = "ok"
                        bad = [k for k in PARAMS[code] if not math.isfinite(est[k])]
                        if bad:
                            status = "nonfinite"
                    except Exception as exc:  # counted as a failure, never dropped
                        est, flags = {"alpha": math.nan, "beta": math.nan, "gamma": math.nan}, {}
                        status = "error:" + type(exc).__name__
                    rows.append({"process": label, "code": code, "T": T, "rep": rep, "seed": s,
                                 "arm": arm, "status": status,
                                 **{f"est_{k}": est[k] for k in ("alpha", "beta", "gamma")},
                                 **{f"on_bound_{k}": int(bool(flags.get(k, False)))
                                    for k in ("alpha", "beta", "gamma")}})
    print(f"fits: {len(rows)} in {time.time() - t0:.1f} s", flush=True)

    with open(os.path.join(run_dir, "replicates.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    results = []
    for label, code, alpha, beta, gamma in PROCESSES:
        true = {"alpha": alpha, "beta": beta, "gamma": gamma}
        for T in LENGTHS:
            for arm in ARMS:
                sub = [r for r in rows if r["process"] == label and r["T"] == T and r["arm"] == arm]
                ok = [r for r in sub if r["status"] == "ok"]
                failed = len(sub) - len(ok)
                cond = {"method": ARM_LABEL[arm], "process": label, "sample size": T}
                results.append({"variable": "failed fits", "value": failed,
                                "conditions": {**cond}})
                for k in PARAMS[code]:
                    est = np.array([r[f"est_{k}"] for r in ok], dtype=float)
                    err = est - true[k]
                    kc = {**cond, "parameter": k}
                    results.append({"variable": "replicates used", "value": len(ok), "conditions": kc})
                    results.append({"variable": "bias of smoothing parameter estimates",
                                    "value": float(np.mean(err)), "conditions": kc})
                    results.append({"variable": "RMSE of smoothing parameter estimates",
                                    "value": float(np.sqrt(np.mean(err ** 2))), "conditions": kc})
                    results.append({"variable": "MAE of smoothing parameter estimates",
                                    "value": float(np.mean(np.abs(err))), "conditions": kc})
                    nb = sum(r[f"on_bound_{k}"] for r in ok)
                    results.append({"variable": "estimates on a bound", "value": nb, "conditions": kc})

    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as f:
            json.dump(results, f)


if __name__ == "__main__":
    main()
