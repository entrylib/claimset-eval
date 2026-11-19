"""Plan PL4 (question Q4): the half-moment coefficients and the comparison measures on real data.

- The petroleum rock samples (data/rock.csv: area, peri, shape, perm; 48 samples): every measure for every variable.
- The European stock index returns (data/EuStockMarkets.csv: DAX, SMI, CAC, FTSE; 1860 daily closes, 1991-1998):
  daily log returns (1859 each), every measure for every index.
- The DAX returns on an expanding window, the first t returns for t = 30 to 1859: for each measure its first,
  last, smallest and largest value, and the window lengths at which it is smallest and largest; the whole paths
  are written to window_paths.csv in the run directory.

Results ($CLAIMSET_RESULTS): "measure value" with conditions {data, variable or index, measure};
"measure over the expanding window" with {data, index, measure, summary}; "window length at the extreme" with
{data, index, measure, summary}.
"""
import csv
import json
import os
from pathlib import Path

import numpy as np

from measures import ALL, hcm_parts

HERE = Path(__file__).resolve().parent
ROCK = HERE / "data" / "rock.csv"
EU = HERE / "data" / "EuStockMarkets.csv"
ROCK_NAMES = {"area": "Area", "peri": "Perimeter", "shape": "Shape", "perm": "Permeability"}


def read(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0] if k != "rownames"}


def all_measures(x):
    y = x[None, :]
    out = {m: float(f(y)[0]) for m, f in ALL.items()}
    R, I = hcm_parts(y)
    out["half central moment, real part"] = float(R[0])
    out["half central moment, imaginary part"] = float(I[0])
    out["half absolute moment"] = float(R[0] + I[0])
    return out


def main():
    results = []
    rock = read(ROCK)
    for col, name in ROCK_NAMES.items():
        for m, v in all_measures(rock[col]).items():
            results.append({"variable": "measure value", "value": v,
                            "conditions": {"data": "petroleum rock samples", "variable": name, "measure": m}})
    eu = read(EU)
    returns = {k: np.diff(np.log(v)) for k, v in eu.items()}
    for idx, r in returns.items():
        for m, v in all_measures(r).items():
            results.append({"variable": "measure value", "value": v,
                            "conditions": {"data": "European stock index returns", "index": idx, "measure": m}})
    # the DAX on an expanding window
    r = returns["DAX"]
    lengths = list(range(30, len(r) + 1))
    paths = {m: np.array([f(r[None, :t])[0] for t in lengths]) for m, f in ALL.items()}
    run_dir = os.environ.get("CLAIMSET_RUN_DIR")
    if run_dir:
        with open(Path(run_dir) / "window_paths.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["window length"] + list(paths))
            for i, t in enumerate(lengths):
                w.writerow([t] + [f"{paths[m][i]:.10g}" for m in paths])
    for m, p in paths.items():
        base = {"data": "European stock index returns", "index": "DAX", "measure": m}
        for summary, value in (("first", p[0]), ("last", p[-1]), ("smallest", p.min()), ("largest", p.max())):
            results.append({"variable": "measure over the expanding window", "value": float(value),
                            "conditions": dict(base, summary=summary)})
        results.append({"variable": "window length at the extreme", "value": lengths[int(p.argmin())],
                        "conditions": dict(base, summary="smallest")})
        results.append({"variable": "window length at the extreme", "value": lengths[int(p.argmax())],
                        "conditions": dict(base, summary="largest")})
    path = os.environ.get("CLAIMSET_RESULTS")
    if path:
        with open(path, "w") as fh:
            json.dump(results, fh)
    else:
        print(len(results), "results")


if __name__ == "__main__":
    main()
