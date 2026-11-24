# Claimset or paper text, read by local models: precision, invented answers, time and tokens

**Study:** `claimset-vs-pdf-local-llm` (no lab record yet; its branch `claimset/claimset-vs-pdf-local-llm` is made when the plan is drafted).
**Status:** parked. A short plan, to be completed after the claimset-vs-pdf study (decision DC9 of that study moved the local models here). Nothing is run before this plan is agreed and recorded, apart from the practice run (`practice-prompt.md`).

## Why a separate study

- **It compares different things.** In claimset-vs-pdf, "PDF" is the file as each hosted app handles it. A local model cannot open a file, so here the PDF is its text as `pdftotext` extracts it. The comparison is claimset text against paper text, with no app in between: it separates the document from the app's handling of a PDF, which claimset-vs-pdf does not (its DC3).
- **It can test time and tokens.** The models run on one machine through a script, so every count and time is measured, and the study is repeatable from its seed.
- **It is cheap to extend.** A model is 200 scripted calls, run unattended.

The two studies share the questions, the reference answers and marking guides, the claimsets' reading views and the grading (the answers of both may be graded in one blind pass, mixed together); each plan says so, and each paper cites the other.

## Research question

For open-weight models run locally, does a paper's claimset, compared with its PDF's text, lead to better answers, fewer invented answers and less time per answer, and how many input and output tokens does each take?

## Materials

- **Questions:** the 100 per-paper questions of claimset-vs-pdf (`study/questions/`, 75 answerable, 25 absent), fixed by the hashes in `study/claimset-vs-pdf-plan.md`. No cross questions (five documents do not fit a local model's context).
- **Claimset condition:** the reading views `claimset/pilot/<name>.claimset.txt` (`claimset render --published` of the versions published on 2026-11-24), as in claimset-vs-pdf.
- **Paper condition:** the PDF's text, `papers/pdftotext/<name>.txt`: `pdftotext -enc UTF-8`, poppler 24.02.0, default reading-order mode, unedited, from the PDFs claimset-vs-pdf attaches (for VES the accepted manuscript; Grundy et al. without its supplement).

| Paper | `papers/pdftotext/` | SHA-256 |
|---|---|---|
| CES | `doi-10-1002-nav-22074.txt` | `a6898845ad474ab249eb89524d3763388967bbda2acd628cf7e51a72a9ca901b` |
| Multi-step estimators | `doi-10-1007-s00180-023-01377-x.txt` | `a7f4b89c96721fb78d94cc66ac7bd49deb181b3598a5b3adbbc0ce13497f97cd` |
| VES | `doi-10-1016-j-ejor-2022-04-040.txt` | `b195141023d44c6817a4b21db02d07dc01f283fc7d8f1020f1c54e41287fa91f` |
| Staying positive | `doi-10-1093-imaman-dpad028.txt` | `4760060203a253d7eb98b0874f292dc796e69be8a010e4c639b399bfb13a4db0` |
| Grundy et al. | `doi-10-1111-jtsa-12843.txt` | `2fc45d676b41360e4b2598fc31f41f679c7948fb9912f636c00ac4322e35d3e1` |

In characters, the reading views are 0.59 to 0.98 of these texts (Multi-step 0.59, Staying positive 0.70, VES 0.83, CES 0.94, Grundy et al. 0.98).

## Subjects

Open-weight models run through Ollama (no front end) on the supervisor's PC (NVIDIA RTX 5070 Ti, 16 GB): from each of Qwen (Alibaba), gpt-oss (OpenAI) and Gemma 4 (Google), the newest model of about the planned size (Qwen 8–14B, gpt-oss 20b, Gemma 4 ~12B) that runs entirely on the GPU with a context holding the longest document, a question and its answer. Each is fixed by its Ollama tag and digest in the practice run. Thinking off where a model allows it, the lowest effort where it does not (gpt-oss). No Mistral model (Mistral is a judge); Claude has no local model. More models may be added before the plan is recorded, by the same rule. The models are fixed effects: the claims are about them.

## Protocol

By the script `claimset-code/claimset-vs-pdf/local_models.py` (tested against a fake Ollama server, `tests/test_local_models.py`):

- One question per chat: one message holding the document, a blank line, "I'm reading this paper." and the question; no system prompt, no follow-up.
- The model's default sampling settings, seed 20261120, at most 4,096 generated tokens, one context length for all calls (set in the practice run).
- The model is unloaded after every call (`keep_alive` 0), so that no cached prompt shortens the next call's reading. One question per chat measures the worst case: in ordinary use a document is read once per chat and later questions reuse it.
- All calls (200 per model) in one random order (seed 20261120); a failed call is tried once more.
- Recorded per call: the answer (and any thinking text), Ollama's `prompt_eval_count` (input tokens), `prompt_eval_duration` (reading time), `eval_count` (output tokens, thinking included), `eval_duration` (generation time), `load_duration`, `done_reason`, each model's digest and Ollama's version. A call whose prompt and answer fill the context is marked **cut**: Ollama drops the start of a prompt longer than the context without an error.
- **Practice run** first, not data (`practice-prompt.md`): fixes the models, digests and context length; checks that every document fits; checks with an invented document that a repeated call reads the whole prompt again.

Grading as in claimset-vs-pdf (§9 of its plan): two judges in turn, Claude Fable then Mistral, a disagreement report, two moderators, a consistency check, locking.

## Hypotheses (draft)

| | Hypothesis | Outcome | Questions |
|---|---|---|---|
| **H1** | The local models score higher with the claimset than with the paper's text | score (1, ½, 0) | 75 answerable |
| **H2** | The local models give invented answers less often with the claimset | invented (0/1) | 25 absent |
| **H3** | The local models take less time per answer with the claimset | total time per answer: reading plus generation (log seconds) | all 100 |

**Decision model,** as in claimset-vs-pdf: models fixed, questions random. H1 and H2: `glmer(cbind(y, n - y) ~ x * model + paper + (1 + x | question), family = binomial)`; H3: `lmer(log(time) ~ x * model + paper + (1 + x | question))`. The averaged effect Δ over the models, tested one-sided against *t* on (questions − 1) degrees of freedom, familywise 5% over the three hypotheses (Bonferroni, 0.0167 each). Before recording: simulate the procedures' level and power for three models, as RN4 did for claimset-vs-pdf.

## Estimates (no test)

- **Input tokens** (`prompt_eval_count`): per model and paper, the median over the 20 questions, and the ratio claimset to paper text. A document's input tokens are fixed for a model (the questions change them only by their own length), so the 20 calls do not replicate anything: the units are the five papers, too few for a useful test.
- **Output tokens** (`eval_count`, thinking included: Ollama does not count a thinking text's tokens apart, so its length in characters is reported beside them): per model and condition, the median and the paired difference by question, with a 95% interval. Output tokens vary by question and can be tested; they are estimated here, and tested only through H3's time.
- **Reading time and generation time** separately, per model and condition.
- **Overreach** on the 25 scope questions, per model and condition.

**Why input and output apart.** They measure different things and cost differently. Input tokens are the document (and the question): what reading costs, fixed by the document. Output tokens are the answer (and any thinking): how much the model writes, which the document may change (a structured record may give shorter or longer answers). A model reads input in parallel, at thousands of tokens a second, and writes output one token at a time, at tens a second; hosted providers price output at several times input. So a claimset can save input tokens and still cost time if it makes answers longer, or the reverse; H3 tests the total, and the split shows where it comes from.

## Limitations (so far)

1. **The paper is given as extracted text.** `pdftotext` loses table layout and turns formulas into strings of characters; an app may read the same PDF better or worse. The results do not stand for what an app does with a PDF.
2. **The claimsets are not much shorter** than the papers' text (0.59 to 0.98 in characters), so time and input tokens may differ little for CES and Grundy et al.
3. **One machine, small models.** Times hold for this GPU; the models are smaller than the hosted ones.
4. **One question per chat** is the worst case for reading cost.
5. As in claimset-vs-pdf: the claimsets were completed for these questions; five papers, one author, one field; the questions and claimsets were written with a Claude agent and one judge is Claude.

## To do before recording

- Practice run (`practice-prompt.md`): models, digests, context length, sizes, prompt cache.
- Simulations of the decision procedures for three (or more) models; the time model's variances from the practice run.
- Whether to add models.
- The lab record: question, terms, hypotheses, plan with the script's commit and the files' hashes, approved with the supervisor's words.
