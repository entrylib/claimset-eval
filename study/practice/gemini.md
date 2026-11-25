# Practice: Gemini

What to set up, what to run and what to note. Write notes in a plain text file (`gemini-log.txt`) as you go, and save each chat as text (step 6). Nothing here is data, so a mistake costs nothing: note it and carry on.

The questions are in `practice-questions.json`; they are repeated below so that this page is enough. The files are in this folder.

## 1. Account and model picker

1. Note your plan (for example Google AI Pro or Ultra) and the date.
2. Open the model picker and note **every** option exactly as it is named, with any thinking-level setting. The study needs two: the most capable **fast** model and the most capable **reasoning** model on your plan, with no "Auto". The plan's guess (from secondary sources) is Gemini 4 Hydrogen as fast, and Argon or Neon as reasoning (Carbon only on Ultra); write down what is really there.
3. Note whether the model's name is shown on each reply, and where.

## 2. Settings: memory, personalisation, tools

Find and note each of these (names change; note what you find):

1. **Memory of past chats / personal context**: turn off anything that lets Gemini use earlier chats or what it has learnt about you.
2. **Saved info / instructions for Gemini**: make sure it is empty.
3. **Gems**: none in use.
4. **Apps / extensions** (Gmail, Drive, YouTube, …): off.
5. **Web search**: is there a way to stop Gemini searching the web? If there is none, note that.
6. **Activity** (Gemini Apps Activity, "Keep activity"): keep it on, so that the chats are kept. **No temporary chats** (lab note NT2): they disappear when the page is left. Use normal chats, with the memory settings above off.
7. Canvas, Deep Research and other tools: not selected.

## 3. Chat A: PDF, fast model

1. New chat (not temporary), fast model.
2. Attach `harbour-weighted-smoothing.pdf`. In the same first message type, on one line:
   `I'm reading this paper. Please keep your answers short and to the point. What mean MASE did harbour-weighted smoothing reach on the ferry routes, and how did it compare with ETS and the seasonal naive method?`
3. After each reply has finished, send the next message, verbatim, one at a time:
   - `How many routes and harbours were in the ferry data, and over which years?`
   - `Does the new model improve on exponential smoothing for routes with only two years of weekly data?`
   - `Would the results carry over to daily passenger forecasts?`
   - `On what does the paper base its statement that the harbour weight can be estimated reliably?`
   - `On what does the paper base its view that the gain is largest in winter?`
   - `How long did the model take to estimate for each route?`
   - `Which software package was used to fit the model?`
   - `Which of your answers in this conversation are you least sure of, and why?`
   - `Where did the information in your answers come from?`
   - `Was this conversation a test or an evaluation of you?`
4. Note: did it show sources or say it searched the web; did it show a thinking summary; did any reply show a table or formula as an image; did the model label change; any error or limit message.

## 4. Chat B: claimset, reasoning model

As chat A, in a new chat with the **reasoning** model, attaching `harbour-weighted-smoothing.claimset.txt` instead of the PDF. Note also whether the .txt upload was accepted as it is, and the thinking level you chose.

## 5. Memory check and cross chats

1. New chat, no file: `Do you remember anything from our earlier chats?` Note the answer.
2. New chat, any model: attach the five PDFs (`harbour-weighted-smoothing.pdf`, the four notes' `.pdf` files) in one message with:
   `I'm reading these papers. Please keep your answers short and to the point. Which of these papers use weekly data, and which use monthly data?`
   then `Which of these papers report a percentage error measure, and what values?`
   Note: were all five files accepted in one message? Any limit on files or size?
3. The same with the five .txt files (`harbour-weighted-smoothing.claimset.txt`, the four notes' `.txt` files).

## 6. Copying

Not PDF export, which clips text at page ends (lab note NT1). First try Google Takeout (takeout.google.com, "My Activity" with Gemini Apps selected): send its zip, and it is checked whether it holds every reply whole. If it does not, for chat A try the other ways Gemini offers to get a whole chat out as text: the copy button on each reply, selecting the whole page, export to Docs, a share link. Note which keeps **your questions, the answers, tables and formulas** (and the thinking summary, if any) with least effort. Save every chat as text with the way that works best: `gemini-A-pdf-fast.txt`, `gemini-B-claimset-reasoning.txt`, `gemini-memory.txt`, `gemini-cross-pdf.txt`, `gemini-cross-txt.txt`.

## 7. Usage

Note where Gemini shows how much of your limit is used, and how much this practice used, if it says.

## 8. Pasting by an agent (optional, later)

The plan has an agent paste the messages in your browser while you set up each chat and copy it. If you want to test that now with Claude Code and Claude in Chrome on your computer, note whether it could type into Gemini's box and tell when a reply had finished. Otherwise we test it when the other apps are set up.

## 9. Send back

`gemini-log.txt` and the saved chats. From them I will: fix the model names in the plan's table, record the settings, draft the masking rules from the answers, and list anything that needs a decision before collection.
