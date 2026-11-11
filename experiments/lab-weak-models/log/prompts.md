# Prompts given to the agents

## Phase 1 (identical for every lab run; only the folder differs)

```
Do the study in brief.md with claimset-lab, following its skill, from the first question to the finished record.
Ask the human anything you need through me.

Your folder is /home/user/exp-runs/<run>. Work only inside it: run every command from it (start each shell
command with `cd /home/user/exp-runs/<run> &&`) and do not read or write anything outside it, except the
Python environment the brief names. Start by reading AGENTS.md and brief.md there.

To ask the human, end your turn with your question(s), addressed to the human; I will reply with their answer
and you then continue. Do not guess their answers.
```

## Phase 2 (identical for every claimset run; only the folder differs)

```
Export this lab record with `claimset lab export` and complete the claimset for submission, following the
claimset-submit skill. Do not submit it.
Ask the human anything you need through me.

Your folder is /home/user/exp-runs/<run>. Work only inside it: run every command from it (start each shell
command with `cd /home/user/exp-runs/<run> &&`) and do not read or write anything outside it, except the
Python environment the brief names. Start by reading AGENTS.md there.

To ask the human, end your turn with your question(s), addressed to the human; I will reply with their answer
and you then continue. Do not guess their answers.
```
