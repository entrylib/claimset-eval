"""Plans PL12-PL14 (question Q6): what the half-moment coefficients gain over the existing measures on real data.

Data: the petroleum rock samples (data/rock.csv: Area, Perimeter, Shape, Permeability; 48 values each) and the daily
log returns of the European stock indices (data/EuStockMarkets.csv: DAX, SMI, CAC, FTSE; 1859 returns each).
Measures: every measure of measures.ALL (the half-moment coefficients and the eleven comparison measures).

    python3 benefits.py sensitivity   PL12: removing the k most extreme values (k = 1, 2, 3)
    python3 benefits.py precision     PL13: bootstrap standard errors, and how far apart each measure places the
                                      data sets of a group relative to its own noise
    python3 benefits.py stability     PL14: rolling windows of 260 returns (step 1) on each index

Results ($CLAIMSET_RESULTS):
  sensitivity: "standardised change on removing the most extreme values", conditions {measure, data, data set, k}:
      (value without the k values farthest from the mean - value on all) / bootstrap standard error on all;
  precision:   "bootstrap standard error", {measure, data, data set}; "discrimination ratio", {measure, data}:
      standard deviation (n - 1) of the measure over the group's four data sets / root mean square of their
      bootstrap standard errors;
  stability:   "spike ratio", {measure, index}: the largest change between consecutive windows / the measure's
      standard deviation over all windows; "roughness", {measure, index}: the median change between consecutive
      windows / the same standard deviation.
Bootstrap: 2000 resamples with replacement, seed 20261124 for the first data set, incremented for each next one.
HM_SYNTH=1 replaces the data by synthetic samples of the same sizes (for testing the code without reading the data).
"""
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np

from measures import ALL

HERE = Path(__file__).resolve().parent
ROCK = {"area": "Area", "peri": "Perimeter", "shape": "Shape", "perm": "Permeability"}
INDICES = ("DAX", "SMI", "CAC", "FTSE")
B, SEED, KS, WINDOW = 2000, 20261124, (1, 2, 3), 260


def read(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0] if k != "rownames"}


def data_sets():
    """[(group, name, values)]: the four rock variables, then the four index return series."""
    if os.environ.get("HM_SYNTH"):
        g = np.random.default_rng(1)
        return ([("petroleum rock samples", n, g.gamma(2.0, 1.0, 48)) for n in ROCK.values()]
                + [("European stock index returns", n, g.standard_t(4, 1859) / 100) for n in INDICES])
    rock, eu = read(HERE / "data" / "rock.csv"), read(HERE / "data" / "EuStockMarkets.csv")
    return ([("petroleum rock samples", name, rock[col]) for col, name in ROCK.items()]
            + [("European stock index returns", name, np.diff(np.log(eu[name]))) for name in INDICES])


def values(y):
    """{measure: value} on one sample."""
    return {m: float(f(y[None, :])[0]) for m, f in ALL.items()}


def bootstrap_se(y, seed):
    """{measure: bootstrap standard error} from B resamples, in chunks."""
    rng = np.random.default_rng(seed)
    out = {m: [] for m in ALL}
    for start in range(0, B, 200):
        idx = rng.integers(0, len(y), size=(min(200, B - start), len(y)))
        ys = y[idx]
        for m, f in ALL.items():
            out[m].append(f(ys))
    return {m: float(np.std(np.concatenate(v), ddof=1)) for m, v in out.items()}


def sensitivity(put):
    for i, (group, name, y) in enumerate(data_sets()):
        full, se = values(y), bootstrap_se(y, SEED + i)
        order = np.argsort(-np.abs(y - y.mean()))
        for k in KS:
            kept = np.delete(y, order[:k])
            cut = values(kept)
            for m in ALL:
                put("standardised change on removing the most extreme values", (cut[m] - full[m]) / se[m],
                    measure=m, data=group, **{"data set": name}, k=k)


def precision(put):
    sets = data_sets()
    vals, ses = {}, {}
    for i, (group, name, y) in enumerate(sets):
        vals[name], ses[name] = values(y), bootstrap_se(y, SEED + i)
        for m in ALL:
            put("bootstrap standard error", ses[name][m], measure=m, data=group, **{"data set": name})
    for group in dict.fromkeys(g for g, _, _ in sets):
        names = [n for g, n, _ in sets if g == group]
        for m in ALL:
            spread = float(np.std([vals[n][m] for n in names], ddof=1))
            noise = float(np.sqrt(np.mean([ses[n][m] ** 2 for n in names])))
            put("discrimination ratio", spread / noise, measure=m, data=group)


def stability(put):
    for group, name, y in data_sets():
        if group != "European stock index returns":
            continue
        windows = np.lib.stride_tricks.sliding_window_view(y, WINDOW)
        for m, f in ALL.items():
            path = f(windows)
            sd = float(np.std(path, ddof=1))
            steps = np.abs(np.diff(path))
            put("spike ratio", float(steps.max()) / sd, measure=m, index=name)
            put("roughness", float(np.median(steps)) / sd, measure=m, index=name)


def main():
    mode = sys.argv[1]
    results = []

    def put(var, value, **cond):
        results.append({"variable": var, "value": float(value), "conditions": cond})
    {"sensitivity": sensitivity, "precision": precision, "stability": stability}[mode](put)
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as fh:
            json.dump(results, fh)
    else:
        print(len(results), "results")


if __name__ == "__main__":
    main()
