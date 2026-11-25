# Practice: ChatGPT

The supervisor's part of the ChatGPT practice: the settings before the agent starts (`chatgpt-agent-prompt.md`), what to note, and how to copy the chats. Nothing here is data. Write notes in `chatgpt-log.txt`.

A Free account is enough to test the procedure (typing, finished replies, settings, attachments, copying). It is not enough to fix the study's models: the plan takes the most capable fast and reasoning configurations on the subscription used for collection, so the model picker and the limits are checked again on that subscription.

## 1. Account and model picker

1. Note the plan (Free) and the date.
2. Open the model picker and note **every** option exactly as named, with any thinking or effort setting and anything marked as limited or locked. For the practice: **fast** is the option without thinking (for example "Instant"); **reasoning** is the thinking option at the highest level offered. Never "Auto".
3. Note whether a reply shows which model produced it (on the reply, or in its menu), and whether ChatGPT ever says it switched model or reached a limit.

## 2. Settings

Find and note each (names change; note what you find):

1. **Memory**: saved memories off, and "reference chat history" off.
2. **Custom instructions / personalisation**: empty.
3. **No temporary chats** (lab note NT2): they disappear when the page is left. Use normal chats, with the memory settings above off, and keep them until they have been taken out and checked (§4).
4. **Web search**: is there a setting or a toggle that turns it off? Note what there is. If none, note that.
5. **Tools** (connectors, apps, canvas, image generation, deep research): not selected.
6. **Data controls**: note whether "improve the model for everyone" is on (it does not change the answers; it is recorded).

## 3. During the run

The agent types; you set up each chat when it asks (a new chat, the model, the file(s)) and say "ready", and "next" when it says the chat is done. Note anything the agent could not do.

## 4. Getting the chats out: transcript and saved page

Nobody copies replies by hand, and the agent copies nothing. Every chat ends with the transcript request (T in the agent's prompt, `transcript` in `practice-questions.json`): the app answers with the whole chat in one code block. When the agent says the chat is done, save the page in Chrome: Ctrl+S, "Webpage, Single File" (.mhtml; "HTML only" saves a page without the chat). Name it `chatgpt-<chat>.mhtml` (chatgpt-A.mhtml, …). The page holds the transcript and the last replies as the app shows them; `claimset-code/claimset-vs-pdf/transcript.py` takes the transcript out and checks that it has every message as sent, every turn, and the last replies word for word as displayed. The page also holds the titles of your other chats: it is processed and not committed. Keep the chats in the app until the check has passed. Not PDF export (it clips text at page ends, lab note NT1), and not the app's account export (it can take days and holds every chat of the account).

## 5. Limits

Note any message about limits (messages, file uploads, thinking), when it appeared, and where ChatGPT shows how much is left.

## 6. Send back

`chatgpt-log.txt`, the agent's log and report, and the saved pages.
