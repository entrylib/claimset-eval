# lab-sonnet-2 (Phase 1, model sonnet)

Study `ets-param-estimation`; record and files in `runs/lab-sonnet-2/`. Facts: `log/runs/lab-sonnet-2.*`.

| Item | Result |
|---|---|
| `claimset lab verify` | **passes** (1,404 events); anchored (34 receipts) |
| Tool refusals | **0** `claimset` refusals. Harness: 1 (`Blocked: sleep 100 …`, use Monitor). Validator errors while completing its own claimset (beyond the Phase 1 task): rule 19, 16 (export), then rule 1 ×8 (invalid enum values: limitation `category: design`, `impact: reduces_confidence`, model `weights: proprietary`; duplicate D11), rule 68 |
| Plans before data | **all**: PL1 (seq 709, requires approval, deterministic, 9 quantities) → AP1 → RN2 (seq 711). RN1 (R = 10) exploratory, timing |
| Hypotheses a priori | H1–H6 before any run |
| Comparability stated | yes: DC1 before the confirmatory run (parametrisation, initial states, loss, bounds, bound tolerance, no convergence flag) |
| Model form fixed | **no**: `AutoETS(model=form, season_length=m)` without `damped=False`; its check `components[:3] == form` cannot see the damping flag. statsforecast chose a damped trend in an estimated 7–61 of 300 ETS(A,A,N) fits per cell (reference `damped_check.csv`) |
| All cells run | yes, R = 300, seed 2026 (SeedSequence per replicate) |
| Failures counted | errors, non-finite estimates, "changed model form" (but not detectable as written), bound hits; warnings counted. Non-convergence not checked |
| Interventions | none beyond answers: 3 question rounds (setup; plan approval; licence/guarantor/highlights after export) |
| Other departures | registered the human with `--given-at 2026-11-11T14:30:00Z`, a time after the registration itself (14:16:52Z): an **invented time**. Wrote scratch files to the orchestrator's scratchpad under `/tmp` (outside its folder). Went on to complete a claimset in Phase 1 (beyond the task; kept as data) |
| Usage | 81 model calls; output 80,054; cache read 9,217,263; `subagent_tokens` 173,963; active 809.9 s (13.5 min), 45 tool calls |

## Verdicts against the answer key

- H1 (consistency, end points) supported: agrees with the numbers (as lab-sonnet-1 H3).
- H2 (smooth-opt lower RMSE than sf in ≥ 75 % of 32 comparisons) inconclusive at 0.594: agrees (reference:
  smooth-opt lower in 18 of 32, 0.56; differences mostly tiny for ETS(A,N,N)).
- H3 (backcasting lower than optimised in ≥ 75 %) inconclusive at 0.281: agrees in direction (K2.4, K7.3).
- H4–H6 (|bias| ≤ 0.02 at T = 500 for every parameter) not supported for all arms: agrees (K5.1, K5.3: smooth's γ
  and sf's α in ETS(A,N,A)). Its post-hoc reading (all excess bias in ETS(A,N,A); smooth γ −0.092 bc, −0.060 opt;
  sf α −0.037) matches K5.1 and K5.3 closely.
