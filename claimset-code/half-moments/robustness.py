"""Plan PL3 (question Q3): how each measure responds to one value moved k standard deviations from the mean.

Single-outlier contamination: base distributions normal(0,1), Student t(5), exponential(1); n = 100 and 1000;
10000 replications for each base distribution and n, the same clean samples for every k; the first value of each
sample replaced by mu + k sigma, k = 0.5, 1, 2, 3, 5, 10, 20, 50, 100; seed 20261120 for the first base
distribution and n, incremented for each next one.

Results ($CLAIMSET_RESULTS):
- "standardised shift": (mean of the measure on contaminated samples - its mean on clean samples) / its standard
  deviation on clean samples, conditions {measure, distribution, n, k};
- "Monte Carlo standard error of the standardised shift": sd of the paired differences / sqrt(replications),
  divided by the same clean standard deviation;
- "growth exponent of the standardised shift": the least-squares slope of log |shift| on log k over k = 10, 20,
  50, 100, conditions {measure, distribution, n}.
Usage: python3 robustness.py [--replications R] [--sizes 100,1000]  (defaults are the plan's)
"""
import argparse
import json
import os

import numpy as np

from measures import ALL

KS = [0.5, 1, 2, 3, 5, 10, 20, 50, 100]
BASES = [  # name, generator, mean, standard deviation
    ("normal(0,1)", lambda r, s: r.standard_normal(s), 0.0, 1.0),
    ("t(5)", lambda r, s: r.standard_t(5, s), 0.0, float(np.sqrt(5 / 3))),
    ("exponential(1)", lambda r, s: r.exponential(1.0, s), 1.0, 1.0),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replications", type=int, default=10000)
    ap.add_argument("--sizes", default="100,1000")
    ap.add_argument("--chunk", type=int, default=500)
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    results = []
    seed = 20261120
    for name, gen, mu, sd in BASES:
        for n in sizes:
            rng = np.random.default_rng(seed)
            seed += 1
            clean = {m: [] for m in ALL}
            diffs = {(m, k): [] for m in ALL for k in KS}
            done = 0
            while done < args.replications:
                c = min(args.chunk, args.replications - done)
                y = gen(rng, (c, n))
                base = {m: f(y) for m, f in ALL.items()}
                for m in ALL:
                    clean[m].append(base[m])
                for k in KS:
                    z = y.copy()
                    z[:, 0] = mu + k * sd
                    for m, f in ALL.items():
                        diffs[(m, k)].append(f(z) - base[m])
                done += c
            for m in ALL:
                s0 = np.concatenate(clean[m])
                sd0 = float(np.std(s0, ddof=1))
                shifts = []
                for k in KS:
                    d = np.concatenate(diffs[(m, k)])
                    shift = float(np.mean(d)) / sd0
                    se = float(np.std(d, ddof=1) / np.sqrt(len(d))) / sd0
                    cond = {"measure": m, "distribution": name, "n": n, "k": k}
                    results.append({"variable": "standardised shift", "value": shift, "conditions": cond})
                    results.append({"variable": "Monte Carlo standard error of the standardised shift", "value": se,
                                    "conditions": cond})
                    shifts.append(shift)
                big = [(k, s) for k, s in zip(KS, shifts) if k >= 10]
                if all(abs(s) > 0 for _, s in big):
                    x = np.log([k for k, _ in big])
                    yv = np.log([abs(s) for _, s in big])
                    slope = float(np.polyfit(x, yv, 1)[0])
                    results.append({"variable": "growth exponent of the standardised shift", "value": slope,
                                    "conditions": {"measure": m, "distribution": name, "n": n}})
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as fh:
            json.dump(results, fh)
    else:
        print(len(results), "results")


if __name__ == "__main__":
    main()
