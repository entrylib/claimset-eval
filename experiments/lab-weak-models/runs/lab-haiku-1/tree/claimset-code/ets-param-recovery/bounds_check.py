"""Check the parameter bounds each implementation actually applies.

Series: ETS(A,A,N) with a moving trend (alpha 0.5, beta 0.8 innovation scale), simulated with a fixed seed.
Reports the beta estimate of statsforecast ets_f (model AAN) and smooth ES (AAN, initial='optimal') on it.
Writes results to $CLAIMSET_RESULTS and, if set, a text report to $CLAIMSET_RUN_DIR.

Usage: python3 bounds_check.py --seed 2026
"""
import json
import os
import sys

import numpy as np
from smooth import ES
from statsforecast.ets import ets_f


def main():
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 2026
    rng = np.random.default_rng(seed)
    n = 300
    e = rng.standard_normal(n)
    eps2 = rng.standard_normal(n)
    level, slope = np.empty(n), np.empty(n)
    level[0], slope[0] = 100.0, 1.0
    for t in range(1, n):
        slope[t] = slope[t - 1] + 0.8 * e[t - 1]
        level[t] = level[t - 1] + slope[t - 1] + 0.5 * e[t - 1]
    y = level + eps2

    sf = ets_f(y, m=1, model="AAN")
    sf_alpha, sf_beta = float(sf["par"][0]), float(sf["par"][1])
    sm = ES(model="AAN", initial="optimal").fit(y)
    sm_alpha, sm_beta = float(sm.persistence_level_), float(sm.persistence_trend_)

    # statsforecast's starting alpha for m=1, from initparam: lower + 0.2 * (upper - lower) / m
    sf_beta_cap = 0.0001 + 0.2 * (0.9999 - 0.0001) / 1
    results = [
        {"variable": "estimated beta", "value": sf_beta,
         "conditions": {"method": "statsforecast ets_f", "series": "ETS(A,A,N) moving trend", "seed": seed}},
        {"variable": "estimated beta", "value": sm_beta,
         "conditions": {"method": "smooth ES, optimised initial states", "series": "ETS(A,A,N) moving trend",
                        "seed": seed}},
        {"variable": "estimated alpha", "value": sf_alpha,
         "conditions": {"method": "statsforecast ets_f", "series": "ETS(A,A,N) moving trend", "seed": seed}},
        {"variable": "estimated alpha", "value": sm_alpha,
         "conditions": {"method": "smooth ES, optimised initial states", "series": "ETS(A,A,N) moving trend",
                        "seed": seed}},
        {"variable": "statsforecast beta upper limit from starting alpha", "value": sf_beta_cap,
         "conditions": {"method": "statsforecast ets_f", "series": "ETS(A,A,N) moving trend", "seed": seed}},
    ]
    report = (f"seed {seed}: statsforecast alpha={sf_alpha:.4f} beta={sf_beta:.4f} "
              f"(cap {sf_beta_cap:.4f}); smooth alpha={sm_alpha:.4f} beta={sm_beta:.4f}\n")
    print(report, end="")

    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as f:
            json.dump(results, f)
    run_dir = os.environ.get("CLAIMSET_RUN_DIR")
    if run_dir:
        with open(os.path.join(run_dir, "bounds_check.txt"), "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
