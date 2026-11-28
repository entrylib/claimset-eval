# Orchestrating a session of lab-weak-models-2

You run one session of an experiment (entrylib/claimset-eval, `experiments/lab-weak-models-2/`). In it, four
agents each do one task; you start them, answer their questions from fixed answers, and archive what they did.
You never help them otherwise. The person who started you only passes messages: do not ask them anything except
to report a stop condition below.

## Your session

Your session (`lab`, `submit`, `control` or `phase2`) is given in the message that started you. ROOT is the folder you were
started in, which the person's bootstrap has set up (`ROOT/runs/<run>/` for each run, `ROOT/venv`); the protocol
files are in `ROOT/../protocol-<session>/`, this file among them.

## 1. Check

1. Check that this session can give its agents nothing beyond their task: your tool list holds no MCP tools (you
   were started with `--strict-mcp-config`), and, for the `control` session only, no skill, agent type, command or
   instruction you can see mentions claimset or EntryLib. If a check fails, stop and tell the person exactly what
   to change; start nothing.
2. Check that `ROOT/runs/` holds the four run folders of your session, each a git repository whose `origin` is
   `ROOT/runs/<run>.git`. Do not change anything in them.
3. Keep `ROOT/log/agents.tsv` (run, model as the Agent tool reports it, start and end time, agent ID) and
   `ROOT/log/questions.md` as you go.

## 2. The tasks

Start the four agents of your session at once, each with the Agent tool (subagent type `general-purpose`, model
`sonnet` for `*-sonnet-*` runs, `haiku` for `*-haiku-*` runs, in the background), with the prompt below for its
session, RUN replaced by the run's name and ROOT by the absolute path. Pass the prompt exactly; add nothing.

**lab** (runs lab-sonnet-1, lab-sonnet-2, lab-haiku-1, lab-haiku-2):
```
Do the study in brief.md with claimset-lab, following its skill, from the first question to the finished record.
Ask the human anything you need through me.

Your folder is ROOT/runs/RUN. Work only inside it: run every command from it (start each shell
command with `cd ROOT/runs/RUN &&`) and do not read or write anything outside it, except the
Python environment the brief names. Start by reading AGENTS.md and brief.md there.

To ask the human, end your turn with your question(s), addressed to the human; I will reply with their answer
and you then continue. Do not guess their answers.
```

**submit** (runs submit-sonnet-1, submit-sonnet-2, submit-haiku-1, submit-haiku-2):
```
Do the study in brief.md and write it up as a claimset for submission, following the claimset-submit skill,
from the first question to the finished claimset. Do not submit it.
Ask the human anything you need through me.

Your folder is ROOT/runs/RUN. Work only inside it: run every command from it (start each shell
command with `cd ROOT/runs/RUN &&`) and do not read or write anything outside it, except the
Python environment the brief names. Start by reading brief.md and .claude/skills/claimset-submit/SKILL.md there.

To ask the human, end your turn with your question(s), addressed to the human; I will reply with their answer
and you then continue. Do not guess their answers.
```

**control** (runs control-sonnet-1, control-sonnet-2, control-haiku-1, control-haiku-2):
```
Do the study in brief.md, from the first question to the finished report.
Ask the human anything you need through me.

Your folder is ROOT/runs/RUN. Work only inside it: run every command from it (start each shell
command with `cd ROOT/runs/RUN &&`) and do not read or write anything outside it, except the
Python environment the brief names. Start by reading brief.md there.

The finished report is report.md in your folder, for the study's guarantor. It ends with a numbered list of
the study's findings, each with the numbers that support it. Keep the code and the outputs the report's
numbers come from in the folder, and commit them.

To ask the human, end your turn with your question(s), addressed to the human; I will reply with their answer
and you then continue. Do not guess their answers.
```

**phase2** (runs claimset-sonnet-1, claimset-sonnet-2, claimset-haiku-1, claimset-haiku-2):
```
Export this lab record with `claimset lab export` and complete the claimset for submission, following the
claimset-submit skill. Do not submit it.
Ask the human anything you need through me.

Your folder is ROOT/runs/RUN. Work only inside it: run every command from it (start each shell
command with `cd ROOT/runs/RUN &&`) and do not read or write anything outside it, except the
Python environment the brief names. Start by reading AGENTS.md there.

To ask the human, end your turn with your question(s), addressed to the human; I will reply with their answer
and you then continue. Do not guess their answers.
```

## 3. While they work

- When an agent ends its turn with a question, answer it with SendMessage to that agent, using only
  `answers.md` (verbatim; several questions get the matching answers in order). Log the question verbatim, the
  answer, and the time in `log/questions.md`.
- When an agent ends its turn without a question and without saying it has finished, send "Continue." once and
  log it as an intervention. If it stops again, record the run as stopped; send nothing more.
- Send nothing else: no hints, corrections, reminders, or anything about other runs, this file or the experiment.
  Anything else you send is an intervention: log it with the reason.
- Never edit, run or inspect anything in a run's folder while its agent works.

## 4. When all four have finished or stopped

1. `bash ROOT/../protocol-<session>/archive.sh ROOT` (writes `ROOT.tar.gz`, with every run's files and git history,
   the transcripts of this session and its agents, `log/` and the environment).
2. Write `log/summary.md`: per run, finished or stopped, number of question rounds, interventions, anything the
   harness refused, and anything else unusual you saw (what you saw, not your assessment of the work), then
   re-run the archive.
3. Tell the person: the archive's path, to upload it to the session that gave them your instructions, and
   nothing else about the results.
