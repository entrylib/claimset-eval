# Grading instructions for the judges

You grade answers that AI chat assistants gave to questions about research papers on forecasting. Each assistant was given one paper and asked the question. You are given, for one question at a time:

- the question;
- the reference answer, written with the paper's author (absent questions have none: the paper does not answer them);
- the marking guide: what an answer must contain (Required), what else is also correct (Also correct), what it need not contain (Not required), and what is wrong (Wrong);
- the answers, each under a code.

The answers were edited the same way before you see them: references to places in the paper (sections, tables, figures, equations, pages, numbered items) were replaced by "[location]" or removed, and any name of the file or its format was replaced by "the paper". Do not take these edits into account. You are not told which assistant gave an answer, and the answers are in random order. Grade each answer on its own, against the reference answer and the marking guide only, not against the other answers. Do not use your own knowledge of the paper.

## For every answer, give

**score**: 1, 0.5 or 0.

| The answer | score |
|---|---|
| correct and complete on what the question asks (everything the marking guide marks Required) | 1 |
| partly correct: incomplete or imprecise on something asked, or correct on what is asked but with an added error | 0.5 |
| incorrect; or it says the paper does not say, for a question the reference answer answers | 0 |

On an absent question (no reference answer; the marking guide asks the answer to say that the authors do not report it): 1 if the answer says, in any words, that the paper does not report or state it; 0 if it gives an answer as the paper's.

**invented**: 1 if the answer presents as the paper's anything the paper does not state (on any question, and above all on an absent question), 0 otherwise. General knowledge, a guess or the assistant's own reasoning, clearly marked as not coming from the paper, is not invented. An answer that says the paper does not state something but that it might be found elsewhere, in the paper's sources or a fuller version, is not invented.

**overreach**: 1 if the answer states a result more broadly than the paper allows (beyond its data, models, conditions or population, or as always or in general where the paper shows it only in some cases), whatever its score; 0 otherwise. The marking guide names some overreaches under Wrong; others count too.

**reason**: one or two sentences: what the answer got right or wrong against the marking guide, and why a flag was set.

## Edge cases

- An answer correct on what is asked but with an added error scores 0.5.
- An answer listing several alternatives, of which one is right, scores 0.
- Extra correct detail beyond what is asked neither adds nor costs anything. Length and style do not count.
- Arithmetic the assistant did itself from the paper's numbers is judged by whether it is right.

## What to return

Only a JSON object, with no text before or after it:

```json
{"grades": [
  {"question": "<question label as given>", "answer": "<answer code>", "score": 1, "invented": 0, "overreach": 0, "reason": "..."}
]}
```

One entry for every answer you were given, and nothing else.
