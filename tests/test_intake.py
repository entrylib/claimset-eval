import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "claimset-code", "claimset-vs-pdf"))
sys.path.insert(0, os.path.dirname(__file__))
import intake  # noqa: E402
import randomise as rz  # noqa: E402
from test_transcript import page, transcript_text  # noqa: E402


class IntakeTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d)
        key, packs = rz.draw()
        rz.write(self.d, key, packs)
        self.key = key
        self.codes = [p["code"] for p in packs if p["configuration"] == "kimi-fast"]
        self.packs = {p["code"]: p for p in packs}
        self.pages = os.path.join(self.d, "pages")
        os.makedirs(self.pages)

    def save(self, code, drop=None):
        msgs = [m["text"] for m in self.packs[code]["messages"]]
        replies = [f"Reply number {i} to the question." for i in range(1, len(msgs) + 1)]
        shown, sent = list(replies), list(msgs)
        if drop:
            msgs, replies = msgs[:drop - 1] + msgs[drop:], replies[:drop - 1] + replies[drop:]
        with open(os.path.join(self.pages, code + ".mhtml"), "wb") as f:
            f.write(page(shown, transcript_text(msgs, replies), messages=sent))

    def run_intake(self, fills=None):
        out = os.path.join(self.d, "out")
        args = ["--key", os.path.join(self.d, "key.json"), "--packs", os.path.join(self.d, "packs"),
                "--configuration", "kimi-fast", "--pages", self.pages, "--all", "--out", out]
        if fills:
            fp = os.path.join(self.d, "fills.json")
            json.dump(fills, open(fp, "w"))
            args += ["--fills", fp]
        return intake.main(args), json.load(open(os.path.join(out, "intake.json"))), out

    def test_all_chats_pass_and_pages_are_hashed_not_kept(self):
        for c in self.codes:
            self.save(c)
        status, report, out = self.run_intake()
        self.assertEqual(status, 0)
        self.assertTrue(report["passed"])
        chat = json.load(open(os.path.join(out, "chats", self.codes[0] + ".json")))
        self.assertEqual(chat["page"]["file"], self.codes[0] + ".mhtml")
        self.assertTrue(chat["page"]["hash"].startswith("sha256:"))
        self.assertFalse(any(f.endswith(".mhtml") for f in os.listdir(out)))

    def test_a_missing_page_or_turn_fails_and_a_fill_mends_the_turn(self):
        for c in self.codes[1:]:
            self.save(c)
        status, report, _ = self.run_intake()
        self.assertEqual(status, 1)
        self.assertIn(f"no page for {self.codes[0]}", report["problems"])
        self.save(self.codes[0], drop=7)
        status, report, _ = self.run_intake()
        self.assertFalse(report["chats"][self.codes[0]]["passed"])
        status, report, _ = self.run_intake({self.codes[0]: {"7": {"reply": "Reply number 7 to the question.", "why": "left out"}}})
        self.assertEqual(status, 0, report["chats"][self.codes[0]])
        self.assertEqual(report["chats"][self.codes[0]]["filled"], [7])

    def test_a_page_of_another_configuration_fails(self):
        for c in self.codes:
            self.save(c)
        other = next(c for c in self.key if self.key[c]["configuration"] != "kimi-fast")
        shutil.copy(os.path.join(self.pages, self.codes[0] + ".mhtml"), os.path.join(self.pages, other + ".mhtml"))
        status, report, _ = self.run_intake()
        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
