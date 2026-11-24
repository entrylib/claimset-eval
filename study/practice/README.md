# Practice chats (claimset-vs-pdf)

The practice chats of the claimset-vs-pdf plan (§10): one round per app, with made-up questions about invented documents, before any data. They check the settings, memory, file limits, pasting, copying and usage meters, and their answers are used to fix the masking rules (§9). They are not data.

## Files

- `invented-paper.pdf`: an invented working paper (harbour-weighted exponential smoothing on a fictional ferry operator's data), 3 pages with two tables, display equations and a figure. Made from `src/invented-paper.md` (pandoc to HTML with MathML, printed to PDF by Chromium), so its text extracts like a journal PDF's.
- `invented-paper.claimset.txt`: its claimset's reading view, `claimset render` of `src/invented-paper.claimset.json` (valid under v0.44).
- `note-a.pdf` … `note-d.pdf` and `note-a.txt` … `note-d.txt`: four one-page invented notes, to fill a cross chat to five files.
- `practice-questions.json`: 8 per-paper questions (2 of each type), 2 cross questions, F1–F3 and the memory check.
- `gemini.md`: the Gemini practice, step by step.

Everything here is invented: the operator, routes, data, results and authors. Only the cited textbooks and articles are real.
