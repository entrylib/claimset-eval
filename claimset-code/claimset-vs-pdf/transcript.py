"""claimset-vs-pdf: take a chat out of a saved chat page by the transcript the app was asked for, and check it.

Each chat ends with the message TRANSCRIPT_REQUEST below, typed verbatim after the last question. The app answers
with the whole conversation in one code block. The supervisor saves the page (Chrome: Ctrl+S, "Webpage, Single
File", .mhtml), which holds the transcript and, as the app displays them, the last few original replies. This
script finds the transcript in the page and checks it three ways:

    users     every message of the chat, in order, word for word as sent (the expected messages are given);
    complete  the turns numbered 1..N without gaps, one reply per message, the code block closed;
    tail      the last replies before the request (F2 and F3, say) are found in the page as displayed, every word
              and number in order (markdown, punctuation and spacing aside): the transcript copied what the app
              showed. The page holds only the last few replies, so the earlier ones are trusted because the
              messages and the tail match.

    python3 transcript.py check PAGE.mhtml --expected MESSAGES.json [--tail 2] [--out CHAT.json]
    python3 transcript.py expected --questions study/practice/practice-questions.json --chat A -o MESSAGES.json

MESSAGES.json is a list of the chat's messages as sent, the transcript request excluded. CHAT.json gets the turns
({n, user, assistant}) and the checks; the exit status is 0 only if every check passed. The page holds personal
data (the titles of the account's other chats): keep pages out of the repository, keep only CHAT.json.

Standard library only.
"""

import argparse
import difflib
import email
import json
import re
import sys
from email import policy
from html.parser import HTMLParser

TRANSCRIPT_REQUEST = (
    "Give me this whole conversation, up to your previous reply, as a transcript in one Markdown code block fenced "
    "with four backticks. Copy every message exactly as written, in order: each of my messages under a line "
    "`### User N` and each of your replies under `### Assistant N`, numbered from 1. Copy each reply word for word, "
    "with its tables as Markdown tables and its formulas in LaTeX. Do not shorten, correct, rephrase or summarise "
    "anything, and add nothing. Write a reference to an attached file as `[file: name]`. Write nothing outside the "
    "code block.")
HEADING = re.compile(r"^#{2,4} (User|Assistant) (\d+)\s*$", re.M)
FILE_REF = re.compile(r"\[file:[^\]]*\]")


def page_html(path):
    """The HTML of a saved page: the text/html part of an .mhtml file, or an .html file as it is."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw.lstrip()[:5].lower() in (b"<!doc", b"<html"):
        return raw.decode("utf-8", "replace")
    msg = email.message_from_bytes(raw, policy=policy.default)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
    raise ValueError(f"{path}: no HTML in the saved page")


class Page(HTMLParser):
    """Collects the text of every <code> element, and the page's visible text without them."""

    BLOCK = {"p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "br", "pre", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.codes, self.text, self.skip, self.code = [], [], 0, None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg", "template"):
            self.skip += 1
        elif tag == "code" and self.code is None and not self.skip:
            self.code, self.depth = [], 0
        elif tag == "code" and self.code is not None:
            self.depth += 1
        if tag in self.BLOCK:
            (self.code if self.code is not None else self.text).append("\n")
        elif tag in ("span", "button", "a") and self.code is None:
            self.text.append(" ")  # a file chip or link next to the text is a word of its own

    def handle_endtag(self, tag):
        if tag in self.BLOCK and self.code is None:
            self.text.append("\n")
        if tag in ("script", "style", "svg", "template"):
            self.skip = max(0, self.skip - 1)
        elif tag == "code" and self.code is not None:
            if self.depth:
                self.depth -= 1
            else:
                self.codes.append("".join(self.code))
                self.code = None

    def handle_data(self, data):
        if self.skip:
            return
        (self.code if self.code is not None else self.text).append(data)


def parse_page(path):
    p = Page()
    p.feed(page_html(path))
    return p.codes, "".join(p.text)


def find_transcript(codes):
    """The last code block that holds the transcript's first headings."""
    hits = [c for c in codes if re.search(r"^#{2,4} User 1\s*$", c, re.M) and re.search(r"^#{2,4} Assistant 1\s*$", c, re.M)]
    return hits[-1] if hits else None


def split_turns(text):
    """[(role, n, body)] in order, cut at the numbered headings only (replies may have headings of their own)."""
    marks = list(HEADING.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1).lower(), int(m.group(2)), text[m.end():end].strip("\n")))
    return out


def words(text):
    """Words for comparing a reply with the page: markdown, LaTeX delimiters and file references dropped."""
    text = FILE_REF.sub(" ", text)
    text = re.sub(r"[*_`#>|]|^\s*[-+]\s|^\s*\d+\.\s|-{3,}|:?-{3,}:?|\$+", " ", text, flags=re.M)
    return re.findall(r"[^\W_]+(?:[.,'’][^\W_]+)*|[^\w\s]", text)


def not_found(reply, page_words):
    """The words and numbers of a reply that do not appear, in order, in the page (punctuation is not counted:
    tables and formulas are displayed with other punctuation than their markdown)."""
    r = words(reply)
    m = difflib.SequenceMatcher(None, r, page_words, autojunk=False)
    got = {k for b in m.get_matching_blocks() for k in range(b.a, b.a + b.size)}
    return [w for k, w in enumerate(r) if k not in got and re.search(r"\w", w)]


def norm(text):
    return re.sub(r"\s+", " ", FILE_REF.sub(" ", text)).strip()


def check(page, expected, tail=2):
    codes, shown = parse_page(page)
    result = {"page": page, "checks": {}, "problems": [], "turns": []}
    found = find_transcript(codes)
    if found is None:
        result["problems"].append("no transcript code block (### User 1 ... ### Assistant 1) in the page")
        return result
    turns = split_turns(found)
    users = [(n, b) for r, n, b in turns if r == "user"]
    replies = {n: b for r, n, b in turns if r == "assistant"}
    order = [(r, n) for r, n, _ in turns]
    want = [x for i in range(1, len(expected) + 1) for x in (("user", i), ("assistant", i))]
    complete = order == want and all(replies[n].strip() for n in replies)
    result["checks"]["complete"] = complete
    if not complete:
        result["problems"].append(f"turns {order[:6]}... do not run User 1, Assistant 1, ... to {len(expected)}"
                                  if order != want else "an empty reply")
    bad = [n for n, b in users if n > len(expected) or norm(b) != norm(expected[n - 1])]
    missing = len(expected) - len(users)
    result["checks"]["users"] = not bad and missing == 0
    for n in bad:
        result["problems"].append(f"User {n} differs from the message sent")
    if missing > 0:
        result["problems"].append(f"{missing} message(s) missing")
    page_words = words(shown)
    last = sorted(replies)[-tail:] if replies else []
    missing_words = {n: not_found(replies[n], page_words) for n in last}
    result["checks"]["tail"] = bool(last) and not any(missing_words.values())
    result["tail"] = {n: len(w) for n, w in missing_words.items()}
    for n, w in missing_words.items():
        if w:
            result["problems"].append(f"Assistant {n}: {len(w)} word(s) not found in the page as displayed: {' '.join(w[:12])}")
    result["turns"] = [{"n": n, "user": b, "assistant": replies.get(n, "")} for n, b in users]
    return result


def expected_practice(questions, chat):
    """The messages of a practice chat (A, B: per-paper; M: memory; X: cross), as practice-questions.json gives them."""
    q = json.load(open(questions))
    per = [x["question"] for x in q["per_paper"]]
    follow = [x["question"] for x in q["follow_ups"]]
    if chat in ("A", "B"):
        return [q["opening"] + " " + per[0]] + per[1:] + follow
    if chat == "M":
        return [q["memory_check"]]
    cross = [x["question"] for x in q["cross"]]
    return [q["opening_cross"] + " " + cross[0]] + cross[1:]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check")
    c.add_argument("page")
    c.add_argument("--expected", required=True, help="JSON list of the chat's messages as sent")
    c.add_argument("--tail", type=int, default=2)
    c.add_argument("--out")
    e = sub.add_parser("expected")
    e.add_argument("--questions", required=True)
    e.add_argument("--chat", required=True, choices=("A", "B", "M", "X"))
    e.add_argument("-o", "--output", required=True)
    args = p.parse_args(argv)
    if args.command == "expected":
        with open(args.output, "w") as f:
            json.dump(expected_practice(args.questions, args.chat), f, ensure_ascii=False, indent=1)
        return 0
    result = check(args.page, json.load(open(args.expected)), args.tail)
    ok = bool(result["checks"]) and all(result["checks"].values()) and not result["problems"]
    result["passed"] = ok
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print(("PASSED" if ok else "FAILED") + f": {len(result['turns'])} turns; checks {result['checks']}; "
          f"words not found in the tail {result.get('tail')}")
    for x in result["problems"]:
        print("  " + x)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
