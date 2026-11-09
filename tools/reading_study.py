"""Reading study: does a claimset help a model answer questions about a paper?

The same questions are put to a model with each paper given in up to three forms (conditions), and the answers
are graded blind against the author's reference answers:

    paper     the paper's text (papers/text/<name>.txt)
    claimset  the claimset's reading view (claimset/pilot/<name>.claimset.txt)
    bundle    for a question naming claims, only those claims and what they rest on (claimset render --claim)

    python3 tools/reading_study.py check                     # question files, documents, planned calls
    python3 tools/reading_study.py run    --out study/runs/R --model claude-opus-5-5 [--dry-run]
    python3 tools/reading_study.py grade  --out study/runs/R [--sheet sheet.csv | --import sheet.csv]
    python3 tools/reading_study.py report --out study/runs/R

Standard library only; the Claude API is called over HTTPS with ANTHROPIC_API_KEY from the environment.
See study/README.md for the protocol and the question format.
"""

import argparse
import csv
import glob
import hashlib
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TYPES = ("lookup", "scope", "evidence", "absent", "cross")
CONDITIONS = ("paper", "claimset", "bundle")
GRADES = ("correct", "partial", "incorrect", "not_stated")
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2026-10-21"

SYSTEM = """You answer a question about one or more research papers. The document you are given is either a \
paper's text or a claimset (a structured record of a paper's claims, evidence and limitations), possibly only \
part of one.

Answer only from the document. Do not use outside knowledge of the paper, its authors or its field. If the \
document does not give the answer, set not_stated to true and say briefly what is missing; do not guess.

Keep the answer short: a sentence or a few, with the numbers, conditions and scope the document gives. Do not \
state a result more broadly than the document does.

In cites, list the places you relied on: paragraph markers such as p3.2 in a paper's text, or identifiers such \
as C4, E2 or L1 in a claimset. Do not put markers or identifiers in the answer itself."""

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "not_stated": {"type": "boolean"},
        "cites": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "not_stated", "cites"],
    "additionalProperties": False,
}

JUDGE_SYSTEM = """You grade an answer to a question about a research paper against a reference answer written \
by the paper's author. You do not see the paper; the reference answer is authoritative.

Grades:
- correct: agrees with the reference on everything the question asks. Extra detail that does not contradict \
the reference is fine.
- partial: right in part; incomplete or imprecise on something the question asks.
- incorrect: contradicts the reference, or answers something else.
- not_stated: the answer says the document does not give this.

If the reference says the paper does not state the answer, grade correct when the answer says so, and \
incorrect when it gives a substantive answer.

overreach is true when the answer states a result more broadly than the reference allows (beyond its data, \
conditions or population), whatever the grade. Give the reason in one sentence."""

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "grade": {"type": "string", "enum": list(GRADES)},
        "overreach": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["grade", "overreach", "reason"],
    "additionalProperties": False,
}

ABSENT_ANSWER = "The paper does not state this."
MARKER = re.compile(r"\[(p\d+\.\d+)\]")
CITE_LIKE = re.compile(r"\[?\bp\d+\.\d+\]?|\b[BCDELW]\d+(?:\.[A-Za-z0-9]+)*\b")  # paragraph markers, claimset ids
TERM = re.compile(r"\[\[[A-Z]\d+:([^\]]+)\]\]")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------- questions and documents ----------

def question_files(paths=None, root=ROOT):
    if paths:
        return sorted(paths)
    return sorted(p for p in glob.glob(os.path.join(root, "study", "questions", "*.json"))
                  if not os.path.basename(p).startswith("_"))


def load_questions(paths, root=ROOT):
    """Every question of the files, each with its file's papers; problems as a list of messages."""
    out, problems, seen = [], [], set()
    for path in paths:
        stem = os.path.splitext(os.path.basename(path))[0]
        try:
            doc = json.loads(read(path))
        except (OSError, ValueError) as e:
            problems.append(f"{path}: {e}")
            continue
        papers = doc.get("papers")
        if not isinstance(papers, list) or not papers or not all(isinstance(p, str) for p in papers):
            problems.append(f"{path}: 'papers' must be a list of paper names")
            continue
        for p in papers:
            for need in (paper_path(p, root), claimset_path(p, root), view_path(p, root)):
                if not os.path.exists(need):
                    problems.append(f"{path}: missing {os.path.relpath(need, root)}")
        ids = claim_ids(papers, root)
        for i, q in enumerate(doc.get("questions") or []):
            where = f"{path}: question {i + 1}"
            if not isinstance(q, dict):
                problems.append(f"{where}: not an object")
                continue
            qid = q.get("id")
            if not isinstance(qid, str) or not qid:
                problems.append(f"{where}: no id")
                continue
            uid = f"{stem}:{qid}"
            if uid in seen:
                problems.append(f"{where}: duplicate id {qid}")
            seen.add(uid)
            t = q.get("type")
            if t not in TYPES:
                problems.append(f"{uid}: type must be one of {', '.join(TYPES)}")
            if (t == "cross") != (len(papers) > 1):
                problems.append(f"{uid}: 'cross' questions, and only they, go in files with several papers")
            if not isinstance(q.get("question"), str) or not q["question"].strip():
                problems.append(f"{uid}: no question")
            answer = q.get("answer")
            if t == "absent":
                answer = answer or ABSENT_ANSWER
            elif not isinstance(answer, str) or not answer.strip():
                problems.append(f"{uid}: no reference answer")
            claims = q.get("claims") or []
            if claims and len(papers) > 1:
                problems.append(f"{uid}: 'claims' (the bundle condition) only in single-paper files")
            for c in claims:
                if ids is not None and c not in ids:
                    problems.append(f"{uid}: claim {c} is not in the claimset")
            if q.get("in_claimset") not in (True, False, None):
                problems.append(f"{uid}: in_claimset must be true, false or absent")
            out.append({"uid": uid, "file": stem, "papers": papers, "id": qid, "type": t,
                        "question": q.get("question", ""), "answer": answer or "", "notes": q.get("notes", ""),
                        "claims": claims, "in_claimset": q.get("in_claimset")})
    return out, problems


def paper_path(name, root=ROOT):
    return os.path.join(root, "papers", "text", f"{name}.txt")


def claimset_path(name, root=ROOT):
    return os.path.join(root, "claimset", "pilot", f"{name}.claimset.json")


def view_path(name, root=ROOT):
    return os.path.join(root, "claimset", "pilot", f"{name}.claimset.txt")


def claim_ids(papers, root=ROOT):
    if len(papers) != 1 or not os.path.exists(claimset_path(papers[0], root)):
        return None
    try:
        doc = json.loads(read(claimset_path(papers[0], root)))
    except ValueError:
        return None
    return {c.get("id") for c in doc.get("claims", []) if isinstance(c, dict)}


def object_ids(node, out=None):
    """Every identifier in a claimset (claims, evidence, limitations, definitions, tables, ...)."""
    out = set() if out is None else out
    if isinstance(node, dict):
        if isinstance(node.get("id"), str):
            out.add(node["id"])
        for v in node.values():
            object_ids(v, out)
    elif isinstance(node, list):
        for v in node:
            object_ids(v, out)
    return out


def render_bundle(name, claim, root=ROOT):
    """The reading view of one claim and what it rests on, from the claimset package."""
    try:
        r = subprocess.run(["claimset", "render", claimset_path(name, root), "--claim", claim],
                           capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("the claimset package is not installed (pip install git+https://github.com/entrylib/claimset)")
    if r.returncode:
        raise RuntimeError(f"claimset render --claim {claim} failed for {name}: {r.stderr.strip()}")
    return r.stdout


def document(q, condition, root=ROOT):
    """The text the model is given for a question under a condition, or None if the condition does not apply."""
    if condition == "bundle":
        if not q["claims"]:
            return None
        name = q["papers"][0]
        return "\n\n".join(render_bundle(name, c, root) for c in q["claims"])
    parts = []
    for name in q["papers"]:
        text = read(paper_path(name, root) if condition == "paper" else view_path(name, root))
        parts.append(f"=== {name} ===\n{text}" if len(q["papers"]) > 1 else text)
    return "\n\n".join(parts)


def tasks(questions, conditions, models, reps, seed):
    """Every call of a run, in a seeded random order so that drift in the API's speed spreads over conditions."""
    out = [{"key": f"{q['uid']}|{c}|{m}|{r}", "q": q, "condition": c, "model": m, "rep": r}
           for q in questions for c in conditions for m in models for r in range(1, reps + 1)
           if not (c == "bundle" and not q["claims"])]
    random.Random(seed).shuffle(out)
    return out


# ---------- model calls ----------

def call_anthropic(model, system, blocks, schema, effort, max_tokens=16000):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is not set")
    body = json.dumps({
        "model": model, "max_tokens": max_tokens, "system": system,
        "messages": [{"role": "user", "content": blocks}],
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}},
    }).encode("utf-8")
    headers = {"content-type": "application/json", "x-api-key": key, "anthropic-version": API_VERSION}
    attempts = 0
    while True:
        attempts += 1
        req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            latency = time.perf_counter() - start
            break
        except urllib.error.HTTPError as e:
            retryable = e.code in (408, 409, 429) or e.code >= 500
            if not retryable or attempts > 4:
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}") from None
            wait = float(e.headers.get("retry-after") or 2 ** attempts)
        except urllib.error.URLError as e:
            if attempts > 4:
                raise RuntimeError(f"connection failed: {e.reason}") from None
            wait = 2 ** attempts
        time.sleep(wait)
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return {"text": text, "usage": data.get("usage", {}), "stop_reason": data.get("stop_reason"),
            "served_model": data.get("model"), "latency_s": round(latency, 3), "attempts": attempts}


def call_fake(model, system, blocks, schema, effort, max_tokens=16000):
    """No network: for --dry-run and tests. Answers 'not stated' to everything; judges every answer correct."""
    chars = len(system) + sum(len(b.get("text", "")) for b in blocks)
    if "grade" in schema["properties"]:
        out = {"grade": "correct", "overreach": False, "reason": "fake judge"}
    else:
        out = {"answer": "Not given.", "not_stated": True, "cites": []}
    return {"text": json.dumps(out), "usage": {"input_tokens": chars // 4, "output_tokens": 20},
            "stop_reason": "end_turn", "served_model": model, "latency_s": 0.0, "attempts": 1}


PROVIDERS = {"anthropic": call_anthropic, "fake": call_fake}


def input_tokens(usage):
    return sum(usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def ask(provider, task, effort, root=ROOT):
    q, cond = task["q"], task["condition"]
    doc = document(q, cond, root)
    blocks = [{"type": "text", "text": f"<document>\n{doc}\n</document>"},
              {"type": "text", "text": f"Question: {q['question']}"}]
    rec = {"key": task["key"], "uid": q["uid"], "file": q["file"], "type": q["type"], "condition": cond,
           "model": task["model"], "rep": task["rep"], "effort": effort, "doc_sha256": sha(doc),
           "doc_chars": len(doc), "time": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        r = PROVIDERS[provider](task["model"], SYSTEM, blocks, ANSWER_SCHEMA, effort)
    except RuntimeError as e:
        return {**rec, "error": str(e)}
    rec.update({"served_model": r["served_model"], "usage": r["usage"], "input_tokens": input_tokens(r["usage"]),
                "output_tokens": r["usage"].get("output_tokens"), "latency_s": r["latency_s"],
                "attempts": r["attempts"], "stop_reason": r["stop_reason"]})
    if r["stop_reason"] != "end_turn":
        return {**rec, "error": f"stop_reason {r['stop_reason']}", "raw": r["text"]}
    try:
        a = json.loads(r["text"])
        rec.update({"answer": a["answer"], "not_stated": bool(a["not_stated"]), "cites": list(a["cites"])})
    except (ValueError, KeyError, TypeError):
        rec.update({"error": "answer is not the expected JSON", "raw": r["text"]})
    return rec


# ---------- run ----------

def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append_jsonl(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def manifest(questions, args, files, root=ROOT):
    docs = {}
    for q in questions:
        for name in q["papers"]:
            docs[f"paper:{name}"] = sha(read(paper_path(name, root)))
            docs[f"claimset:{name}"] = sha(read(view_path(name, root)))
    return {"questions": {os.path.relpath(p, root): sha(read(p)) for p in files},
            "documents": dict(sorted(docs.items())), "system": sha(SYSTEM), "answer_schema": sha(json.dumps(ANSWER_SCHEMA)),
            "conditions": args.conditions, "models": args.model, "reps": args.reps, "effort": args.effort,
            "seed": args.seed, "provider": args.provider, "script": sha(read(os.path.abspath(__file__)))}


def cmd_run(args, root=ROOT):
    files = question_files(args.questions, root)
    questions, problems = load_questions(files, root)
    if problems:
        raise SystemExit("question files have problems; run `check`:\n  " + "\n  ".join(problems))
    plan = tasks(questions, args.conditions, args.model, args.reps, args.seed)
    if args.dry_run:
        est = {}
        for t in plan:
            doc = document(t["q"], t["condition"], root)
            est.setdefault(t["condition"], []).append((len(SYSTEM) + len(doc) + len(t["q"]["question"])) // 4)
        print(f"{len(questions)} questions, {len(plan)} calls")
        for c, toks in est.items():
            print(f"  {c:9} {len(toks):5} calls, about {statistics.mean(toks):8.0f} input tokens each, "
                  f"{sum(toks) / 1e6:.2f}M in all")
        return 0
    os.makedirs(args.out, exist_ok=True)
    man = manifest(questions, args, files, root)
    mpath = os.path.join(args.out, "manifest.json")
    if os.path.exists(mpath):
        old = json.loads(read(mpath))
        if old != man and not args.force:
            changed = sorted(k for k in man if man[k] != old.get(k))
            raise SystemExit(f"{mpath} differs from this run ({', '.join(changed)}); "
                             "use a new --out, or --force to continue anyway")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2)
    apath = os.path.join(args.out, "answers.jsonl")
    done = {r["key"] for r in load_jsonl(apath) if not r.get("error")}
    todo = [t for t in plan if t["key"] not in done][:args.max_calls or None]
    print(f"{len(plan)} calls planned, {sum(t['key'] in done for t in plan)} done, {len(todo)} to make now")
    errors = 0
    for i, t in enumerate(todo, 1):
        rec = ask(args.provider, t, args.effort, root)
        append_jsonl(apath, rec)
        errors += bool(rec.get("error"))
        print(f"[{i}/{len(todo)}] {t['key']}: {rec.get('error') or 'ok'}", file=sys.stderr)
    print(f"{len(todo) - errors} answers written, {errors} errors (run again to retry them)")
    return 1 if errors else 0


# ---------- grade ----------

def blind(text):
    """The answer as the judge sees it: no markers or identifiers that would show which condition produced it."""
    text = TERM.sub(lambda m: m.group(1), text or "")
    text = re.sub(r"[(\[][\s,;]*[)\]]", "", CITE_LIKE.sub("", text))     # brackets left empty
    text = re.sub(r"([,;])(?:\s*[,;])+", r"\1", text)                      # separators left in a row
    return re.sub(r"\s+([,.;:])", r"\1", re.sub(r"\s{2,}", " ", text)).strip()


def cites_valid(rec, q, root=ROOT):
    """How many of an answer's cites exist in the document it was given (markers in a paper, ids in a claimset)."""
    cites = [c.strip("[] ") for c in rec.get("cites") or []]
    if not cites:
        return 0, 0
    if rec["condition"] == "paper":
        known = set()
        for name in q["papers"]:
            known |= set(MARKER.findall(read(paper_path(name, root))))
    else:
        known = set()
        for name in q["papers"]:
            known |= object_ids(json.loads(read(claimset_path(name, root))))
    ok = sum(1 for c in cites if c in known or c.split(".")[0] in known)
    return ok, len(cites)


def final_grade(g):
    h = g.get("human") or {}
    return h.get("grade") or g["grade"], h.get("overreach", g["overreach"])


def cmd_grade(args, root=ROOT):
    questions, problems = load_questions(question_files(args.questions, root), root)
    if problems:
        raise SystemExit("question files have problems; run `check`")
    qs = {q["uid"]: q for q in questions}
    answers = [r for r in load_jsonl(os.path.join(args.out, "answers.jsonl")) if not r.get("error")]
    gpath = os.path.join(args.out, "grades.jsonl")
    grades = {g["key"]: g for g in load_jsonl(gpath)}
    if args.sheet:
        return write_sheet(args.sheet, answers, grades, qs)
    if args.import_sheet:
        return import_sheet(args.import_sheet, grades, gpath)
    todo = [r for r in answers if r["key"] not in grades and r["uid"] in qs]
    errors = 0
    for i, r in enumerate(todo, 1):
        q = qs[r["uid"]]
        ok, n = cites_valid(r, q, root)
        g = {"key": r["key"], "judge": args.judge, "cites_valid": ok, "cites": n,
             "blinded": blind(r["answer"]) != (r["answer"] or "").strip()}   # identifiers removed from the text
        if r.get("not_stated"):
            g.update({"grade": "not_stated", "overreach": False, "reason": "the answer says the document does not give it"})
        else:
            blocks = [{"type": "text", "text": f"Question ({q['type']}): {q['question']}\n\n"
                       f"Reference answer: {q['answer']}\n" + (f"Author's note: {q['notes']}\n" if q["notes"] else "")
                       + f"\nAnswer to grade: {blind(r['answer'])}"}]
            try:
                out = PROVIDERS[args.provider](args.judge, JUDGE_SYSTEM, blocks, JUDGE_SCHEMA, args.effort)
                j = json.loads(out["text"])
                g.update({"grade": j["grade"], "overreach": bool(j["overreach"]), "reason": j["reason"]})
            except (RuntimeError, ValueError, KeyError) as e:
                errors += 1
                print(f"[{i}/{len(todo)}] {r['key']}: {e}", file=sys.stderr)
                continue
        append_jsonl(gpath, g)
    print(f"{len(todo) - errors} answers graded, {errors} errors")
    return 1 if errors else 0


SHEET = ["row", "question", "reference", "notes", "answer", "judge_grade", "judge_overreach", "judge_reason",
         "human_grade", "human_overreach"]


def write_sheet(path, answers, grades, qs):
    """A blinded sheet for checking the judge: no condition, model or cites; rows in random order."""
    rows = []
    for r in answers:
        g = grades.get(r["key"])
        if not g or r["uid"] not in qs:
            continue
        q = qs[r["uid"]]
        rows.append({"row": sha(r["key"])[:12], "question": q["question"], "reference": q["answer"],
                     "notes": q["notes"], "answer": blind(r["answer"]), "judge_grade": g["grade"],
                     "judge_overreach": g["overreach"], "judge_reason": g.get("reason", ""),
                     "human_grade": "", "human_overreach": ""})
    random.Random(0).shuffle(rows)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SHEET)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows written to {path}; fill human_grade ({', '.join(GRADES)}) and human_overreach "
          "(true/false) where you disagree, then run grade --import")
    return 0


def import_sheet(path, grades, gpath):
    by_row = {sha(k)[:12]: k for k in grades}
    changed = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            grade, over = row.get("human_grade", "").strip(), row.get("human_overreach", "").strip().lower()
            if not grade and not over:
                continue
            key = by_row.get(row["row"])
            if key is None:
                raise SystemExit(f"row {row['row']} is not in this run")
            if grade and grade not in GRADES:
                raise SystemExit(f"row {row['row']}: human_grade must be one of {', '.join(GRADES)}")
            human = {}
            if grade:
                human["grade"] = grade
            if over:
                human["overreach"] = over in ("true", "yes", "1")
            grades[key]["human"] = human
            changed += 1
    with open(gpath, "w", encoding="utf-8") as f:
        for g in grades.values():
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"{changed} human grades recorded")
    return 0


# ---------- report ----------

def score(q, grade):
    """1 for a right answer, 0.5 for a partial one; for an 'absent' question, 1 for saying it is not stated."""
    if q["type"] == "absent":
        return 1.0 if grade in ("not_stated", "correct") else 0.0
    return {"correct": 1.0, "partial": 0.5}.get(grade, 0.0)


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def rate(k, n):
    return {"k": k, "n": n, "rate": round(k / n, 3) if n else None, "ci95": wilson(k, n)}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.mean(xs), 3) if xs else None


def summary(rows):
    answerable = [r for r in rows if r["q"]["type"] != "absent"]
    absent = [r for r in rows if r["q"]["type"] == "absent"]
    scope = [r for r in rows if r["q"]["type"] == "scope"]
    cited = [r for r in rows if r["g"].get("cites")]
    return {
        "answers": len(rows),
        "correct": rate(sum(r["grade"] == "correct" for r in answerable), len(answerable)),
        "score": mean([r["score"] for r in answerable]),
        "said_not_stated_when_answerable": rate(sum(r["grade"] == "not_stated" for r in answerable), len(answerable)),
        "answered_absent_question": rate(sum(r["score"] == 0 for r in absent), len(absent)),
        "overreach_on_scope_questions": rate(sum(bool(r["overreach"]) for r in scope), len(scope)),
        "input_tokens": mean([r["a"].get("input_tokens") for r in rows]),
        "output_tokens": mean([r["a"].get("output_tokens") for r in rows]),
        "latency_s_median": round(statistics.median(r["a"]["latency_s"] for r in rows), 2) if rows else None,
        "answers_with_cites": rate(len(cited), len(rows)),
        "cites_valid": rate(sum(r["g"]["cites_valid"] for r in cited), sum(r["g"]["cites"] for r in cited)),
    }


def paired(rows, base, other, seed=1, n_boot=2000):
    """Other condition minus base, per question (mean over runs), with a bootstrap CI that resamples papers."""
    per = {}
    for r in rows:
        if r["condition"] in (base, other):
            per.setdefault((r["uid"], r["model"]), {}).setdefault(r["condition"], []).append(r)
    diffs = {}
    for (uid, model), by in per.items():
        if base in by and other in by:
            paper = "+".join(by[base][0]["q"]["papers"])
            d_score = statistics.mean(x["score"] for x in by[other]) - statistics.mean(x["score"] for x in by[base])
            ratio = (statistics.mean(x["a"]["input_tokens"] for x in by[other])
                     / statistics.mean(x["a"]["input_tokens"] for x in by[base]))
            diffs.setdefault(model, []).append((paper, d_score, ratio))
    out = {}
    for model, ds in sorted(diffs.items()):
        papers = sorted({p for p, _, _ in ds})
        by_paper = {p: [d for d in ds if d[0] == p] for p in papers}
        rng = random.Random(seed)
        boot = []
        for _ in range(n_boot):
            sample = [d for p in rng.choices(papers, k=len(papers)) for d in by_paper[p]]
            boot.append(statistics.mean(d[1] for d in sample))
        boot.sort()
        out[model] = {
            "questions": len(ds), "papers": len(papers),
            "score_difference": round(statistics.mean(d[1] for d in ds), 3),
            "ci95_by_paper": [round(boot[int(0.025 * n_boot)], 3), round(boot[int(0.975 * n_boot) - 1], 3)]
            if len(papers) > 1 else None,
            "input_token_ratio_geomean": round(math.exp(statistics.mean(math.log(d[2]) for d in ds)), 3),
            "per_paper_score_difference": {p: round(statistics.mean(d[1] for d in by_paper[p]), 3) for p in papers},
        }
    return out


def cmd_report(args, root=ROOT):
    questions, _ = load_questions(question_files(args.questions, root), root)
    qs = {q["uid"]: q for q in questions}
    grades = {g["key"]: g for g in load_jsonl(os.path.join(args.out, "grades.jsonl"))}
    rows, errors = [], 0
    for a in load_jsonl(os.path.join(args.out, "answers.jsonl")):
        if a.get("error"):
            errors += 1
            continue
        g = grades.get(a["key"])
        if not g or a["uid"] not in qs:
            continue
        grade, over = final_grade(g)
        q = qs[a["uid"]]
        rows.append({"a": a, "g": g, "q": q, "uid": a["uid"], "model": a["model"], "condition": a["condition"],
                     "grade": grade, "overreach": over, "score": score(q, grade)})
    rep = {"graded_answers": len(rows), "failed_calls": errors, "by_model_and_condition": {}, "by_type": {},
           "by_in_claimset": {}, "paired": {}}
    for model in sorted({r["model"] for r in rows}):
        for cond in CONDITIONS:
            sel = [r for r in rows if r["model"] == model and r["condition"] == cond]
            if sel:
                rep["by_model_and_condition"][f"{model} / {cond}"] = summary(sel)
                for t in TYPES:
                    st = [r for r in sel if r["q"]["type"] == t]
                    if st:
                        rep["by_type"][f"{model} / {cond} / {t}"] = {"answers": len(st), "score": mean([r["score"] for r in st])}
                for flag in (True, False):
                    st = [r for r in sel if r["q"]["in_claimset"] is flag and r["q"]["type"] != "absent"]
                    if st:
                        rep["by_in_claimset"][f"{model} / {cond} / in_claimset={str(flag).lower()}"] = {
                            "answers": len(st), "score": mean([r["score"] for r in st])}
    for other in ("claimset", "bundle"):
        p = paired(rows, "paper", other)
        if p:
            rep["paired"][f"{other} - paper"] = p
    with open(os.path.join(args.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    text = markdown(rep)
    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return 0


def fmt(r):
    if not r or r["rate"] is None:
        return "-"
    return f"{r['rate']:.2f} ({r['k']}/{r['n']})"


def markdown(rep):
    lines = [f"# Reading study report", "", f"{rep['graded_answers']} graded answers; {rep['failed_calls']} failed calls.",
             "", "| model / condition | answers | correct | score | not stated (answerable) | answered absent | "
             "overreach (scope) | input tokens | output tokens | latency s (median) | cites valid |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, s in rep["by_model_and_condition"].items():
        lines.append(f"| {k} | {s['answers']} | {fmt(s['correct'])} | {s['score']} | "
                     f"{fmt(s['said_not_stated_when_answerable'])} | {fmt(s['answered_absent_question'])} | "
                     f"{fmt(s['overreach_on_scope_questions'])} | {s['input_tokens']} | {s['output_tokens']} | "
                     f"{s['latency_s_median']} | {fmt(s['cites_valid'])} |")
    for name, p in rep["paired"].items():
        lines += ["", f"## {name}, per question", "", "| model | questions | papers | score difference | 95% CI (papers resampled) | input token ratio |",
                  "|---|---|---|---|---|---|"]
        for model, d in p.items():
            lines.append(f"| {model} | {d['questions']} | {d['papers']} | {d['score_difference']} | "
                         f"{d['ci95_by_paper'] or '-'} | {d['input_token_ratio_geomean']} |")
    if rep["by_in_claimset"]:
        lines += ["", "## Score by whether the claimset holds the answer", "", "| model / condition / in claimset | answers | score |", "|---|---|---|"]
        lines += [f"| {k} | {v['answers']} | {v['score']} |" for k, v in rep["by_in_claimset"].items()]
    lines += ["", "## Score by question type", "", "| model / condition / type | answers | score |", "|---|---|---|"]
    lines += [f"| {k} | {v['answers']} | {v['score']} |" for k, v in rep["by_type"].items()]
    return "\n".join(lines) + "\n"


# ---------- check ----------

def cmd_check(args, root=ROOT):
    files = question_files(args.questions, root)
    questions, problems = load_questions(files, root)
    print(f"{len(files)} question files, {len(questions)} questions")
    by = {}
    for q in questions:
        by.setdefault(q["file"], {}).setdefault(q["type"], 0)
        by[q["file"]][q["type"]] += 1
    for f, counts in by.items():
        print(f"  {f}: " + ", ".join(f"{t} {counts[t]}" for t in TYPES if t in counts))
    names = sorted({n for q in questions for n in q["papers"]})
    for name in names:
        if not (os.path.exists(claimset_path(name, root)) and os.path.exists(view_path(name, root))):
            continue
        try:
            r = subprocess.run(["claimset", "render", claimset_path(name, root)], capture_output=True, text=True)
        except FileNotFoundError:
            problems.append("the claimset package is not installed; cannot check the reading views")
            break
        if r.returncode:
            problems.append(f"{name}: claimset render failed: {r.stderr.strip()[:200]}")
        elif r.stdout.strip() != read(view_path(name, root)).strip():
            problems.append(f"{name}: the reading view is out of date; run claimset render")
    for p in problems:
        print("PROBLEM", p)
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--questions", nargs="*", help="question files (default: study/questions/*.json)")
    sub.add_parser("check", parents=[common], help="check question files and documents")
    run = sub.add_parser("run", parents=[common], help="put the questions to the models")
    run.add_argument("--out", required=True, help="run directory, e.g. study/runs/pilot-1")
    run.add_argument("--model", action="append", required=True, help="model id; repeat for several")
    run.add_argument("--conditions", nargs="+", default=list(CONDITIONS), choices=CONDITIONS)
    run.add_argument("--reps", type=int, default=3)
    run.add_argument("--effort", default="medium", choices=("low", "medium", "high", "xhigh", "max"))
    run.add_argument("--seed", type=int, default=1)
    run.add_argument("--provider", default="anthropic", choices=sorted(PROVIDERS))
    run.add_argument("--max-calls", type=int, help="stop after this many calls (a trial run)")
    run.add_argument("--dry-run", action="store_true", help="print the plan and token estimate; no calls")
    run.add_argument("--force", action="store_true", help="continue a run although its inputs changed")
    grade = sub.add_parser("grade", parents=[common], help="grade the answers blind against the reference answers")
    grade.add_argument("--out", required=True)
    grade.add_argument("--judge", default="claude-opus-5-5")
    grade.add_argument("--effort", default="medium", choices=("low", "medium", "high", "xhigh", "max"))
    grade.add_argument("--provider", default="anthropic", choices=sorted(PROVIDERS))
    grade.add_argument("--sheet", help="write a blinded CSV for checking the judge's grades")
    grade.add_argument("--import", dest="import_sheet", help="read human grades back from that CSV")
    report = sub.add_parser("report", parents=[common], help="summarise a graded run")
    report.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    return {"check": cmd_check, "run": cmd_run, "grade": cmd_grade, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
