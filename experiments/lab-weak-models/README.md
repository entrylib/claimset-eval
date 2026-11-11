# Experiment: can weaker models run claimset-lab and write a correct claimset?

Claude Sonnet and Claude Haiku agents (started by an orchestrating agent with the Agent tool's `model`
parameter) do a small simulation study with the `claimset-lab` skill (Phase 1, two runs per model), then
complete a claimset from one identical lab record with the `claimset-submit` skill (Phase 2, two runs per
model). The orchestrator answers their questions from fixed answers, does not help otherwise, and scores the
results against a reference analysis the agents never see.

| Path | What |
|---|---|
| `study/brief.md` | the study, as given to every agent (nothing about the experiment) |
| `study/human.md` | the fixed answers given in place of the human |
| `reference/` | the reference analysis (`simulate.py`, `optcheck.py`, their CSVs) and `answer_key.md`: never shown to the agents |
| `runs/<run>/` | each run's folder as the agent left it (archived after the run; git history in `repo.bundle`) |
| `log/` | setup notes, the questions asked and answers given, per-run records (commands, refusals, tokens, time) |
| `results/` | scoring per run, `summary.md`, `report.md` |

## Software

claimset 0.41.6 (lab record v0.21, specification v0.41), smooth 1.2.0, statsforecast 2.1.1, numpy 2.5.4,
pandas 2.3.3, scipy 1.18.1, Python 3.13.18, in one virtual environment (`/home/user/venv`) shared by every run.
Claude Code 2.1.322 as the harness.

## Protocol and its departures from the request

See `log/setup.md`.

## Results

Ran on 2026-11-11 (Phase 1 ≈ 51 min and Phase 2 ≈ 20 min of agent time). `results/summary.md` has the tables;
`results/report.md` what each model managed, where it failed, and the changes proposed to the skills, the
specification, the tools and the rubric. `tools/` holds the standard-library scripts used for scoring
(`transcript.py`, `lab_summary.py`, `validate_runs.py`); the rubric was run from a separate environment with
`entrylib-rubric` 0.2.0, without `--novelty` (nothing was sent).
