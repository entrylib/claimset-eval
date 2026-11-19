# Working on this repository

The claimsets in `claimset/pilot/` are made by hand, one paper at a time, with the paper's author deciding what each claim is. They follow the Claimset specification in the `claimset` package (`pip install git+https://github.com/entrylib/claimset`).

- Edit claimsets freely; there is no lab record. After every change run `claimset validate` on the file and regenerate its reading view with `claimset render`.
- In a claimset made here against `papers/text/`, every claim, evidence object and limitation has `source_spans` pointing at `[pN.M]` markers of the paper's text. A native claimset taken from EntryLib is kept as published, and spans are optional: the specification asks for them only in converted papers, and the reading study does not use them. It needs them only to serve as the gold for comparing conversions (`tools/compare.py`).
- Ask the author about anything uncertain, one question at a time.
- `tools/` and `tests/` use only the Python standard library. Before committing a change to Python code, run `python3 -m unittest discover -s tests`; a change to claimsets, papers or text alone needs no test run.
- Never put credentials in a file, a command line or a commit.
- The converter is proprietary (private repository `entrylib/claimset-convert`). Never copy its instructions, prompts or code into this repository.
- Papers under non-commercial licences (`NC` in `papers/papers.csv`): nothing derived from them (text, excerpts, claimsets) ever goes into the converter repository, its instructions, tests or examples.
