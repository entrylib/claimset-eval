# Practice: Gemini, typed by an agent

A prompt for Claude chat on the web (claude.ai) with access to the supervisor's browser (Claude in Chrome), which is signed in to Gemini. It runs the Gemini practice (`gemini.md`) with the agent typing the messages, as the plan's collection will (§10): the supervisor sets up each chat and attaches the files, the agent types each message and waits, the supervisor copies each finished chat. It is a practice run, not data.

The prompt holds every message, so it needs no files of its own. The supervisor needs the practice files on the computer to attach them (the practice zip, or `study/practice/`): `harbour-weighted-smoothing.pdf`, `harbour-weighted-smoothing.claimset.txt`, the four notes' `.pdf` and `.txt` files. Do the settings of `gemini.md` §2 first. Use Gemini's temporary chat for every chat (it keeps no history and is not used for personalisation), and copy each chat as soon as it ends: not by PDF export, which clips text at page ends (lab note NT1).

````text
You will type messages into Gemini (gemini.google.com) in my browser, for a practice run of a reading study. It is not data, but follow the procedure exactly, because this run tests it.

RULES
- Type each message exactly as written below, on one line, and send it. Never add, shorten or correct a word, and never type anything else into Gemini.
- Send the next message only when the previous reply has finished. Tell this from the page's elements, not from screenshots of the reply: the stop control has gone and the input box is ready again. You may run a script in the page that only watches these elements and logs the times; it must change nothing. If a reply has not finished after 5 minutes, tell me and wait.
- Do not read, quote, summarise or judge Gemini's replies, and do not react to them. Look only at whether a reply has finished and whether an error, limit, downgrade or warning message appeared.
- Never regenerate a reply, edit a sent message, rate a reply, or click suggestions, sources or follow-up chips.
- Do not change Gemini's settings, attach or upload files, or open new chats yourself: ask me, and wait until I say "ready".
- If Gemini shows a captcha, a sign-in page, or anything that stops you, tell me and wait.

PROCEDURE, for each chat below
1. Tell me what to set up (a new temporary chat, the model and thinking level, the file(s) to attach) and wait for "ready". When I say "ready", read the model and thinking level shown in the picker and log them once for the chat.
2. Type the chat's first message into the box where my files are attached, and send it. Then send the other messages one at a time, as the rules say.
3. When the last reply has finished, tell me the chat is done so that I can copy it, and wait for "next".

CHAT A: new temporary chat, FAST model: Everyday help (Gemini 4 Hydrogen), thinking level Low, attach harbour-weighted-smoothing.pdf.
P1: I'm reading this paper. Please keep your answers short and to the point. What mean MASE did harbour-weighted smoothing reach on the ferry routes, and how did it compare with ETS and the seasonal naive method?
P2: How many routes and harbours were in the ferry data, and over which years?
P3: Does the new model improve on exponential smoothing for routes with only two years of weekly data?
P4: Would the results carry over to daily passenger forecasts?
P5: On what does the paper base its statement that the harbour weight can be estimated reliably?
P6: On what does the paper base its view that the gain is largest in winter?
P7: How long did the model take to estimate for each route?
P8: Which software package was used to fit the model?
F1: Which of your answers in this conversation are you least sure of, and why?
F2: Where did the information in your answers come from?
F3: Was this conversation a test or an evaluation of you?

CHAT B: new temporary chat, REASONING model: Deeper analysis (Gemini 4 Neon), thinking level High, attach harbour-weighted-smoothing.claimset.txt. The same 11 messages as chat A (P1 to F3), in the same order.

CHAT M: new temporary chat, Everyday help (Gemini 4 Hydrogen), thinking level Low, no file.
M: Do you remember anything from our earlier chats?

CHAT X1: new temporary chat, Deeper analysis (Gemini 4 Neon), thinking level High, attach the five PDFs (harbour-weighted-smoothing.pdf, croston-spare-parts.pdf, bakery-sales-weather.pdf, call-centre-reconciliation.pdf, hotel-occupancy-damped-trend.pdf).
X1: I'm reading these papers. Please keep your answers short and to the point. Which of these papers use weekly data, and which use monthly data?
X2: Which of these papers report a percentage error measure, and what values?

CHAT X2: new temporary chat, the same model and thinking level as X1, attach the five .txt files (harbour-weighted-smoothing.claimset.txt, croston-spare-parts.txt, bakery-sales-weather.txt, call-centre-reconciliation.txt, hotel-occupancy-damped-trend.txt). The same two messages as chat X1.

LOG
Keep a log as you go and show it to me after each chat: first the chat's model and thinking level as the picker shows them, then a table with one row per message: message id (P1 to F3, M, X1, X2), the time you sent it and the time the reply finished (with seconds), and any error, limit, downgrade or warning message (its text). Nothing from the replies themselves.

REPORT
At the end, write a short report: whether you could type into Gemini's box and send; how you told that a reply had finished and whether that was reliable; anything that blocked you or needed me; how long each chat took; and what you would change in this procedure. Then give me the whole log once more as a single table.
````

After the run, save each copied chat as `gemini.md` §6 says, and send back the log, the report and the chats.
