import json
import os
import sys
import tempfile
import unittest
from email.message import EmailMessage
from html import escape

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "claimset-code", "claimset-vs-pdf"))
import transcript as tr  # noqa: E402

EXPECTED = ["I'm reading this paper. What MASE did HWS reach?", "Which software was used?",
            "Where did the information in your answers come from?"]
REPLIES = ["HWS reached a mean MASE of **0.812**, against 0.861 for ETS.\n\n| Method | MASE |\n|---|---:|\n| HWS | 0.812 |",
           "The paper does not say which software was used.",
           "Everything came from the PDF you uploaded, [file: paper.pdf] apart from my own arithmetic."]


def transcript_text(expected=EXPECTED, replies=REPLIES):
    out = []
    for i, (u, a) in enumerate(zip(expected, replies), 1):
        out += [f"### User {i}", u, "", f"### Assistant {i}", a, ""]
    return "\n".join(out)


def page(shown_replies, code, mhtml=True):
    """A saved chat page: the replies as displayed (the last ones only, as ChatGPT keeps), then the transcript
    in a code block; wrapped in MHTML like Chrome's 'Webpage, Single File'."""
    body = "".join(f'<div data-role="assistant"><p>{escape(r).replace("**", "")}</p>'
                   f'<span class="chip">paper.pdf</span></div>' for r in shown_replies)
    body += f'<div data-role="assistant"><pre><div>markdown</div><code>{escape(code)}</code></pre></div>'
    html = f"<!DOCTYPE html><html><body><nav>Other chat title</nav>{body}<script>var x=1;</script></body></html>"
    if not mhtml:
        return html.encode()
    m = EmailMessage()
    m.set_content(html, subtype="html", cte="quoted-printable")
    m.add_related("body{}", subtype="css")
    return m.as_bytes()


class TranscriptTest(unittest.TestCase):
    def write(self, data, suffix=".mhtml"):
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        f.write(data)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def run_check(self, data, expected=EXPECTED, suffix=".mhtml"):
        return tr.check(self.write(data, suffix), expected, tail=2)

    def test_faithful_transcript_passes_and_gives_turns(self):
        r = self.run_check(page(REPLIES[1:], transcript_text()))
        self.assertEqual(r["problems"], [])
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual([t["n"] for t in r["turns"]], [1, 2, 3])
        self.assertEqual(r["turns"][1]["assistant"], REPLIES[1])
        self.assertIn("| HWS | 0.812 |", r["turns"][0]["assistant"])

    def test_plain_html_page_works_too(self):
        r = self.run_check(page(REPLIES[1:], transcript_text(), mhtml=False), suffix=".html")
        self.assertTrue(all(r["checks"].values()))

    def test_a_changed_word_in_the_tail_fails(self):
        changed = REPLIES[:2] + [REPLIES[2].replace("own arithmetic", "own reading")]
        r = self.run_check(page(REPLIES[1:], transcript_text(replies=changed)))
        self.assertFalse(r["checks"]["tail"])
        self.assertTrue(any("reading" in p for p in r["problems"]))

    def test_tables_formatting_and_file_chips_do_not_fail_the_tail(self):
        r = self.run_check(page(REPLIES, transcript_text()), expected=EXPECTED)
        self.assertTrue(r["checks"]["tail"])
        r = tr.check(self.write(page(REPLIES, transcript_text())), EXPECTED, tail=3)
        self.assertTrue(r["checks"]["tail"], r["problems"])

    def test_a_reworded_message_fails(self):
        r = self.run_check(page(REPLIES[1:], transcript_text(expected=[EXPECTED[0], "Which software did they use?",
                                                                        EXPECTED[2]])))
        self.assertFalse(r["checks"]["users"])
        self.assertIn("User 2 differs from the message sent", r["problems"])

    def test_a_missing_turn_fails(self):
        r = self.run_check(page(REPLIES[1:], transcript_text(EXPECTED[:2], REPLIES[:2])))
        self.assertFalse(r["checks"]["complete"])
        self.assertFalse(r["checks"]["users"])

    def test_headings_inside_a_reply_do_not_split_it(self):
        replies = REPLIES[:2] + ["### Sources\nEverything came from the PDF you uploaded."]
        r = self.run_check(page(replies[1:], transcript_text(replies=replies)))
        self.assertTrue(r["checks"]["complete"], r["problems"])
        self.assertIn("### Sources", r["turns"][2]["assistant"])

    def test_no_transcript_fails(self):
        r = self.run_check(page(REPLIES, "print('hello')"))
        self.assertIn("no transcript", r["problems"][0])

    def test_cli_writes_the_chat_and_exit_status(self):
        expected = self.write(json.dumps(EXPECTED).encode(), ".json")
        out = self.write(b"", ".json")
        good = self.write(page(REPLIES[1:], transcript_text()))
        self.assertEqual(tr.main(["check", good, "--expected", expected, "--out", out]), 0)
        self.assertTrue(json.load(open(out))["passed"])
        bad = self.write(page(REPLIES[1:], transcript_text(replies=REPLIES[:2] + ["Something else entirely."])))
        self.assertEqual(tr.main(["check", bad, "--expected", expected, "--out", out]), 1)

    def test_expected_messages_of_a_practice_chat(self):
        q = os.path.join(os.path.dirname(__file__), "..", "study", "practice", "practice-questions.json")
        a = tr.expected_practice(q, "A")
        self.assertEqual(len(a), 11)
        self.assertTrue(a[0].startswith("I'm reading this paper. Please keep your answers short"))
        self.assertEqual(tr.expected_practice(q, "M"), ["Do you remember anything from our earlier chats?"])

    def test_request_is_saved_in_the_practice_questions(self):
        q = os.path.join(os.path.dirname(__file__), "..", "study", "practice", "practice-questions.json")
        self.assertEqual(json.load(open(q))["transcript"], tr.TRANSCRIPT_REQUEST)

    def test_every_practice_prompt_ends_its_chats_with_the_request_verbatim(self):
        d = os.path.join(os.path.dirname(__file__), "..", "study", "practice")
        for name in ("gemini-agent-prompt.md", "chatgpt-agent-prompt.md"):
            text = open(os.path.join(d, name)).read()
            self.assertIn("T: " + tr.TRANSCRIPT_REQUEST + "\n", text, name)


if __name__ == "__main__":
    unittest.main()
