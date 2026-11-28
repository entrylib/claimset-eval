# Experiment: Sonnet and Haiku agents with and without Claimset lab (replication and extension of entrylib:2026.000005)

Replicates the pilot in `../lab-weak-models/` with claimset 0.45.0, and adds a control arm: the same study done
without claimset-lab, by agents that never learn it exists. The study's own lab record is on the branch
`claimset/lab-weak-models-2` (questions, hypotheses H1–H12, plans PL1–PL3).

Three orchestrator sessions run on the guarantor's machine, each in a Docker container of its own, each in a folder set up by `protocol/bootstrap.sh`,
each starting four Agent-tool subagents (two Sonnet, two Haiku) and answering them from `protocol/answers.md`:

| Session | Runs | Agents' task | Folder |
|---|---|---|---|
| `lab` | lab-{sonnet,haiku}-{1,2} | the pilot's Phase 1 prompt, `protocol/brief-lab.md` (the pilot's brief) | claimset files, guard hook, skills |
| `nolab` | nolab-{sonnet,haiku}-{1,2} | the control prompt, `protocol/brief-control.md` (the pilot's brief without claimset and EntryLib) | no claimset anywhere; installs blocked |
| `claimset` | claimset-{sonnet,haiku}-{1,2} | the pilot's Phase 2 prompt, on four copies of one `lab` record | claimset files, guard hook, skills |

`protocol/ORCHESTRATOR.md` is what each orchestrator follows. Each session's archive (`archive.sh`) is uploaded
here, captured in the record, graded blind and scored.
