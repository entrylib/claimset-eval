import collections
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "claimset-code", "claimset-vs-pdf"))
import randomise as rz  # noqa: E402
import transcript as tr  # noqa: E402


class RandomiseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key, cls.packs = rz.draw()

    def test_design_counts(self):
        self.assertEqual(len(self.packs), 120)
        per = collections.Counter(p["configuration"] for p in self.packs)
        self.assertEqual(set(per.values()), {12})
        # 274 messages per configuration: 226 questions, 36 follow-ups, 12 transcript requests
        for name in per:
            mine = [p for p in self.packs if p["configuration"] == name]
            self.assertEqual(sum(len(p["messages"]) + 1 for p in mine), 274)
            self.assertEqual(collections.Counter((p["paper"], p["condition"]) for p in mine),
                             collections.Counter({(x, c): 1 for x in list(rz.PAPERS) + ["cross"] for c in rz.CONDITIONS}))

    def test_each_pair_has_both_conditions_back_to_back(self):
        for name in {p["configuration"] for p in self.packs}:
            mine = sorted((p for p in self.packs if p["configuration"] == name), key=lambda p: (p["pair"], p["position"]))
            for a, b in zip(mine[::2], mine[1::2]):
                self.assertEqual(a["paper"], b["paper"])
                self.assertEqual({a["condition"], b["condition"]}, set(rz.CONDITIONS))

    def test_messages_are_every_question_once_then_the_follow_ups(self):
        q = rz.load_questions()
        for p in self.packs:
            ids = [m["id"] for m in p["messages"]]
            self.assertEqual(ids[-3:], ["F1", "F2", "F3"])
            self.assertEqual(sorted(ids[:-3]), sorted(x["id"] for x in q[p["paper"]]))
            opening = rz.OPENING_CROSS if p["paper"] == "cross" else rz.OPENING
            self.assertTrue(p["messages"][0]["text"].startswith(opening + " "))

    def test_files_are_named_by_short_title_and_condition(self):
        for p in self.packs:
            self.assertTrue(all(f.endswith(rz.EXT[p["condition"]]) for f in p["files"]))
            self.assertEqual(len(p["files"]), 5 if p["paper"] == "cross" else 1)
            for f in p["files"]:
                self.assertTrue(os.path.exists(os.path.join(rz.ROOT, "study", "attachments", f)), f)

    def test_codes_are_unique_and_the_draw_is_fixed_by_the_seed(self):
        self.assertEqual(len(self.key), 120)
        self.assertEqual(rz.draw()[0], self.key)
        self.assertNotEqual(rz.draw(1)[0], self.key)
        self.assertTrue(all(set(c) <= set(rz.CODE_LETTERS) and len(c) == 4 for c in self.key))

    def test_codes_avoid_earlier_draws_and_orders_follow_the_seed(self):
        used = set(list(self.key)[:30])
        key, packs = rz.draw(used=used)
        self.assertFalse(used & set(key))
        self.assertEqual([p["messages"] for p in packs], [p["messages"] for p in self.packs])

    def test_kimi_fast_is_collected_first_and_deepseek_is_gone(self):
        self.assertEqual([c["name"] for c in rz.CONFIGS[:5]],
                         ["kimi-fast", "grok-fast", "chatgpt-fast", "gemini-fast", "qwen-fast"])
        self.assertFalse(any(c["app"] == "DeepSeek" for c in rz.CONFIGS))

    def test_qwen_prompts_ask_for_the_copied_transcript(self):
        out = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out)
        rz.write(out, self.key, self.packs)
        qwen = open(os.path.join(out, "prompts", "5-qwen-fast.md"), encoding="utf-8").read()
        self.assertIn("Click Copy on the transcript's code block", qwen)
        kimi = open(os.path.join(out, "prompts", "1-kimi-fast.md"), encoding="utf-8").read()
        self.assertNotIn("Click Copy", kimi)

    def test_written_prompts_hold_every_message_and_the_request(self):
        out = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out)
        rz.write(out, self.key, self.packs)
        first = open(os.path.join(out, "prompts", "1-kimi-fast.md"), encoding="utf-8").read()
        mine = [p for p in self.packs if p["configuration"] == "kimi-fast"]
        for p in mine:
            self.assertIn(f"CHAT {p['code']} ", first)
            for m in p["messages"]:
                self.assertIn(m["text"], first)
        self.assertEqual(first.count("T: " + tr.TRANSCRIPT_REQUEST), 12)
        self.assertIn("web search is off", first)
        pack = json.load(open(os.path.join(out, "packs", mine[0]["code"] + ".json"), encoding="utf-8"))
        self.assertEqual(pack["messages"], mine[0]["messages"])


if __name__ == "__main__":
    unittest.main()
