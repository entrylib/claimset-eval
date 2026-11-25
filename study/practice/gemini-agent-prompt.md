# Practice: Gemini, typed by an agent

A prompt for Claude Code on the supervisor's computer, with the Claude in Chrome extension connected to the supervisor's Chrome, signed in to Gemini. It runs the Gemini practice (`gemini.md`) with the agent typing the messages, as the plan's collection will (§10): the supervisor sets up each chat and attaches the files, the agent types each message and waits, the supervisor copies each finished chat. It is a practice run, not data.

Before starting: have this folder (`study/practice/` of a clone of `entrylib/claimset-eval`, or the practice zip) on the computer, Chrome open on gemini.google.com and signed in, and the settings of `gemini.md` §2 done or ready to do together.

````text
You will type messages into Gemini in my Chrome (Claude in Chrome) for a practice run of a reading study. It is not data, but follow the procedure exactly, because this run tests it.

Files: the study's practice folder is <PATH TO study/practice>. Read gemini.md and practice-questions.json there first. The messages to type are in gemini.md §3–§5, verbatim.

Rules
- Type each message exactly as written, on one line, and send it. Never add, shorten or correct a word, and never type anything else into Gemini.
- Send the next message only when the previous reply has finished: the stop or "generating" control has gone and the input box is ready again. If a reply has not finished after 10 minutes, tell me and wait.
- Do not read, quote, summarise or judge Gemini's replies, and do not react to them. Look at the page only to see whether a reply has finished, which model label is shown, and whether an error, limit or warning message appeared.
- Never regenerate a reply, edit a sent message, rate a reply, or click suggestions, sources or follow-up chips.
- Do not change Gemini's settings, attach or upload files, or open new chats yourself: ask me, and wait until I say "ready".
- If Gemini shows a captcha, a sign-in page, or anything that stops you, tell me and wait.

For each chat (A, B, the memory check, cross PDF, cross .txt in gemini.md):
1. Tell me what to set up: a new chat, which model (fast or reasoning, as gemini.md says), which file(s) to attach. Wait for "ready".
2. Type the first message (with the files I attached) and send it; then the rest, one at a time, as above.
3. When the last reply has finished, tell me the chat is done so that I can copy it. Wait for "next".

Log, as you go, in ~/claimset-practice/gemini-agent-log.csv, one row per message: chat, message id (P1–P8, F1–F3, X1, X2, M), the time you sent it and the time the reply finished (ISO, with seconds), the model label shown on the reply if any, and any error, limit or warning message (its text). Nothing from the replies themselves.

At the end, write ~/claimset-practice/gemini-agent-report.md: whether you could type into Gemini's box and send, how you told that a reply had finished and whether that was reliable, anything that blocked you or needed me, how long each chat took, and what you would change in this procedure. Then show me the report.
````

After the run, save the copied chats as `gemini.md` §6 says, and send back the log, the report and the chats.
