"""claimset-vs-pdf: take in one configuration's 12 saved chat pages and write their checked transcripts.

    python3 intake.py --key RN/key.json --packs RN/packs --configuration kimi-fast --pages DIR
                      [--fills study/collection/fills.json] [--tail 2] [--all] [--out DIR]

DIR (pages) holds <code>.mhtml (or .html) for every chat of the configuration, and <code>.md where the transcript
was copied from the page (Qwen). Each chat is checked with transcript.check against the messages its pack says were
sent. fills.json ({code: {n: {"reply": ..., "why": ...}}}) puts back turns an app left out of its transcript though
its page shows them; each filled message and reply must be found on the page. --all also compares every reply with
the page (apps whose page holds the whole chat) and reports the words not found, reply by reply.

Writes, to --out (default $CLAIMSET_RUN_DIR):

    chats/<code>.json   the chat: code, the page's file name and sha256 (the page is not kept: it holds the titles
                        of the account's other chats), the checks, problems, filled turns and the turns
    intake.json         per chat: passed, checks, turns, filled, not-on-page, reply comparison counts

Exit status 0 only if the pages are exactly the configuration's chats and every chat passed. Standard library only.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcript as tr  # noqa: E402


def sha256(path):
    with open(path, "rb") as f:
        return "sha256:" + hashlib.sha256(f.read()).hexdigest()


def find_page(pages, code):
    for ext in (".mhtml", ".html"):
        p = os.path.join(pages, code + ext)
        if os.path.exists(p):
            return p
    return None


def intake(key, packs, configuration, pages, fills=None, tail=2, compare_all=False):
    """[(code, chat)] for the configuration's chats in collection order, and a list of problems with the set."""
    fills = fills or {}
    codes = sorted((c for c, k in key.items() if k["configuration"] == configuration),
                   key=lambda c: (key[c]["pair"], key[c]["position"]))
    problems = []
    seen = {os.path.splitext(f)[0] for f in os.listdir(pages) if f.endswith((".mhtml", ".html"))}
    for extra in sorted(seen - set(codes)):
        problems.append(f"page {extra} is not a chat of {configuration}")
    out = []
    for code in codes:
        page = find_page(pages, code)
        if page is None:
            problems.append(f"no page for {code}")
            continue
        with open(os.path.join(packs, code + ".json"), encoding="utf-8") as f:
            expected = [m["text"] for m in json.load(f)["messages"]]
        md = os.path.join(pages, code + ".md")
        fill = {int(n): x["reply"] for n, x in fills.get(code, {}).items()}
        r = tr.check(page, expected, tail, md if os.path.exists(md) else None, fill or None, compare_all)
        r["passed"] = bool(r["checks"]) and all(r["checks"].values()) and not r["problems"]
        r["page"] = {"file": os.path.basename(page), "hash": sha256(page)}
        if os.path.exists(md):
            r["transcript_file"] = {"file": os.path.basename(md), "hash": sha256(md)}
        out.append((code, dict({"code": code}, **r)))
    return out, problems


def summary(chat):
    keep = ("passed", "checks", "problems", "filled", "not_on_page", "tail", "all_replies", "injected_turns",
            "dropped_request", "page")
    return dict({"turns": len(chat["turns"])}, **{k: chat[k] for k in keep if k in chat})


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--key", required=True)
    p.add_argument("--packs", required=True)
    p.add_argument("--configuration", required=True)
    p.add_argument("--pages", required=True)
    p.add_argument("--fills")
    p.add_argument("--tail", type=int, default=2)
    p.add_argument("--all", action="store_true")
    p.add_argument("--out", default=os.environ.get("CLAIMSET_RUN_DIR"))
    args = p.parse_args(argv)
    if not args.out:
        p.error("--out or $CLAIMSET_RUN_DIR is needed")
    key = json.load(open(args.key, encoding="utf-8"))
    fills = json.load(open(args.fills, encoding="utf-8")) if args.fills else {}
    chats, problems = intake(key, args.packs, args.configuration, args.pages, fills, args.tail, args.all)
    os.makedirs(os.path.join(args.out, "chats"), exist_ok=True)
    for code, chat in chats:
        with open(os.path.join(args.out, "chats", code + ".json"), "w", encoding="utf-8") as f:
            json.dump(chat, f, ensure_ascii=False, indent=1)
            f.write("\n")
    report = {"configuration": args.configuration, "problems": problems,
              "chats": {code: summary(chat) for code, chat in chats}}
    report["passed"] = not problems and len(chats) == 12 and all(c["passed"] for _, c in chats)
    with open(os.path.join(args.out, "intake.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for code, chat in chats:
        print(f"{code}: {'PASSED' if chat['passed'] else 'FAILED'}, {len(chat['turns'])} turns"
              + (f", filled {chat['filled']}" if chat.get("filled") else "")
              + (f", replies with words not found on the page {[n for n, k in chat['all_replies'].items() if k]}"
                 if chat.get("all_replies") else ""))
        for x in chat["problems"]:
            print("  " + x)
    for x in problems:
        print(x)
    print("ALL PASSED" if report["passed"] else "NOT ALL PASSED")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
