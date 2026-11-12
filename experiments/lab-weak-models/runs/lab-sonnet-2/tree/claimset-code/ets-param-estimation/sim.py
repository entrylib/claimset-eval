"""Monte Carlo: ETS smoothing-parameter estimation, smooth.ES vs statsforecast AutoETS.

Writes results as JSON to $CLAIMSET_RESULTS and per-fit details to $CLAIMSET_RUN_DIR/fits.csv.
"""
import argparse, json, math, os, sys, time, warnings
import numpy as np
from multiprocessing import Pool

M = 12
L0, B0 = 100.0, 1.0
S0 = [10.0 * math.sin(2 * math.pi * j / M) for j in range(M)]
# (process label, form, season_length, true params)
SETS = [
    ("ANN", "ANN", 1, {"alpha": 0.1}),
    ("ANN", "ANN", 1, {"alpha": 0.5}),
    ("AAN", "AAN", 1, {"alpha": 0.3, "beta": 0.05}),
    ("AAN", "AAN", 1, {"alpha": 0.5, "beta": 0.2}),
    ("ANA", "ANA", M, {"alpha": 0.2, "gamma": 0.1}),
]
ARMS = ["smooth optimised", "smooth backcasting", "statsforecast"]
BOUND_TOL = 1e-3


def simulate(form, p, T, rng):
    e = rng.standard_normal(T)
    y = np.empty(T)
    l, b = L0, B0
    s = list(S0)
    a = p["alpha"]
    for t in range(T):
        if form == "ANN":
            y[t] = l + e[t]; l = l + a * e[t]
        elif form == "AAN":
            y[t] = l + b + e[t]; l = l + b + a * e[t]; b = b + p["beta"] * e[t]
        else:
            k = t % M
            y[t] = l + s[k] + e[t]; l = l + a * e[t]; s[k] = s[k] + p["gamma"] * e[t]
    return y


def fit_smooth(y, form, m, initial):
    from smooth import ES
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mod = ES(model=form, lags=[m] if m > 1 else None, initial=initial, loss="likelihood", bounds="usual")
        mod.fit(y)
    pv = mod.persistence_vector
    est = {"alpha": pv.get("alpha"), "beta": pv.get("beta"), "gamma": pv.get("gamma")}
    ok_form = str(mod.model_name).replace("ETS(", "").replace(")", "").replace(",", "") == form or form in str(getattr(mod, "model_type", ""))
    return est, len(w), ok_form


def fit_sf(y, form, m):
    from statsforecast.models import AutoETS
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mod = AutoETS(model=form, season_length=m).fit(y)
    par = mod.model_["par"]
    est = {"alpha": float(par[0]), "beta": float(par[1]), "gamma": float(par[2])}
    ok_form = mod.model_["components"][:3] == form
    return est, len(w), ok_form


def bound_hit(name, v, est):
    a = est["alpha"]
    if name == "alpha":
        lo, hi = 0.0, 1.0
    elif name == "beta":
        lo, hi = 0.0, a
    else:
        lo, hi = 0.0, 1.0 - a
    return int(abs(v - lo) < BOUND_TOL or abs(v - hi) < BOUND_TOL)


def one_cell(task):
    si, T, R, seed = task
    label, form, m, p = SETS[si]
    t0 = time.time()
    rows = []
    for r in range(R):
        rng = np.random.default_rng(np.random.SeedSequence([seed, si, T, r]))
        y = simulate(form, p, T, rng)
        for arm in ARMS:
            try:
                if arm == "smooth optimised":
                    est, nw, okf = fit_smooth(y, form, m, "optimal")
                elif arm == "smooth backcasting":
                    est, nw, okf = fit_smooth(y, form, m, "backcasting")
                else:
                    est, nw, okf = fit_sf(y, form, m)
                err = ""
                vals = {k: est[k] for k in p}
                if not okf:
                    err = "form changed"
                if any(v is None or not np.isfinite(v) for v in vals.values()):
                    err = err or "non-finite estimate"
            except Exception as ex:
                err, nw, vals = "error: " + type(ex).__name__ + ": " + str(ex)[:80], 0, {}
            for k, tv in p.items():
                v = vals.get(k) if not err else None
                rows.append(dict(set=si, process=label, T=T, rep=r, arm=arm, param=k, true=tv,
                                 est=v, fail=int(bool(err)), warned=int(nw > 0),
                                 bound=(bound_hit(k, v, vals) if v is not None else 0), err=err))
    return rows, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=300)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--Ts", type=int, nargs="+", default=[50, 100, 250, 500])
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--sets", type=int, nargs="+", default=list(range(len(SETS))))
    a = ap.parse_args()
    tasks = [(si, T, a.R, a.seed) for T in sorted(a.Ts, reverse=True) for si in a.sets]
    rows, timing = [], {}
    with Pool(a.procs) as pool:
        for rr, dt in pool.imap_unordered(one_cell, tasks):
            rows += rr
            timing[(rr[0]["set"], rr[0]["T"])] = dt
    outdir = os.environ.get("CLAIMSET_RUN_DIR", ".")
    import csv
    with open(os.path.join(outdir, "fits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    results = summarise(rows, a)
    total = sum(timing.values())
    results.append({"variable": "cell compute time (summed over cells)", "value": total, "unit": "s"})
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as f:
            json.dump(results, f)
    print("rows", len(rows), "cpu-seconds", round(total, 1))


def label(si):
    l, _, _, p = SETS[si]
    return f"ETS({','.join(l)}) " + ",".join(f"{k}={v}" for k, v in p.items())


def summarise(rows, a):
    res = []
    import collections
    g = collections.defaultdict(list)
    for r in rows:
        g[(r["set"], r["T"], r["arm"], r["param"])].append(r)
    stat = {}
    for (si, T, arm, k), rs in sorted(g.items()):
        ok = [r for r in rs if not r["fail"]]
        cond = {"method": arm, "process": label(si), "parameter": k, "T": T}
        res.append({"variable": "replicates", "value": len(rs), "conditions": cond})
        res.append({"variable": "failure", "value": len(rs) - len(ok), "conditions": cond})
        res.append({"variable": "bound hit", "value": sum(r["bound"] for r in ok), "conditions": cond})
        res.append({"variable": "warned fits", "value": sum(r["warned"] for r in ok), "conditions": cond})
        if len(ok) < 2:
            continue
        d = np.array([r["est"] - r["true"] for r in ok])
        bias, se = d.mean(), d.std(ddof=1) / math.sqrt(len(d))
        rmse, mae = math.sqrt((d ** 2).mean()), np.abs(d).mean()
        stat[(si, T, arm, k)] = (bias, se, rmse)
        res.append({"variable": "bias", "value": bias, "conditions": cond,
                    "interval": {"level": 0.90, "lower": bias - 1.645 * se, "upper": bias + 1.645 * se}})
        res.append({"variable": "RMSE", "value": rmse, "conditions": cond})
        res.append({"variable": "MAE", "value": float(mae), "conditions": cond})
    Ts = sorted(set(k[1] for k in stat))
    Tlo, Thi = min(Ts), max(Ts)
    # H1: share of (arm, set, parameter) series with RMSE at Thi below RMSE at Tlo
    keys = sorted(set((k[0], k[2], k[3]) for k in stat))
    falls = [stat[(s, Thi, arm, p)][2] < stat[(s, Tlo, arm, p)][2] for (s, arm, p) in keys
             if (s, Thi, arm, p) in stat and (s, Tlo, arm, p) in stat]
    res.append({"variable": "share of series with RMSE lower at largest T than at smallest T",
                "value": sum(falls) / len(falls), "conditions": {"n series": len(falls)}})
    # H2, H3: shares of comparisons
    def share(a1, a2):
        ks = [(s, T, p) for (s, T, arm, p) in stat if arm == a1 and (s, T, a2, p) in stat]
        w = [stat[(s, T, a1, p)][2] < stat[(s, T, a2, p)][2] for (s, T, p) in ks]
        return sum(w) / len(w), len(w)
    v, n = share("smooth optimised", "statsforecast")
    res.append({"variable": "share of comparisons with RMSE lower, smooth optimised vs statsforecast", "value": v, "conditions": {"n comparisons": n}})
    v, n = share("smooth backcasting", "smooth optimised")
    res.append({"variable": "share of comparisons with RMSE lower, smooth backcasting vs smooth optimised", "value": v, "conditions": {"n comparisons": n}})
    # H4-H6: bias bounds at largest T
    for arm in ARMS:
        hi, lo = [], []
        for (s, T, ar, p), (b, se, _) in stat.items():
            if ar == arm and T == Thi:
                hi.append(abs(b) + 1.645 * se); lo.append(max(0.0, abs(b) - 1.645 * se))
        res.append({"variable": "max upper 90% bound of absolute bias at largest T", "value": max(hi), "conditions": {"method": arm}})
        res.append({"variable": "max lower 90% bound of absolute bias at largest T", "value": max(lo), "conditions": {"method": arm}})
    # exclusion counts
    for arm in ARMS:
        nf = sum(1 for r in rows if r["arm"] == arm and r["fail"] and r["param"] == "alpha")
        res.append({"variable": "fits excluded by failure", "value": nf, "conditions": {"method": arm}})
    return res


if __name__ == "__main__":
    main()
