# claimset-haiku-1 (Phase 2, model haiku)

File `runs/claimset-haiku-1/tree/claimset/ets-estimation/ets-estimation.claimset.json` (**not committed**).
Common to all runs: `claimset-common.md`.

| Item | Result |
|---|---|
| Validates | **yes**, at the 6th validator outcome (2 errors → 2 → 4 (rule 1: limitation `category: methodological`, not an allowed value) → 2 → 1 (rule 69: `ethics` must be a list) → valid) |
| Warnings left | 1: W1 (model weights) |
| Rubric 0.2 | **paper 79 (medium)**, the highest; C1 79, C2 79, C3 80. Costs: **no scope on any claim −10**; plan anchor −3; unchecked C4 −3; small limitations −1/−2. Not charged "no prior work" (relates C1–C3 to B1) |
| Claims | C1, C2 correct; C3 partly correct (unscoped "consistency"); C4, C5 correct. **No scope** on any claim ✘ |
| Missing findings | as `claimset-common.md`; its limitations are generic (bound estimates kept, bounds differ, one design) |
| Invented / wrong values | **misattribution**: the record's research agent (Claude Sonnet, which ran every event) is replaced by itself: contributor P1 now has model Claude Haiku 5.5 with CRediT formal_analysis/software, `contribution_record: complete`, `record_source: harness`. The paper thus says a Haiku agent did the research. Reference B1 (DOI 10.1016/S0169-2070(01)00110-8, Hyndman et al. 2002) is real and correctly cited (checked) |
| Decisions | highlights C1, C3, C2 (chosen after the human's answer was repeated); ethics empty list; A2 lab record still a local path outside its folder (not packaged) |
| Rule breaches | none found; left the file uncommitted |
| Questions / interventions | 3 question rounds (11 questions, then 3 repeated questions answered with the same fixed answers); none |
| Usage | 54 model calls; output 69,641; cache read 5,907,612; `subagent_tokens` 147,294; active 263.9 s (4.4 min), 29 tool calls |
