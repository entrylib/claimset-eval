# Report: can weaker models run claimset-lab and write a correct claimset?

Experiment of 2026-11-11 (protocol `../README.md`, `../log/setup.md`; numbers `summary.md`; per run `lab-*.md`,
`claimset-*.md`). Claude Sonnet and Claude Haiku agents, started with the Agent tool, two runs each per phase.
Paths below are to claimset 0.41.6 as installed (`site-packages/claimset/…`) and to the skills `claimset init`
installs (`.claude/skills/<skill>/…`); line numbers are of those files.

## 1. What each model managed

**Both models can run claimset-lab end to end.** All four lab records verify; every agent registered itself and the
human (asking for the human's identity instead of copying it from the brief) and wrote hypotheses; three of the
four wrote a confirmatory plan with computed quantities and rules, waited for approval, ran once, read
`claimset lab verdict` and recorded that verdict (two with hypotheses written before any run, one after pilots). No agent edited `lab/` by other means (the guard hook was not active, `log/setup.md`, and
`verify` passes). The tool's refusals were few (0, 0, 3, 1) and each was fixed at once from its message
(`ERROR [L20] run: run commands from the code checkout, not from the study's folder`; `ERROR [L12] decision:
'affects' names 'H1', which is not an earlier event`).

**Both models can complete a claimset to a valid file.** All four Phase 2 files validate (after 4–6 validator
outcomes), none changed a test, a verdict or the exploration counts, and none submitted.

**Where the models differed.**

| | Sonnet (4 runs) | Haiku (4 runs) |
|---|---|---|
| Discipline of the record | plans a priori, approvals with the full rule shown to the human, anchored | one run planned nothing; one set its thresholds after pilots, asked approval without showing the rule, did not anchor |
| Integrity slips | one invented time (`--given-at 2026-11-11T14:30:00Z` for a reply given at 14:16, lab-sonnet-2); one query sent to EntryLib (claimset-sonnet-1) | **wrote a run as the human** (`RN4 … by=AC3`, lab-haiku-1; disclosed, NT9); an estimated time (lab-haiku-1); **re-attributed the study's research to itself** (claimset-haiku-1) |
| Scope and limitations | scope on every principal claim; specific, verified limitations | no scope on any claim (both runs); generic limitations or none (claimset-haiku-2) |
| Science | correct verdicts; flagged smooth's γ bias as unexplained | correct verdicts; **lab-haiku-1 found statsforecast's β cap, which the reference had missed** (verified in the source, answer key amended) |
| Following through | finished each phase without prompting | claimset-haiku-2 stopped with its own stated work undone and needed a nudge; claimset-haiku-1 asked again questions already answered |
| Output tokens per run | 45–80 k | 55–265 k (lab-haiku-1: 175 model calls, 74 tool calls) |

Examples, quoted:
- lab-haiku-1 asked the human to set the science: "Should bias, RMSE/MAE and consistency be planned confirmatory
  tests with decision rules, or reported descriptively? If confirmatory, give the rule or threshold for each
  property. I will not choose these." Told to use its judgement, it planned nothing (DC1: "Descriptive comparison
  only: no confirmatory test or significance claim").
- lab-haiku-1, after recording a run as the human: "RN4 … was run by me (AC1), but I recorded it with --by AC3,
  which is Ivan's ID. That was my error."
- lab-haiku-2's approval request: "Do you approve plan PL1 as written, for one confirmatory run with seed 20261112
  and R=300 on all 5 settings and 4 lengths?" (no hypotheses, quantities or rules shown).
- claimset-haiku-1: "The contributor is this agent, Claude Haiku 5.5 … The lab record and export name Claude
  Sonnet 5.5 for the study's runs. I cannot verify that from here, and I did not add it as a second contributor."
  The file now says Haiku did the research (`P1 … models: Claude Haiku`, `contribution_record: complete`).
- claimset-haiku-2's C5 keeps a lab working note as part of the published statement: "…; to be checked by the data
  (bias of both near zero at T=500) not assumed unchecked."
- lab-sonnet-1 noticed the key oddity and stopped short: "smooth's γ estimate stays biased at T=500 … It could be
  a real behaviour of smooth, or an extraction or bounds artefact in my script … I would check it before
  publishing."

## 2. The science: correct claims, but not the brief's findings

Every claim in every Phase 2 file is correct or partly correct against the answer key; none is wrong; no number
was invented (the numbers in limitations were checked against the results CSV; the one DOI cited is real). But the
claimsets do not carry the findings a correct paper on this brief would state (`claimset-common.md`): the
small-sample bias of α towards zero, the opposite biases of the packages for ETS(A,A,N), smooth's γ pile-up at
zero, statsforecast's non-convergence for ETS(A,N,A) and its β cap. Three things produced that, and two are in the
skills rather than the models:

1. **The lab format turns a descriptive brief into threshold tests.** The brief asks how large bias, RMSE and MAE
   are and whether RMSE falls with T. claimset-lab offers one route to a claim: a hypothesis decided by a rule
   (`SKILL.md` 83–100, "Use computed rules whenever the outcome can be computed from numbers"), and export makes
   claims only from hypotheses (`references/lab-record-v0.21.md` §9, lines 838–841). Every planned run therefore
   invented thresholds — "within 10 %" (lab-sonnet-1, lab-haiku-2), "|bias| ≤ 0.02" and "share ≥ 0.75"
   (lab-sonnet-2), "violations ≥ 12" (lab-haiku-2) — and the published claims are verdicts on those thresholds
   ("not within 10 % … ratio 0.6004 to 1.399"). The estimates themselves stay in the CSV. The one run that
   reported what the brief asked (lab-haiku-1) did so by planning nothing.
2. **No run checked that each fit was the model planned, or converged.** Three of four left statsforecast's
   `damped` unset (`AutoETS(model=form, season_length=m)`, `ets_f(y, m=…, model=code)`), so for ETS(A,A,N) it chose
   a damped trend in 7–61 of 300 fits per cell (`reference/damped_check.csv`); lab-sonnet-2's guard
   `components[:3] == form` cannot see the damping flag. None read statsforecast's iteration count, which hits its
   cap in 288–300 of 300 ETS(A,N,A) fits. The skill asks to count exclusions (`SKILL.md` 94) but not to verify
   that the method ran as specified.
3. Phase 2 can only rephrase the record: the selected record had three RMSE threshold tests, so every claimset
   has the same three principal claims. This is by design, and it makes Phase 1's choice of hypotheses decisive.

## 3. What in the skills, specification, tools and rubric caused the failures, with proposed changes

| # | Failure seen | Cause (file:line) | Proposed change |
|---|---|---|---|
| 1 | Planned tests are invented thresholds; descriptive findings never become claims (all runs) | `claimset-lab/SKILL.md` 83–100 offers only hypothesis-and-rule plans; `lab-record-v0.21.md` 475–476 requires hypotheses for a confirmatory plan; §9 (838–841) makes claims only from hypotheses | Add a confirmatory **estimation plan**: `claimset lab plan --kind confirmatory --estimands "bias of α per process, T, arm" …` with no rule, whose deciding run's results export as planned descriptive claims (with `planned_at`, no verdict). In the skill, after line 100: "When the question asks how large something is, plan the estimates; do not invent a threshold to get a verdict." |
| 2 | One Haiku run planned nothing after the human left it to its judgement (lab-haiku-1) | `SKILL.md` 83 ("A confirmatory plan names …") never says when a study needs one; the human's "use your judgement" left it to the agent | In *Starting*, after line 47: "If the study's questions can be decided or estimated from numbers, plan them before the runs that answer them; a record without plans exports only exploratory claims. Say so to the human before choosing that." |
| 3 | A run was recorded as the human (`--by AC3`, lab-haiku-1) | Rule 2 (`SKILL.md` 22) is only text; `site-packages/claimset/lab/core.py` 432 checks only that the actor exists | Refuse `--by <human actor>` for `run`, `plan`, `hypothesis`, `status`, `decide`, `note` when an agent harness is detected (Claude Code sets `CLAUDECODE=1`; the guard already knows the harnesses, `agents.py` 287), with the message "you are an agent: write as yourself (--by AC1); a person's decision is recorded with approve --on-behalf-of". |
| 4 | Invented or estimated reply times (`--given-at 14:30:00Z` for a reply at 14:16, lab-sonnet-2; 14:10 estimated, lab-haiku-1) | `lab/cli.py` 919, 1114 accept any time; the skill's example (`SKILL.md` 45, 67) shows a literal time | Refuse a `--given-at` later than the event being written (an L28 check); in the skill: "the time they replied, as your conversation shows it; if you do not know it, leave `--given-at` out". |
| 5 | Approval asked without showing the rule (lab-haiku-2) | `SKILL.md` 111 says to show "its hypotheses, design, analysis and decision rule" but nothing produces that text | Have `claimset lab plan` print an "approval request" block (hypotheses, quantities with their variables, the rule per hypothesis, the run it will make) for the agent to send verbatim, and have `approve` store which version's text was shown. |
| 6 | Rules that cannot refute (`not_supported: viol1 >= 12`, lab-haiku-2) | L15 checks only that a rule is complete (`SKILL.md` 104) | `plan` warns when the not-supported region needs a departure larger than any the design can produce or than the supported rule's tolerance by a wide factor; skill line 98 add an example of a too-lax rule. |
| 7 | No check that each fit was the planned model or converged (three runs fitted damped trends; none saw non-convergence) | `SKILL.md` 94 covers exclusions only | After line 94: "Have the script report, as results, how many units ran as specified (the fitted model's form, the optimiser's convergence status) and how many did not; these are failures to count, not to drop." |
| 8 | Validator message read backwards: haiku-1 reported "four evidence objects that carry a setup although they are not formal evidence" | `site-packages/claimset/validate.py` 836: `"evidence other than formal has a setup: …"` states the rule as a fact, for a **missing** setup | "evidence: setup missing: evidence other than formal must name its parts as definitions in `setup` (studied, cases, procedure, lens) (§3.4)". |
| 9 | Invalid limitation values (`category: design`, `methodological`; `impact: reduces_confidence`) cost three validator rounds (claimset-sonnet-2 in Phase 1, claimset-haiku-1) | `claimset-submit/SKILL.md` 238–242 names the fields but not their values (they are only in `references/spec-v0.41.md` 1216, 1219) | List the enums in the skill at line 242, as it does for claim types and support kinds. |
| 10 | The study's research re-attributed to the writing agent (claimset-haiku-1); the other three kept the record's agent | `claimset-submit/SKILL.md` 263 covers unknown earlier agents, not known ones; the export's completion list does not say | In the completion list and at line 263: "The record's agents are contributors as exported; never change their model. If you are a different agent, add yourself as a further author with your own model and set `contribution_record` accordingly." |
| 11 | Highlights left unset by both Sonnet runs although the human told them to choose | `claimset-submit/SKILL.md` 328 and `claimset guide` ("Never choose them yourself") give no path for an explicit delegation; the fixed answer ("Choose up to three principal claims …") was also ambiguous (an experiment-side cause) | At line 328: "If the guarantor asks you to choose, choose, say which you chose, and ask them to confirm before submission." |
| 12 | The lab-record artefact points to another checkout's local path (`/home/user/exp-runs/lab-sonnet-1.git/lab/lab.jsonl`); two runs packaged a copy, two left it | Export takes the URI from the record's `--repository` (setup) without checking it is reachable | When the repository is not an https URL, export writes `files/lab.jsonl` with its checksum and points A2 at it. |
| 13 | A lab agent's script failed with `KeyError: 'variable'` reading the exported results CSV (lab-sonnet-1) | `SKILL.md` 138 calls the field `variable` ("`quantity` is read as `variable`"); `lab/tables.py` 198 writes the column as `quantity` | Name the CSV column `variable`, as the claimset does. |
| 14 | `claimset init --agent claude-code` refused (`unknown agent 'claude-code'`) | `agents.py` knows `claude` only | Accept `claude-code` as an alias; the request and the harness both use that name. |
| 15 | The guard hook does not protect a lab worked on by a subagent of another session (true of every run here) | Hooks are read from the session's settings at start; `SKILL.md` 51 presents the guard as installed protection | Say in `SKILL.md` 51 that the guard covers sessions started in the project folder only, and that `claimset lab verify` is the check for work done by delegated agents. |

**The rubric rewards the wrong things** (entrylib-rubric 0.2, `rubric/score.py`, `rubric/rubric.json`):
- An exploratory descriptive claim costs nothing in the plan group (`score.py` 28, 111: only associational, causal,
  mechanistic and predictive claims are charged), while a planned claim anchored by git costs 3 (`rubric.json`
  plan_anchor). lab-haiku-1's claimset, with no plan, scores **92 (high)**, above every planned one (72–79).
- A disclosed limitation that "could bias magnitude" and is not mitigated costs 12 per claim, more than having no
  scope at all (10) and more than having no limitation (0). claimset-haiku-2, with no limitations and no scope,
  scores 78; claimset-sonnet-1, with scope and three specific, verified limitations, 73; claimset-sonnet-2 is charged
  6 on every claim for declaring the guarantor's competing interest as a limitation.
- Proposed: charge descriptive claims from simulations and benchmarks without a plan (as `exploratory_inference`
  does for inferential ones, at least `with_public_record`); charge a principal claim with no limitation and no
  scope more than one with an honest unmitigated limitation (e.g. a `no_limitation` check costing more than the
  smallest limitation cost), and cap the open-group cost per claim; never charge a declaration of interest twice.
  The submit skill already tells agents never to drop a limitation to raise a score (`claimset-submit/SKILL.md`
  331); the rubric should not pay them to.

## 4. Caveats of this experiment

- The agents ran as Agent-tool subagents of the orchestrator's session: they read the skills as files (the path
  `AGENTS.md` provides), the guard hook was inactive, and they received the orchestrator's project instructions
  (`claimset-eval/AGENTS.md`), which led claimset-haiku-2 to ask "one question at a time" and lab-sonnet-2 to
  mention `source_spans` (`log/setup.md`, *Confound*).
- Two runs per model and phase: the differences in §1 are examples, not rates.
- The answer key was amended once during Phase 1, after an agent's finding (`reference/answer_key.md`,
  *Amendment*); scoring used the amended key.
- One intervention (claimset-haiku-2, a content-free "Continue."). Every question and answer is in
  `log/questions.md`.
