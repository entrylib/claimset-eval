"""What leaving `damped` unset in statsforecast does to the ETS(A,A,N) arm (three of the four lab runs did).

Refits the reference's ETS(A,A,N) series with AutoETS(model="AAN", season_length=1) (damped unset, so it chooses
between ETS(A,A,N) and ETS(A,Ad,N) by AICc) and writes damped_check.csv: per DGP and T, how many fits chose a
damped trend, and bias and RMSE of alpha and beta from these fits, beside the fixed-form arm (damped=False).
"""
import csv, os, warnings
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import simulate as S


def job(args):
    di, ti = args
    warnings.filterwarnings("ignore")
    from statsforecast.models import AutoETS
    dgp, form, par = S.DGPS[di]
    n = S.TS[ti]
    rows = []
    for r in range(300):
        y = S.simulate(form, par, n, np.random.default_rng([S.BASE_SEED, di, n, r]))
        f = AutoETS(model="AAN", season_length=1).fit(y).model_
        rows.append((f["method"], float(f["par"][0]), float(f["par"][1])))
    return dgp, n, par, rows


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    fixed = {}
    with open(os.path.join(here, "summary.csv")) as f:
        for r in csv.DictReader(f):
            if r["arm"] == "statsforecast":
                fixed[(r["dgp"], int(r["T"]), r["parameter"])] = (float(r["bias"]), float(r["rmse"]))
    jobs = [(di, ti) for di, d in enumerate(S.DGPS) if d[1] == "AAN" for ti in range(len(S.TS))]
    out = []
    with ProcessPoolExecutor(4) as ex:
        for dgp, n, par, rows in ex.map(job, jobs):
            damped = sum(m == "ETS(A,Ad,N)" for m, _, _ in rows)
            for i, p in ((1, "alpha"), (2, "beta")):
                d = np.array([r[i] for r in rows]) - par[p]
                fb, fr = fixed[(dgp, n, p)]
                out.append({"dgp": dgp, "T": n, "parameter": p, "n_damped_chosen": damped, "n": len(rows),
                            "bias_damped_unset": float(d.mean()), "rmse_damped_unset": float(np.sqrt((d ** 2).mean())),
                            "bias_fixed_form": fb, "rmse_fixed_form": fr})
    with open(os.path.join(here, "damped_check.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)


if __name__ == "__main__":
    main()
