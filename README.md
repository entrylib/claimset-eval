# claimset-eval

Hand-made claimsets of five forecasting papers, made with the paper's author, as reference conversions for developing and testing the Claimset converter.

- `papers/pilot/`: the papers (PDF); `papers/papers.csv` lists them with their licences.
- `papers/text/`: the papers' extracted text. Its `[pN.M]` markers (page N, paragraph M) are what the claimsets' `source_spans` point to.
- `claimset/pilot/`: one claimset per paper (`<name>.claimset.json`) and its reading view (`<name>.claimset.txt`, made by `claimset render`). `<name>` is made from the paper's DOI (claimset spec v0.34 §2.4) and is the same as its text's in `papers/text/`: `doi-10-1002-nav-22074` for 10.1002/nav.22074.
- `claimset/trials/`: field trials of specification 0.38: seven papers from other fields (physics, ecology, a clinical trial, a preregistered experiment, cell biology, chemistry, history) converted without their authors, each with a log of what the core could not hold. See `claimset/trials/README.md`.
- `tools/compare.py`: compares a candidate claimset (a converter's output) with the hand-made one of the same paper, without any model: claims (one-to-one, and many-to-one to show bundled claims), the links between them, definitions, evidence with its tables and setup, limitations, references and relations. `python3 tools/compare.py claimset/pilot/X.claimset.json candidate.json --text papers/text/X.txt [--json report.json]`.
