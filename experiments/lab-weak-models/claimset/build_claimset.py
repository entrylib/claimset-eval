# Builds lab-weak-models.claimset.json; then run `claimset renumber`, `claimset validate` and `claimset render` on it.
import json
import re

COMMIT = "d3eb0e00a61ab50d7d2a62dfeb89c681d1c9eb87"
BASE = f"https://github.com/entrylib/claimset-eval/tree/{COMMIT}/experiments/lab-weak-models/"
RUBRIC = "8a6f9f948a83c0a6f8c60c1e101ed5c4f5399caf"
PUB = {"level": "public"}
OUT = "/home/user/claimset-eval/experiments/lab-weak-models/claimset/lab-weak-models.claimset.json"


def art(i, kind, path, desc, licence="CC-BY-4.0"):
    return {"id": i, "kind": kind, "uri": BASE + path, "version": COMMIT, "licence": licence,
            "availability": PUB, "description": desc}


def d(i, term, kind, text, **kw):
    x = {"id": i, "term": term, "kind": kind, "definition": text}
    x.update(kw)
    return x


definitions = [
    d("D1", "claimset-lab", "method",
      "The claimset-lab skill (`.claude/skills/claimset-lab/SKILL.md`, installed by `claimset init --agent claude`) "
      "and the `claimset lab` commands of claimset 0.41.6, which keep a lab record (lab record specification v0.21): "
      "an append-only, hash-chained log of questions, hypotheses, plans, approvals, runs, results and verdicts, kept on "
      "a study branch and pushed after every command."),
    d("D2", "claimset-submit", "method",
      "The claimset-submit skill of claimset 0.41.6 (claimset specification v0.41), together with `claimset lab "
      "export`, `claimset validate` and `claimset render`: it turns a lab record into a claimset and completes it "
      "for submission."),
    d("D3", "Sonnet agent", "method",
      "A Claude Code 2.1.322 subagent started with the Agent tool (type general-purpose) on the model "
      "claude-sonnet-5-5, working in a folder of its own that holds the study brief, `AGENTS.md` and the claimset "
      "skills as files; it asks the human by ending its turn with its questions.", part_of=["D5"]),
    d("D4", "Haiku agent", "method",
      "The same as the [[D3:Sonnet agent]], on the model claude-haiku-5-5.", part_of=["D5"]),
    d("D5", "agents under test", "method",
      "The two agent configurations compared: the [[D3:Sonnet agent]] and the [[D4:Haiku agent]].",
      members=["D3", "D4"]),
    d("D6", "ETS estimation brief", "setting",
      "The research task given to every agent (`study/brief.md`): compare how well smooth 1.2.0 (`ES`) and "
      "statsforecast 2.1.1 (`AutoETS` with a fixed model form) estimate the smoothing parameters of the ETS model "
      "that generated simulated data, by bias, RMSE and MAE and by whether the RMSE falls as the series length grows; "
      "five processes (ETS(A,N,N) with α 0.1 and 0.5, ETS(A,A,N) with (α, β) (0.3, 0.05) and (0.5, 0.2), ETS(A,N,A) "
      "with m = 12 and (α, γ) (0.2, 0.1)), series lengths 50, 100, 250 and 500, 300 replicates per cell, smooth's "
      "default backcasting as a separate arm, failures counted."),
    d("D7", "lab phase", "design",
      "Phase 1: four runs, two of the [[D3:Sonnet agent]] and two of the [[D4:Haiku agent]], each in its own git "
      "repository with a local remote, given the same task (\"Do the study in brief.md with claimset-lab, following "
      "its skill, from the first question to the finished record. Ask the human anything you need through me.\"). "
      "The orchestrating agent relays questions and answers them only from [[D9:the fixed answers]], gives no other "
      "help, and never shows an agent another run or [[D10:the answer key]]. Runs in parallel on one 4-core "
      "machine."),
    d("D8", "claimset phase", "design",
      "Phase 2: the lab record of run lab-sonnet-1 (the only one that verifies, planned before its data and fixed "
      "statsforecast's model form) copied to four folders, with the draft its agent had exported removed; two "
      "[[D3:Sonnet agent]] and two [[D4:Haiku agent]] runs, each told \"Export this lab record with `claimset lab "
      "export` and complete the claimset for submission, following the claimset-submit skill. Do not submit it.\" "
      "Questions answered as in [[D7:the lab phase]]."),
    d("D9", "fixed answers", "design",
      "The answers the orchestrating agent gives in place of the human, the same to every run (`study/human.md`): "
      "name and ORCID iD; licence CC-BY-4.0; funding none; the competing interest of the brief; \"Approved.\" for a "
      "plan that names its quantities and decision rule before the data are run, otherwise \"Please state the "
      "quantities and the decision rule first.\"; for highlights \"Choose up to three principal claims you consider "
      "most important.\"; for anything else \"Use your judgement and say what you decided.\"", part_of=["D7", "D8"]),
    d("D10", "answer key", "data",
      "The findings a correct paper on [[D6:the brief]] would state, with their numbers (`reference/answer_key.md`), "
      "from a reference simulation of the full design written by the orchestrating agent before Phase 1 without "
      "claimset-lab (`reference/simulate.py`, `optcheck.py`, `damped_check.py`). Amended once during Phase 1 "
      "(statsforecast's β cap)."),
    d("D11", "record verifies", "variable", "Whether `claimset lab verify` reports the lab record OK at the end of a run (hash chain, rules, run files)."),
    d("D12", "tool refusals", "variable", "Number of commands that `claimset` refused in a run with a lab rule (L1–L30) or an argument or overwrite error; validator errors on a claimset are counted separately."),
    d("D13", "plans before data", "variable",
      "Whether each confirmatory run of a lab record ran under a plan with its decision rule recorded, and approved by "
      "the human, before the run, and whether its hypotheses were written before any run informed them: `all`, "
      "`all, hypotheses after pilots` or `none` (no plan)."),
    d("D14", "model form fixed", "variable",
      "Whether a run's simulation script fixed statsforecast's model form as the brief asks (`damped=False`); "
      "without it, `AutoETS(model=\"AAN\")` and `ets_f(..., model=\"AAN\")` choose between ETS(A,A,N) and ETS(A,Ad,N)."),
    d("D15", "convergence checked", "variable", "Whether a run's script read any optimiser status (for statsforecast, the iteration count `model_[\"fit\"].nit`) and counted fits that did not converge."),
    d("D16", "output tokens", "variable", "Model output tokens of an agent over its whole run, summed from the usage of every model call in its transcript.", unit="1"),
    d("D17", "active time", "variable", "Time an agent spent working in a run, excluding waits for answers, as reported by the harness.", unit="min"),
    d("D18", "record anchored", "variable", "Whether the agent anchored the finished record (`claimset lab anchor`)."),
    d("D19", "runs written as the human", "variable", "Number of run events an agent recorded with `--by` the human's actor ID."),
    d("D20", "claimset validates", "variable", "Whether `claimset validate` reports the final claimset valid (no errors)."),
    d("D21", "validator outcomes until valid", "variable", "The position, among the validator outcomes a claimset run saw (the export's own summary included), of the first with no errors.", unit="1"),
    d("D22", "warnings left", "variable", "Validator warnings on the final claimset.", unit="1"),
    d("D23", "EntryLib rubric 0.2", "method",
      "The scoring rubric EntryLib applies to published claimsets (entrylib-rubric 0.2.0), run on this machine with "
      "`claimset score` and without `--novelty`: each principal claim starts at 100 and loses fixed costs for its "
      "problems (support, plan, checkability, context, open limitations and assumptions); the paper's score is that of "
      "its lowest principal claim."),
    d("D24", "reliability score", "variable", "The paper score of a claimset under [[D23:EntryLib rubric 0.2]], 0–100.", unit="1"),
    d("D25", "claim correctness", "variable",
      "Each claim of a claimset checked against [[D10:the answer key]]: `correct` (direction and magnitude agree "
      "within Monte Carlo error), `partly correct` (direction agrees; magnitude, scope or a qualifier does not), "
      "`wrong`, or `not supported by the record`."),
    d("D26", "answer-key findings stated", "variable", "Number of the answer key's findings on bias (K2–K5), statsforecast's non-convergence (K1.2) and statsforecast's β cap (K8) that a claimset states as claims.", unit="1"),
    d("D27", "principal claims with scope", "variable", "Number of a claimset's principal claims that have a scope.", unit="1"),
    d("D28", "limitations", "variable", "Number of limitations a claimset records.", unit="1"),
    d("D29", "research agent's model kept", "variable", "Whether a completed claimset keeps the model of the agent that did the research, as the lab record names it."),
    d("D30", "interventions", "variable", "Number of messages the orchestrating agent sent a run that were not answers from [[D9:the fixed answers]].", unit="1"),
    d("D31", "reference simulation", "design",
      "The reference analysis behind [[D10:the answer key]]: 300 series per cell of [[D6:the brief]], each fitted by "
      "smooth with optimised initial states, smooth with backcasting and statsforecast `AutoETS(model, season_length, "
      "damped=False)` with its defaults (likelihood, bounds `both`), seeds `numpy.random.default_rng([20261111, "
      "process, T, replicate])`."),
    d("D32", "statsforecast β cap", "concept",
      "In statsforecast 2.1.1 (`statsforecast.ets.initparam`), when α is estimated its starting value is "
      "$\\alpha_0 = 0.0001 + 0.2 \\cdot (0.9999 - 0.0001)/m$ (0.20006 for $m = 1$), and the upper bound of β is set to "
      "$\\min(0.9999, \\alpha_0)$ for the whole optimisation, so β cannot exceed $\\alpha_0$."),
    d("D33", "statsforecast iteration cap", "variable", "Number of statsforecast fits whose optimiser stopped at its iteration cap (`nit` = 1001) in [[D31:the reference simulation]].", unit="1"),
]

models = [
    {"id": "M1", "provider": "Anthropic", "name": "Claude Opus", "version": "5.5", "identifier": "claude-opus-5-5",
     "weights": "api_only", "accessed": "2026-11-11"},
    {"id": "M2", "provider": "Anthropic", "name": "Claude Sonnet", "version": "5.5", "identifier": "claude-sonnet-5-5",
     "weights": "api_only", "accessed": "2026-11-11"},
    {"id": "M3", "provider": "Anthropic", "name": "Claude Haiku", "version": "5.5", "identifier": "claude-haiku-5-5",
     "weights": "api_only", "accessed": "2026-11-11"},
]

contributors = [
    {"id": "P1", "type": "agent", "name": "Claude Code", "label": "orchestration and analysis",
     "system": {"name": "Claude Code", "version": "2.1.322"},
     "positions": ["author"], "models": [{"model": "M1", "role": "orchestrator"}],
     "credit_roles": ["methodology", "investigation", "formal_analysis", "software", "data_curation", "writing_original_draft"],
     "ai_tasks": [{"task": "analysis", "extent": "full"}, {"task": "code", "extent": "full"},
                  {"task": "writing", "extent": "full"}, {"task": "json_preparation", "extent": "full"},
                  {"task": "literature_search", "extent": "assisted"}],
     "tools": ["code_execution", "file_access", "web_search"], "record_source": "harness"},
    {"id": "P2", "type": "human", "name": "Ivan Svetunkov", "orcid": "0000-0001-7826-0281",
     "positions": ["guarantor", "supervisor"], "credit_roles": ["conceptualization", "supervision"]},
]

SET = {"harness": "Claude Code 2.1.322, Agent tool, subagent type general-purpose", "effort": None, "temperature": None}
SUBJECTS = [{"model": "M2", "role": "subject", "settings": SET, "record_source": "harness", "prompts": "A3"},
            {"model": "M3", "role": "subject", "settings": SET, "record_source": "harness", "prompts": "A3"}]

lab_cols = ["D11", "D12", "D13", "D14", "D15", "D18", "D19", "D16", "D17"]
lab_rows = [
    ("r1", "lab-sonnet-1", "D3", [True, 0, "all", True, False, True, 0, 52609, 11.2]),
    ("r2", "lab-sonnet-2", "D3", [True, 0, "all", False, False, True, 0, 80054, 13.5]),
    ("r3", "lab-haiku-1", "D4", [True, 3, "none", False, False, True, 1, 265066, 16.7]),
    ("r4", "lab-haiku-2", "D4", [True, 1, "all, hypotheses after pilots", False, False, False, 0, 122979, 11.8]),
]
cs_cols = ["D20", "D21", "D22", "D24",
           {"variable": "D25", "conditions": {"outcome": "correct"}},
           {"variable": "D25", "conditions": {"outcome": "partly correct"}},
           {"variable": "D25", "conditions": {"outcome": "wrong"}},
           "D26", "D27", "D28", "D29", "D30", "D16"]
cs_rows = [
    ("r1", "claimset-sonnet-1", "D3", [True, 4, 2, 73, 4, 1, 0, 0, 3, 3, True, 0, 50493]),
    ("r2", "claimset-sonnet-2", "D3", [True, 5, 3, 72, 5, 0, 0, 0, 3, 3, True, 0, 44792]),
    ("r3", "claimset-haiku-1", "D4", [True, 6, 1, 79, 4, 1, 0, 0, 0, 3, False, 0, 69641]),
    ("r4", "claimset-haiku-2", "D4", [True, 4, 11, 78, 3, 2, 0, 0, 0, 0, True, 1, 55371]),
]

evidence = [
    {"id": "E1", "profile": "quant", "design": "experiment",
     "description": (
         "[[D7:The lab phase]]: two runs each of the [[D3:Sonnet agent]] and the [[D4:Haiku agent]] did [[D6:the ETS "
         "estimation brief]] with [[D1:claimset-lab]]. For each run the orchestrating agent read the final lab record "
         "(`tools/lab_summary.py`: plans, approvals and runs in record order, the actor of every event, anchors), the "
         "run's script, and its transcript (`tools/transcript.py`: every tool call, every refusal, model-call usage), "
         "and recorded the variables of table T1. Every question and answer is in `log/questions.md`."),
     "setup": {"studied": ["D3", "D4"], "cases": ["D6"], "procedure": ["D7", "D9", "D1"],
               "lens": ["D10", "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19"]},
     "estimand": "per-run outcomes of the lab phase", "n": 4, "data_origin": "primary", "preregistered": False,
     "models": SUBJECTS, "artefacts": ["A1", "A2", "A3", "A4", "A5", "A8", "A9"], "availability": PUB,
     "tables": [{"id": "T1", "description": "Outcomes of the four lab runs of the lab phase on the ETS estimation brief",
                 "row_labels": ["run", "agent"], "columns": lab_cols,
                 "rows": [{"id": i, "label": [r, a], "values": v} for i, r, a, v in lab_rows],
                 "artefact": "A8"}]},
    {"id": "E2", "profile": "quant", "design": "experiment",
     "description": (
         "[[D8:The claimset phase]]: two runs each of the [[D3:Sonnet agent]] and the [[D4:Haiku agent]] exported "
         "one lab record and completed the claimset with [[D2:claimset-submit]]. For each final claimset the "
         "orchestrating agent ran `claimset validate` and `claimset score` ([[D23:EntryLib rubric 0.2]]), counted the "
         "validator outcomes in the transcript (`tools/validate_runs.py`), checked that no record-derived field "
         "(hypothesis, planning, planned_at, test, exploration counts) had changed, and scored every claim against "
         "[[D10:the answer key]] (table T1). Table T2 scores, under the same rubric, the two claimsets that lab-phase "
         "agents wrote on their own records after finishing them (beyond their task)."),
     "setup": {"studied": ["D3", "D4"], "cases": ["D6"], "procedure": ["D8", "D9", "D2"],
               "lens": ["D10", "D23", "D20", "D21", "D22", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D16"]},
     "estimand": "per-run outcomes of the claimset phase", "n": 4, "data_origin": "primary", "preregistered": False,
     "models": SUBJECTS, "artefacts": ["A1", "A2", "A3", "A6", "A8", "A9", "A10"], "availability": PUB,
     "tables": [
         {"id": "T1", "description": "Outcomes of the four claimset runs of the claimset phase, all from the lab record of lab-sonnet-1",
          "row_labels": ["run", "agent"], "columns": cs_cols,
          "rows": [{"id": i, "label": [r, a], "values": v} for i, r, a, v in cs_rows], "artefact": "A8"},
         {"id": "T2", "description": "EntryLib rubric 0.2 scores of the two claimsets written by lab-phase agents on their own records",
          "row_labels": ["run", "agent", "planning of the principal claims"], "columns": ["D24", "D28", "D27"],
          "rows": [{"id": "r1", "label": ["lab-sonnet-2", "D3", "confirmatory"], "values": [73, 4, 3]},
                   {"id": "r2", "label": ["lab-haiku-1", "D4", "exploratory"], "values": [92, 0, 3]}],
          "artefact": "A8"}]},
    {"id": "E3", "profile": "simulation",
     "description": (
         "[[D31:The reference simulation]] of [[D6:the brief]] (R = 300 per cell, 20 cells, three arms, 110 s on 4 "
         "cores), with `optcheck.py` and `damped_check.py`. Table T1: statsforecast's β estimates for ETS(A,A,N) with "
         "(α, β) = (0.5, 0.2), against smooth's; table T2: statsforecast fits of ETS(A,N,A) that stopped at the "
         "optimiser's iteration cap. The β cap was first reported by run lab-haiku-1 (its exploratory run RN1); it was "
         "verified here against the statsforecast 2.1.1 source and these estimates, and added to the answer key."),
     "setup": {"studied": ["D31"], "cases": ["D6"], "procedure": ["D31"], "lens": ["D32", "D33"]},
     "model": "ETS in innovations form with Gaussian errors, σ = 1, l0 = 100, b0 = 1, s_j = 10 sin(2πj/12)",
     "parameters": "A6", "runs": 300, "seeds": ["20261111"],
     "artefacts": ["A6", "A7"], "availability": PUB, "data_origin": "primary",
     "tables": [
         {"id": "T1", "description": "statsforecast and smooth (optimised initial states) estimates of β for ETS(A,A,N) with α = 0.5, β = 0.2, 300 series per length",
          "row_labels": ["series length"],
          "columns": [{"variable": "largest statsforecast β estimate"},
                      {"variable": "statsforecast fits within 0.001 of 0.20006"},
                      {"variable": "smooth fits with β above 0.20006"}],
          "rows": [{"id": "r1", "label": [50], "values": [0.20006, 100, 131]},
                   {"id": "r2", "label": [100], "values": [0.20006, 135, 146]},
                   {"id": "r3", "label": [250], "values": [0.20006, 132, 132]},
                   {"id": "r4", "label": [500], "values": [0.20006, 144, 137]}],
          "artefact": "A6"},
         {"id": "T2", "description": "statsforecast fits of ETS(A,N,A) (α = 0.2, γ = 0.1, m = 12) at the optimiser's iteration cap, of 300 per length",
          "row_labels": ["series length"], "columns": ["D33"],
          "rows": [{"id": "r1", "label": [50], "values": [288]}, {"id": "r2", "label": [100], "values": [296]},
                   {"id": "r3", "label": [250], "values": [300]}, {"id": "r4", "label": [500], "values": [299]}],
          "artefact": "A6"}]},
]


def claim(i, statement, about, support, scope=None, role="principal", typ="descriptive", strength="low",
          rationale=None, limitations=None, assumptions=None, depends_on=None, novelty="no_prior_found"):
    c = {"id": i, "statement": statement, "type": typ, "role": role, "planning": "exploratory",
         "provenance": "author_stated", "support": support}
    if about:
        about.setdefault("comparator", None)
        about.setdefault("conditions", [])
        marked = set(re.findall(r"\[\[(D\d+):", statement))
        about["conditions"] = [x for x in about["conditions"] if not (isinstance(x, str) and re.fullmatch(r"D\d+", x)) or x in marked]
        for k in ("subject", "object", "comparator"):
            v = about.get(k)
            for x in (v if isinstance(v, list) else [v]):
                if isinstance(x, str) and re.fullmatch(r"D\d+", x):
                    assert x in marked, (i, k, x)
        c["about"] = about
    if novelty:
        c["novelty"] = novelty
    if scope:
        scope = json.loads(json.dumps(scope))
        if scope.get("conditions") is not None and SPEC.get(i):
            scope["conditions"] = scope["conditions"] + [SPEC[i]]
        c["scope"] = scope
    if assumptions:
        c["assumptions"] = assumptions
    if limitations:
        c["limitations"] = limitations
    if depends_on:
        c["depends_on"] = depends_on
    c["assessments"] = [{"by": "author", "strength": strength, "rationale": rationale}]
    return c


SCOPE_P1 = {"data_type": "agent runs on one simulation study task",
            "conditions": ["claimset 0.41.6 with its skills read as files", "Claude Code 2.1.322 Agent-tool subagents",
                           "two runs per agent", "fixed answers in place of the human"],
            "excludes": ["agents in sessions of their own with the guard hook active", "other study tasks and fields"]}
SCOPE_P2 = dict(SCOPE_P1, conditions=["one lab record (lab-sonnet-1) completed four times"] + SCOPE_P1["conditions"][:2] + ["two runs per agent", "fixed answers in place of the human"])
SCOPE_R = {"conditions": ["entrylib-rubric 0.2.0, without --novelty", "the six claimsets of this study"],
           "excludes": ["other rubric versions"]}
SPEC = {"C1": "records as left at the end of each lab run", "C2": "the two Sonnet lab runs", "C3": "the two Haiku lab runs",
        "C4": "the statsforecast arm of each run's script", "C5": "the statsforecast arm of each run's script",
        "C7": "the final file of each claimset run", "C8": "the 20 claims of the four claimsets", "C9": "claims only, not limitations or open questions",
        "C11": "the three lab runs with a plan and the one without", "C12": "principal claims only", "C13": "the two Haiku lab runs",
        "C14": "the two Haiku claimset runs", "C15": "claimsets written in either phase", "C16": "claimsets completed from one lab record",
        "C17": "costs per claim", "C19": "the lab phase"}
EXPL = "Exploratory: no plan or decision rule was registered before the runs; "
SEARCH = " One web search found no earlier study of agents keeping pre-planned lab records or completing claimsets."

claims = [
    claim("C1", "Every lab record that the [[D5:agents under test]] kept with [[D1:claimset-lab]] on [[D6:the ETS estimation brief]] passes `claimset lab verify` ([[D11:record verifies]]).",
          {"subject": "D5", "relation": "keep lab records that pass", "object": "D11", "conditions": ["D1", "D6"]},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1"], "artefacts": ["A1"]}],
          SCOPE_P1, strength="moderate",
          rationale=EXPL + "four of four records verify, each checked by the tool itself; four runs on one task." + SEARCH,
          limitations=["L2", "L5"], assumptions=["C21"]),
    claim("C2", "In both of its lab runs, the [[D3:Sonnet agent]] ran every confirmatory test under a plan with a computed decision rule, written with its hypotheses before any run and approved by the human before the test ([[D13:plans before data]]).",
          {"subject": "D3", "relation": "plans before the data in every run", "object": "D13", "conditions": ["D1", "D6"]},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1.r1", "E1.T1.r2"], "artefacts": ["A1", "A2"]}],
          SCOPE_P1, rationale=EXPL + "two runs; the record's own order of events shows it." + SEARCH,
          limitations=["L1", "L2", "L5"], assumptions=["C22"]),
    claim("C3", "In neither of its lab runs did the [[D4:Haiku agent]] test every hypothesis under a plan written before the data that informed it ([[D13:plans before data]]): one run recorded no plan, the other fixed its hypotheses and thresholds after three pilot runs.",
          {"subject": "D4", "relation": "does not plan before the data", "object": "D13", "conditions": ["D1", "D6"]},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1.r3", "E1.T1.r4"], "artefacts": ["A1", "A2"]}],
          SCOPE_P1, rationale=EXPL + "two runs; in one, the human had left the choice of confirmatory tests to the agent's judgement." + SEARCH,
          limitations=["L1", "L2", "L5"], assumptions=["C22"]),
    claim("C4", "Three of the four lab runs of the [[D5:agents under test]] left statsforecast's damped-trend option unset, so that their statsforecast arm selected between a damped and an undamped trend, against the fixed model forms of [[D6:the brief]] ([[D14:model form fixed]]).",
          {"subject": "D5", "relation": "do not fix the model form", "object": "D14", "conditions": ["D6"]},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1"], "artefacts": ["A1"]}],
          SCOPE_P1, rationale=EXPL + "read from each run's script; the consequence (a damped trend chosen in 7 to 61 of 300 fits per cell) is from the reference's damped_check." + SEARCH,
          limitations=["L1", "L5"]),
    claim("C5", "None of the four lab runs of the [[D5:agents under test]] checked whether statsforecast's optimiser converged ([[D15:convergence checked]]).",
          {"subject": "D5", "relation": "do not check", "object": "D15", "conditions": ["D6"]},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1"], "artefacts": ["A1"]}],
          SCOPE_P1, role="secondary", rationale=EXPL + "read from each run's script; it bears on the ETS(A,N,A) results (C6).",
          limitations=["L5"], depends_on=["C6"]),
    claim("C6", "In [[D31:the reference simulation]], statsforecast's optimiser stopped at its iteration cap in nearly every ETS(A,N,A) fit, at every series length ([[D33:statsforecast iteration cap]]).",
          {"subject": "statsforecast 2.1.1", "relation": "stops at its iteration cap for", "object": "D33", "conditions": ["D31"]},
          [{"kind": "simulation", "evidence": "E3", "results": ["E3.T2"], "artefacts": ["A6", "A7"]}],
          {"conditions": ["statsforecast 2.1.1 AutoETS defaults", "ETS(A,N,A), m = 12, α = 0.2, γ = 0.1"]},
          role="secondary", strength="moderate", rationale=EXPL + "300 fits per length, read from statsforecast's own iteration count.",
          novelty="not_applicable"),
    claim("C7", "Every claimset that the [[D5:agents under test]] completed with [[D2:claimset-submit]] from one lab record validates with no errors ([[D20:claimset validates]]), at the fourth to sixth validator outcome ([[D21:validator outcomes until valid]]).",
          {"subject": "D5", "relation": "complete claimsets that validate", "object": ["D20", "D21"], "conditions": ["D2", "D8"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1"], "artefacts": ["A1", "A2"]}],
          SCOPE_P2, strength="moderate", rationale=EXPL + "four of four; the validator is the tool's own check." + SEARCH,
          limitations=["L2", "L5", "L6"], assumptions=["C22"]),
    claim("C8", "No claim of the four claimsets that the [[D5:agents under test]] completed with [[D2:claimset-submit]] is wrong against [[D10:the answer key]]: each is correct or partly correct ([[D25:claim correctness]]).",
          {"subject": "D5", "relation": "write no wrong claim", "object": "D25", "comparator": "D10", "conditions": ["D2", "D8"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1"], "artefacts": ["A6", "A8"]}],
          SCOPE_P2, rationale=EXPL + "20 claims scored by one non-blind scorer against a key it wrote; the claims come from one record." + SEARCH,
          limitations=["L3", "L4", "L5"], assumptions=["C21"]),
    claim("C9", "None of the four claimsets that the [[D5:agents under test]] completed with [[D2:claimset-submit]] states as a claim any of [[D10:the answer key]]'s findings on bias, on statsforecast's non-convergence or on statsforecast's β cap ([[D26:answer-key findings stated]]).",
          {"subject": "D5", "relation": "do not state", "object": "D26", "comparator": "D10", "conditions": ["D2", "D8"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1"], "artefacts": ["A6", "A8"]}],
          SCOPE_P2, rationale=EXPL + "the claimsets could only restate the one record they were given (C10); two of them put the seasonal γ result into a limitation or an open question." + SEARCH,
          limitations=["L3", "L4", "L5"], assumptions=["C21"], depends_on=["C10"]),
    claim("C10", "The lab record that [[D8:the claimset phase]] started from holds three hypotheses, each a threshold test on the RMSE (a band for the ratio of the two packages, backcasting better in most cells at the shortest length, the longest length against the shortest), and no hypothesis about the size of the bias or the RMSE.",
          {"subject": "the lab record of lab-sonnet-1", "relation": "holds only threshold tests", "object": None, "conditions": ["D8"]},
          [{"kind": "empirical_quant", "evidence": "E2", "artefacts": ["A1"]}],
          {"conditions": ["the lab record of run lab-sonnet-1, 1,130 events"]},
          role="supporting", strength="high", rationale=EXPL + "read from the record itself.", novelty="not_applicable"),
    claim("C11", "The single route of [[D1:claimset-lab]] from runs to claims, a hypothesis decided by a rule, led the [[D5:agents under test]] to turn [[D6:the brief]]'s questions about the size of bias and RMSE into tests of thresholds they chose themselves, leaving the estimates the brief asked for in the results files.",
          {"subject": "D1", "relation": "leads agents to replace estimates by threshold tests", "object": None, "conditions": ["D6"]},
          [{"kind": "argument", "warrant": "W1"}],
          SCOPE_P1, typ="interpretive", rationale=EXPL + "an interpretation of four runs: three planned runs invented thresholds (10 %, 0.02, 0.75, 12 violations); the unplanned run reported the estimates.",
          limitations=["L1", "L5"], depends_on=["C9", "C10"]),
    claim("C12", "The two claimsets that the [[D4:Haiku agent]] completed give a scope to none of their three principal claims, against all three in each of the two that the [[D3:Sonnet agent]] completed ([[D27:principal claims with scope]]).",
          {"subject": "D4", "relation": "gives no scope to principal claims", "object": "D27", "comparator": "D3", "conditions": ["D2", "D8"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1"], "artefacts": ["A1"]}],
          SCOPE_P2, rationale=EXPL + "two runs per agent." + SEARCH, limitations=["L1", "L2", "L5"]),
    claim("C13", "In one of its two lab runs, the [[D4:Haiku agent]] recorded a run with the human's actor ID as its author, and `claimset lab` accepted it ([[D19:runs written as the human]]).",
          {"subject": "D4", "relation": "records a run as the human", "object": "D19", "conditions": ["D1"]},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1.r3"], "artefacts": ["A1", "A2"]}],
          SCOPE_P1, role="secondary", rationale=EXPL + "one event in one record (RN4 by AC3); the agent disclosed it and noted the correction.",
          limitations=["L1"]),
    claim("C14", "In one of its two claimset runs, the [[D4:Haiku agent]] replaced the model of the agent that had done the research, as the lab record names it, with its own ([[D29:research agent's model kept]]).",
          {"subject": "D4", "relation": "replaces the research agent's model", "object": "D29", "conditions": ["D2"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1.r3"], "artefacts": ["A1"]}],
          SCOPE_P2, role="secondary", rationale=EXPL + "one claimset; the other Haiku run kept the research agent and added itself.",
          limitations=["L1"]),
    claim("C15", "Under [[D23:EntryLib rubric 0.2]], the claimset whose principal claims were not planned tests has a higher [[D24:reliability score]] than each of the six claimsets whose principal claims were planned tests.",
          {"subject": "D23", "relation": "scores unplanned claims above planned ones", "object": "D24", "conditions": ["six claimsets of this study"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1", "E2.T2"], "artefacts": ["A8", "A10"]}],
          SCOPE_R, strength="moderate", rationale=EXPL + "the scores are computed; the cause is in the rubric's code (C17)." + SEARCH,
          limitations=["L5"], depends_on=["C20"]),
    claim("C16", "Under [[D23:EntryLib rubric 0.2]], the claimset with no limitations and no scope (claimset-haiku-2) has a higher [[D24:reliability score]] than the claimset from the same record with scoped claims and three specific limitations (claimset-sonnet-1).",
          {"subject": "D23", "relation": "scores a claimset without limitations or scope above one with both", "object": "D24", "conditions": ["claimsets from one lab record"]},
          [{"kind": "empirical_quant", "evidence": "E2", "results": ["E2.T1.r1", "E2.T1.r4"], "artefacts": ["A8", "A10"]}],
          SCOPE_R, strength="moderate", rationale=EXPL + "two scores, computed; the cause is in the rubric's costs (C17)." + SEARCH,
          limitations=["L5"], depends_on=["C17"]),
    claim("C17", "In [[D23:EntryLib rubric 0.2]], an unmitigated limitation that could bias a claim's magnitude costs the claim 12 points, more than a missing scope (10 points).",
          {"subject": "D23", "relation": "charges", "object": None},
          [{"kind": "demonstration", "artefacts": ["A10"]}],
          SCOPE_R, role="supporting", strength="high", rationale="Read from the rubric's code at the commit artefact A10 names (rubric.json, checks limitation and no_scope).",
          novelty="not_applicable"),
    claim("C20", "In [[D23:EntryLib rubric 0.2]], a descriptive claim made without a plan costs nothing in the plan group, and a planned claim whose plan is anchored only by a git push costs 3 points.",
          {"subject": "D23", "relation": "charges planned claims more than unplanned descriptive ones", "object": None, "comparator": None, "conditions": []},
          [{"kind": "demonstration", "artefacts": ["A10"]}],
          dict(SCOPE_R, conditions=SCOPE_R["conditions"] + ["claims of type descriptive"]), role="supporting", strength="high",
          rationale="Read from the rubric's code at the commit artefact A10 names (score.py, lines 28 and 111: only associational, causal, mechanistic and predictive claims are charged without a plan; rubric.json, plan_anchor).",
          novelty="not_applicable"),
    claim("C18", "When statsforecast 2.1.1 fits ETS(A,A,N) with its defaults, its estimate of β never exceeds its starting value of α ([[D32:statsforecast β cap]]), so that no estimate can lie above a true β of 0.2.",
          {"subject": "statsforecast 2.1.1", "relation": "caps β at its starting α", "object": "D32", "conditions": ["D31"]},
          [{"kind": "simulation", "evidence": "E3", "results": ["E3.T1"], "artefacts": ["A6", "A7"]}],
          {"conditions": ["statsforecast 2.1.1 AutoETS defaults, model AAN, m = 1", "ETS(A,A,N) with (α, β) = (0.5, 0.2)", "series lengths 50 to 500, 300 series each"]},
          role="secondary", strength="high",
          rationale=EXPL + "the cap is in the package's code (initparam) and every one of 1,200 estimates respects it. It makes statsforecast's lower RMSE for β = 0.2 at long series an artefact of the cap.",
          novelty="no_prior_found"),
    claim("C19", "The [[D32:statsforecast β cap]] was reported by a [[D4:Haiku agent]] lab run (lab-haiku-1, in an exploratory run) and was missing from [[D10:the answer key]] as written before the lab phase.",
          {"subject": "D4", "relation": "finds what the reference missed", "object": "D32", "comparator": "D10"},
          [{"kind": "empirical_quant", "evidence": "E1", "results": ["E1.T1.r3"], "artefacts": ["A2", "A6"]}],
          SCOPE_P1, role="secondary", rationale=EXPL + "one finding of one run; the reference's bound check compared β with the estimated α, not the starting one.",
          limitations=["L4"], depends_on=["C18"], novelty="not_applicable"),
    {"id": "C21", "statement": "[[D10:The answer key]] states the findings that a correct paper on [[D6:the brief]] would state, with correct numbers.",
     "type": "descriptive", "role": "supporting", "support": [{"kind": "assumption"}], "provenance": "author_stated",
     "assumption_category": "methodological", "check": "unchecked"},
    {"id": "C22", "statement": "The [[D5:agents under test]], run as subagents of an orchestrating session, act as they would in sessions of their own started in their run folders.",
     "type": "descriptive", "role": "supporting", "support": [{"kind": "assumption"}], "provenance": "author_stated",
     "assumption_category": "methodological", "check": "unchecked"},
]

warrants = [
    {"id": "W1", "reasoning": "inductive", "premises": ["C10"], "text": (
        "The claimset-lab skill offers one route from a run to a claim: a hypothesis decided by a rule, with computed "
        "rules preferred whenever the outcome can be computed from numbers (SKILL.md, lines 83–100), and export makes "
        "claims only from hypotheses with a verdict or a final status (lab record v0.21 §9). Every planned run "
        "accordingly chose thresholds the brief did not give (an RMSE ratio within 10 %, |bias| at most 0.02, shares "
        "of at least 0.75, at least 12 violations), and its claims are the verdicts on them; the one run without a "
        "plan wrote notes and claims about the estimates themselves (the γ pile-up, statsforecast's seasonal α bias, "
        "the β cap).")},
]

limitations = [
    {"id": "L1", "category": "sample_size", "statement": "Two runs per agent and phase: differences between the Sonnet and Haiku agents rest on two runs each and could reverse with more runs.",
     "affects": ["C2", "C3", "C4", "C11", "C12", "C13", "C14"], "impact": "could_reverse", "mitigation": "none"},
    {"id": "L2", "category": "confounding", "statement": "The agents ran as subagents of the orchestrating session: they read the skills as files, the claimset guard hook of their folders was not active, and they received the orchestrating session's own project instructions (which led one Haiku run to ask its questions one at a time); four runs shared one 4-core machine.",
     "affects": ["C1", "C2", "C3", "C7", "C12"], "impact": "could_bias_magnitude", "mitigation": "none"},
    {"id": "L3", "category": "measurement", "statement": "One scorer, the orchestrating agent, wrote the answer key and the protocol and scored every claim, knowing which agent wrote it.",
     "affects": ["C8", "C9"], "impact": "could_bias_magnitude", "mitigation": "partial", "mitigation_evidence": "E3"},
    {"id": "L4", "category": "deviation", "statement": "The answer key was amended once during the lab phase, after a Haiku run reported statsforecast's β cap; the claimsets were scored against the amended key.",
     "affects": ["C8", "C9", "C19"], "impact": "could_bias_magnitude", "mitigation": "none"},
    {"id": "L5", "category": "sampling", "statement": "One study task (an ETS simulation comparison in Python), one version of claimset (0.41.6) and of its skills, one harness (Claude Code 2.1.322).",
     "affects": ["C1", "C2", "C3", "C4", "C5", "C7", "C8", "C9", "C11", "C12", "C15", "C16"], "impact": "reduces_transferability", "mitigation": "none"},
    {"id": "L6", "category": "deviation", "statement": "One claimset run (claimset-haiku-2) stopped with its own stated work undone and was sent one message with no content (\"Continue.\") before it finished.",
     "affects": ["C7"], "impact": "could_bias_magnitude", "mitigation": "none"},
]

artefacts = [
    art("A1", "data", "runs/", "The eight runs as the agents left them: each folder's files without its git directory, and its full git history (study branch included) in repo.bundle."),
    art("A2", "trace", "log/transcripts/", "The eight agents' transcripts (Claude Code subagent JSONL), with every tool call and result and the usage of every model call."),
    art("A3", "prompt", "log/prompts.md", "The task prompts given to the agents in each phase."),
    art("A4", "protocol", "study/", "The study brief and the fixed answers given in place of the human."),
    art("A5", "data", "log/", "Setup notes, every question and answer, agent IDs and usage per turn."),
    art("A6", "data", "reference/", "The reference analysis: estimates.csv, summary.csv, consistency.csv, optcheck.csv, damped_check.csv and answer_key.md."),
    art("A7", "code", "reference/", "The reference analysis scripts simulate.py, optcheck.py and damped_check.py.", licence="MIT"),
    art("A8", "data", "results/", "Scoring per run, rubric scores as JSON, summary.md and report.md."),
    art("A9", "code", "tools/", "The scoring scripts transcript.py, lab_summary.py and validate_runs.py.", licence="MIT"),
    {"id": "A10", "kind": "software", "uri": f"https://github.com/entrylib/rubric/tree/{RUBRIC}", "version": RUBRIC,
     "licence": "Apache-2.0", "availability": PUB,
     "description": "EntryLib's scoring rubric, entrylib-rubric 0.2.0 (src/rubric/rubric.json holds the costs; src/rubric/score.py applies them)."},
]

references = []

open_questions = [
    {"id": "O1", "question": "Whether the differences between the Sonnet and Haiku agents hold over more runs, other study tasks and agents in sessions of their own is not established.", "claims": ["C2", "C3", "C12", "C19"]},
    {"id": "O3", "question": "Whether refusing writes by a human actor in agent harnesses, and keeping the research agent's model through export, would prevent the misattributions of a run and of a study's research is not tested.", "claims": ["C13", "C14"]},
    {"id": "O4", "question": "Whether a skill instruction to report each fit's model form and optimiser status as results would close the gaps in fixing the model form and checking convergence is not tested.", "claims": ["C4", "C5"]},
    {"id": "O2", "question": "Whether a plan that fixes estimates rather than a decision rule would lead agents to state the brief's findings as claims is not tested.", "claims": ["C9", "C11"]},
]

paper = {
    "title": "Claude Sonnet and Claude Haiku agents keeping Claimset lab records and completing claimsets: a pilot on one simulation study",
    "licence": "CC-BY-4.0",
    "classification": {"keywords": ["AI research agents", "lab records", "pre-registration", "claimsets",
                                    "agent evaluation", "research integrity", "scoring rubric"]},
    "declarations": {"funding": [],
                     "competing_interests": "The guarantor owns EntryLib, which develops the claimset tools, skills and rubric the study evaluates; the study was done to improve them."},
    "contributions": ["C1", "C2", "C3", "C7", "C8", "C9", "C4", "C11", "C12", "C15", "C16"],
    "autonomy": "human_supervised",
    "contribution_record": "partial",
    "origin": "native",
}

out = {"schema_version": "0.41", "paper": paper, "contributors": contributors, "models": models,
       "definitions": definitions, "claims": claims, "evidence": evidence, "warrants": warrants,
       "limitations": limitations, "artefacts": artefacts, "references": references, "open_questions": open_questions}
import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("written", OUT)
