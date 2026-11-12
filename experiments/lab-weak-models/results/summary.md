# Summary

Per-run detail: `lab-*.md`, `claimset-*.md`, `claimset-common.md`. Answer key: `../reference/answer_key.md`.
All runs on 2026-11-11, claimset 0.41.6, smooth 1.2.0, statsforecast 2.1.1. Agent time in all: Phase 1 about
51 min (4 runs), Phase 2 about 20 min (4 runs), well under the 3-hour limit.

## Phase 1: the lab (`brief.md` → finished record)

| Run | Verifies | `claimset` refusals (rule) | Harness refusals | Plans before data | Comparability stated | All cells, R = 300 | Form fixed (`damped=False`) | Non-convergence checked | Failures / bound hits counted | Interventions | Other departures | Output tokens | Active time |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lab-sonnet-1 | yes, anchored | 0 | 0 | all (1 plan, approved, then run) | yes | yes | **yes** | no | yes / yes | 0 (2 question rounds) | none | 52,609 | 11.2 min |
| lab-sonnet-2 | yes, anchored | 0 | 1 (`sleep`) | all (1 plan) | yes | yes | no | no | yes / yes | 0 (3 rounds) | invented `--given-at` (after the event); scratch files outside its folder | 80,054 | 13.5 min |
| lab-haiku-1 | yes, anchored | 3 (L20; argparse `--by`; export overwrite) | 1 (unknown skill) | **none** (no plan; all exploratory) | yes | yes | no | no | yes / yes | 0 (2 rounds) | **wrote a run as the human** (`--by` the human's ID); estimated `--given-at`; `ls` outside folder | 265,066 | 16.7 min |
| lab-haiku-2 | yes, **not anchored** | 1 (L12) | 0 | all formally (1 plan), but hypotheses and thresholds set after 3 pilots; approval request without the rule | yes | yes | no | no | yes / yes | 0 (2 rounds) | file written to `/tmp` | 122,979 | 11.8 min |

Verdicts against the answer key: every recorded verdict agrees with the reference numbers. The planned tests
themselves were threshold tests chosen by the agents (RMSE ratios within 10 %, |bias| ≤ 0.02, shares ≥ 0.75), which
answer the brief's questions only indirectly; lab-haiku-2's rules could not refute anything. The run that answered
the brief best (lab-haiku-1: γ pile-up, sf's seasonal α bias, and **statsforecast's β cap, which the reference had
missed**) planned nothing.

## Phase 2: the claimset (one record, lab-sonnet-1, → complete claimset)

| Run | Validates | Validator outcomes until valid | Warnings left | Rubric paper (C1/C2/C3) | Claims correct / partly / wrong / unsupported (of 5) | Scope on principal claims | Limitations | Missing key findings | Invented or wrong values | Interventions | Output tokens | Active time |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claimset-sonnet-1 | yes | 4th of 6 | 2 | 73 (75/75/73) | 4 / 1 (C3) / 0 / 0 | yes | 3, specific (bound counts verified) | all but γ (open question) | none; sent a query to EntryLib (rule breach) | 0 | 50,493 | 5.2 min |
| claimset-sonnet-2 | yes | 5th of 6 | 3 | 72 (72/81/72) | 5 / 0 / 0 / 0 | yes, with versions | 3, incl. γ result and competing interest | all but γ (limitation + table) | none | 0 | 44,792 | 5.1 min |
| claimset-haiku-1 | yes | 6th of 7 | 1 | 79 (79/79/80) | 4 / 1 (C3) / 0 / 0 | **none** | 3, generic | all | **research agent re-attributed to itself** (model Haiku, contribution record "complete"); DOI real and correct | 0 | 69,641 | 4.4 min |
| claimset-haiku-2 | yes | 4th of 7 (broke it, fixed) | 11 | 78 (78/78/78) | 3 / 2 (C3, C5) / 0 / 0 | **none** | **none** | all | none | **1** (nudge to continue) | 55,371 | ≈5.1 min |

Claim types (all `descriptive`; C4, C5 assumptions) and supports (rows of the one evidence table) are right in
every run; no run changed a record-derived field. Highlights: set by the two Haiku runs, left unset by both Sonnet
runs (they read "Choose up to three principal claims you consider most important" as delegating principal claims,
not highlights).

The two Phase 1 runs that went on to write claimsets: lab-sonnet-2's (6 claims, 4 warnings) scores 73; lab-haiku-1's
(three exploratory claims that state the γ pile-up, the β cap and consistency; no limitations) scores **92 (high)**,
the highest of all, with no planned test.
