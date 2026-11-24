"""claimset-vs-pdf, local models: put every per-paper question to open-weight models through Ollama, one question
per chat, in both conditions, and record the answer with Ollama's counts and times.

    python3 local_models.py sizes    --model qwen3.5:9b=false --model gpt-oss:20b=low --model gemma4:12b --num-ctx 40960
    python3 local_models.py practice --model ... --num-ctx 40960 --document invented.txt --question "..."
    python3 local_models.py run      --out DIR --model ... --num-ctx 40960 [--limit N]
    python3 local_models.py summary  --out DIR

A model is NAME or NAME=THINK, THINK one of false, true, low, medium, high: Ollama's `think` for that model
(omitted when not given). `sizes` and `practice` are for the practice run, before collection: `sizes` sends each
document alone (one token generated) to see whether it fits the context, `practice` sends an invented document
twice to check that the second call reads the whole prompt again (no cached prompt). `run` writes manifest.json
(settings, Ollama's version, each model's digest, every input file's SHA-256), calls.jsonl (the calls in their
random order) and replies.jsonl (one line per attempt); it resumes where it stopped, and tries a failed call once
more. `summary` writes
summary.csv: per model, paper and condition, the medians of Ollama's counts and times and the number of cut prompts.

Each call: a new chat of one user message, the document (the claimset's reading view or the PDF's pdftotext
text), a blank line, "I'm reading this paper." and the question; no system prompt. The model's own default
sampling settings, a fixed seed and context length, at most NUM_PREDICT generated tokens, and keep_alive 0, so
that Ollama unloads the model after each call and no cached prompt shortens the next call's reading.

Standard library only.
"""

import argparse
import csv
import hashlib
import json
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PAPERS = ("doi-10-1002-nav-22074", "doi-10-1007-s00180-023-01377-x", "doi-10-1016-j-ejor-2022-04-040",
          "doi-10-1093-imaman-dpad028", "doi-10-1111-jtsa-12843")
CONDITIONS = ("claimset", "pdf")
SEED = 20261120
NUM_PREDICT = 4096
MAX_ATTEMPTS = 2
OPENING = "I'm reading this paper."
THINK = {"false": False, "true": True, "low": "low", "medium": "medium", "high": "high"}
KEPT = ("done_reason", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration",
        "load_duration", "total_duration", "created_at")


def document_path(paper, condition):
    if condition == "claimset":
        return os.path.join(ROOT, "claimset", "pilot", paper + ".claimset.txt")
    return os.path.join(ROOT, "papers", "pdftotext", paper + ".txt")


def questions_path(paper):
    return os.path.join(ROOT, "study", "questions", paper + ".json")


def sha256(path):
    with open(path, "rb") as f:
        return "sha256:" + hashlib.sha256(f.read()).hexdigest()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def message(document, question):
    return document.rstrip("\n") + "\n\n" + OPENING + "\n" + question


def parse_model(text):
    name, _, think = text.partition("=")
    if think and think not in THINK:
        raise SystemExit(f"{text}: THINK must be one of {', '.join(THINK)}")
    return {"name": name, "think": think or None}


def is_cut(reply, num_ctx):
    """A prompt cut at the context limit, or an answer stopped by it: Ollama drops the start of a prompt longer
    than num_ctx without an error, so a prompt that fills the context is not the whole document."""
    used = (reply.get("prompt_eval_count") or 0) + (reply.get("eval_count") or 0)
    return used >= num_ctx or (reply.get("done_reason") == "length" and reply.get("eval_count", 0) < NUM_PREDICT)


class Ollama:
    def __init__(self, host, timeout=3600):
        self.host = (host if "://" in host else "http://" + host).rstrip("/")
        self.timeout = timeout

    def request(self, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.host + path, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            e.close()
            raise ValueError(f"HTTP {e.code} from Ollama: {detail}") from None

    def version(self):
        return self.request("/api/version").get("version")

    def digests(self):
        return {m["name"]: m.get("digest") for m in self.request("/api/tags").get("models", [])}

    def chat(self, model, content, num_ctx, num_predict=NUM_PREDICT):
        body = {"model": model["name"], "messages": [{"role": "user", "content": content}], "stream": False,
                "keep_alive": 0, "options": {"num_ctx": num_ctx, "seed": SEED, "num_predict": num_predict}}
        if model["think"] is not None:
            body["think"] = THINK[model["think"]]
        return self.request("/api/chat", body)


def plan_calls(models, seed=SEED):
    calls = []
    for paper in PAPERS:
        for q in json.loads(read(questions_path(paper)))["questions"]:
            for condition in CONDITIONS:
                for m in models:
                    calls.append({"model": m["name"], "paper": paper, "condition": condition,
                                  "question_id": q["id"], "type": q["type"]})
    random.Random(seed).shuffle(calls)
    for i, c in enumerate(calls, 1):
        c["call"] = i
    return calls


def manifest(client, models, num_ctx):
    digests = client.digests()
    missing = [m["name"] for m in models if m["name"] not in digests]
    if missing:
        raise SystemExit(f"not in Ollama: {', '.join(missing)} (ollama pull them first)")
    files = sorted({document_path(p, c) for p in PAPERS for c in CONDITIONS} | {questions_path(p) for p in PAPERS})
    return {"seed": SEED, "num_ctx": num_ctx, "num_predict": NUM_PREDICT, "keep_alive": 0, "opening": OPENING,
            "ollama_version": client.version(), "script": sha256(os.path.abspath(__file__)),
            "models": [dict(m, digest=digests[m["name"]]) for m in models],
            "files": {os.path.relpath(f, ROOT): sha256(f) for f in files}}


def run(args):
    os.makedirs(args.out, exist_ok=True)
    client, models = Ollama(args.host), [parse_model(m) for m in args.model]
    now = manifest(client, models, args.num_ctx)
    mpath, cpath, rpath = (os.path.join(args.out, n) for n in ("manifest.json", "calls.jsonl", "replies.jsonl"))
    if os.path.exists(mpath):
        before = json.loads(read(mpath))
        changed = [k for k in now if k != "ollama_version" and now[k] != before[k]]
        if changed:
            raise SystemExit(f"{mpath} differs in {', '.join(changed)}: resume only with the same settings and files")
        if now["ollama_version"] != before["ollama_version"]:
            print(f"warning: Ollama {before['ollama_version']} -> {now['ollama_version']}; recorded per reply",
                  file=sys.stderr)
    else:
        with open(mpath, "w") as f:
            json.dump(now, f, indent=1)
            f.write("\n")
        with open(cpath, "w") as f:
            for c in plan_calls(models):
                f.write(json.dumps(c) + "\n")
    calls = [json.loads(line) for line in read(cpath).splitlines()]
    attempts, answered = {}, set()
    for line in (read(rpath).splitlines() if os.path.exists(rpath) else []):
        r = json.loads(line)
        attempts[r["call"]] = attempts.get(r["call"], 0) + 1
        if "error" not in r:
            answered.add(r["call"])
    # A call that failed (Ollama's error, a timeout) is tried once more on a later run; its errors stay recorded.
    todo = [c for c in calls if c["call"] not in answered and attempts.get(c["call"], 0) < MAX_ATTEMPTS][: args.limit]
    model = {m["name"]: m for m in models}
    texts, questions = {}, {}
    for i, c in enumerate(todo, 1):
        key = (c["paper"], c["condition"])
        if key not in texts:
            texts[key] = read(document_path(*key))
        if c["paper"] not in questions:
            questions[c["paper"]] = {q["id"]: q["question"]
                                     for q in json.loads(read(questions_path(c["paper"])))["questions"]}
        started = time.time()
        try:
            reply = client.chat(model[c["model"]], message(texts[key], questions[c["paper"]][c["question_id"]]),
                                args.num_ctx)
            out = {k: reply.get(k) for k in KEPT}
            out.update(answer=reply.get("message", {}).get("content", ""),
                       thinking=reply.get("message", {}).get("thinking"), cut=is_cut(reply, args.num_ctx),
                       capped=reply.get("done_reason") == "length" and reply.get("eval_count", 0) >= NUM_PREDICT)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            out = {"error": f"{type(e).__name__}: {e}"}
        out.update(c, wall_seconds=round(time.time() - started, 3), ollama_version=now["ollama_version"])
        with open(rpath, "a") as f:
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
        print(f"{i}/{len(todo)} call {c['call']} {c['model']} {c['paper']} {c['condition']} {c['question_id']}"
              + (f" ERROR {out['error']}" if "error" in out else f" prompt {out['prompt_eval_count']}"
                 + (" CUT" if out["cut"] else "")), file=sys.stderr)


def summary(args):
    replies = [json.loads(line) for line in read(os.path.join(args.out, "replies.jsonl")).splitlines()]
    final = {}
    for r in replies:  # a call's last attempt stands for it
        final[r["call"]] = r
    groups = {}
    for r in final.values():
        groups.setdefault((r["model"], r["paper"], r["condition"]), []).append(r)
    fields = ("prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration")
    path = os.path.join(args.out, "summary.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "paper", "condition", "replies", "errors", "cut", "capped", "median prompt tokens",
                    "median prompt seconds", "median answer tokens", "median answer seconds"])
        for (model, paper, condition), rs in sorted(groups.items()):
            ok = [r for r in rs if "error" not in r]
            med = {k: statistics.median(r[k] for r in ok) if ok else None for k in fields}
            secs = (lambda ns: None if ns is None else round(ns / 1e9, 3))
            w.writerow([model, paper, condition, len(rs), len(rs) - len(ok), sum(r["cut"] for r in ok),
                        sum(r["capped"] for r in ok),
                        med["prompt_eval_count"], secs(med["prompt_eval_duration"]), med["eval_count"],
                        secs(med["eval_duration"])])
    print(path)


def sizes(args):
    """Each document alone, one token generated: its prompt tokens against the context length."""
    client = Ollama(args.host)
    for m in map(parse_model, args.model):
        for paper in PAPERS:
            for condition in CONDITIONS:
                r = client.chat(m, message(read(document_path(paper, condition)), ""), args.num_ctx, num_predict=1)
                n = r.get("prompt_eval_count")
                print(f"{m['name']}\t{paper}\t{condition}\t{n}\t{'FITS' if n < args.num_ctx - NUM_PREDICT else 'TOO LONG'}")


def practice(args):
    """The invented document and question twice per model: both calls should read the whole prompt."""
    client, document = Ollama(args.host), read(args.document)
    for m in map(parse_model, args.model):
        for attempt in (1, 2):
            r = client.chat(m, message(document, args.question), args.num_ctx)
            print(json.dumps({"model": m["name"], "attempt": attempt, **{k: r.get(k) for k in KEPT},
                              "answer": r.get("message", {}).get("content", "")}, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("sizes", "practice", "run", "summary"):
        s = sub.add_parser(name)
        if name != "summary":
            s.add_argument("--model", action="append", required=True)
            s.add_argument("--num-ctx", type=int, required=True)
            s.add_argument("--host", default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
        if name in ("run", "summary"):
            s.add_argument("--out", required=True)
        if name == "run":
            s.add_argument("--limit", type=int)
        if name == "practice":
            s.add_argument("--document", required=True)
            s.add_argument("--question", required=True)
    args = p.parse_args(argv)
    {"sizes": sizes, "practice": practice, "run": run, "summary": summary}[args.command](args)


if __name__ == "__main__":
    main()
