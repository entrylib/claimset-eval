# File-reading check, before each app's collection

DeepSeek's free chat reads only the first 20 pages or 10,000 tokens of an attachment, and was dropped for it (lab decision on DeepSeek). Before an app's first study chat, this check shows whether it reads the study's longest files to the end. It is a practice run: no study question is asked, and it is not data.

For each app, in its **fast** configuration (Grok: Fast; ChatGPT: Instant; Gemini: Everyday help, Hydrogen, Low), two new normal chats, typed by the agent with the prompt below:

- **R1:** attach `vector-exponential-smoothing.pdf` (37 pages).
- **R2:** attach `vector-exponential-smoothing.claimset.txt` (about 80,000 characters, 20,000 tokens).

Each chat asks for the last entry of the reference list, which ends both files, and then for the transcript. Save each page as `<app>-R1.mhtml` and `<app>-R2.mhtml`.

**Expected answers** (for the person checking, not for the agent): R1, the PDF: Withycombe (1989), "Forecasting with combined seasonal indices", *International Journal of Forecasting* 5, 547–552. R2, the claimset: B23, the DOI 10.32614/CRAN.package.forecast (the R `forecast` package). An app passes if both answers name these, and both transcripts pass `transcript.py`. If it fails, or warns that it read only part of a file, the app is not collected until a decision is recorded.

````text
You will type messages into <APP> (<URL>) in my browser, for a short check of a reading study. It is not data, but follow the procedure exactly.

RULES
- Type each message exactly as written below, on one line, and send it. Never type anything else.
- Send the next message only when the previous reply has finished, told from the page's visible elements (the visible stop control gone, the reply's own buttons shown). Watch only visible controls.
- Do not read, quote, summarise or judge the replies. Log any error, limit or warning message, in particular one saying that only part of a file was read, with its text.
- Never regenerate, edit, rate, or click suggestions or sources. Do not change settings, attach files or open chats yourself: ask me and wait for "ready".

For each chat: tell me what to set up (a new normal chat, the FAST configuration, the file), wait for "ready", check that the file is attached in the tab you are driving, then send the messages. When the reply to T has finished, tell me: "Chat <id> is done. Save the page as <app>-<id>.mhtml", and wait for "next".

CHAT R1: new normal chat, FAST configuration; attach vector-exponential-smoothing.pdf.
1: I'm reading this paper. Please keep your answers short and to the point. What is the last entry in its reference list?
T: Give me this whole conversation, up to your previous reply, as a transcript in one Markdown code block fenced with four backticks. Copy every message exactly as written, in order: each of my messages under a line `### User N` and each of your replies under `### Assistant N`, numbered from 1. Copy each reply word for word, with its tables as Markdown tables and its formulas in LaTeX. Do not shorten, correct, rephrase or summarise anything, and add nothing. Write a reference to an attached file as `[file: name]`. Write nothing outside the code block.

CHAT R2: new normal chat, FAST configuration; attach vector-exponential-smoothing.claimset.txt. The same two messages (1, then T).

At the end, show me a log: for each chat, the setting the picker showed, the times of each message and reply, and any error, limit or warning message (its text). Nothing from the replies themselves.
````

Replace `<APP>` and `<URL>` before pasting: Grok (grok.com), ChatGPT (chatgpt.com), Gemini (gemini.google.com).
