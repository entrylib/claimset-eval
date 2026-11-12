<!-- claimset:begin (written by `claimset init`; edit outside these lines) -->
## Claimset

This project keeps its research in Claimset lab records and publishes it as claimsets: papers written for LLM readers. Four skills say how. Read a skill's `SKILL.md` before the work it covers, whether or not your harness loads skills by itself:

| Skill | For |
|---|---|
| `.claude/skills/claimset-lab/SKILL.md` | doing research: keeping the lab record, planning tests before running them, recording every run and result |
| `.claude/skills/claimset-submit/SKILL.md` | turning finished research, or a lab record, into a claimset, validating and submitting it |
| `.claude/skills/claimset-revise/SKILL.md` | answering the reviews of a published claimset |
| `.claude/skills/claimset-review/SKILL.md` | reviewing a claimset as the platform does |

- Start a session with `claimset studies` and carry on inside the study's record. Without the `claimset` command, run the copy bundled with the skills: `python3 .claude/skills/claimset-lab/scripts/claimset studies`.

- **People decide; you ask.** The guarantor, the licence, the highlights, and approvals of plans and of the final claimset are the human's. Never fill them in yourself.
- **Never invent.** No data, numbers, citations, DOIs, ORCID iDs or model names. Give your model as your system prompt or environment states it, or leave `--model` out and let `$CLAIMSET_MODEL`, which the human sets, give it.
- **Write to a lab record only with `claimset lab` commands.** Never edit, move or delete files under `lab/` or `claimset/*/lab/` by other means; correct a mistake with `--supersedes`.
- **Validate before you hand over** (`claimset validate`), and submit only when the human approves.
- **Offer a score before submitting; never require it.** Ask the human whether to score the claimset first (`claimset score`, on this machine, by EntryLib's rubric). If they want it, give the score and the biggest issues, and let them decide whether to submit as it is or amend it and score again.
- **If a push or `claimset submit` fails for want of network, say so:** the sandbox your harness runs commands in may need to allow the git host and entrylib.org.
<!-- claimset:end -->
