# claimset-sonnet-1 (Phase 2, model sonnet)

File `runs/claimset-sonnet-1/tree/claimset/ets-estimation/ets-estimation.claimset.json` (committed and pushed on the
study branch). Validator history `log/runs/claimset-sonnet-1.validate.txt`; tool calls `log/runs/claimset-sonnet-1.commands.md`.
Common to all runs: `claimset-common.md`.

| Item | Result |
|---|---|
| Validates | **yes**, at the 4th validator outcome (export draft 2 errors → `validate` 2 errors (rules 16, 19) → 1 error (rule 64: `about.object` D6 not marked in the rewritten statement) → valid); 6 validator outcomes in all |
| Warnings left | 2: W39 (no highlights), W2 (self-reported model) |
| Rubric 0.2 | **paper 73 (medium)**; C1 75, C2 75, C3 73. Biggest costs: its own limitation L1 (bound estimates in the RMSE, could bias magnitude, not mitigated) −12 on every claim; no prior work −5; plan anchored by git only −3; unchecked assumption C4 −3 |
| Claims | C1 correct; C2 correct; C3 partly correct (called "consistency"; L2 states that only the end points are compared); C4, C5 correct. Scope on every principal claim (conditions and `excludes`, incl. "model form fixed, no model selection") ✔ |
| Missing findings | as `claimset-common.md`; the γ difference is an open question (O2) and the bound counts a limitation (L1: 1891/1218/1191 of 9600, 1159/588/314 for γ — verified against the results CSV) |
| Invented values | none found. Subfield `openalex:subfields/2613` taken from EntryLib's list (fetched), not confirmed with the human (who said "use your judgement"); model weights `api_only` |
| Decisions | highlights left unset (read the human's "choose up to three principal claims" as delegating principal claims only); conceptualization given to the guarantor; CC-BY-4.0 on code and lab record; packaged `files/sim.py` and `files/lab.jsonl` with checksums (`claimset package --update`) |
| Rule breaches | **sent query words to EntryLib** (`mcp__Entrylib__search_claims`) and fetched `entrylib.org/subfields.json`, against the brief's "do not … send anything to EntryLib"; tried `pip install` of the rubric (blocked by the harness's classifier; it did not work around it). No submission |
| Questions / interventions | 1 question round (8 questions in one message); no intervention |
| Usage | 44 model calls; output 50,493 tokens; cache read 4,829,257; `subagent_tokens` 149,225; active 312.8 s (5.2 min), 25 tool calls |
