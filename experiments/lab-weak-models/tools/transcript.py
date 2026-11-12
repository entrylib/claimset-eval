"""Summarise an agent transcript (Claude Code subagent JSONL): tokens, tool calls, commands, errors and refusals.

python3 transcript.py RUN.jsonl [--commands FILE.md] [--json FILE.json]
Standard library only.
"""
import argparse, json, re, sys
from collections import Counter

REFUSAL = re.compile(r"\b(?:refused|refuses|REFUSED)\b|\bL(?:[1-9]|[12]\d|30)\b[:)]|\bERROR\b|\berror\(s\)|rule \d+")
LRULE = re.compile(r"\b(L(?:[1-9]|[12]\d|30))\b")


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for c in content or []:
        if isinstance(c, dict):
            if c.get("type") == "text":
                out.append(c.get("text", ""))
            elif c.get("type") == "tool_result":
                out.append(text_of(c.get("content")))
    return "\n".join(out)


def summarise(path):
    usage = Counter()
    tools = Counter()
    models = Counter()
    calls = {}
    commands = []
    errors = []
    first = last = None
    for line in open(path):
        o = json.loads(line)
        ts = o.get("timestamp")
        if ts:
            first = first or ts
            last = ts
        m = o.get("message") or {}
        if o.get("type") == "assistant":
            models[m.get("model")] += 1
            u = m.get("usage") or {}
            for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
                usage[k] += u.get(k) or 0
            for c in m.get("content") or []:
                if c.get("type") == "tool_use":
                    tools[c["name"]] += 1
                    calls[c["id"]] = (c["name"], c.get("input") or {})
                    inp = c.get("input") or {}
                    if c["name"] == "Bash":
                        commands.append({"ts": ts, "tool": "Bash", "text": inp.get("command", "")})
                    elif c["name"] in ("Write", "Edit", "Read"):
                        commands.append({"ts": ts, "tool": c["name"], "text": inp.get("file_path", "")})
                    else:
                        commands.append({"ts": ts, "tool": c["name"], "text": json.dumps(inp)[:300]})
        elif o.get("type") == "user":
            for c in m.get("content") or [] if isinstance(m.get("content"), list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    t = text_of(c.get("content"))
                    name, inp = calls.get(c.get("tool_use_id"), ("?", {}))
                    if c.get("is_error") or (name == "Bash" and REFUSAL.search(t)):
                        errors.append({"ts": ts, "tool": name, "is_error": bool(c.get("is_error")),
                                       "input": (inp.get("command") or inp.get("file_path") or "")[:400],
                                       "rules": sorted(set(LRULE.findall(t))), "output": t[-1500:]})
    return {"first": first, "last": last, "models": dict(models), "usage": dict(usage),
            "total_tokens": sum(usage.values()), "tools": dict(tools), "n_commands": len(commands),
            "commands": commands, "errors": errors}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--commands")
    ap.add_argument("--json")
    a = ap.parse_args()
    s = summarise(a.transcript)
    if a.commands:
        with open(a.commands, "w") as f:
            f.write(f"# Tool calls ({s['n_commands']})\n\n")
            for i, c in enumerate(s["commands"], 1):
                f.write(f"{i}. `{c['ts']}` **{c['tool']}**\n\n```\n{c['text']}\n```\n\n")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({k: v for k, v in s.items() if k != "commands"}, f, indent=1)
    print(json.dumps({k: s[k] for k in ("first", "last", "models", "usage", "total_tokens", "tools", "n_commands")}))
    print(f"errors/refusal candidates: {len(s['errors'])}")


if __name__ == "__main__":
    main()
