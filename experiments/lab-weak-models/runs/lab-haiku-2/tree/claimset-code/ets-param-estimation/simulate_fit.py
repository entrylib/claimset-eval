"""Simulate ETS series with known parameters and estimate them with smooth and statsforecast.

Usage: python3 simulate_fit.py --reps R [--lengths 50 100 250 500] [--seed 20261111]
Writes results to $CLAIMSET_RESULTS (JSON list) and per-replicate estimates to $CLAIMSET_RUN_DIR.
"""
import argparse, csv, json, math, os, time
import numpy as np

M = 12
SETTINGS = [  # (process, parameter names, values)
    ("ETS(A,N,N)", ("alpha",), (0.1,)),
    ("ETS(A,N,N)", ("alpha",), (0.5,)),
    ("ETS(A,A,N)", ("alpha", "beta"), (0.3, 0.05)),
    ("ETS(A,A,N)", ("alpha", "beta"), (0.5, 0.2)),
    ("ETS(A,N,A)", ("alpha", "gamma"), (0.2, 0.1)),
]
FORM = {"ETS(A,N,N)": "ANN", "ETS(A,A,N)": "AAN", "ETS(A,N,A)": "ANA"}
BASE_SEED = 20261111
TOL = 1e-4  # an estimate within TOL of a bound counts as on that bound
ARMS = ("smooth_backcasting", "smooth_optimised", "statsforecast_optimised")


def simulate(process, pars, T, rng):
    """Innovations form, sigma = 1. l0 = 100, b0 = 1, seasonal states 10 sin(2 pi k / 12), k = 0..11,
    where observation t (1-based) has season index (t - 1) mod 12. No burn-in."""
    eps = rng.standard_normal(T)
    y = np.empty(T)
    l = 100.0
    if process == "ETS(A,N,N)":
        a = pars["alpha"]
        for t in range(T):
            y[t] = l + eps[t]
            l = l + a * eps[t]
    elif process == "ETS(A,A,N)":
        a, b_ = pars["alpha"], pars["beta"]
        b = 1.0
        for t in range(T):
            y[t] = l + b + eps[t]
            l, b = l + b + a * eps[t], b + b_ * eps[t]
    elif process == "ETS(A,N,A)":
        a, g = pars["alpha"], pars["gamma"]
        s = 10.0 * np.sin(2 * np.pi * np.arange(M) / M)
        for t in range(T):
            k = t % M
            y[t] = l + s[k] + eps[t]
            l, s[k] = l + a * eps[t], s[k] + g * eps[t]
    else:
        raise ValueError(process)
    return y


def fit_smooth(y, process, pars_names, optimised):
    from smooth import ES
    lags = [1, M] if process == "ETS(A,N,A)" else [1]
    kw = dict(model=FORM[process], lags=lags, loss="likelihood", bounds="usual",
              initial="optimal" if optimised else "backcasting")
    m = ES(**kw)
    m.fit(y)
    est = {"alpha": m.persistence_level_}
    if "beta" in pars_names:
        est["beta"] = m.persistence_trend_
    if "gamma" in pars_names:
        g = np.atleast_1d(np.asarray(m.persistence_seasonal_, dtype=float)).ravel()
        if g.size != 1:
            raise ValueError("expected one seasonal smoothing parameter, got %d" % g.size)
        est["gamma"] = g[0]
    return {k: float(v) for k, v in est.items()}


def fit_statsforecast(y, process, pars_names):
    from statsforecast.models import ets_f
    m = M if process == "ETS(A,N,A)" else 1
    r = ets_f(y, m=m, model=FORM[process])
    par = r["par"]
    est = {"alpha": par[0]}
    if "beta" in pars_names:
        est["beta"] = par[1]
    if "gamma" in pars_names:
        est["gamma"] = par[2]
    return {k: float(v) for k, v in est.items()}


def on_bound(est):
    a = est["alpha"]
    flags = {}
    flags["alpha"] = a <= TOL or a >= 1 - TOL
    if "beta" in est:
        b = est["beta"]
        flags["beta"] = b <= TOL or abs(b - a) <= TOL
    if "gamma" in est:
        g = est["gamma"]
        flags["gamma"] = g <= TOL or abs(g - (1 - a)) <= TOL
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--lengths", type=int, nargs="+", default=[50, 100, 250, 500])
    ap.add_argument("--seed", type=int, default=BASE_SEED)
    ap.add_argument("--settings", type=int, nargs="*", default=None,
                    help="indices into SETTINGS (default all)")
    args = ap.parse_args()
    settings = [SETTINGS[i] for i in args.settings] if args.settings else SETTINGS

    run_dir = os.environ.get("CLAIMSET_RUN_DIR", ".")
    os.makedirs(run_dir, exist_ok=True)
    rows = []
    timing = {}
    for si, (process, names, values) in enumerate(SETTINGS):
        if (process, names, values) not in settings:
            continue
        pars = dict(zip(names, values))
        for T in args.lengths:
            for r in range(args.reps):
                rng = np.random.default_rng([args.seed, si, T, r])
                y = simulate(process, pars, T, rng)
                for arm in ARMS:
                    t0 = time.perf_counter()
                    status, est = "ok", None
                    try:
                        if arm == "statsforecast_optimised":
                            est = fit_statsforecast(y, process, names)
                        else:
                            est = fit_smooth(y, process, names, arm == "smooth_optimised")
                        if not all(math.isfinite(v) for v in est.values()):
                            status, est = "nonfinite", None
                    except Exception as exc:  # counted, not dropped
                        status, est = "error:" + type(exc).__name__, None
                    dt = time.perf_counter() - t0
                    timing[arm] = timing.get(arm, 0.0) + dt
                    row = {"arm": arm, "process": process, "setting": si, "T": T, "rep": r,
                           "status": status, "seconds": round(dt, 4)}
                    for p in names:
                        row["true_" + p] = pars[p]
                        row["est_" + p] = est[p] if est else ""
                    if est:
                        bflags = on_bound(est)
                        row["on_bound"] = ";".join(k for k, v in bflags.items() if v)
                    else:
                        row["on_bound"] = ""
                    rows.append(row)

    with open(os.path.join(run_dir, "estimates.csv"), "w", newline="") as f:
        keys = sorted({k for row in rows for k in row}, key=lambda k: (k not in ("arm", "process", "setting", "T", "rep", "status"), k))
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    results = []
    for arm in ARMS:
        for si, (process, names, values) in enumerate(SETTINGS):
            if (process, names, values) not in settings:
                continue
            setting_label = ", ".join(f"{p}={v}" for p, v in zip(names, values))
            for T in args.lengths:
                cell = [x for x in rows if x["arm"] == arm and x["setting"] == si and x["T"] == T]
                cond = {"method": arm, "process": process, "setting": setting_label, "series length": T}
                n_err = sum(1 for x in cell if x["status"].startswith("error"))
                n_nf = sum(1 for x in cell if x["status"] == "nonfinite")
                results.append({"variable": "failed fits (excluded)", "value": n_err, "conditions": cond})
                results.append({"variable": "non-finite estimates (excluded)", "value": n_nf, "conditions": cond})
                ok = [x for x in cell if x["status"] == "ok"]
                for p, v in zip(names, values):
                    est = np.array([float(x["est_" + p]) for x in ok])
                    err = est - v
                    pc = dict(cond, **{"parameter": p})
                    nb = sum(1 for x in ok if p in x["on_bound"].split(";"))
                    results.append({"variable": f"estimates on a bound of {p} (included)", "value": nb, "conditions": pc})
                    if len(err):
                        results.append({"variable": f"bias of {p} estimate", "value": float(err.mean()), "conditions": pc})
                        results.append({"variable": f"RMSE of {p} estimate", "value": float(np.sqrt((err ** 2).mean())), "conditions": pc})
                        results.append({"variable": f"MAE of {p} estimate", "value": float(np.abs(err).mean()), "conditions": pc})
                    results.append({"variable": "valid fits", "value": len(ok), "conditions": pc})

    # Decision counts for the confirmatory hypotheses (fixed thresholds; see the plan).
    rmse, bias = {}, {}
    for arm in ARMS:
        for si, (process, names, values) in enumerate(SETTINGS):
            if (process, names, values) not in settings:
                continue
            for T in args.lengths:
                ok = [x for x in rows if x["arm"] == arm and x["setting"] == si and x["T"] == T and x["status"] == "ok"]
                for p, v in zip(names, values):
                    err = np.array([float(x["est_" + p]) - v for x in ok])
                    if len(err):
                        rmse[(arm, si, p, T)] = float(np.sqrt((err ** 2).mean()))
                        bias[(arm, si, p, T)] = float(err.mean())
    keys1 = [k for k in rmse if k[3] == min(args.lengths)]
    viol1 = viol2 = viol3 = 0
    t_lo, t_hi = min(args.lengths), max(args.lengths)
    for arm, si, p, T in keys1:
        if (arm, si, p, t_hi) in rmse and rmse[(arm, si, p, t_hi)] >= 0.5 * rmse[(arm, si, p, t_lo)]:
            viol1 += 1
    for arm, si, p, T in [k for k in rmse if k[0] == "smooth_optimised"]:
        sf = rmse.get(("statsforecast_optimised", si, p, T))
        if sf is not None:
            ratio = sf / rmse[(arm, si, p, T)]
            if ratio < 0.9 or ratio > 1.1:
                viol2 += 1
    for (arm, si, p, T), b in bias.items():
        if T == t_hi and abs(b) > 0.02:
            viol3 += 1
    results.append({"variable": "H1 violations (count)", "value": viol1, "conditions": {"hypothesis": "H1"}})
    results.append({"variable": "H2 violations (count)", "value": viol2, "conditions": {"hypothesis": "H2"}})
    results.append({"variable": "H3 violations (count)", "value": viol3, "conditions": {"hypothesis": "H3"}})

    out = os.environ.get("CLAIMSET_RESULTS", os.path.join(run_dir, "results.json"))
    with open(out, "w") as f:
        json.dump(results, f)
    print("replicates:", args.reps, "lengths:", args.lengths)
    for arm in ARMS:
        print(arm, "total seconds:", round(timing.get(arm, 0.0), 1))


if __name__ == "__main__":
    main()
