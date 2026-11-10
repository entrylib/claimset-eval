# Reading study (pilot)

Does a claimset help a model answer questions about a paper: with fewer tokens, as accurately, and with fewer invented answers? The pilot uses the papers of `claimset/pilot/`, whose claimsets were made with their author. It estimates effects; it is not powered to prove them. Its results (effect sizes, how much questions on one paper agree, how often conditions disagree) size the full study.

## Conditions

Each question is put to each model in up to three conditions:

| Condition | The model is given |
|---|---|
| `paper` | the paper's text, `papers/text/<name>.txt` |
| `claimset` | the claimset's reading view, `claimset/pilot/<name>.claimset.txt` |
| `bundle` | only the claims the question names and what they rest on (`claimset render --claim`); only for questions with `claims` |

The instructions are the same in every condition: answer only from the document, say when it does not give the answer, do not state a result more broadly than the document does, and list the paragraph markers or claimset identifiers relied on. Calls are made in a seeded random order, so a change in the API's speed during a run falls on all conditions alike.

## Questions

One file per paper in `study/questions/<name>.json`, and files for questions across papers; see `_template.json` and `_template-cross.json` (files starting with `_` are not read). Each question has:

- `id`, unique in its file;
- `type`:
  - `lookup`: what was found, on which data;
  - `scope`: whether a result holds under other conditions, data or populations (tests overreach);
  - `evidence`: what supports a claim and what limits it;
  - `absent`: something the paper does not say, close enough that a model might guess; the reference answer is that it is not stated;
  - `cross`: a question across the papers of a file with several papers;
- `question`, and `answer`: the reference answer, written from the paper (not required for `absent`);
- `notes` (optional): what a right answer must include;
- `claims` (optional): the claims that answer it, which enables the `bundle` condition;
- `in_claimset` (optional): whether the claimset holds the answer. Mark it after writing the question, so that the questions come from the paper and not from the claimset; the report gives scores for each value separately.

About 20 questions a paper, a quarter of them `absent`, is the plan. Write and commit the questions and reference answers before the first run, and do not change them afterwards: the run records the hash of every input in `manifest.json` and refuses to continue if one changed.

## Running

```
python3 tools/reading_study.py check
python3 tools/reading_study.py run --out study/runs/pilot-1 --model claude-opus-5-5 --model claude-sonnet-5-5 --dry-run
python3 tools/reading_study.py run --out study/runs/pilot-1 --model claude-opus-5-5 --model claude-sonnet-5-5 --max-calls 10
python3 tools/reading_study.py run --out study/runs/pilot-1 --model claude-opus-5-5 --model claude-sonnet-5-5
python3 tools/reading_study.py grade --out study/runs/pilot-1
python3 tools/reading_study.py grade --out study/runs/pilot-1 --sheet study/runs/pilot-1/sheet.csv
python3 tools/reading_study.py grade --out study/runs/pilot-1 --import study/runs/pilot-1/sheet.csv
python3 tools/reading_study.py report --out study/runs/pilot-1
```

- `check` validates the question files, that every paper has its text, claimset and an up-to-date reading view, and that named claims exist.
- `run` needs `ANTHROPIC_API_KEY` in the environment, or with `--provider` the key of another provider: `openai`, `deepseek`, `minimax`, `mistral`, `qwen`, `moonshot`, `zai`, `xai`, `openrouter` (each `<PROVIDER>_API_KEY`, `DASHSCOPE_API_KEY` for qwen), or `local` for a server at `OPENAI_BASE_URL`; `grade` takes `--provider` too, for the judge. Providers without a JSON-schema mode are given the schema in the instructions, and a reply that does not follow it is a failed call. `--dry-run` prints the number of calls and an estimate of the input tokens; `--max-calls` makes a short trial. A run can be stopped and started again with the same command: it continues where it stopped and retries failed calls. Defaults: 3 repetitions, effort `medium`, all three conditions. A refused request is recorded as a failed call, not passed to another model, so that every answer comes from the model named.
- `grade` has a judge model compare each answer with the reference answer. The judge sees the question, the reference answer, the notes and the answer with paragraph markers and claimset identifiers removed, so it cannot tell the condition. An answer that says the document does not give it is graded `not_stated` without the judge. `--sheet` writes a blinded CSV in random order for checking the judge; fill `human_grade` and `human_overreach` where you disagree and read it back with `--import`. Human grades replace the judge's.
- `report` writes `report.md` and `report.json` to the run directory.

## What is recorded and reported

`answers.jsonl` holds one line per call: the condition, model, repetition, the hash and length of the document given, the API's token counts, the time the call took, the answer, whether the model said the document does not give it, and its cites. `grades.jsonl` holds the grades, and how many of each answer's cites exist in the document it was given.

The report gives, for each model and condition:

- **correct** and **score** (correct 1, partial 0.5) on answerable questions;
- **not stated (answerable)**: how often the model said the answer is not there when the paper gives it; in the claimset condition this is mostly what the claimset leaves out;
- **answered absent**: how often it gave an answer to an `absent` question (invented answers);
- **overreach (scope)**: answers to `scope` questions that state a result more broadly than the reference allows;
- **input and output tokens**, and the **median time** per answer;
- **cites valid**: the share of cited markers or identifiers that exist in the document.

And, per question, the difference between the claimset (or bundle) and the paper in score, with a 95% interval that resamples papers, and the ratio of input tokens; also the score by question type and by `in_claimset`.

## Cost

`--dry-run` gives the input tokens. Five papers of about 20,000 tokens, 20 questions each, three conditions, two models and three repetitions are about 1,700 calls and 20 million input tokens, half for each model: about $40 for Claude Opus 5.5 ($4 per million input tokens) and $20 for Claude Sonnet 5.5 ($2). Grading adds one short call per answer.
