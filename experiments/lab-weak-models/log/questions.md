# Questions asked by the agents and the answers given

Answers are from `study/human.md`, verbatim. Times are UTC.

Phase 1 started 2026-11-11T14:15:51Z: lab-sonnet-1, lab-sonnet-2 (model sonnet), lab-haiku-1, lab-haiku-2 (model haiku), in parallel.

## lab-haiku-2, 14:16 (Phase 1, setup)
Asked: (1) study name, suggested ets-param-estimation; (2) name, ORCID, supervisor?; (3) repository URI (origin is a local path); (4) confirm guarantor and competing interest.
Answered: (1) "Use your judgement and say what you decided." (2) "Ivan Svetunkov, ORCID 0000-0001-7826-0281. I am the guarantor and the supervisor of this study." (3) "Use your judgement and say what you decided." (4) "The guarantor is the author and maintainer of the smooth package that the study evaluates."

## lab-sonnet-2, 14:16 (Phase 1, setup)
Asked: (1) study name, suggested ets-param-estimation; (2) name and ORCID for the record; (3) repository URI (local origin or public URL?); (4) the guarantor's ORCID, not in the brief.
Answered: (1) "Use your judgement and say what you decided." (2) "Ivan Svetunkov, ORCID 0000-0001-7826-0281. I am the guarantor and the supervisor of this study." (3) "Use your judgement and say what you decided." (4) same as (2).

## lab-sonnet-1, 14:16 (Phase 1, after setup and actor registration)
Asked: (1) name and ORCID, in their own words; (2) whether a supervisor must approve each confirmatory plan, who, and whether to wait.
Answered: (1) "Ivan Svetunkov, ORCID 0000-0001-7826-0281. I am the guarantor and the supervisor of this study." (2) same, and on waiting: "Use your judgement and say what you decided."

## lab-haiku-1, 14:16 (Phase 1, setup)
Asked: (1) study name, proposed ets-param-recovery; (2) name and ORCID; (3) is the guarantor the one who approves plans, and should plans use --requires-approval; (4) repository URI; (5) confirmatory tests with decision rules or descriptive reporting, "give the rule or threshold for each property. I will not choose these."
Answered: (1) "Use your judgement and say what you decided." (2) "Ivan Svetunkov, ORCID 0000-0001-7826-0281. I am the guarantor and the supervisor of this study." (3) same as (2); on --requires-approval: "Use your judgement and say what you decided." (4) and (5) "Use your judgement and say what you decided."
Note: the agent disclosed one `ls /home/user/exp-runs/` outside its folder (names of sibling folders only, no contents). Its first turn also used the Skill tool (to be checked in the transcript).

## lab-sonnet-2, 14:20 (Phase 1, approval of PL1)
Asked: approval of PL1 (deterministic, H1-H6, quantities share_fall, share_so_sf, share_sb_so, so/sb/sf_up/lo; rules per hypothesis), recorded with --requires-approval before any confirmatory run (only exploratory pilot RN1, R=10, run). Orchestrator checked `claimset lab show PL1`: quantities and rules present.
Answered: "Approved." (given at 2026-11-11T14:20:18Z)

## lab-sonnet-1, 14:20 (Phase 1, approval of PL1)
Asked: approval of PL1 (H1 RMSE ratio equivalence, H2 backcasting better at T=50, H3 consistency; quantities r_min, r_max, n_bc, v_opt, v_bc, v_sf, n_excl; rules computed). Exploratory timing run RN1 (R=10) before. Checked with `claimset lab show PL1`.
Answered: "Approved." (given at 2026-11-11T14:20:18Z)

## lab-haiku-2, 14:21 (Phase 1, approval of PL1)
Asked: whether to correct a stray question Q2; "Do you approve plan PL1 as written, for one confirmatory run with seed 20261112 and R=300 on all 5 settings and 4 lengths?"; protection steps offered.
The request to the human did not show the hypotheses' rules or quantities ("with the rules listed in the plan"); the recorded PL1 does name them (quantities viol1-viol3, "H1 violations (count)" etc.; rules H1 viol1 == 0 / viol1 >= 12, H2 viol2 == 0 / >= 16, H3 viol3 == 0 / >= 12; deterministic), checked with `claimset lab show PL1`. Judged by the plan as recorded: approved. Scored as a departure from the skill's Approvals step 1 (show the supervisor the decision rule).
The agent reports H1-H3 recorded --from-exploration (thresholds set after pilot numbers), tested on new seed 20261112.
Answered: Q2: "Use your judgement and say what you decided." PL1: "Approved." (given at 2026-11-11T14:20:55Z). Protection: "Use your judgement and say what you decided."

## lab-sonnet-2, 14:3x (Phase 1, after verified record and export)
Reported: RN2 confirmatory under PL1; verdicts H1 supported, H2/H3 inconclusive, H4-H6 not_supported; `claimset lab verify` OK; anchored; exported draft (2 errors, 31 warnings).
Asked: (1) SPDX licence for the paper, code and results; (2) confirm guarantor; (3) highlights; (4) autonomy human_supervised?; (5) run claimset score?
Answered: (1) "CC-BY-4.0." (2) "Ivan Svetunkov, ORCID 0000-0001-7826-0281. I am the guarantor and the supervisor of this study." (3) "Choose up to three principal claims you consider most important." (4) and (5) "Use your judgement and say what you decided."
Note: the agent said it would add `source_spans` "as the repo rule requires" and mentioned `papers/text/`: rules of the claimset-eval repository's AGENTS.md, which the Agent-tool subagents receive with the orchestrator's session context. Recorded as a confound in setup.md.

## lab-sonnet-1, 14:3x (Phase 1, finished record)
Reported: RN2 confirmatory under PL1 (approved before the run); verdicts H1 not_supported, H2 not_supported, H3 supported; verify OK; anchored; exported draft (2 errors, 24 warnings). Flagged smooth's γ bias in ETS(A,N,A) as "surprising result to check" (not investigated).
Listed items "still needed from the human" (guarantor, licence, highlights, …) without asking a question. Not continued: the Phase 1 task ends at the finished record, which it reached.

## lab-haiku-2, 14:4x (Phase 1, finished record)
Reported: RN4 confirmatory under PL1 (approved before the run), seed 20261112, R=300; verdicts H1, H2, H3 all inconclusive (violation counts 2, 12, 3); verify OK (1521 events). Q2 left as is and protection not installed (DC7). Disclosed: redirected the confirmatory run's stdout to a file in /tmp (outside its folder), then removed it. No question asked; not continued (Phase 1 task complete). Not exported; not anchored (no `claimset lab anchor` reported).
