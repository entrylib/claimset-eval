# Phase 0: setup notes

Date: 2026-11-11.

## Installation

`pip install claimset smooth statsforecast` into a fresh virtual environment `/home/user/venv`:
claimset 0.41.6, smooth 1.2.0, statsforecast 2.1.1 (with numpy 2.5.4, pandas 2.3.3, scipy 1.18.1, nlopt 2.11.0,
greybox 1.0.11). Python 3.13.18.

## Skills

- `claimset agents` does not exist in claimset 0.41.6; the entry point is `claimset guide` (read in full), with
  `claimset guide claimset-lab` / `claimset-submit` for one skill.
- `claimset init --agent claude-code` is refused: `ERROR: unknown agent 'claude-code': one of claude, codex,
  gemini, …`. The name is `claude`. `claimset init --agent claude --guard` installs
  `.claude/skills/{claimset-lab,claimset-submit,claimset-revise,claimset-review}` (each with its references and
  a bundled copy of the tool), `AGENTS.md` (the rules and a table pointing at each `SKILL.md`), `CLAUDE.md`
  (`@AGENTS.md`) and `.claude/settings.json` (a `PreToolUse` hook `claimset lab guard` on
  Edit|Write|MultiEdit|NotebookEdit|Bash, and a `SessionStart` hook `claimset studies`).
- Read: `claimset-lab/SKILL.md` (266 lines), `claimset-submit/SKILL.md` (352 lines). The references are long
  (lab record spec 916 lines, specification 1,972 lines).

## How the runs are set up (and where this departs from a normal session)

- **Folders outside the repository.** Each run works in `/home/user/exp-runs/<run>/`, a git repository of its own
  (first commit: `brief.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.gitignore`) with a remote `origin` that is a
  local bare repository (`/home/user/exp-runs/<run>.git`), so that study branches can be pushed and anchored
  without leaving the machine. The run folders are not inside `claimset-eval` because they are git repositories
  and because a worktree of `claimset-eval` (the Agent tool's worktree isolation) would contain the reference;
  worktree isolation is therefore not used. After a run, its folder is copied into `runs/<run>/` (without `.git`)
  with `repo.bundle` (`git bundle create --all`) holding its full history, including the study branch.
- **Skills are read, not loaded.** An Agent-tool subagent runs in the orchestrator's session: it does not load the
  run folder's `.claude/skills` as skills, and its `CLAUDE.md` is not read automatically. The task tells the agent
  to read `AGENTS.md` in its folder, which (as written by `claimset init`) tells it to read each `SKILL.md`
  "whether or not your harness loads skills by itself". This is the path the tool provides for harnesses that do
  not load skills.
- **The guard hook is not active.** Hooks come from the session's settings, which are read when the session
  starts (checked: a `PreToolUse` hook written to the orchestrator's project settings mid-session did not take
  effect). So the run folders' `claimset lab guard` hook does not run for the subagents. Tool refusals recorded
  are therefore the `claimset` tool's own (rules L1–L30, validator errors); any edit of `lab/` by other means is
  detected afterwards by `claimset lab verify` and by reading the agent's commands.
- **Model identity.** `CLAIMSET_MODEL` is not set; the agents report their own model as the skill asks.
- **Asking the human.** The agent ends its turn with its question(s); the orchestrator answers from
  `study/human.md` with SendMessage, which continues the same agent. Every exchange is logged in `questions.md`.
- **Concurrency.** The machine has 4 cores; runs are started in parallel, so a run's computing time is shared.

## Reference analysis

`reference/simulate.py` (R = 300, all 20 cells × 3 arms, 110 s on 4 cores) and `reference/optcheck.py`. While
checking the reference, two facts that bear on the answer key were found and verified:
- statsforecast 2.1.1 stops at its optimiser's iteration cap (`nit` = 1001) in 288–300 of 300 ETS(A,N,A) fits per
  T, and its estimates there have a higher SSE (profile criterion, least-squares initial states) than smooth's;
- smooth's γ ≈ 0 for ETS(A,N,A) is where that criterion is lowest for most series (an exact profile computation,
  `optcheck.py`, and a grid search on four series), i.e. a pile-up of the estimator at the boundary, not an
  extraction error.
- `AutoETS(model="AAN")` without `damped=False` chose a damped trend for 6 of 40 series: leaving it unset is model
  selection.

The brief fixes the data generating process's initial states (l_0 = 100, b_0 = 1, s_j = 10 sin(2πj/12)), which
the request did not give, so that every run simulates the same processes as the reference.

## Confound found during Phase 1

Agent-tool subagents receive the orchestrator's project instructions (`claimset-eval/CLAUDE.md` → `AGENTS.md`:
hand-made pilot claimsets, `source_spans` to `papers/text/`, "ask the author … one question at a time", run
`claimset validate` and `claimset render` after every change). lab-sonnet-2 cited them ("source_spans, as the repo
rule requires"). They do not apply to the runs; any effect on a run (e.g. `source_spans` added, one question at a
time) is noted in its scoring and not counted against the skills.

The Phase 1 task ends at the finished record. Agents that go on to export and complete a claimset in Phase 1 are
answered from `human.md` like any other question; their Phase 1 claimsets are kept as data but Phase 2 starts from
the selected record only (`lab/` and the code), without any claimset a lab agent drafted.

## Answer key amended during Phase 1

lab-haiku-1 reported that statsforecast caps β at its starting α (≈ 0.20). Verified against the statsforecast
2.1.1 source (`initparam`: `upper[1] = min(upper[1], alpha)` with the starting α) and the reference estimates:
statsforecast's β never exceeds 0.20006 for ETS(A,A,N) (0.5, 0.2). The answer key was amended (K0.7, K8; K7.2
qualified). The reference missed it because its bound flag used β ≤ α̂ (the estimate), not the starting α. The
agent did not see the key; the finding is credited to that run.
