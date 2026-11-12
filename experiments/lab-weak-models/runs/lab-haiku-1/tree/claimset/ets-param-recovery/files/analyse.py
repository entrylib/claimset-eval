"""Summarise the replicate file written by simulate.py.

Reads the replicate CSV as data (--replicates PATH), prints bias, RMSE and MAE of successful fits,
and writes the share of fits on a bound per arm, process, length and parameter to $CLAIMSET_RESULTS.
Failures are counted, not dropped.

Usage: python3 analyse.py --replicates PATH [--output share|error]

--output error writes bias, RMSE and MAE of successful fits instead of the share on a bound.
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

TRUE = {
    "ETS(A,N,N) alpha=0.1": {"alpha": 0.1},
    "ETS(A,N,N) alpha=0.5": {"alpha": 0.5},
    "ETS(A,A,N) alpha=0.3 beta=0.05": {"alpha": 0.3, "beta": 0.05},
    "ETS(A,A,N) alpha=0.5 beta=0.2": {"alpha": 0.5, "beta": 0.2},
    "ETS(A,N,A) m=12 alpha=0.2 gamma=0.1": {"alpha": 0.2, "gamma": 0.1},
}
ARM_LABEL = {
    "smooth_opt": "smooth ES, optimised initial states",
    "smooth_bc": "smooth ES, backcasting initial states (default)",
    "sf": "statsforecast ets_f, optimised initial states",
}


OUTPUT = sys.argv[sys.argv.index("--output") + 1] if "--output" in sys.argv else "share"


def main():
    path = sys.argv[sys.argv.index("--replicates") + 1]
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for r in rows:
        groups[(r["process"], int(r["T"]), r["arm"])].append(r)

    results = []
    for (proc, T, arm), sub in sorted(groups.items()):
        ok = [r for r in sub if r["status"] == "ok"]
        failed = len(sub) - len(ok)
        for par, true in TRUE[proc].items():
            err = [float(r["est_" + par]) - true for r in ok]
            n = len(err)
            bias = sum(err) / n
            rmse = math.sqrt(sum(e * e for e in err) / n)
            mae = sum(abs(e) for e in err) / n
            share = sum(int(r["on_bound_" + par]) for r in ok) / n
            print(f"{proc:38s} T={T:<4d} {arm:10s} {par:5s} n_ok={n} failed={failed} "
                  f"bias={bias:+.4f} rmse={rmse:.4f} mae={mae:.4f} on_bound={share:.3f}")
            cond = {"method": ARM_LABEL[arm], "process": proc, "sample size": T, "parameter": par}
            if OUTPUT == "error":
                results.append({"variable": "bias of smoothing parameter estimates", "value": bias, "conditions": cond})
                results.append({"variable": "RMSE of smoothing parameter estimates", "value": rmse, "conditions": cond})
                results.append({"variable": "MAE of smoothing parameter estimates", "value": mae, "conditions": cond})
            else:
                results.append({"variable": "share of estimates on a bound", "value": share, "conditions": cond})

    path_out = os.environ.get("CLAIMSET_RESULTS")
    if path_out:
        with open(path_out, "w") as f:
            json.dump(results, f)


if __name__ == "__main__":
    main()
