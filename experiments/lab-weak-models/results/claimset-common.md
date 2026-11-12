# Phase 2: what is common to the four claimset runs

All four started from the same record (lab-sonnet-1, study `ets-estimation`): three hypotheses decided by one
approved plan (H1 not supported, H2 not supported, H3 supported) and two assumptions. Export turns exactly these
into claims (lab record §9: claims come only from hypotheses with a verdict or final status), so every run has the
same five claims, C1–C3 principal, C4–C5 assumptions. None of the four changed a record-derived field (`hypothesis`,
`planning`, `planned_at`, `planned_at_anchor`, `test`) or the exploration counts (checked against the exported draft).

## The claims against the answer key (same for every run unless its file says otherwise)

| Claim | Statement (gist) | Against the key | Type | Support |
|---|---|---|---|---|
| C1 | with optimised initial states, smooth's and statsforecast's RMSE are not within 10 % of each other in every cell; ratio 0.6004–1.399 over 32 cells | **correct** (K4.3, K5.3; the extremes are α in ETS(A,N,A) and β in ETS(A,A,N) (0.5, 0.2), the latter produced by statsforecast's β cap, K8, which the record does not know) | descriptive ✔ | E1.T1.r1 ✔ |
| C2 | at T = 50 backcasting has the lower RMSE in 0 of 8 cells | **correct** (reference: 0 of 8; K2.4, K7.3) | descriptive ✔ | E1.T1.r2 ✔ |
| C3 | RMSE at T = 500 below RMSE at T = 50 in all 8 cells for every arm ("consistency") | **correct on its numbers, partly correct as "consistency"**: smooth's γ RMSE barely falls and is not monotone (K5.1, K6.2); right only when scoped to the end-point criterion | descriptive ✔ | E1.T2 ✔ |
| C4 | assumption: both maximise the Gaussian likelihood | **correct** (K0.2); `check: unchecked` (it could have been checked from the documentation; honest) | assumption ✔ | assumption ✔ |
| C5 | assumption: α, β, γ mean the same in both | **correct** (K0.1) | assumption ✔ | assumption ✔ |

## Findings of the answer key missing from every claimset

Not in the record, so out of reach of Phase 2 by construction (a Phase 2 agent can add claims only from what the
record holds): K1.2 statsforecast's non-convergence for ETS(A,N,A); K8 statsforecast's β cap; K5.4 the γ pile-up
explained. In the record's results but not claimed by any run: K2.1 small-sample bias of α towards zero (−0.05 at
T = 50); K3.1 strong α bias in ETS(A,A,N) at T = 50; K4.1–K4.2 opposite α biases and sf's β bias; K5.1–K5.3 the
seasonal results (two runs put the γ result into a limitation or an open question, see their files); K7.1 the
practical equivalence of the packages for ETS(A,N,N). The record's three hypotheses are threshold tests of RMSE
ratios and end points; the brief's questions (bias, efficiency, consistency per setting) are answered only in the
results CSV.
