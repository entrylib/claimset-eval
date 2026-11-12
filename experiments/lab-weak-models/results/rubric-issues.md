# Issues with EntryLib's scoring rubric found in this experiment

entrylib-rubric 0.2.0 (commit 8a6f9f948a83c0a6f8c60c1e101ed5c4f5399caf), run locally with `claimset score`.
Paths are inside the installed package `rubric/`. Not part of the claimset.

1. **Unplanned descriptive claims are never charged for lacking a plan.** `score.py` 28 and 111 charge
   `exploratory_inference` only for associational, causal, mechanistic and predictive claims. A descriptive
   claim from a simulation or benchmark with no plan costs 0 in the plan group, while a planned claim anchored by
   git costs 3 (`rubric.json`, `plan_anchor`). Seen: lab-haiku-1's claimset, with no planned test, scored 92;
   every claimset with planned tests scored 72–79.

2. **Disclosed limitations cost more than leaving things out.** An unmitigated limitation that "could bias
   magnitude" costs 12 per claim and one that "could reverse" costs 20 (`rubric.json`, `limitation`), against 10
   for no scope and 0 for no limitations at all. Seen: claimset-haiku-2, with no limitations and no scope, scored
   78; claimset-sonnet-1, with scope and three specific, verified limitations, scored 73. The submit skill tells
   agents never to drop a limitation for the score; the rubric rewards dropping it.

3. **Limitation costs add up without a cap.** Each limitation is charged on every claim it affects, and the
   costs are summed. A claim with several honest limitations can lose 30–40 points in the "open" group alone. In
   this paper's own claimset, C2 and C3 lose 20 (L1) + 6 (L2) + 2 (L5) + 3 (unchecked assumption).

4. **Declaring a competing interest as a limitation is charged on every claim.** claimset-sonnet-2 recorded the
   guarantor's competing interest as a `researcher_position` limitation mitigated partially and lost 6 points on
   every principal claim, although it is already declared in `paper.declarations`. Nothing tells the author to
   declare it only once.

5. **The support cost is the best of a claim's supports, with no check of what the evidence shows.**
   `score.py` 73–90 takes the cheapest support kind. An interpretive claim resting on an argument costs 30; adding
   any evidence pointer makes it 0, whatever that evidence shows. Seen here: C8 went from 29 to 59 by adding a
   table of the plans' thresholds. That table is real support, but the rubric would have given the same 30 points
   for any evidence pointer. `EVIDENCE_KINDS` (line 27) also counts `demonstration` as evidence.

6. **The unlinked-numbers check accepts any `results` entry.** `score.py` 150–153 charges a claim whose
   statement has a digit only when none of its supports lists `results`; it does not check that the numbers come
   from those results. `_has_numbers` (93–96) counts digits in names, such as "claimset-haiku-2", as numbers.

7. **Problems are inherited through `depends_on`, and the report does not say so.** `_closure` (172) charges a
   claim for the problems of every claim it rests on. Seen: C10 and C11 lost 5 points each for the unlinked
   numbers of C13 and C14. In the JSON report, a claim's `problems` lists the inherited problem IDs, but the
   paper-level `problems` entry lists only the claims charged directly, so the two disagree.

8. **The paper's score is its weakest principal claim.** `score.py` 269–271. One interpretive principal claim
   (C8, 29) set the whole paper to 29 while the other principal claims scored 60–88. Authors are pushed towards
   fewer principal claims and away from interpretive ones. Band edges make it sharper: 59 is "low", 60 is
   "medium" (`rubric.json`, `bands`).

9. **Studying an API model costs every claim about it.** The validator's `api_model_dependency` flag
   (`claimset/validate.py` 3390) costs 5 per claim (`verifiability_flags`). It cannot be avoided when the
   proprietary model is the subject of the study, not a tool of the analysis.

10. **Related: the validator's W13 warns even when the rationale complies.** "Exploratory principal claim: say so
    in the assessment rationale" (`claimset/validate.py` 3190) is raised for every exploratory principal claim,
    without reading the rationale. This claimset's 11 W13 warnings all have rationales that start "Exploratory:".
