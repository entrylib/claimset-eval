# lab-haiku-1 (Phase 1, model haiku)

Study `ets-param-recovery`; record and files in `runs/lab-haiku-1/`. Facts: `log/runs/lab-haiku-1.*`.

| Item | Result |
|---|---|
| `claimset lab verify` | **passes** (968 events); anchored (44 receipts) |
| Tool refusals | `claimset`: **3** — L20 (`run` from the study's folder: "run commands from the code checkout"), an argparse refusal (`unrecognized arguments: --by AC1`, a command that takes no `--by`), export refusing to overwrite (`exists; … add --force`). Harness: 1 (`Unknown skill: claimset-lab`: it called the Skill tool, which the subagent does not have). Validator (own claimset, beyond the task): rule 10 ×8, rule 61 ×8 (misread, see report), rule 1, 16, 19 |
| Plans before data | **none**: no plan at all. Every run exploratory (RN1 bounds check, RN2 full simulation, RN3 and RN4 analysis); H1–H4 recorded after RN3 and prompted by it, all set `inconclusive` "because exploratory evidence cannot confirm". It asked the human whether to make confirmatory tests and was told to use its judgement; it chose a descriptive study (DC1) |
| Comparability stated | yes: DC2, DC4, DC5 (arms, failures, each package's bounds), before the full run |
| Model form fixed | **no**: `ets_f(y, m=…, model=code)` with `damped` unset (damped trend chosen in an estimated 7–61 of 300 ETS(A,A,N) fits per cell) |
| All cells run | yes, R = 300, seed 2026 |
| Failures counted | errors, non-finite, "non-convergence flags" (none read), bound shares |
| Interventions | none beyond answers: 2 question rounds |
| Other departures | **wrote a run as the human**: RN4 and its results recorded `--by AC3` (the human's actor), disclosed and noted in NT9 (skill rule 2). Registered the human first with an **estimated time** (14:10:00Z; the answer came at 14:16), then re-registered (AC3 supersedes AC2). Ran `ls /home/user/exp-runs/` (sibling folder names), disclosed. Built its claimset with its own script after `claimset lab export --force` |
| Found beyond the reference | **statsforecast caps β at its starting α ≈ 0.20** (RN1, NT4/NT8, claim C2): correct, verified, and missed by the reference (answer key amended, K0.7, K8) |
| Usage | 175 model calls; output 265,066; cache read 27,373,897; `subagent_tokens` 253,033; active 1,004.3 s (16.7 min), 74 tool calls |

## Notes against the answer key

NT2 (smooth γ on the lower bound: bc 0.90–1.00, opt 0.39–0.67) — K5.1 ✔; NT3 (sf seasonal α bias ≈ −0.04 at
T = 250, 500) — K5.3 ✔; NT4/NT8 (sf β on its ≈ 0.2 cap in 48–59 %, its lower RMSE "comes from the cap") — K8 ✔;
NT5/NT7 (consistency except smooth's γ and sf's seasonal α) — K6.2 ✔; NT6 (backcasting ≈ optimised at T ≥ 250) —
K2.4, K4.5 ✔. The most accurate account of the findings of the four runs, without a single planned test.
