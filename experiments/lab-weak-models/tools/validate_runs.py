"""List every `claimset validate` (and export/package validator summary) in a transcript, with its outcome line.

python3 validate_runs.py RUN.jsonl. Standard library only.
"""
import json, re, sys

SUMMARY = re.compile(r"(?:IN)?VALID submission: \d+ error\(s\), \d+ warning\(s\)|Validator: \d+ error\(s\), \d+ warning\(s\)")
ERR = re.compile(r"ERROR\s+\[rule \d+\][^\n]{0,140}")


def main(path):
    calls = {}
    n = 0
    for line in open(path):
        o = json.loads(line)
        m = o.get("message") or {}
        if o.get("type") == "assistant":
            for c in m.get("content") or []:
                if c.get("type") == "tool_use" and c["name"].lower() == "bash":
                    calls[c["id"]] = c["input"].get("command", "")
        elif o.get("type") == "user" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in calls:
                    cmd = calls[c["tool_use_id"]]
                    content = c.get("content")
                    text = content if isinstance(content, str) else "\n".join(x.get("text", "") for x in content or [] if isinstance(x, dict))
                    sums = SUMMARY.findall(text)
                    if "validate" in cmd or "export" in cmd or "package" in cmd or sums:
                        if not sums:
                            continue
                        n += 1
                        errs = sorted(set(ERR.findall(text)))
                        print(f"{n}. {o.get('timestamp')} {' | '.join(sums)}")
                        for e in errs:
                            print(f"     {e}")
    print(f"total validator outcomes: {n}")


if __name__ == "__main__":
    main(sys.argv[1])
