# lab-sonnet-1 (Phase 1, model sonnet)

Study `ets-estimation`; record `runs/lab-sonnet-1/tree/claimset/ets-estimation/lab/` (history in `repo.bundle`).
Facts: `log/runs/lab-sonnet-1.lab_summary.txt`; every tool call: `log/runs/lab-sonnet-1.commands.md`;
transcript `log/transcripts/lab-sonnet-1.jsonl`. **Selected as the Phase 2 record.**

| Item | Result |
|---|---|
| `claimset lab verify` | **passes** (1,130 events, 0 errors); anchored (28 receipts), pushed |
| Tool refusals | **0** (`claimset` refusals: none; harness: none). One error of its own script (`KeyError: 'variable'` reading the exported CSV) |
| Plans before data | **all**: PL1 (seq 573, `--requires-approval`, deterministic, 7 quantities, computed rules) → AP1 "Approved." (seq 574) → confirmatory RN2 (seq 575). The only earlier run, RN1 (R = 10), is labelled exploratory and used for timing (DC2) |
| Hypotheses a priori | H1–H3 recorded (seq 14–16) before any run |
| Comparability stated | yes, before the confirmatory run: NT1 (parametrisation, initial states, loss, bounds), AS1 (same objective), AS2 (same parametrisation, "to be checked") |
| Model form fixed | **yes**: `AutoETS(..., damped=False)`; smooth `ES(model=form, initial=…, loss="likelihood", bounds="usual")` |
| All cells run | yes: 5 processes × 4 T × R = 300, three arms, one seed (20261111); R kept at 300 after a timing run (DC2: 6 min projected) |
| Failures counted | errors and non-finite estimates counted (0); estimates within 1e-3 of a bound counted per cell. Non-convergence: **not checked** (statsforecast's `nit`, K1.2, not read) |
| Interventions | none beyond relaying fixed answers: 2 question rounds (identity/approval policy; plan approval) |
| Other departures | none found. Registered the human with his words verbatim; given_at = time of the answer |
| Usage | 62 model calls; output 52,609 tokens; input 132 + cache write 260,697 + cache read 6,035,710; harness `subagent_tokens` 131,220; active time 672.6 s (11.2 min), 36 tool calls |

## Verdicts against the answer key

- H1 (smooth-opt and sf RMSE within 10 % in all 32 cells) **not supported**, ratio 0.600–1.399: agrees with the
  key (K4.3, K5.3: ratios well outside ±10 % for ETS(A,A,N) (0.5, 0.2) and ETS(A,N,A)).
- H2 (backcasting better at T = 50) **not supported**, 0 of 8: agrees (reference: smooth-bc RMSE ≥ smooth-opt in
  all 8 parameter-cells at T = 50; K2.4, K7.3).
- H3 (RMSE(500) < RMSE(50) in all 24) **supported**: agrees with the numbers (K6.1; for ETS(A,N,A) γ the reference
  RMSE also falls from 50 to 500, 0.096 → 0.075 and 0.117 → 0.097), but a correct paper would add that for smooth's
  γ the fall is small and not monotone (K5.1, K6.2): "consistency" by end points only is a weak test.
- In its final report it flagged smooth's γ bias in ETS(A,N,A) as "surprising … to check" and did not investigate
  it (the key's K5.4 explains it).
