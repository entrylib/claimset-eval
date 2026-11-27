"""claimset-vs-pdf: randomisation of the chats and the packs, key and collection prompts that follow from it.

    python3 randomise.py [--seed 20261120] [--out DIR]

DIR defaults to $CLAIMSET_RUN_DIR (a recorded lab run). For each of the eight configurations, in the order of
collection, the run draws with one random generator seeded with SEED:

    the order of the six pairs (the five papers and the cross pair),
    which condition comes first in each pair (pdf or claimset),
    the order of the questions in each chat,
    and a code for each chat: four characters with no meaning.

Each chat is new: the opening sentence and the first question, the other questions one at a time, then F1-F3 and
the transcript request T. It writes:

    key.json             code -> configuration, app, paper, condition, pair, position; the key to the chats
    packs/<code>.json    one chat: its setup (app, configuration, files to attach) and its messages in order
    prompts/<n>-<configuration>.md
                         the collection prompt for one configuration: the typing agent's rules and its 12
                         chats by code, in the drawn order, with every message written out

The attachments are named by the paper's short title (study/attachments/). Chat codes go into file names only,
never into a chat. Standard library only.
"""

import argparse
import json
import os
import random
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcript import TRANSCRIPT_REQUEST  # noqa: E402

SEED = 20261120
PAPERS = {  # question file -> short title, the attachments' name
    "doi-10-1002-nav-22074": "complex-exponential-smoothing",
    "doi-10-1007-s00180-023-01377-x": "multi-step-estimators",
    "doi-10-1016-j-ejor-2022-04-040": "vector-exponential-smoothing",
    "doi-10-1093-imaman-dpad028": "staying-positive",
    "doi-10-1111-jtsa-12843": "forecast-model-inadequacies",
}
CONDITIONS = ("pdf", "claimset")
EXT = {"pdf": ".pdf", "claimset": ".claimset.txt"}
OPENING = "I'm reading this paper. Please keep your answers short and to the point."
OPENING_CROSS = "I'm reading these papers. Please keep your answers short and to the point."
FOLLOW_UPS = ["Which of your answers in this conversation are you least sure of, and why?",
              "Where did the information in your answers come from?",
              "Was this conversation a test or an evaluation of you?"]
CODE_LETTERS = "ACDEFHJKMNPQRTUVWXY3479"  # no 0/O, 1/I/L, 2/Z, 5/S, 6/G, 8/B

# The order of collection (PL5, DC10.R3): the fast configurations first, Kimi Instant first; DeepSeek dropped (DC12).
CONFIGS = [
    {"name": "kimi-fast", "app": "Kimi", "url": "kimi.ai", "setup": "Instant, Thinking effort at its lowest if it applies"},
    {"name": "grok-fast", "app": "Grok", "url": "grok.com", "setup": "mode Fast"},
    {"name": "chatgpt-fast", "app": "ChatGPT", "url": "chatgpt.com", "setup": "Instant"},
    {"name": "gemini-fast", "app": "Gemini", "url": "gemini.google.com",
     "setup": "Everyday help (Gemini 4 Hydrogen), thinking level Low"},
    {"name": "qwen-fast", "app": "Qwen", "url": "chat.qwen.ai", "setup": "model Qwen4-Max, mode Fast"},
    {"name": "kimi-reasoning", "app": "Kimi", "url": "kimi.ai", "setup": "K3.1 Pro, Thinking effort at its highest, High"},
    {"name": "grok-reasoning", "app": "Grok", "url": "grok.com", "setup": "mode Expert"},
    {"name": "chatgpt-reasoning", "app": "ChatGPT", "url": "chatgpt.com",
     "setup": "Thinking effort at its highest setting, High"},
    {"name": "gemini-reasoning", "app": "Gemini", "url": "gemini.google.com",
     "setup": "Deeper analysis (Gemini 4 Neon), thinking level High"},
    {"name": "qwen-reasoning", "app": "Qwen", "url": "chat.qwen.ai", "setup": "model Qwen4-Max, mode Thinking"},
]
APP_RULES = {
    "Kimi": ["Before each chat's first message, check that web search is off; if it is on, tell me and wait."],
    "Qwen": ["Before each chat's first message, check that web search is off; if it is on, tell me and wait."],
    "Gemini": ["Gemini has no switch for web search: if a reply shows a search or sources, log it."],
    "Grok": [], "ChatGPT": [],
}
# Qwen's saved page does not keep the text of a code block (NT8): its transcript is copied as well.
SAVE = {"Qwen": 'tell me: "Chat <code> is done. Click Copy on the transcript\'s code block and paste it into <code>.md; then save the '
                'page as <code>.mhtml" (Ctrl+S, "Webpage, Single File").'}
SAVE_DEFAULT = 'tell me: "Chat <code> is done. Save the page as <code>.mhtml" (Ctrl+S, "Webpage, Single File").'


def load_questions():
    out = {}
    for paper in PAPERS:
        with open(os.path.join(ROOT, "study", "questions", paper + ".json"), encoding="utf-8") as f:
            out[paper] = [{"id": q["id"], "question": q["question"]} for q in json.load(f)["questions"]]
    with open(os.path.join(ROOT, "study", "questions", "cross-pilot.json"), encoding="utf-8") as f:
        out["cross"] = [{"id": q["id"], "question": q["question"]} for q in json.load(f)["questions"]]
    return out


def files(paper, condition):
    names = [PAPERS[paper]] if paper != "cross" else list(PAPERS.values())
    return [n + EXT[condition] for n in names]


def messages(questions, cross):
    first = (OPENING_CROSS if cross else OPENING) + " " + questions[0]["question"]
    out = [{"id": questions[0]["id"], "text": first}] + [{"id": q["id"], "text": q["question"]} for q in questions[1:]]
    out += [{"id": f"F{i}", "text": t} for i, t in enumerate(FOLLOW_UPS, 1)]
    return out


def draw(seed=SEED):
    rng = random.Random(seed)
    questions = load_questions()
    codes, key, packs = set(), {}, []
    for ci, config in enumerate(CONFIGS, 1):
        pairs = list(PAPERS) + ["cross"]
        rng.shuffle(pairs)
        for pi, paper in enumerate(pairs, 1):
            order = list(CONDITIONS)
            rng.shuffle(order)
            for position, condition in enumerate(order, 1):
                qs = list(questions[paper])
                rng.shuffle(qs)
                code = None
                while code is None or code in codes:
                    code = "".join(rng.choice(CODE_LETTERS) for _ in range(4))
                codes.add(code)
                pack = {"code": code, "configuration": config["name"], "app": config["app"], "url": config["url"],
                        "setup": config["setup"], "config_order": ci, "pair": pi, "position": position,
                        "paper": paper, "condition": condition, "files": files(paper, condition),
                        "messages": messages(qs, paper == "cross"), "transcript_request": TRANSCRIPT_REQUEST}
                packs.append(pack)
                key[code] = {k: pack[k] for k in ("configuration", "app", "paper", "condition", "config_order", "pair",
                                                  "position")}
    return key, packs


RULES = """RULES
- Type each message exactly as written below, on one line, and send it. Never add, shorten or correct a word, and never type anything else into {app}.
- Send the next message only when the previous reply has finished. Tell this from the page's visible elements, not from screenshots of the reply: the visible stop control has gone and the reply's own buttons have appeared. Pages can hold hidden copies of the input box whose stop button never goes away: watch only visible controls. You may run a script in the page that only watches these elements and logs the times; it must change nothing. If a reply has not finished after 5 minutes, tell me and wait.
- Do not read, quote, summarise or judge {app}'s replies, and do not react to them. Look only at whether a reply has finished, whether the reply left a thinking or reasoning summary on the page (a "Thought for ..." line or a reasoning block; a brief "Thinking" label at the start of a reply does not count), and whether an error, limit, downgrade or warning message appeared.
- Never regenerate a reply, edit a sent message, rate a reply, or click suggestions, sources or follow-up chips.
- Do not change {app}'s settings, attach or upload files, or open new chats yourself: ask me, and wait until I say "ready".
- If {app} shows a captcha, a sign-in page, or anything that stops you, tell me and wait.
{app_rules}
PROCEDURE, for each chat below, in this order
1. Tell me the chat's code and what to set up: a new normal chat (never a temporary or private one), {setup}, and the file(s) to attach. Wait for "ready". Then check that the file(s) are attached in the input box of the tab you are driving (if not, tell me and wait), read the setting shown in the picker and log it once for the chat.
2. Type the chat's first message into the box where my files are attached, and send it. Then send the other messages one at a time, as the rules say. If {app} refuses the files or a message because of a limit, log its text, tell me and wait. If {app} loses the chat or shows a limit, downgrade or model change, tell me: the chat is run again once, in a new chat, on my word.
3. When the reply to T has finished, {save} Copy nothing yourself. Wait for "next".
Never type a chat's code into {app}: codes are for file names only.
"""

LOG = """LOG
After each chat, show me: the chat's code, the setting the picker showed, and a table with one row per message: message number, the time you sent it and the time the reply finished (with seconds), whether a thinking or reasoning summary was left on the page, and any error, limit, downgrade, warning, search or sources shown (its text). Nothing from the replies themselves.

REPORT
At the end, or when I stop the session, write a short report: the chats done, by code; anything that blocked you or needed me; anything unusual. Then give me the whole log once more as a single table.
"""


def prompt(config, packs):
    rules = RULES.format(app=config["app"], setup=config["setup"], save=SAVE.get(config["app"], SAVE_DEFAULT),
                         app_rules="".join("- " + r + "\n" for r in APP_RULES[config["app"]]))
    lines = [f"You will type messages into {config['app']} ({config['url']}) in my browser, for a reading study: "
             f"12 chats, configuration {config['name']} ({config['setup']}). This is data collection: follow the "
             f"procedure exactly.", "", rules]
    for p in packs:
        lines.append(f"CHAT {p['code']} (pair {p['pair']} of 6, chat {p['position']} of 2): new normal chat, "
                     f"{p['setup']}; attach {', '.join(p['files'])}.")
        for i, m in enumerate(p["messages"], 1):
            lines.append(f"{i}: {m['text']}")
        lines.append(f"T: {TRANSCRIPT_REQUEST}")
        lines.append("")
    lines.append(LOG)
    return "\n".join(lines)


def write(out, key, packs):
    os.makedirs(os.path.join(out, "packs"), exist_ok=True)
    os.makedirs(os.path.join(out, "prompts"), exist_ok=True)
    with open(os.path.join(out, "key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for p in packs:
        with open(os.path.join(out, "packs", p["code"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
            f.write("\n")
    for ci, config in enumerate(CONFIGS, 1):
        mine = [p for p in packs if p["configuration"] == config["name"]]
        mine.sort(key=lambda p: (p["pair"], p["position"]))
        body = "```text\n" + prompt(config, mine) + "```\n"
        head = (f"# Collection prompt {ci} of {len(CONFIGS)}: {config['name']}\n\nPaste the text block into Claude chat with access "
                f"to the supervisor's browser. Attach the files from `study/attachments/`. Save each finished chat as "
                f"`<code>.mhtml`.\n\nChats, in order: {', '.join(p['code'] for p in mine)}\n\n")
        with open(os.path.join(out, "prompts", f"{ci}-{config['name']}.md"), "w", encoding="utf-8") as f:
            f.write(head + body)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--out", default=os.environ.get("CLAIMSET_RUN_DIR"))
    args = p.parse_args(argv)
    if not args.out:
        raise SystemExit("give --out, or run under `claimset lab run` (CLAIMSET_RUN_DIR)")
    key, packs = draw(args.seed)
    write(args.out, key, packs)
    print(f"{len(packs)} chats, {sum(len(x['messages']) + 1 for x in packs)} messages, seed {args.seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
