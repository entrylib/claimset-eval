import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "claimset-code", "claimset-vs-pdf"))
import grading  # noqa: E402
import randomise as rz  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
QUESTIONS = os.path.join(ROOT, "study", "questions")


class GradingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()
        key, packs = rz.draw()
        rz.write(cls.d, key, packs)
        cls.key = key
        os.makedirs(os.path.join(cls.d, "chats"))
        for p in packs:
            if p["configuration"] != "kimi-fast":
                continue
            turns = [{"n": i, "user": m["text"], "assistant": f"{m['id']} answer, see claim C3 (Table 2) in the {p['condition'].upper()}."}
                     for i, m in enumerate(p["messages"], 1)]
            json.dump({"turns": turns}, open(os.path.join(cls.d, "chats", p["code"] + ".json"), "w"))
        cls.qs = grading.questions(QUESTIONS)
        cls.answers, cls.akey, cls.batches = grading.build(key, os.path.join(cls.d, "packs"), os.path.join(cls.d, "chats"),
                                                           cls.qs, {"kimi-fast"}, "s1")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def test_build_takes_the_per_paper_answers_masked_and_coded(self):
        self.assertEqual(len(self.answers), 200)  # 5 papers x 20 questions x 2 conditions; no cross, no follow-ups
        self.assertEqual(sum(len(b) for b in self.batches), 100)
        self.assertTrue(all(len(item["answers"]) == 2 for b in self.batches for item in b))
        for a in self.answers:
            self.assertNotIn("C3", a["text"])
            self.assertNotIn("Table 2", a["text"])
            self.assertNotIn("PDF", a["text"])
            self.assertNotIn("CLAIMSET", a["text"])
        self.assertEqual({k["condition"] for k in self.akey.values()}, {"pdf", "claimset"})
        self.assertEqual(set(self.akey), {a["answer"] for a in self.answers})
        self.assertFalse(any("notes" in item for b in self.batches for item in b))
        again = grading.build(self.key, os.path.join(self.d, "packs"), os.path.join(self.d, "chats"), self.qs, {"kimi-fast"}, "s1")
        self.assertEqual(again[0], self.answers)

    def test_answer_code_names_the_right_answer(self):
        for a in self.answers:
            k = self.akey[a["answer"]]
            self.assertTrue(a["text"].startswith(k["question"] + " answer"), a)
            self.assertEqual(a["question"], f"{k['paper']}#{k['question']}")

    def test_prompt_holds_the_instructions_and_every_answer(self):
        text = grading.prompt("INSTRUCTIONS", self.batches[0])
        self.assertTrue(text.startswith("INSTRUCTIONS"))
        for item in self.batches[0]:
            self.assertIn(item["marking"], text)
            for a in item["answers"]:
                self.assertIn(f"#### Answer {a['answer']}", text)

    def grades_for(self, batch, **change):
        out = [{"question": item["question"], "answer": a["answer"], "score": 1, "invented": 0, "overreach": 0,
                "reason": "Right."} | change for item in batch for a in item["answers"]]
        return {"grades": out}

    def test_grades_are_checked(self):
        b = self.batches[0]
        got, problems = grading.check_grades(b, self.grades_for(b))
        self.assertEqual(problems, [])
        _, problems = grading.check_grades(b, self.grades_for(b, score=2))
        self.assertTrue(problems)
        short = self.grades_for(b)
        short["grades"].pop()
        _, problems = grading.check_grades(b, short)
        self.assertTrue(any(p.startswith("no grade for") for p in problems))
        self.assertEqual(grading.parse_output("```json\n" + json.dumps(self.grades_for(b)) + "\n```"), self.grades_for(b))

    def test_sheet_uses_fresh_codes_and_the_look_reads_only_the_pdf(self):
        grades = {}
        for b in self.batches:
            grades.update(grading.check_grades(b, self.grades_for(b))[0])
        text, mkey = grading.sheet(self.batches, grades, "s2")
        self.assertEqual(sorted(mkey.values()), sorted(grades))
        self.assertFalse(set(mkey) & set(grades))
        for code in grades:
            self.assertNotIn(code, text)
        self.assertNotIn("pdf", text.lower().replace("application/json", ""))
        moderation = {m: {"approved": True} for m in mkey}
        final, problems = grading.interim(grades, moderation, mkey)
        self.assertEqual(problems, [])
        self.assertEqual(grading.look(self.akey, self.qs, final)[1], "no room")
        # one PDF answer of 25 to an absent question changed to invented (4%): still no room; two (8%): room
        codes = [c for c, k in self.akey.items() if k["condition"] == "pdf" and self.qs[k["paper"]][k["question"]]["type"] == "absent"]
        ms = [next(m for m, c in mkey.items() if c == code) for code in codes[:2]]
        for m in ms:
            moderation[m] = {"approved": False, "score": 0, "invented": 1, "overreach": 0, "reason": "Invented."}
            final, _ = grading.interim(grades, moderation, mkey)
            if m == ms[0]:
                self.assertEqual(grading.look(self.akey, self.qs, final)[1], "no room")
        numbers, verdict = grading.look(self.akey, self.qs, final)
        self.assertEqual(verdict, "room")
        self.assertEqual(numbers["n answerable"], 75)
        self.assertEqual(numbers["n absent"], 25)
        del moderation[m]
        self.assertTrue(grading.interim(grades, moderation, mkey)[1])


if __name__ == "__main__":
    unittest.main()
