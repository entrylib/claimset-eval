"""Build the claimset submission for study ets-param-recovery from the lab export.

Reads the draft written by `claimset lab export` (it keeps the lab's hypotheses, runs and exploration
counts) and the recorded results CSV, and writes the completed claimset in place. Table values are
copied from the recorded results (run RN4 for bias, RMSE and MAE; run RN3 for the share on a bound).

Usage (from the code checkout):
  claimset lab export --study ets-param-recovery --force
  python3 claimset-code/ets-param-recovery/build_claimset.py
"""
import csv
import hashlib
import json
import math
import os
import shutil

STUDY = "ets-param-recovery"
BASE = os.path.join("claimset", STUDY)
DRAFT = os.path.join(BASE, f"{STUDY}.claimset.json")
RESULTS = os.path.join(BASE, "files", f"{STUDY}.results.csv")

PROCESSES = [
    ("ETS(A,N,N) alpha=0.1", "ANN"),
    ("ETS(A,N,N) alpha=0.5", "ANN"),
    ("ETS(A,A,N) alpha=0.3 beta=0.05", "AAN"),
    ("ETS(A,A,N) alpha=0.5 beta=0.2", "AAN"),
    ("ETS(A,N,A) m=12 alpha=0.2 gamma=0.1", "ANA"),
]
ARMS = [
    ("smooth ES, optimised initial states", "smooth_opt"),
    ("smooth ES, backcasting initial states (default)", "smooth_bc"),
    ("statsforecast ets_f, optimised initial states", "sf"),
]
LENGTHS = [50, 100, 250, 500]
PARAMS = {"ANN": ["alpha"], "AAN": ["alpha", "beta"], "ANA": ["alpha", "gamma"]}
VAR_BIAS = "bias of smoothing parameter estimates"
VAR_RMSE = "RMSE of smoothing parameter estimates"
VAR_MAE = "MAE of smoothing parameter estimates"
VAR_BOUND = "share of estimates on a bound"
COLUMNS = [VAR_BIAS, VAR_RMSE, VAR_MAE, VAR_BOUND]


def sig4(x):
    """Four significant digits, as the evidence tables give values."""
    if x == 0 or not math.isfinite(x):
        return x
    return float(f"{x:.4g}")


def load_values():
    """Map (method, process, T, parameter, variable) -> value from the recorded results."""
    values = {}
    with open(RESULTS, newline="") as f:
        for row in csv.DictReader(f):
            cond = json.loads(row["conditions"])
            q, run = row["quantity"], row["run"]
            if q in (VAR_BIAS, VAR_RMSE, VAR_MAE) and run != "RN4":
                continue
            if q == VAR_BOUND and run != "RN3":
                continue
            if q not in (VAR_BIAS, VAR_RMSE, VAR_MAE, VAR_BOUND):
                continue
            key = (cond["method"], cond["process"], int(cond["sample size"]), cond["parameter"], q)
            values[key] = float(row["value"])
    return values


def build_table(values):
    rows, index = [], {}
    for proc, code in PROCESSES:
        for T in LENGTHS:
            for arm_label, arm in ARMS:
                for par in PARAMS[code]:
                    rid = f"r{len(rows) + 1}"
                    cells = [values[(arm_label, proc, T, par, c)] for c in COLUMNS]
                    rows.append({"id": rid, "label": [arm_label, proc, T, par],
                                 "values": [sig4(v) for v in cells]})
                    index[(arm_label, proc, T, par)] = rid
    table = {"id": "T1",
             "description": ("Bias, RMSE and MAE of the smoothing-parameter estimates of successful fits, and the "
                             "share of estimates on a bound, for 5 processes, 4 series lengths and 3 arms, "
                             "300 replicates per cell (lab runs RN4 and RN3); values to four significant digits"),
             "row_labels": ["method", "process", "sample size", "parameter"],
             "columns": ["D4", "D5", "D6", "D8"],
             "units": ["1", "1", "1", "1"],
             "rows": rows}
    return table, index


def main():
    with open(DRAFT) as f:
        cs = json.load(f)
    values = load_values()
    table, index = build_table(values)

    def rows_for(arms, procs, lengths, pars):
        out = []
        for arm in arms:
            for proc, code in procs:
                for T in lengths:
                    for par in pars.get(code, []):
                        out.append(f"E1.T1.{index[(arm, proc, T, par)]}")
        return out

    # All of the study's terms (definitions), with the design's parts.
    cs["definitions"] = [
        {"id": "D1", "term": "smooth ES", "kind": "method",
         "definition": ("The ES class of the Python package smooth (Ivan Svetunkov) with the model form fixed; "
                        "estimated smoothing parameters by likelihood; usual bounds (alpha, beta, gamma in [0,1], "
                        "beta at most alpha, gamma at most 1 minus alpha); initial states optimised (initial='optimal') "
                        "or by backcasting (initial='backcasting', its default). Two arms: optimised and backcasting.")},
        {"id": "D2", "term": "statsforecast ETS", "kind": "method",
         "definition": ("The ets_f function of statsforecast (Nixtla) with the model form fixed; likelihood loss "
                        "(opt_crit 'lik'); smoothing parameters bounded to [0.0001, 0.9999], with beta's upper bound "
                        "set to the starting alpha (about 0.2 for non-seasonal models); initial states optimised.")},
        {"id": "D3", "term": "ETS innovations-form data", "kind": "data",
         "definition": ("Simulated series of length T in {50, 100, 250, 500} from ETS(A,N,N), ETS(A,A,N) and ETS(A,N,A) "
                        "with m=12 in innovations form, additive Gaussian errors with sigma=1, l_0=100, b_0=1 and "
                        "s_j=10 sin(2 pi j/12) for j=0,...,11; no burn-in. ETS(A,N,N): $y_t = l_{t-1} + \\varepsilon_t$, "
                        "$l_t = l_{t-1} + \\alpha \\varepsilon_t$. ETS(A,A,N): $y_t = l_{t-1} + b_{t-1} + \\varepsilon_t$, "
                        "$l_t = l_{t-1} + b_{t-1} + \\alpha \\varepsilon_t$, $b_t = b_{t-1} + \\beta \\varepsilon_t$. "
                        "ETS(A,N,A): $y_t = l_{t-1} + s_{t-m} + \\varepsilon_t$, $l_t = l_{t-1} + \\alpha \\varepsilon_t$, "
                        "$s_t = s_{t-m} + \\gamma \\varepsilon_t$; $\\varepsilon_t \\sim N(0,1)$ i.i.d.")},
        {"id": "D4", "term": VAR_BIAS, "kind": "variable",
         "definition": "Mean over successful replicates of (estimate minus true value) of a smoothing parameter."},
        {"id": "D5", "term": VAR_RMSE, "kind": "variable",
         "definition": "Root mean squared error of a smoothing-parameter estimate around its true value, over successful replicates."},
        {"id": "D6", "term": VAR_MAE, "kind": "variable",
         "definition": "Mean absolute error of a smoothing-parameter estimate around its true value, over successful replicates."},
        {"id": "D7", "term": "Monte Carlo replicate design", "kind": "design",
         "definition": ("5 processes x 4 series lengths x 300 replicates per cell. Each replicate has its own fixed seed "
                        "derived from the base seed 2026; the three arms are fitted to the same series. Fit failures "
                        "and non-finite estimates are counted, not dropped.")},
        {"id": "D8", "term": VAR_BOUND, "kind": "variable",
         "definition": ("Share of successful replicates whose estimate lies within 0.001 of a bound of the "
                        "implementation's parameter range: smooth 0 or 1 (beta also at alpha); statsforecast "
                        "0.0001 or 0.9999 (beta also at its cap).")},
    ]

    cs["evidence"] = [{
        "id": "E1",
        "profile": "simulation",
        "description": ("Monte Carlo comparison of smoothing-parameter estimates of smooth ES (two initial-state arms) "
                        "and statsforecast ets_f on simulated ETS data (definitions D3 and D7). The bias, RMSE and MAE "
                        "come from lab run RN4 (analyse.py --output error) and the share on a bound from RN3 (analyse.py), "
                        "both over the replicate file of RN2 (simulate.py --seed 2026 --reps 300). The lab record "
                        "holds all runs; every result is in files/ets-param-recovery.results.csv. All 18,000 fits succeeded."),
        "model": "ETS innovations-form models of definition D3, with m=12 for ETS(A,N,A)",
        "parameters": "A5",
        "runs": ["RN2", "RN3", "RN4"],
        "seeds": "base seed 2026; replicate seed 2026*10^7 + p*10^6 + T_index*10^5 + replicate (p process, T_index length, replicate 0 to 299)",
        "outputs": "E1.T1",
        "setup": {"studied": ["D1", "D2"], "cases": ["D3"], "procedure": ["D7"],
                  "lens": ["D4", "D5", "D6", "D8"]},
        "availability": {"level": "public"},
        "lab_runs": ["RN2", "RN3", "RN4"],
        "execution": {"code_version": "f18283ae36f7c8f444f9bc23a5a4b4a497983660",
                      "notes": "Scripts simulate.py and analyse.py in claimset-code/ets-param-recovery/."},
        "tables": [table],
    }]

    cs["claims"] = [
        {"id": "C1", "role": "principal", "type": "descriptive", "novelty": "no_prior_found",
         "statement": ("For ETS(A,N,A) with $m=12$ and true $\\gamma=0.1$ in [[D3:ETS innovations-form data]], "
                       "[[D1:smooth ES]] estimates $\\gamma$ with a bias towards zero for series of 50 to 250 "
                       "observations, under both initial-state methods."),
         "about": {"subject": "D1", "relation": "estimates the seasonal smoothing parameter with a bias towards zero",
                   "object": None, "comparator": None, "conditions": ["D3"]},
         "scope": {"data_type": "simulated", "conditions": "ETS(A,N,A) with m=12, Gaussian errors, series length 50 to 250"},
         "support": [{"kind": "simulation", "evidence": "E1", "artefacts": ["A3"],
                      "results": rows_for([ARMS[0][0], ARMS[1][0]], [PROCESSES[4]], [50, 100, 250], {"ANA": ["gamma"]})}],
         "assumptions": ["C5"],
         "hypothesis": {"lab_event": "H1", "outcome": "inconclusive"}, "planning": "exploratory",
         "assessments": [{"by": "author", "strength": "low",
                          "rationale": ("The result is exploratory, not tested under a plan: one simulation study, with no independent "
                                        "check; one web search found no head-to-head study of these estimators.")}]},
        {"id": "C2", "role": "principal", "type": "descriptive", "novelty": "no_prior_found",
         "statement": ("For ETS(A,A,N) with true $(\\alpha,\\beta)=(0.5,0.2)$ in [[D3:ETS innovations-form data]], "
                       "[[D2:statsforecast ETS]] estimates $\\beta$ on its cap in roughly half of replicates "
                       "at every series length from 50 to 500."),
         "about": {"subject": "D2", "relation": "estimates beta on its cap in a share of replicates",
                   "object": None, "comparator": None, "conditions": ["D3"]},
         "scope": {"data_type": "simulated", "conditions": "ETS(A,A,N), Gaussian errors, series length 50 to 500"},
         "support": [{"kind": "simulation", "evidence": "E1", "artefacts": ["A3"],
                      "results": rows_for([ARMS[2][0]], [PROCESSES[3]], LENGTHS, {"AAN": ["beta"]})}],
         "assumptions": ["C5"],
         "hypothesis": {"lab_event": "H2", "outcome": "inconclusive"}, "planning": "exploratory",
         "assessments": [{"by": "author", "strength": "low",
                          "rationale": ("The result is exploratory, not tested under a plan: one simulation study, with no independent "
                                        "check; one web search found no head-to-head study of these estimators.")}]},
        {"id": "C4", "role": "principal", "type": "descriptive", "novelty": "no_prior_found",
         "statement": ("For non-seasonal ETS in [[D3:ETS innovations-form data]], the RMSE of the estimates of "
                       "$\\alpha$ and $\\beta$ from [[D1:smooth ES]] with optimised initial states falls at each "
                       "series length from 50 to 500."),
         "about": {"subject": "D1", "relation": "has an RMSE for alpha and beta that falls with series length",
                   "object": None, "comparator": None, "conditions": ["D3"]},
         "scope": {"data_type": "simulated", "conditions": "ETS(A,N,N) and ETS(A,A,N), Gaussian errors, series length 50 to 500"},
         "support": [{"kind": "simulation", "evidence": "E1", "artefacts": ["A3"],
                      "results": rows_for([ARMS[0][0]], PROCESSES[:4], LENGTHS, {"ANN": ["alpha"], "AAN": ["alpha", "beta"]})}],
         "assumptions": ["C5"],
         "hypothesis": {"lab_event": "H4", "outcome": "inconclusive"}, "planning": "exploratory",
         "assessments": [{"by": "author", "strength": "low",
                          "rationale": ("The result is exploratory, not tested under a plan: one simulation study, with no independent "
                                        "check; one web search found no head-to-head study of these estimators.")}]},
        {"id": "C5", "role": "supporting", "type": "descriptive",
         "statement": ("The errors are i.i.d. $N(0,1)$ and the data are generated exactly by the stated "
                       "innovations-form ETS model."),
         "support": [{"kind": "assumption"}],
         "assumption_category": "statistical", "check": "unchecked"},
    ]

    # Files of the submission: the simulation code and its parameters, copied beside the results CSV.
    files = os.path.join(BASE, "files")
    os.makedirs(files, exist_ok=True)
    src = os.path.join("claimset-code", STUDY)
    params = {"processes": [{"label": l, "model": c} for l, c in PROCESSES],
              "smoothing_true": {"ETS(A,N,N) alpha=0.1": {"alpha": 0.1}, "ETS(A,N,N) alpha=0.5": {"alpha": 0.5},
                                 "ETS(A,A,N) alpha=0.3 beta=0.05": {"alpha": 0.3, "beta": 0.05},
                                 "ETS(A,A,N) alpha=0.5 beta=0.2": {"alpha": 0.5, "beta": 0.2},
                                 "ETS(A,N,A) m=12 alpha=0.2 gamma=0.1": {"alpha": 0.2, "gamma": 0.1}},
              "lengths": LENGTHS, "replicates": 300, "sigma": 1, "level0": 100, "trend0": 1,
              "season0": "10 sin(2 pi j / 12), j = 0..11", "base_seed": 2026}
    with open(os.path.join(files, "simulation-parameters.json"), "w") as f:
        json.dump(params, f, indent=2)
        f.write("\n")
    for name in ("simulate.py", "analyse.py"):
        shutil.copy(os.path.join(src, name), os.path.join(files, name))

    def artefact(aid, kind, uri, description):
        path = os.path.join(files, uri.split("/", 1)[1])
        with open(path, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        return {"id": aid, "kind": kind, "uri": uri, "version": f"sha256:{digest}",
                "availability": {"level": "public"}, "licence": "CC-BY-4.0", "description": description}

    keep = [a for a in cs["artefacts"] if a["id"] in ("A1", "A2")]
    keep.append(artefact("A3", "code", "files/simulate.py",
                         "Script that simulates the ETS data, fits smooth (two arms) and statsforecast ets_f, and writes the replicate file (lab run RN2)."))
    keep.append(artefact("A4", "code", "files/analyse.py",
                         "Script that summarises the replicate file: bias, RMSE and MAE (RN4) and the share on a bound (RN3)."))
    keep.append(artefact("A5", "data", "files/simulation-parameters.json",
                         "Simulation parameters: processes, true smoothing parameters, lengths, replicates, initial states, base seed."))
    cs["artefacts"] = keep

    cs["paper"]["licence"] = "CC-BY-4.0"
    cs["paper"]["contributions"] = ["C2", "C1", "C4"]
    cs["paper"]["autonomy"] = "human_supervised"
    cs["paper"]["declarations"] = {
        "funding": [],
        "competing_interests": "The guarantor is the author and maintainer of the smooth package that the study evaluates.",
    }
    cs["paper"]["classification"] = {"keywords": ["exponential smoothing", "ETS state space models",
                                                  "parameter estimation", "smooth package", "statsforecast",
                                                  "Monte Carlo simulation"]}

    people = {p["id"]: p for p in cs["contributors"]}
    people["P2"]["positions"] = ["supervisor", "guarantor"]
    for a in cs["artefacts"]:
        a.setdefault("licence", "CC-BY-4.0")

    with open(DRAFT, "w") as f:
        json.dump(cs, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {DRAFT}: {len(cs['claims'])} claims, {len(cs['evidence'])} evidence, "
          f"{len(table['rows'])} table rows")


if __name__ == "__main__":
    main()
