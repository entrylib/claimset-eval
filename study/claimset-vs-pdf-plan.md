# Claimset or PDF: do LLMs answer questions about a paper better from its claimset?

**Study:** `claimset-vs-pdf` (lab record on branch `claimset/claimset-vs-pdf`, entrylib/claimset-eval)
**Actors:** AC1 research agent (records, randomises, pastes, processes); AC2 Ivan Svetunkov (supervisor; sets up chats, copies them, moderates grades); a second moderator, to be registered before grading.
**Status:** recorded on 2026-11-24 (lab events seq 17–34: Q1, TM1–TM12, H1–H3, PL1), approved by the supervisor (AP1), anchored on the study branch. Revised on 2026-11-25, before any data (seq 36–38): the chat protocol asks for short answers in its opening sentence (TM13, correcting TM7), and PL2 is the version of the plan that holds it, otherwise unchanged, approved by the supervisor (AP2). Revised a third time on 2026-11-25, before any data (seq 50–55), approved by the supervisor (AP4): the futility look after DeepSeek's fast configuration, collected first (§3.3, DC10.R2), the apps' configurations as found in the practice (§7), masking of every identifier, and the extended transcript checks; TM17–TM19 correct the chat protocol, grading and the apps, and PL4 is the plan version that holds them. Revised again on 2026-11-25, before any data (seq 43–47), approved by the supervisor (AP3): after the practice chats (NT1–NT3), the chat protocol (TM14), the apps (TM15) and grading (TM16) are corrected and PL3 is the version of the plan that holds them: normal chats only, web search where it cannot be switched off, plain file names, the model recorded once per chat, every chat ending with a transcript request whose page is saved, transcripts checked, and file names and citation tags masked. Hypotheses, decision rule, analysis and data are unchanged. Recorded supervisor decisions DC1–DC9 (Claude models excluded; no no-document and no paper-as-text condition; grading; the level; the decision model; no local model in this study, DC9, which replaces DC4 and DC8) and the simulations RN1–RN4 that chose the model.

---

## 1. Research question and what "better" means

**Claimset.** A research paper written as a structured record for LLM readers, following the Claimset specification (v0.44, `github.com/entrylib/claimset`). The paper is a set of atomic, self-contained **claims**, each with its scope and conditions, and the objects that support, condition and limit them: the **evidence** for each claim (data, methods, results tables, proofs), definitions, assumptions and **limitations**. Every object has an identifier and is linked to the others by it, and every claim records its type, scope, support, strength and verifiability. It is a distillation of the paper's argument, not a transcription: it carries the claims and the results they rest on, not the full text, and is shorter than the paper's body. A claimset is stored as JSON and read by models as plain text, its **reading view**. The five claimsets used here were written with the papers' author and are published on EntryLib.

**LLM.** A large language model used through its provider's own chat app, with tools and web search off.

**RQ1.** When a paper's claimset holds what a question asks, do LLMs answer questions about the paper better from its claimset than from its PDF?

The claimsets were completed for this question set: anything a question asks that the paper states is in the claimset. RQ1 is therefore about how well models read a claimset that has the answer, against the PDF that has it too; it is not about what a claimset leaves out (§11).

**Better** has two parts, tested separately (§2):
- **Correct answers:** on a question the paper answers, the answer is correct and complete. Scored per answer:

| Answer to a question the paper answers | Score |
|---|---|
| correct and complete | 1 |
| partly correct (incomplete or imprecise on something asked, or correct with an added error) | ½ |
| incorrect, or "the paper does not say" | 0 |

- **No invented answers:** on a question the paper does not answer (an **absent question**), the answer says the paper does not state it, rather than presenting something as the paper's. A flag per answer: **invented** = 1 if the answer presents as the paper's anything the paper does not state, 0 otherwise. Outside knowledge clearly marked as not from the paper is not invented.

A further aspect is measured as a secondary outcome:
- **Overreach:** the answer states a result more broadly than the paper allows (beyond its data, conditions or population), whatever its score. A flag, 0 or 1.

The comparison is **pragmatic**: each condition is the file as the app handles it (the app may extract, chunk or retrieve from a PDF). The effect estimated is that of giving an LLM the claimset file instead of the PDF in ordinary use; the two differ in format, length, structure and content at once (§11).

## 2. Questions, conditions and hypotheses

**Questions** (fixed before this plan, with the author's reference answers):
- **Per-paper questions:** 20 for each of the 5 pilot papers, 100 in all: 30 lookup, 25 scope, 20 evidence, 25 absent. The 75 answerable ones (lookup, scope, evidence) are all answered in the claimsets; the 25 absent ones are answered by neither document.
- **Cross questions:** 13 across the papers (5 identification, 3 comparison, 5 relation); the claimsets hold the answer to 10. Exploratory (§6).

The question files (`study/questions/`, with each question's reference answer and marking guide), SHA-256:

| File | SHA-256 |
|---|---|
| `doi-10-1002-nav-22074.json` (CES) | `acb606f1e8c6b50e5485666431d64d930284b9c244a4730cece0010f851ae4de` |
| `doi-10-1007-s00180-023-01377-x.json` (Multi-step estimators) | `52bf7a3e7a5f4cec58dfca9360b39a9fc6c8ecd1d0652f9b0df201bd3e762171` |
| `doi-10-1016-j-ejor-2022-04-040.json` (VES) | `43a59d01bc6dc37e39b243690b686bbfc41c573f5c6ea8662a8f42656226a862` |
| `doi-10-1093-imaman-dpad028.json` (Staying positive) | `dcbde5b3fd800f05d5a4157f0e3b86d247caeeab734e12bb670ca12fb92ab9ea` |
| `doi-10-1111-jtsa-12843.json` (Grundy et al.) | `903e6f444ce416c40c8b0ae8620025412446e4110984324fe392adee000c3252` |
| `cross-pilot.json` (cross questions) | `8a82fce9fde05bafddc48ddf0a19a19c41d0578b476358dbd7f60ca94e9d46c7` |

**Conditions:**
- **PDF:** the paper's published PDF, attached to the chat (cross chats: all five). For Grundy et al., the supplement is not attached; the questions do not need it. For VES, the authors' accepted manuscript: its tables are text, while in the published PDF they are images; every element the questions need is the same in both.

| Paper | PDF (`papers/pilot/`) | SHA-256 |
|---|---|---|
| CES | `Svetunkov et al. (2022) - Complex exponential smoothing.pdf` | `7ef69f7eb75152314abaa10bca49e9bc66802825ee5f674a86cbf26c3d900b6a` |
| Multi-step estimators | `s00180-023-01377-x.pdf` | `cfdbf84a4554a060e83ab8591996aba0c7dce56d121f1b2e51b3d7ec33d29780` |
| VES | `Svetunkov et al. (2022) - Vector exponential smoothing - accepted manuscript.pdf` | `02438f242d7e2b86215b9bf15f3dbe4164d0472f1c2726f9b974a20c5b2db1c9` |
| Staying positive | `dpad028.pdf` | `45bd7257df064666d76be2d9e57feec66cc35e564590cf78ca369d005ef752cb` |
| Grundy et al. | `Journal Time Series Analysis - 2025 - Grundy - Online Detection of Forecast Model Inadequacies Using Forecast Errors.pdf` | `31c61a89b8f89bb21677045e5fc043b1b157517ca05f1f26c4712fc3bfde34ec` |

- **Claimset:** the paper's claimset reading view, the plain text the Claimset specification defines for models to read (its Appendix D), attached as a .txt file (cross chats: all five). It is `claimset render --published` of the version below, as published on EntryLib on 2026-11-24: the text EntryLib serves for that version without the two parts EntryLib adds to it, SCORES (its rubric's assessment of the record, with a list of open problems) and HOW TO CITE. The SCORES part is left out because it is the platform's assessment, not the paper's content, and it points at the claims it finds weak, which would help the claimset condition on the scope questions for a reason that is not the format.

| Paper | Claimset | Reading view (`claimset/pilot/<name>.claimset.txt`), SHA-256 |
|---|---|---|
| CES | entrylib:2026.000012@v3 | `c207bc53eb568f14608eaaeb9aa82936b7247e4c60aedfaf78f6f4706a6f9d71` |
| Multi-step estimators | entrylib:2026.000011@v4 | `3c9a799dee12f81ff95e6b6afc5764df4178aed706233e8a9c9cb676fc1bd8f3` |
| VES | entrylib:2026.000017@v1 | `db78dc8f3c031565be83bdcc7c6ba27d8e48d6acc52ab08e8fd3d5d6fdba16f2` |
| Staying positive | entrylib:2026.000006@v6 | `3291932ef6d66a9f8eac86c4e9ab286e37d81863ed1aac68e213bab53fc6d9d4` |
| Grundy et al. | entrylib:2026.000010@v4 | `0baa250662c333fb33015cc197d9b5bbabc57c98ed4a5c1427df1d7836f991d7` |

**Hypotheses.** Two co-primary hypotheses answer RQ1; one secondary hypothesis looks inside the answers.

| | Hypothesis | Outcome | Questions | Part of RQ1 it answers |
|---|---|---|---|---|
| **H1** (co-primary) | LLMs score higher with the claimset than with the PDF on questions the paper answers | score | the 75 answerable | correct answers |
| **H2** (co-primary) | LLMs give invented answers less often with the claimset than with the PDF | invented (0/1) | the 25 absent | no invented answers |
| **H3** (secondary) | LLMs overreach less often with the claimset than with the PDF | overreach (0/1) | the 25 scope | not saying more than the paper says |

How the hypotheses answer RQ1 is fixed in §3.2.

## 3. Decision model and tests

### 3.1 The model

Each hypothesis is decided by one logistic mixed model, fitted to its questions in both conditions, for the ten confirmatory models (§7). The **models are fixed effects**: the ten apps are the population the claims are about, chosen by rule, not a sample of LLMs. The **questions are random effects**: the claims extend to questions like these, about these papers.

| Symbol | Variable | Coding |
|---|---|---|
| *y*, *n* | H1: the answer's score as points, *y* = 2 × score ∈ {0, 1, 2} of *n* = 2; H2, H3: the flag, *y* ∈ {0, 1} of *n* = 1 | the outcome, one answer |
| *x* | condition | dummy: 1 = claimset, 0 = PDF |
| *M*₂ … *M*₁₀ | model | dummies, model 1 the baseline |
| *a* | questions already put in the chat | count: 0–19 |
| *P*₂ … *P*₅ | paper | dummies, paper 1 (CES) the baseline |

$$\operatorname{logit} p_{ijc} = \beta_0 + \beta_1 x_c + \sum_{m=2}^{10} \mu_m M_{m,i} + \sum_{m=2}^{10} \gamma_m\, x_c M_{m,i} + \beta_2 a_{ijc} + \sum_{p=2}^{5} \pi_p P_{p,j} + w_{0j} + w_{1j} x_c,$$

$$y_{ijc} \sim \text{Binomial}(n, p_{ijc}), \qquad \begin{pmatrix} w_{0j} \\ w_{1j} \end{pmatrix} \sim N(\mathbf{0}, \Sigma_w).$$

- β₁ + γᵢ is model *i*'s own effect of the claimset (log odds ratio; γ₁ = 0).
- *w*₀ⱼ is question *j*'s difficulty, *w*₁ⱼ how much its effect departs from the models' average.
- The score as two binomial points makes ½ one point of two: a logit model for an outcome bounded by 0 and 1. The ordinal model of §4 checks it.

In R: `lme4::glmer(cbind(y, n - y) ~ x * model + a + paper + (1 + x | question), family = binomial)`.

**The tested quantity** is the claimset's effect averaged over the ten models:

$$\Delta = \frac{1}{10}\sum_{i=1}^{10} (\beta_1 + \gamma_i) = \beta_1 + \frac{1}{10}\sum_{m=2}^{10} \gamma_m,$$

with its standard error from the estimates' covariance matrix. It is checked by refitting with sum-coded models, where Δ is a single coefficient; the two must agree.

**Test.** *t* = Δ̂ / SE(Δ̂), compared with the *t* distribution on (number of questions − 1) degrees of freedom: 74 for H1, 24 for H2 and H3. One-sided, each at α = 0.05/3 ≈ 0.0167 (familywise 0.05 over the three confirmatory hypotheses, Bonferroni).

**Dimensions.**

| | Answers (rows) | Fixed effects | Random effects | Variance parameters | Answers per question |
|---|---|---|---|---|---|
| H1 | 10 × 75 × 2 = 1,500 | 25 (intercept, *x*, 9 model, 9 condition × model, *a*, 4 paper) | 150 (75 questions × intercept, slope) | 3 | 20 |
| H2, H3 | 10 × 25 × 2 = 500 | 25 | 50 (25 × 2) | 3 | 20 |

**If a fit fails** (the optimiser reports failure, or the Hessian is not positive definite), the correlation of the question effects is dropped; if it still fails, the question slope. The model fitted is reported. A singular fit (a variance estimated at zero) is kept and reported. Every fit reports whether it converged and whether it is singular.

### 3.2 Decisions

| | Questions | Outcome | Null hypothesis | Alternative | Supported if | Not supported (refuted) if |
|---|---|---|---|---|---|---|
| **H1** | 75 answerable | score | Δ ≤ 0 | Δ > 0 | *t* > 2.169 | *t* < −2.169 |
| **H2** | 25 absent | invented | Δ ≥ 0 | Δ < 0 | *t* < −2.258 | *t* > 2.258 |
| **H3** | 25 scope | overreach | Δ ≥ 0 | Δ < 0 | *t* < −2.258 | *t* > 2.258 |

(2.169 and 2.258 are the 0.9833 quantiles of the *t* distribution on 74 and 24 degrees of freedom.)

- **Supported:** the one-sided test rejects in the direction the hypothesis states.
- **Not supported (refuted):** the one-sided test in the opposite direction rejects at the same level: the ten apps do significantly worse with the claimset on it. Each outcome is declared wrongly with probability at most α.
- **Inconclusive:** neither. Reported with Δ̂ and its interval, on the odds-ratio and the raw scale; not read as "equally good".

**Answer to RQ1**, fixed in advance:
- **Yes, better:** H1 and H2 both supported.
- **Better in part:** one of H1, H2 supported and the other inconclusive; the result says which.
- **No:** either refuted, or both inconclusive.
- A claimset that only makes models say "not stated" more often, while answering no better, is reported as such: H2 supported, H1 inconclusive.

**Ceiling rule.** If the mean score with the PDF on the answerable questions is above 0.9 (averaged over the ten models), an inconclusive H1 is reported as uninformative: there was little room to improve.

### 3.3 Futility look (draft, for approval: PL5)

The five fast configurations are collected first, Kimi Instant first, then Grok Fast, ChatGPT Instant, Gemini 4 Hydrogen at Low and Qwen4-Max Fast. Kimi lists Instant ("fast chat, quick replies") apart from its flagship, K3.1 Pro, so it is very likely the smallest model behind any of the fast options; no data of the study ranks the configurations. Once, after Kimi Instant's 12 chats, its answers to the per-paper questions are given **interim grades**: Claude Fable alone grades them as one batch of coded, masked answers, and the supervisor alone moderates them, blind to condition. The interim grades are recorded (hashed) and used for the look only. A recorded run then computes, with the PDF only:

- the mean score on the 75 answerable questions;
- the rate of invented answers on the 25 absent questions;
- the rate of overreach on the 25 scope questions.

**No room:** the mean score is at least 0.95 and both rates are at most 0.05. The claimset then has nothing to improve on even for one of the weakest configurations, and the study **may stop**. Otherwise it continues, with no further look.

- **Non-binding and futility only.** The supervisor decides, and the decision is recorded with its reason. Stopping because there is nothing to find cannot raise the tests' error rate; there is no stopping because a result looks good. If Kimi Instant is not in fact among the weakest, "no room" could stop a study in which a weaker configuration would show a difference: the supervisor may then continue.
- **Blind.** The run reports only "room" or "no room" to the supervisor and the moderators and seals its numbers until the analysis; nothing by condition is shown before then.
- **If the study stops,** H1–H3 are not tested; Kimi Instant's results are reported as estimates from the interim grades, with the reason for stopping.
- **If the study continues,** the full grading of §9 follows after collection, over all answers mixed in one pool, with both judges (Fable and Mistral) and both moderators; the interim grades play no part in it.
- **Judges see only batches of coded answers** and are never told which configuration or batch an answer comes from.

**Precision** (by simulation, §12, RN7 for ten models; with guessed variances): H1 detects a gain of about 7 points in mean score with power about 0.96, and about 4 points with power about 0.6; H2 and H3 detect a drop of about 18 points in the rate of flagged answers with power about 0.94, and about 10 points with power about one third.

## 4. Sensitivity and estimation (reported, not decided)

- **Ordinal model for the score:** `ordinal::clmm(Y ~ x * model + a + paper + (1 + x | question))`, the cumulative logit for the ordered score (0, ½, 1); its averaged effect and *t* as in §3.
- **Raw differences:** each model's mean score (or rate) with the claimset minus with the PDF, and their average.
- **The effect on the score scale:** the mean predicted score (or rate) in each condition, averaged over the ten models and the questions, and their difference.
- **Generalising to other LLMs:** the models as random effects, with the provider, `(1 + x | provider) + (1 + x | model) + (1 + x | question)`, and Δ tested against *t* on (providers − 1) = 4 degrees of freedom. With five providers this has little power; it says how far the result can be read beyond these apps.
- **Fast against reasoning:** the mean of the reasoning models' effects minus the mean of the fast models' effects, with its standard error from the decision model.
- **Each model's own effect,** β₁ + γᵢ, with its interval and the model's mean score with the PDF; a model whose mean score with the PDF on the answerable questions is above 0.9 is marked as at the ceiling (§11).

## 5. Expected values (sanity check)

What the estimates should show if the models describe the experiment correctly. A result far from these is first checked as a possible fault (grading, import, protocol) before it is interpreted.

| Quantity | Expected | Reasoning | A warning sign |
|---|---|---|---|
| Δ, H1 | ≥ 0, near 0 | the answers are in both documents; the claimset may gain on tables and formulas and lose on detail | strongly negative: models read the claimset badly |
| Δ, H2 | < 0 | the claimset states its scope and limitations explicitly | — |
| Δ, H3 | < 0 | claims carry their conditions | — |
| each model's effect β₁ + γᵢ | mostly of the sign of Δ; smaller for reasoning models | reasoning models extract more from a messy PDF | one model strongly opposite: check its chats |
| reasoning minus fast | < 0 | as above | — |
| β₂ (questions asked) | ≤ 0, small | longer contexts help little or hurt a little | large: context loss; check per app |
| π (paper) | ≠ 0 | papers differ in difficulty and format | — |
| μ (model) | ≠ 0; reasoning models higher | reasoning models answer better | — |
| SD of *w*₀ (question difficulty) | large, about 1–1.5 on the logit scale | questions differ most | ≈ 0: grading ignores the question |
| SD of *w*₁ (effect by question) | smaller than SD of *w*₀ | the effect varies less than the difficulty | — |
| corr(*w*₀, *w*₁) | < 0 | easy questions leave less room to gain | — |
| mean score with the PDF | below 0.9 | the questions were written to need the paper | above 0.9: ceiling (§3.2) |

## 6. Exploratory analyses (reported, not decided)

- **Cross questions:** the mean score difference per model, the ten models' *t*, and the cross kinds; the 10 questions whose answer the claimsets hold separately from the 3 they do not.
- **Interactions**, each added to the decision model for the score one at a time, with the expected sign of its interaction with the condition:

| Interaction with the condition | Expected sign | Reasoning |
|---|---|---|
| paper | small; the effect of one sign for every paper | a paper with a strongly opposite effect: check its claimset and questions |
| where the answer is (text, table, figure, equation) | > 0 for table, figure, equation against text | PDF extraction loses tables and mathematics most |
| numeric answer | > 0 | numbers sit in tables and formulas |
| parts (facts the answer needs) | > 0 | the claimset keeps related facts together |
| location in the paper (0–1) | > 0 | retrieval and truncation lose late parts of a PDF more |
| spread (one passage or several sections) | > 0 | the claimset gathers what the PDF spreads out |
| overlap (question with document, words) | > 0 | checks item bias: a large positive interaction means the claimset wins where questions use its words |
| questions asked (*a*) | > 0 | the longer PDF context degrades faster along a chat |

The condition is randomised within every model and question, so leaving these out of the decision model cannot bias the effect. A variable fixed before the condition acts on the answer may enter; one the condition can change (post-treatment: answer length, time to answer, tokens of context so far, whether the app said it truncated the file, the model's own certainty) is described but not adjusted for, since adjusting for it biases the effect (Rosenbaum 1984; Montgomery, Nyhan & Torres 2018). Item variables are coded per question before collection, from the reference answer and its source in the paper.

- Also: scores by question type; F1–F3 coded; the share of chats in which F3 says "test"; judge–judge and moderator–moderator agreement; the blinding index; answer length.

## 7. Subjects (models)

Purposive sample, fixed by rule before collection: from each hosted provider's app, one **fast** and one **reasoning** configuration, each the most capable of its kind on the supervisor's plan; no Auto mode; the thinking level fixed. Current names, from secondary sources (to confirm in each picker):

| Provider (app, plan) | Fast | Reasoning |
|---|---|---|
| Google (Gemini, Google Pro) | "Everyday help", Gemini 4 Hydrogen, thinking level Low | "Deeper analysis", Gemini 4 Neon, thinking level High (Gemini 4 Carbon is locked on the plan) |
| OpenAI (ChatGPT Plus) | "Instant" | "Thinking effort" at its highest setting, "High" |
| xAI (Grok Plus) | "Fast" | "Expert" (no Heavy on the plan) |
| Alibaba (Qwen Chat) | Qwen4-Max, mode "Fast" | Qwen4-Max, mode "Thinking" |
| Moonshot (Kimi Plus) | "Instant", Thinking effort at its lowest if it applies | "K3.1 Pro", Thinking effort at its highest, "High" |

As found in the practice and the reading checks (lab notes NT1–NT7) (draft, for approval: PL5). ChatGPT, Grok and Kimi show no model name beyond these labels. The labels shown are recorded once per chat. **DeepSeek was dropped** (DC12): its free chat reads only the first 20 pages or 10,000 tokens of a file, so it read neither document whole for most papers, and its transcripts failed on long files; its two chats were excluded unread. Qwen Chat and Kimi took its place, and each read the 37-page VES PDF to its last page.

Ten confirmatory subjects. Claude is excluded (DC1). Conclusions are about these ten apps as used in late 2026, on questions like these; how far they extend to other LLMs is a sensitivity analysis (§4).

**Sample.** Per-paper: 10 models × 100 questions × 2 conditions = 2,000 answers; cross: 10 × 13 × 2 = 260 answers. Fixed in advance; no interim analysis.

## 8. Threats to validity and how the design meets them

1. **Time and carryover (crossover trials; Senn 2002).** Chats are collected in pairs: one paper's PDF chat and its claimset chat, back to back, in a random order within the pair, with the pairs in a random order. Anything that changes over time (the provider updating the model) then falls on both conditions alike. New chats with memory and chat-history settings off keep one chat from influencing the next; the practice chats check this ("Do you remember anything from our earlier chats?").
2. **Subject drift and silent downgrades.** Apps update models and may switch to a lesser model when a usage limit is reached. The model and thinking level are set once per chat and recorded from the app's picker (the apps tried show no model on each reply), and are not changed during collection; for each message, any limit, downgrade or model-change notice is noted. A chat with such a notice is run again once, in a new chat, and counted as a deviation.
3. **Items as a sample (the language-as-fixed-effect fallacy; Clark 1973).** Questions are random effects in the decision model, so the claims extend to questions like these, about these papers (Baayen, Davidson & Bates 2008; Barr et al. 2013).
4. **Item bias.** The author wrote the questions and the reference answers with the agent, and the claimsets were completed for them (§11). The overlap interaction (§6) checks lexical bias; structural bias is a limitation.
5. **Position in long contexts (Liu et al. 2024).** 20 questions in one chat lengthen the context: randomised question order, questions asked in the decision model, its interaction explored.
6. **Evaluation awareness (Needham et al. 2025).** Natural wording and one plain opening sentence, whose only instruction is to keep answers short (the same in every chat and both conditions); F3, asked last, is the manipulation check. Exploratory: results without chats in which a model said, unprompted, that it was being tested.
7. **Experimenter effects (Rosenthal 1966; Orne 1962).** The messages are fixed and pasted verbatim; the agent that pastes them does not read the replies, beyond seeing that a reply has finished; nobody reacts to an answer.
8. **Blinding of assessors (Schulz & Grimes 2002).** See §9; blinding success is measured (Bang et al. 2004), with a consequence fixed in advance.
9. **LLM-as-judge biases (Zheng et al. 2023; Panickssery et al. 2024).** Two judges from different families (Claude Fable and Mistral), neither a subject; answer length recorded; every grade moderated.
10. **Missing data (intention to treat).** A model's failure (it cannot read the file, refuses, answers off-topic) is an outcome and is scored. A failure of the infrastructure (the app errors or loses the chat) means the whole chat is run again once, in a new chat; if that fails too, its answers are excluded from both conditions and counted.
11. **Pragmatic conditions (PRECIS-2; Loudon et al. 2015).** How each app handles a PDF is part of the treatment; file limits (five PDFs in a cross chat) are checked in the practice chats, and any deviation is recorded.
12. **Terms of use.** The agent only types and waits; it never extracts or copies replies. The app itself writes each chat's transcript when asked, and the supervisor saves the page (§10).

## 9. Grading

Neither the judges nor the moderators learn which condition or model an answer came from.

1. **Coding.** The import run takes each chat from its checked transcript (§10), splits it into answers and gives each a random code. The key (code → model, condition, chat) goes to a file that only the final analysis run reads.
2. **Masking**, the same in both conditions: claimset identifiers of every kind (claims, definitions, evidence and its tables and rows, warrants, limitations, artefacts, references: C12, D4, E3.T1.r2, L2, B3, …) and paragraph markers, and locators (page, section, table, figure, appendix numbers) are replaced by "[location]"; phrases naming the document's form ("the claimset", "the reading view", "the PDF", "the .txt file") by "the paper"; file names, the apps' file-name chips and their citation tags (such as ChatGPT's `<FileCite …/>`) are removed. Masking is tried on the practice chats first and its rules fixed before grading.
3. **Two judges**, in turn: first Claude Fable grades every answer, then Mistral (its most capable model, through its API), independently, without seeing Fable's grades. Each grades every answer against the reference answer and its **marking guide** (what is required, what else is correct, what is not required, what is wrong), written so that it does not tell the documents apart; graders never see the authors' notes on the questions: a grade, the flags (invented, overreach) and a reason. Answers are graded one question at a time, all its answers in random order, models and conditions mixed. Instructions are fixed and their hash recorded.
4. **Disagreement report**, once both judges have graded every answer and before moderation: a recorded run, blind to model and condition, lists the answers on which the judges differ (in the grade or a flag), question by question, with both judges' reasons; for each question and judge, any systematic difference (one judge giving ½ where the other gives 1, or flagging more often); and the agreement (weighted κ for the score, κ for each flag). It describes and proposes no grade: the agent is a Claude model, and a grade from it would be a third judge, of the same family as one of the two, and would anchor the moderators.
5. **Two moderators**, the supervisor and a second person, last. Each reviews every answer on the blinded sheet, with both judges' grades and reasons and the disagreement report: where the judges agree, they approve the grade or replace it, with a reason; where the judges differ, they choose the grade, with a reason. Where the moderators disagree, they agree a grade together, still blind. The agreed grade is analysed; the judges' and moderators' grades are kept.
6. **Consistency check**, after moderation and before locking: a recorded run, blind, flags within each question the answers that state the same thing but have different agreed grades. The moderators review them again, blind, and keep or change each grade, with a reason.
7. **Marking guides stay fixed** (by their hashes). If moderation shows a guide to be ambiguous, its clarification is recorded as a deviation from the plan, with the reason, and applied to every answer of that question, blind, before locking.
8. **Locking.** The final grades are recorded (hashed) before the key is opened; only then does the analysis join grades to models and conditions.
9. **Agreement**, after locking, reported and never used to change a grade: judge with judge, each judge with the final grade, and moderator with moderator (weighted κ for the score, κ for each flag), overall and by question type.
10. **Blinding check**, after grades are locked: each judge and each moderator guesses the condition of a random 10% of answers (PDF, claimset, cannot tell). If Bang's blinding index for correct guesses exceeds 0.2 for any assessor, the results are also reported with the judges' grades alone, and the report says that blinding was partial.

The rubric's edge cases, fixed in the judges' instructions: an answer correct on what is asked but with an added error scores ½; an answer listing several alternatives of which one is right scores 0; under the claimset, "this record does not say; the paper might" on an absent question is not an invented answer.

## 10. Collection

- **Practice chats** first, one per app, with made-up questions about invented documents (`study/practice/`): settings, memory, typing by the agent, file limits, transcripts, usage meters, masking. Not data. What they found is recorded in lab notes NT1–NT3.
- **Chats per model:** 6 with the PDF (5 per-paper + 1 cross) and 6 with the claimset; 12 in all, with 274 messages (226 questions, 36 follow-ups, 12 transcript requests).
- **Each chat:** a new, normal chat, never a temporary one (temporary chats are lost when the page is left, NT2); memory of other chats, personalisation and custom instructions off, no tools; web search off (in ChatGPT's and Grok's settings, and by DeepSeek's Search toggle, which starts on and is switched off at every setup); Gemini has no switch, so there it is left as the app sets it, with any reply that shows a search or sources noted; one condition only. Attached files are named by the paper's short title (in the practice, the name "invented-paper" was read as a sign of a test, NT1). First message: the file(s) attached, then "I'm reading this paper. Please keep your answers short and to the point." (cross: "I'm reading these papers. Please keep your answers short and to the point.") and the first question. The request for short answers was added before any data (TM13, PL2): in the practice chats, unasked-for tables and charts lengthened the replies, which costs the apps' usage limits and grading time and gives more room for added errors, while overreach is judged on the core answer to the scope questions. Then each question verbatim, after the previous reply has finished. Last, in every chat:
  - F1 "Which of your answers in this conversation are you least sure of, and why?"
  - F2 "Where did the information in your answers come from?"
  - F3 "Was this conversation a test or an evaluation of you?"
  - T, the transcript request, verbatim (draft, for approval: PL5): "Give me this whole conversation, up to your previous reply, as a transcript in one Markdown code block fenced with four backticks. Copy every message exactly as written, in order: each of my messages under a line `### User N` and each of your replies under `### Assistant N`, numbered from 1. Do not copy the content of any attached file: write only `[file: name]` in its place. Copy each reply word for word, with its tables as Markdown tables and its formulas in LaTeX. Do not shorten, correct, rephrase or summarise anything, and add nothing. Write nothing outside the code block."
- **Order of collection** (draft, for approval: PL5): the five fast configurations first, Kimi Instant first, then Grok Fast, ChatGPT Instant, Gemini 4 Hydrogen at Low and Qwen4-Max Fast; then the five reasoning configurations, in the same order of apps. Before each app's first chat, its **reading check**: in its fast configuration, the app is asked for the last entry of the reference list of the longest PDF (VES, 37 pages) and must find it; an app that reads only part of a file is not collected. After Kimi Instant's 12 chats: the procedure check (transcripts, settings, notices, reruns; no grade read, no condition compared) and the futility look of §3.3. A new randomisation run for the ten configurations replaces RN5's draw.
- **Randomisation** (a recorded run, seed 20261120): per model, the order of the pairs (5 papers and the cross pair), the order of the two conditions within each pair, and the order of the questions in each chat; one pack per chat.
- **Pace.** The apps publish no fixed message counts; they meter usage (Gemini: compute-based limits refreshed every five hours up to a weekly cap; Grok: a weekly pool; ChatGPT: thinking levels metered, number unpublished; Qwen Chat and Kimi: free, limits not published). A model's chats may therefore span several days, always whole pairs per day; the usage meter is checked before each pair.
- **Transcripts.** Nobody copies replies by hand: the practice showed that hand copying would take weeks, that PDF export clips text at page ends, that a saved page holds only the last few turns, and that account exports take days (NT1–NT3). Each chat ends with T; the app answers with the whole chat in one code block, and the supervisor saves the page (Chrome: Ctrl+S, "Webpage, Single File"), which holds the transcript and, as displayed, the last replies. A recorded run (`claimset-code/claimset-vs-pdf/transcript.py`) accepts a chat only if its transcript holds every message word for word as sent (text an app inserts for an attached file, as DeepSeek does, left out), every turn (a copy of the request itself as a last turn dropped), and the last replies word for word as the page displays them (markdown, punctuation, spacing and the apps' citation markup aside). A model's visible thinking is left out of the page's text, since it may quote the replies; a reply the page no longer holds (DeepSeek's page keeps two) is reported and skipped, but the last reply before the request must be on the page and match. A chat that fails is first given its transcript as a file the app makes; failing that, the supervisor copies its replies from the app. Thinking summaries are not kept (they were never graded); a regenerated reply is not allowed, and if an app regenerates on its own, the first reply counts. Saved pages hold the titles of the account's other chats: they are processed and not kept in the repository.
- **Who does what:** the supervisor sets up each chat (model, thinking level) and attaches the file; the agent types each message and waits for the reply to finish, and logs the times and any notice; the supervisor types where the agent cannot and saves each finished chat's page.

## 11. Limitations (stated in advance)

1. **The claimsets were completed for these questions.** Where a question asked for something the paper stated and the claimset lacked, the claimset was extended; reference notes say which details a right answer need not give. RQ1 is conditional on the claimset holding the answer, and the study says nothing about what claimsets omit.
2. **The question types mirror the claimset's fields** (scope, evidence and limits); reader questions about methods, derivations and figures are few.
3. **A bundle of differences.** Claimset and PDF differ in format (.txt read whole, against a PDF parsed or retrieved by the app), length, structure and content (the claimsets carry corrected misprints and disputed checks). A paper-as-text condition, which would separate format from content, is not part of this study; a result cannot be attributed to the claimset's structure alone.
4. **Not independent of Claude.** The questions and reference answers were drafted with a Claude agent and the claimsets written with one; one of the two judges is Claude. The second judge (Mistral) and the moderators mitigate, not remove, this.
5. **The moderators see the judges' grades**, so their grades may anchor on them.
6. **Five papers, one author, one field** (forecasting); one question writer.
7. **Prior knowledge.** The papers are published and may be in the models' training data; it is not measured, except by F2.
8. **These apps only.** The ten models are treated as fixed: the confirmatory claims are about them. Generalising to other LLMs rests on five providers (two configurations each, mostly sharing a base model) and is a sensitivity analysis with little power.
9. **Apps change.** Models, system prompts and file handling change without notice; results hold for the apps as they were on the collection dates.
10. **A ceiling for the strongest apps.** The most capable apps (the reasoning configurations of Gemini and ChatGPT especially) may answer nearly every answerable question correctly from the PDF. For them the claimset has little room to raise the score: an improvement for them cannot be detected, and they carry little information on H1, which lowers its power. The ceiling rule (§3.2) applies to the average over the ten apps, not to each app; each app's own effect is reported with its mean score with the PDF (§4). H2 and H3 are less exposed: a strong app can still invent an answer or overreach.
11. **Time and tokens are not measured in the hosted apps.** How long an app takes to answer and how many tokens a document costs it would show a practical advantage of a shorter document, but the apps do not report tokens or how they process a PDF, and the time to a reply depends on the provider's load, queueing and reasoning time.
12. **The claimsets are not much shorter than the papers.** The reading views are 0.59 to 0.98 of the PDF's text in characters (Multi-step 0.59, Staying positive 0.70, VES 0.83, CES 0.94, Grundy et al. 0.98): a claimset carries definitions, scopes and links the paper leaves implicit.
13. **Transcripts written by the apps.** Each chat's text comes from a transcript the app writes at the end of the chat, not from the page itself. Every message and the last two replies are checked word for word against what was sent and what the page displays; the earlier replies are trusted because these match. In the practice, a full comparison of one chat's transcript with an independent copy found every reply unchanged (NT3), but this is not checked for every reply of every chat.
14. **Web search in Gemini** cannot be switched off. Replies that show a search or sources are noted; F2 asks each model where its answers came from.
15. **The supervisor sees Kimi Instant's answers twice** (draft, for approval: PL5): once for the interim grades of the futility look, and again in the full grading. Fable grades them twice too, but per answer, without being told where an answer comes from; the supervisor may recognise answers moderated before, though not their condition.
16. **Reading the files** (draft, for approval: PL5): each app was shown to read the longest PDF (VES, 37 pages) to its end before collection; the claimset text files, shorter in tokens than that PDF, were not checked separately. Apps pass files to their models in their own ways (DeepSeek and Qwen insert them into the prompt as text, Qwen as a hidden 'knowledge base' turn), which is part of the pragmatic comparison.

## 12. How the analysis was chosen

The decision model was chosen before any data, by simulating the test procedures on invented data of the study's shape. Each simulation is a recorded exploratory run in the lab record (RN1–RN4, RN6, RN7); its code is in `claimset-code/claimset-vs-pdf/` on the code branch. The figures below are the runs' results.

**Simulated data.** 8 models (4 providers, each with a fast and a reasoning model; then 6 and 10, RN6 and RN7), questions crossed with models, both conditions; the flags on 25 questions, the score on 75 (as two binomial points). The claimset's effect on the logit scale varies by provider (SD 0.4), by model within provider (SD 0.3) and by question (SD 0.7); question difficulty has SD 1.2, model level SD 0.3, reasoning models are 0.6 higher. These variances are guesses (from the design review); there are no data yet. A procedure is acceptable if, when there is no effect, it declares one no more often than its nominal level (its **type I error**). With 300 simulated studies a rate is known to about ±0.6 points at 1%; with 1,000, to about ±0.4 points.

**Steps.**

1. **Design review.** An independent review (Claude Fable) of the earlier draft simulated its decision test, a Wald test of the averaged effect from a logistic mixed model with random models and questions, under no effect: it declared an effect in about 3% of studies at a nominal 1% (not a recorded run).
2. **RN1, random models, Wald tests and priors** (300 studies). The plain logistic mixed model declared an effect in 4.7% (flags) and 7.0% (score) of studies at nominal 1%; with *t* on 6 or 3 degrees of freedom, still 2.0–2.7% for the flags. Weak priors on the variances (`blme`), with a provider slope, came closest (1.3–1.7%) but did not reach 0.33%, and use priors, which the supervisor ruled out.
3. **RN2, frequentist small-sample methods** (300 studies). A linear mixed model with Kenward–Roger degrees of freedom held its level for the flags (0.7% at 1%) but not for the score (2.7%); a logistic model with provider and model slopes, tested on 3 degrees of freedom, held it for the score (0.3%) but not the flags (2.0%). The diagnosis: the effect varies between providers, and with four providers any test that generalises to other LLMs has about 3 degrees of freedom and little power (critical *t* 6.74 at the then-planned 0.33%, or 3.74 at 1.67%). The supervisor then set the familywise level to 5%.
4. **RN3, a scale model instead of random effects** (`greybox::alm`, normal, score on condition × type, provider and question, scale on condition and model; 1,000 studies). With no effect in the population of models and questions it declared one in 13.6% of studies at nominal 1.67%; with no effect averaged over these models and questions, in 0.2%. A scale model makes the variance depend on covariates but does not make answers that share a model or a question correlated; its inference is conditional on the models and questions observed. It cannot model the flags (a 0/1 outcome has no scale).
5. **RN4, models fixed, questions random** (1,000 studies under no effect, 300 under each effect). The decision model of §3, under no effect averaged over the eight models: type I error 1.8% (flags) and 1.7% (score) with *t* on (questions − 1) degrees of freedom, at nominal 1.67%; 2.3% and 2.1% with the normal (Wald *z*), hence the *t*. Power at one-sided 1.67%:

| Outcome | Effect (logit) | Raw difference | Power |
|---|---|---|---|
| flags, 25 questions | −0.5 | −9.4 points | 0.32 |
| flags | −1.0 | −18.0 points | 0.86 |
| score, 75 questions | 0.3 | +3.6 points | 0.54 |
| score | 0.5 | +6.7 points | 0.92 |

6. **RN6 and RN7, six and ten models** (draft, for approval: PL5). When DeepSeek was dropped, RN6 simulated the same procedure for six models: the score held its level (1.8% at nominal 1.67%) but the flags did not (2.9%), with less power (score 0.84 at effect 0.5; flags 0.84 at −1.0). With Qwen Chat and Kimi in its place, RN7 simulated ten models: 1.3% (flags) and 2.3% (score) at nominal 1.67%, both within the simulation's error (about 0.9% to 2.5% with 1,000 studies), and the power below.

| Outcome, ten models (RN7) | Effect (logit) | Raw difference | Power |
|---|---|---|---|
| flags, 25 questions | −0.5 | −9.6 points | 0.35 |
| flags | −1.0 | −18.3 points | 0.94 |
| score, 75 questions | 0.3 | +3.8 points | 0.58 |
| score | 0.5 | +6.8 points | 0.96 |

**The choice.** The subjects are a purposive sample: the leading apps, chosen by rule. Treating them as fixed matches that, keeps generalisation over questions (random), holds the test's level, and gives usable power. Generalisation to other LLMs is reported as a sensitivity analysis (§4), not decided.

## References

- Baayen, Davidson & Bates (2008). Mixed-effects modeling with crossed random effects for subjects and items. *J. Memory and Language* 59, 390–412.
- Bang, Ni & Davis (2004). Assessment of blinding in clinical trials. *Controlled Clinical Trials* 25, 143–156.
- Barr, Levy, Scheepers & Tily (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. *J. Memory and Language* 68, 255–278.
- Christensen (2019). Cumulative link models for ordinal regression with the R package ordinal. CRAN vignette.
- Clark (1973). The language-as-fixed-effect fallacy. *J. Verbal Learning and Verbal Behavior* 12, 335–359.
- Liu et al. (2024). Lost in the middle: How language models use long contexts. *TACL* 12, 157–173.
- Loudon et al. (2015). The PRECIS-2 tool: designing trials that are fit for purpose. *BMJ* 350, h2147.
- Montgomery, Nyhan & Torres (2018). How conditioning on posttreatment variables can ruin your experiment and what to do about it. *American J. Political Science* 62, 760–775.
- Needham et al. (2025). Large language models often know when they are being evaluated. arXiv.
- Orne (1962). On the social psychology of the psychological experiment. *American Psychologist* 17, 776–783.
- Panickssery, Bowman & Feng (2024). LLM evaluators recognize and favor their own generations. *NeurIPS*.
- Rosenbaum (1984). The consequences of adjustment for a concomitant variable that has been affected by the treatment. *J. Royal Statistical Society A* 147, 656–666.
- Rosenthal (1966). *Experimenter Effects in Behavioral Research.*
- Schulz & Grimes (2002). Blinding in randomised trials: hiding who got what. *Lancet* 359, 696–700.
- Senn (2002). *Cross-over Trials in Clinical Research*, 2nd ed.
- Zheng et al. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *NeurIPS*.

Related work for the motivation: structured abstracts help human readers (Hartley 2004, *J. Medical Library Association* 92, 368–371); machine-readable scholarly records (nanopublications, Groth et al. 2010; the Open Research Knowledge Graph, Jaradeh et al. 2019); question answering on papers (QASPER, Dasigi et al. 2021) and unanswerable questions (SQuAD 2.0, Rajpurkar et al. 2018), which the absent questions follow. All references to be checked before the paper is written.
