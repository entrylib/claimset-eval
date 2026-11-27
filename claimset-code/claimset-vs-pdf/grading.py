"""claimset-vs-pdf: coded, masked answers for the judges, their grades, the blind moderation sheet, and the futility
look (plan §3.3 and §9).

    python3 grading.py build --key KEY --packs PACKS --chats CHATS --questions DIR --configuration NAME [...]
                             --seed SEED [--batch 10] [--out DIR]
        Splits the per-paper chats of the configurations into answers (the follow-ups F1-F3 and the cross chats
        are left out), masks each (mask.py) and gives it a random answer code. Writes:
          answers.json        [{answer, question, text}]: the masked answers, by answer code
          answer-key.json     answer code -> chat, configuration, condition, paper, question, turn: read only by
                              the look and the analysis
          batches/NN.json     the judges' batches: whole questions (question, reference answer, marking guide; never
                              the authors' notes), each with all its answers in random order
    python3 grading.py prompt INSTRUCTIONS BATCH
        The judge's prompt for one batch: the fixed instructions, then the batch.
    python3 grading.py grades --batches DIR --outputs DIR --judge NAME [--out DIR]
        Reads each batch's judge output (OUTPUTS/NN.txt, a JSON object as the instructions ask) and checks it: one
        grade for every answer, score 0, 0.5 or 1, flags 0 or 1, a reason. Writes grades-JUDGE.json, and the
        outputs as given to outputs-JUDGE/.
    python3 grading.py sheet --batches DIR --grades FILE --seed SEED [--out DIR]
        The moderator's sheet: every answer under a fresh moderation code (not the answer code), question by
        question in a new random order, with the judge's grade and reason. Writes moderation.html (opened in a
        browser; it saves the moderator's grades as moderation.json) and moderation-key.json (moderation code ->
        answer code; the moderator never opens it).
    python3 grading.py look --key answer-key.json --questions DIR --grades FILE --moderation FILE
                            --moderation-key FILE [--out DIR]
        The futility look: the interim grades (the judge's grades, as the moderator approved or replaced them),
        then, with the PDF only, the mean score on the answerable questions and the rates of invented answers on
        the absent and of overreach on the scope questions. Prints only "room" or "no room"; writes the interim
        grades (interim-grades.json) and the numbers (sealed.json, not opened until the analysis).

--out defaults to $CLAIMSET_RUN_DIR. Standard library only.
"""

import argparse
import glob
import html
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mask  # noqa: E402
from randomise import CODE_LETTERS  # noqa: E402

ANSWERABLE = ("lookup", "scope", "evidence")
FOLLOW_UPS = ("F1", "F2", "F3")


def out_dir(path):
    path = path or os.environ.get("CLAIMSET_RUN_DIR")
    if not path:
        sys.exit("--out or $CLAIMSET_RUN_DIR is needed")
    os.makedirs(path, exist_ok=True)
    return path


def dump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def questions(directory):
    """paper -> question id -> question (the per-paper question files, named by paper)."""
    out = {}
    for path in glob.glob(os.path.join(directory, "doi-*.json")):
        out[os.path.basename(path)[:-5]] = {q["id"]: q for q in load(path)["questions"]}
    return out


def new_codes(rng, n, length, used=()):
    codes, used = [], set(used)
    while len(codes) < n:
        c = "".join(rng.choice(CODE_LETTERS) for _ in range(length))
        if c not in used:
            used.add(c)
            codes.append(c)
    return codes


def build(key, packs, chats, qs, configurations, seed, batch=10):
    """(answers, answer_key, batches) for the per-paper chats of the configurations."""
    rng = random.Random(f"{seed}:answers")
    raw = []
    for chat_code in sorted(key):
        k = key[chat_code]
        if k["configuration"] not in configurations or k["paper"] == "cross":
            continue
        ids = [m["id"] for m in load(os.path.join(packs, chat_code + ".json"))["messages"]]
        turns = load(os.path.join(chats, chat_code + ".json"))["turns"]
        if len(turns) != len(ids):
            raise ValueError(f"{chat_code}: {len(turns)} turns for {len(ids)} messages")
        for n, (qid, t) in enumerate(zip(ids, turns), 1):
            if qid not in FOLLOW_UPS:
                raw.append((chat_code, k, qid, n, t["assistant"]))
    codes = new_codes(rng, len(raw), 6)
    answers, answer_key, by_question = [], {}, {}
    for code, (chat_code, k, qid, n, text) in zip(codes, raw):
        label = f"{k['paper']}#{qid}"
        answers.append({"answer": code, "question": label, "text": mask.mask(text).strip()})
        answer_key[code] = {"chat": chat_code, "configuration": k["configuration"], "condition": k["condition"],
                            "paper": k["paper"], "question": qid, "turn": n}
        by_question.setdefault(label, []).append(answers[-1])
    labels = sorted(by_question)
    rng.shuffle(labels)
    items = []
    for label in labels:
        paper, qid = label.split("#")
        q = qs[paper][qid]
        group = [{"answer": a["answer"], "text": a["text"]} for a in by_question[label]]
        rng.shuffle(group)
        items.append({"question": label, "text": q["question"], "reference": q.get("answer"),
                      "marking": q["marking"], "answers": group})
    batches = [items[i:i + batch] for i in range(0, len(items), batch)]
    answers.sort(key=lambda a: a["answer"])
    return answers, answer_key, batches


def prompt(instructions, batch):
    parts = [instructions.rstrip(), "", "## The questions and answers to grade", ""]
    for item in batch:
        parts += [f"### Question {item['question']}", "", item["text"], "",
                  "Reference answer: " + (item["reference"] or "none (an absent question: the paper does not answer it)"),
                  "", "Marking guide: " + item["marking"], ""]
        for a in item["answers"]:
            parts += [f"#### Answer {a['answer']}", "", a["text"], ""]
    return "\n".join(parts)


def parse_output(text):
    """The JSON object of a judge's output (a code fence around it allowed)."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object")
    return json.loads(m.group(0))


def check_grades(batch, output):
    """({answer code: grade}, problems) for one batch and the judge's parsed output."""
    want = {a["answer"]: item["question"] for item in batch for a in item["answers"]}
    got, problems = {}, []
    for g in output.get("grades", []):
        code = g.get("answer")
        if code not in want:
            problems.append(f"grade for an answer not in the batch: {code}")
            continue
        if code in got:
            problems.append(f"two grades for {code}")
        if g.get("question") != want[code]:
            problems.append(f"{code}: question {g.get('question')} is not {want[code]}")
        if g.get("score") not in (0, 0.5, 1) or g.get("invented") not in (0, 1) or g.get("overreach") not in (0, 1):
            problems.append(f"{code}: score {g.get('score')}, invented {g.get('invented')}, overreach {g.get('overreach')}")
        if not str(g.get("reason", "")).strip():
            problems.append(f"{code}: no reason")
        got[code] = {k: g.get(k) for k in ("question", "score", "invented", "overreach", "reason")}
    problems += [f"no grade for {c}" for c in want if c not in got]
    return got, problems


SHEET = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moderation sheet</title>
<style>
:root{--bg:#fbfbfa;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#deddd8;--accent:#2f5d8a;--warn:#9a4b00}
@media (prefers-color-scheme:dark){:root{--bg:#1b1b1a;--fg:#ecebe6;--muted:#a3a29c;--card:#252524;--line:#3a3a37;--accent:#8db7e0;--warn:#e0a060}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0;padding:16px}
main{max-width:900px;margin:0 auto}
header{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:1}
.q{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:20px 0 8px}
.q h2{font-size:15px;margin:0 0 6px}.lab{color:var(--muted);font-size:13px}
.a{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:12px 16px;margin:8px 0 8px 16px}
.a.done{border-left-color:var(--accent)}.a.changed{border-left-color:var(--warn)}
pre{white-space:pre-wrap;word-wrap:break-word;font:14px/1.5 ui-monospace,monospace;margin:6px 0}
.judge{color:var(--muted);font-size:14px;margin:6px 0}
label{margin-right:14px}textarea{width:100%;box-sizing:border-box;min-height:44px;font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px}
button{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);cursor:pointer}
.row{margin:6px 0}
</style></head><body><main>
<header><b>Moderation sheet</b> &middot; <span id="progress"></span> &middot;
<button id="save">Download moderation.json</button>
<div class="lab">For each answer: tick <i>Approve</i> to keep the judge's grade and flags, or change them and give a reason. Your work is kept in this browser as you go; download the file when done (or at any time) and send it back.</div></header>
<div id="items"></div></main>
<script>
const DATA = __DATA__;
const KEY = "moderation:" + DATA.sheet;
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { state = {}; }
const el = (t, a = {}, ...kids) => { const e = document.createElement(t); for (const k in a) { if (k === "text") e.textContent = a[k]; else e.setAttribute(k, a[k]); } kids.forEach(c => e.appendChild(c)); return e; };
function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} progress(); }
function progress() {
  const n = DATA.items.reduce((s, q) => s + q.answers.length, 0);
  const d = Object.values(state).filter(s => s.approved || (s.reason || "").trim()).length;
  document.getElementById("progress").textContent = d + " of " + n + " done";
}
function card(a) {
  const s = state[a.code] || (state[a.code] = {score: a.judge.score, invented: a.judge.invented, overreach: a.judge.overreach, reason: "", approved: false});
  const box = el("div", {class: "a"});
  const mark = () => { const changed = s.score !== a.judge.score || s.invented !== a.judge.invented || s.overreach !== a.judge.overreach;
    s.changed = changed; if (changed) s.approved = false; appr.checked = s.approved;
    box.className = "a" + (changed ? " changed" : "") + (s.approved || (changed && s.reason.trim()) ? " done" : ""); save(); };
  const sel = el("select");
  [["1", "1"], ["0.5", "½"], ["0", "0"]].forEach(([v, t]) => { const o = el("option", {value: v, text: t}); if (Number(v) === s.score) o.selected = true; sel.appendChild(o); });
  sel.onchange = () => { s.score = Number(sel.value); mark(); };
  const box1 = el("input", {type: "checkbox"}); box1.checked = !!s.invented; box1.onchange = () => { s.invented = box1.checked ? 1 : 0; mark(); };
  const box2 = el("input", {type: "checkbox"}); box2.checked = !!s.overreach; box2.onchange = () => { s.overreach = box2.checked ? 1 : 0; mark(); };
  const appr = el("input", {type: "checkbox"}); appr.checked = s.approved; appr.onchange = () => { if (appr.checked) { s.score = a.judge.score; s.invented = a.judge.invented; s.overreach = a.judge.overreach; sel.value = String(s.score); box1.checked = !!s.invented; box2.checked = !!s.overreach; } s.approved = appr.checked; mark(); };
  const why = el("textarea", {placeholder: "Reason (needed when you change the grade or a flag)"}); why.value = s.reason; why.oninput = () => { s.reason = why.value; mark(); };
  box.append(el("div", {class: "lab", text: "Answer " + a.code}), el("pre", {text: a.text}),
    el("div", {class: "judge", text: "Judge: score " + a.judge.score + ", invented " + a.judge.invented + ", overreach " + a.judge.overreach + ". " + a.judge.reason}),
    el("div", {class: "row"}, el("label", {}, appr, document.createTextNode(" Approve")), el("label", {text: "Score "}), sel,
      el("label", {}, document.createTextNode("  "), box1, document.createTextNode(" invented")), el("label", {}, box2, document.createTextNode(" overreach"))),
    why);
  mark();
  return box;
}
const root = document.getElementById("items");
DATA.items.forEach((q, i) => {
  root.appendChild(el("div", {class: "q"}, el("div", {class: "lab", text: "Question " + (i + 1) + " of " + DATA.items.length}), el("h2", {text: q.text}),
    el("div", {}, el("b", {text: "Reference answer: "}), document.createTextNode(q.reference || "none (an absent question: the paper does not answer it)")),
    el("div", {}, el("b", {text: "Marking guide: "}), document.createTextNode(q.marking))));
  q.answers.forEach(a => root.appendChild(card(a)));
});
document.getElementById("save").onclick = () => {
  const out = {sheet: DATA.sheet, grades: state};
  const url = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], {type: "application/json"}));
  const link = el("a", {href: url, download: "moderation.json"}); document.body.appendChild(link); link.click(); link.remove();
};
progress();
</script></body></html>
"""


def sheet(batches, grades, seed):
    """(html text, moderation key) with fresh moderation codes and a new random order."""
    rng = random.Random(f"{seed}:moderation")
    items = [item for b in batches for item in b]
    rng.shuffle(items)
    answers = [a for item in items for a in item["answers"]]
    codes = new_codes(rng, len(answers), 5, used={a["answer"] for a in answers})
    key, data = {}, {"sheet": f"{seed}", "items": []}
    k = 0
    for item in items:
        group = list(item["answers"])
        rng.shuffle(group)
        out = []
        for a in group:
            key[codes[k]] = a["answer"]
            g = grades[a["answer"]]
            out.append({"code": codes[k], "text": a["text"],
                        "judge": {x: g[x] for x in ("score", "invented", "overreach", "reason")}})
            k += 1
        data["items"].append({"text": item["text"], "reference": item["reference"], "marking": item["marking"],
                              "answers": out})
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return SHEET.replace("__DATA__", payload), key


def interim(grades, moderation, moderation_key):
    """{answer code: final grade}: the judge's grade where approved, the moderator's where changed (with a reason)."""
    out, problems = {}, []
    for mcode, code in moderation_key.items():
        g, m = grades[code], moderation.get(mcode)
        if m is None or not (m.get("approved") or str(m.get("reason", "")).strip()):
            problems.append(f"answer {mcode} not moderated")
            continue
        if m.get("approved"):
            out[code] = {x: g[x] for x in ("score", "invented", "overreach")} | {"moderation": "approved"}
        else:
            out[code] = {"score": m["score"], "invented": m["invented"], "overreach": m["overreach"],
                         "moderation": "changed", "reason": m["reason"]}
    return out, problems


def look(answer_key, qs, final):
    """The numbers of the futility look, with the PDF only, and the verdict."""
    score, invented, overreach = [], [], []
    for code, g in final.items():
        k = answer_key[code]
        if k["condition"] != "pdf":
            continue
        kind = qs[k["paper"]][k["question"]]["type"]
        if kind in ANSWERABLE:
            score.append(g["score"])
        if kind == "absent":
            invented.append(g["invented"])
        if kind == "scope":
            overreach.append(g["overreach"])
    mean = lambda x: sum(x) / len(x) if x else float("nan")  # noqa: E731
    numbers = {"pdf mean score, answerable": mean(score), "n answerable": len(score),
               "pdf invented rate, absent": mean(invented), "n absent": len(invented),
               "pdf overreach rate, scope": mean(overreach), "n scope": len(overreach)}
    no_room = (numbers["pdf mean score, answerable"] >= 0.95 and numbers["pdf invented rate, absent"] <= 0.05
               and numbers["pdf overreach rate, scope"] <= 0.05)
    return numbers, "no room" if no_room else "room"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    for a in ("--key", "--packs", "--chats", "--questions"):
        b.add_argument(a, required=True)
    b.add_argument("--configuration", action="append", required=True)
    b.add_argument("--seed", required=True)
    b.add_argument("--batch", type=int, default=10)
    b.add_argument("--out")
    pr = sub.add_parser("prompt")
    pr.add_argument("instructions")
    pr.add_argument("batch")
    g = sub.add_parser("grades")
    g.add_argument("--batches", required=True)
    g.add_argument("--outputs", required=True)
    g.add_argument("--judge", required=True)
    g.add_argument("--out")
    s = sub.add_parser("sheet")
    s.add_argument("--batches", required=True)
    s.add_argument("--grades", required=True)
    s.add_argument("--seed", required=True)
    s.add_argument("--out")
    lk = sub.add_parser("look")
    for a in ("--key", "--questions", "--grades", "--moderation", "--moderation-key"):
        lk.add_argument(a, required=True)
    lk.add_argument("--out")
    args = p.parse_args(argv)

    if args.command == "prompt":
        print(prompt(open(args.instructions, encoding="utf-8").read(), load(args.batch)))
        return 0
    out = out_dir(args.out)
    if args.command == "build":
        answers, answer_key, batches = build(load(args.key), args.packs, args.chats, questions(args.questions),
                                             set(args.configuration), args.seed, args.batch)
        dump(os.path.join(out, "answers.json"), answers)
        dump(os.path.join(out, "answer-key.json"), answer_key)
        os.makedirs(os.path.join(out, "batches"), exist_ok=True)
        for i, batch in enumerate(batches, 1):
            dump(os.path.join(out, "batches", f"{i:02d}.json"), batch)
        print(f"{len(answers)} answers to {sum(len(b) for b in batches)} questions in {len(batches)} batches")
        return 0
    if args.command == "grades":
        grades, problems = {}, []
        kept = os.path.join(out, f"outputs-{args.judge}")
        os.makedirs(kept, exist_ok=True)
        for path in sorted(glob.glob(os.path.join(args.batches, "*.json"))):
            name = os.path.basename(path)[:-5]
            try:
                raw = open(os.path.join(args.outputs, name + ".txt"), encoding="utf-8").read()
                with open(os.path.join(kept, name + ".txt"), "w", encoding="utf-8") as f:
                    f.write(raw)  # the judge's output as given, kept with the run
                output = parse_output(raw)
            except (OSError, ValueError) as e:
                problems.append(f"batch {name}: {e}")
                continue
            got, bad = check_grades(load(path), output)
            grades.update(got)
            problems += [f"batch {name}: {x}" for x in bad]
        dump(os.path.join(out, f"grades-{args.judge}.json"), grades)
        print(f"{len(grades)} grades; " + ("no problems" if not problems else f"{len(problems)} problem(s)"))
        for x in problems:
            print("  " + x)
        return 1 if problems else 0
    if args.command == "sheet":
        batches = [load(path) for path in sorted(glob.glob(os.path.join(args.batches, "*.json")))]
        text, key = sheet(batches, load(args.grades), args.seed)
        with open(os.path.join(out, "moderation.html"), "w", encoding="utf-8") as f:
            f.write(text)
        dump(os.path.join(out, "moderation-key.json"), key)
        print(f"{len(key)} answers on the sheet")
        return 0
    final, problems = interim(load(args.grades), load(args.moderation)["grades"], load(args.moderation_key))
    if problems:
        print(f"{len(problems)} answer(s) not moderated; no look")
        return 1
    numbers, verdict = look(load(args.key), questions(args.questions), final)
    dump(os.path.join(out, "interim-grades.json"), final)
    dump(os.path.join(out, "sealed.json"), dict(numbers, verdict=verdict))
    print(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
