# Practice chats (claimset-vs-pdf)

The practice chats of the claimset-vs-pdf plan (§10): one round per app, with made-up questions about invented documents, before any data. They check the settings, memory, file limits, pasting, copying and usage meters, and their answers are used to fix the masking rules (§9). They are not data.

## Files

- `harbour-weighted-smoothing.pdf`: an invented working paper (harbour-weighted exponential smoothing on a fictional ferry operator's data), 3 pages with two tables, display equations and a figure. Made from `src/invented-paper.md` (pandoc to HTML with MathML, printed to PDF by Chromium), so its text extracts like a journal PDF's.
- `harbour-weighted-smoothing.claimset.txt`: its claimset's reading view, `claimset render` of `src/invented-paper.claimset.json` (valid under v0.44).
- `croston-spare-parts`, `bakery-sales-weather`, `call-centre-reconciliation`, `hotel-occupancy-damped-trend` (each `.pdf` and `.txt`): four one-page invented notes, to fill a cross chat to five files.

The files have plain names, as the study's attachments will: in the first Gemini practice the name `invented-paper` was taken by the model as a sign of a test (lab note NT1).
- `practice-questions.json`: 8 per-paper questions (2 of each type), 2 cross questions, F1–F3 and the memory check.
- `gemini.md`: the Gemini practice, step by step.
- `gemini-agent-prompt.md`: the same practice with an agent (Claude chat on the web with access to the supervisor's browser) typing the messages, as in collection.
- `chatgpt.md` and `chatgpt-agent-prompt.md`, `grok.md` and `grok-agent-prompt.md`, `deepseek.md` and `deepseek-agent-prompt.md`, `qwen.md` and `qwen-agent-prompt.md`, `kimi.md` and `kimi-agent-prompt.md`: the same for the other apps (Qwen's and Kimi's start with the file-reading check).
- `file-reading-check.md`: whether an app reads the study's longest files to the end.

Everything here is invented: the operator, routes, data, results and authors. Only the cited textbooks and articles are real.
- `check-<app>.md` (grok, chatgpt, gemini, qwen, kimi): the short check before each app's collection, three chats: the longest files read to the end, five files at once, and the transcript leaving attached files out.
