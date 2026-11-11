# claimset-haiku-2 (Phase 2, model haiku)

File `runs/claimset-haiku-2/tree/claimset/ets-estimation/ets-estimation.claimset.json` (**not committed**).
Common to all runs: `claimset-common.md`.

| Item | Result |
|---|---|
| Validates | **yes**, first at the 4th validator outcome (2 → 2 → 2 (rule 16) → valid with 21 warnings); later broke it (11 errors, rule 64: rewritten statements dropped the `[[D…]]` marks of their `about`) and fixed it at the 7th |
| Warnings left | 11 (W1 ×7 recommended fields, W2, W3 partial contribution record, W22 on C5) |
| Rubric 0.2 | **paper 78 (medium)**; C1–C3 78. Costs: no scope −10; no prior work −5; plan anchor −3; unchecked C4 −3. **No limitations at all**, so no limitation costs |
| Claims | C1, C2 correct; C3 partly correct ("as consistency predicts", unscoped); C4 correct; **C5 partly correct**: its statement keeps the lab agent's working note "…; to be checked by the data (bias of both near zero at T=500) not assumed unchecked", which contradicts its `check: unchecked` and is false for γ (K5.1). **No scope** on any claim ✘ |
| Missing findings | as `claimset-common.md`, and no limitation: nothing on bound estimates or the γ results |
| Invented values | none found. Kept the Sonnet research agent (P1) and added itself as P3 ("claimset write-up", `record_source: harness`), `contribution_record: partial`: the correct treatment |
| Decisions | highlights C1–C3; asked its questions "one at a time" (from `claimset-eval`'s AGENTS.md, a confound; the submit skill says one message) |
| Rule breaches | none found; left the file uncommitted |
| Questions / interventions | 3 question rounds; **1 intervention** (a content-free "Continue." after it stopped with its own stated work undone) |
| Usage | 59 model calls; output 55,371; cache read 6,688,781; `subagent_tokens` 149,645; active ≈ 5.1 min (first to last event), 31 tool calls |
