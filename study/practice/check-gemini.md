# Check before collection: Gemini

Three short chats in Gemini's fast configuration (Everyday help (Gemini 4 Hydrogen), thinking level Low), typed by an agent (Claude chat with access to the browser). Not data. They check what the practice chats could not: that Gemini reads the study's longest files to the end (R1: the 37-page VES PDF; R2: the 20,000-token VES claimset), that it takes five files at once (X1), and that the transcript request leaves the attached files out (DeepSeek and Qwen copied them in; lab decision DC12). Files: R1 and R2 from `study/attachments/`, X1 from `study/practice/`. Save each page as `gemini-R1.mhtml`, `gemini-R2.mhtml`, `gemini-X1.mhtml`, and send them with the agent's log.

Expected answers, for checking only: R1, Withycombe (1989), "Forecasting with combined seasonal indices", International Journal of Forecasting 5, 547–552; R2, B23, the DOI 10.32614/CRAN.package.forecast (the R `forecast` package).

````text
You will type messages into Gemini (gemini.google.com) in my browser, for a short check of a reading study: three chats. It is not data, but follow the procedure exactly.

RULES
- Type each message exactly as written below, on one line, and send it. Never type anything else into Gemini.
- Send the next message only when the previous reply has finished, told from the page's visible elements: the visible stop control has gone and the reply's own buttons have appeared. Watch only visible controls; pages can hold hidden copies of the input box.
- Do not read, quote, summarise or judge the replies. Log any error, limit or warning message, in particular one saying that only part of a file was read, with its exact text; if one appears, tell me and wait.
- Never regenerate, edit or rate a reply, or click suggestions, sources or chips. Do not change settings, attach files or open chats yourself: ask me and wait for "ready".
- Before each chat's first message, check that web search is off; if it is on, tell me and wait.

For each chat: tell me what to set up (a new normal chat, never a temporary one; Everyday help (Gemini 4 Hydrogen), thinking level Low; the file(s) to attach) and wait for "ready". Check that the file(s) are attached in the tab you are driving, then send the messages. When the reply to T has finished, tell me: "Chat <id> is done. Save the page as gemini-<id>.mhtml", and wait for "next".

CHAT R1: attach vector-exponential-smoothing.pdf.
1: I'm reading this paper. Please keep your answers short and to the point. What is the last entry in its reference list?
T: Give me this whole conversation, up to your previous reply, as a transcript in one Markdown code block fenced with four backticks. Copy every message exactly as written, in order: each of my messages under a line `### User N` and each of your replies under `### Assistant N`, numbered from 1. Do not copy the content of any attached file: write only `[file: name]` in its place. Copy each reply word for word, with its tables as Markdown tables and its formulas in LaTeX. Do not shorten, correct, rephrase or summarise anything, and add nothing. Write nothing outside the code block.

CHAT R2: attach vector-exponential-smoothing.claimset.txt. The same two messages as R1 (1, then T).

CHAT X1: attach the five PDFs harbour-weighted-smoothing.pdf, croston-spare-parts.pdf, bakery-sales-weather.pdf, call-centre-reconciliation.pdf, hotel-occupancy-damped-trend.pdf.
1: I'm reading these papers. Please keep your answers short and to the point. Which of these papers use weekly data, and which use monthly data?
T: the same transcript message as in R1.

At the end, show me a log: for each chat, the setting the picker showed, the times of each message and reply, and any error, limit or warning message (its text). Nothing from the replies themselves.
````
