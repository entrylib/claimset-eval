import argparse
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import reading_study as rs  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

# A small claimset of the invented paper, enough for ids and bundles; the reading view is written by hand,
# since these tests must not depend on the claimset package.
CLAIMSET = {
    "claims": [{"id": "C1", "statement": "The pruned loss is within 1+eps."},
               {"id": "C2", "statement": "SEP has a lower Brier score than random forest on UCI-40."}],
    "evidence": [{"id": "E1", "tables": [{"id": "E1.T1"}]}],
    "limitations": [{"id": "L1"}],
}
VIEW = "CLAIMSET Sparse ensemble pruning\nC1 The pruned loss is within 1+eps.\nC2 SEP is better on UCI-40.\n"
QUESTIONS = {
    "papers": ["invented"],
    "questions": [
        {"id": "Q1", "type": "lookup", "question": "What is SEP's Brier score?", "answer": "0.112",
         "claims": ["C2"], "in_claimset": True},
        {"id": "Q2", "type": "scope", "question": "Does C1 hold for unbounded losses?",
         "answer": "Not shown; losses are assumed bounded in [0, 1].", "in_claimset": False},
        {"id": "Q3", "type": "absent", "question": "How long did training take?"},
    ],
}


def make_root():
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "papers", "text"))
    os.makedirs(os.path.join(root, "claimset", "pilot"))
    os.makedirs(os.path.join(root, "study", "questions"))
    shutil.copy(os.path.join(FIXTURES, "invented.txt"), rs.paper_path("invented", root))
    with open(rs.claimset_path("invented", root), "w") as f:
        json.dump(CLAIMSET, f)
    with open(rs.view_path("invented", root), "w") as f:
        f.write(VIEW)
    with open(os.path.join(root, "study", "questions", "invented.json"), "w") as f:
        json.dump(QUESTIONS, f)
    return root


def args(**kw):
    base = {"questions": None, "out": None, "model": ["m1"], "conditions": list(rs.CONDITIONS), "reps": 2,
            "effort": "medium", "seed": 1, "provider": "fake", "max_calls": None, "dry_run": False,
            "force": False, "judge": "j", "sheet": None, "import_sheet": None}
    base.update(kw)
    return argparse.Namespace(**base)


class ReadingStudyTest(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.out = os.path.join(self.root, "study", "runs", "t")
        self.bundle = rs.render_bundle
        rs.render_bundle = lambda name, claim, root=None: f"CLAIM {claim} of {name}\n"

    def tearDown(self):
        rs.render_bundle = self.bundle
        shutil.rmtree(self.root)

    def questions(self):
        qs, problems = rs.load_questions(rs.question_files(None, self.root), self.root)
        self.assertEqual(problems, [])
        return qs

    def test_valid_questions_load(self):
        qs = self.questions()
        self.assertEqual([q["uid"] for q in qs], ["invented:Q1", "invented:Q2", "invented:Q3"])
        self.assertEqual(qs[2]["answer"], rs.ABSENT_ANSWER)

    def test_broken_questions_are_reported(self):
        bad = json.loads(json.dumps(QUESTIONS))
        bad["questions"] += [{"id": "Q1", "type": "lookup", "question": "x", "answer": "y"},
                             {"id": "Q5", "type": "guess", "question": "x", "answer": "y"},
                             {"id": "Q6", "type": "lookup", "question": "x"},
                             {"id": "Q7", "type": "lookup", "question": "x", "answer": "y", "claims": ["C9"]},
                             {"id": "Q8", "type": "cross", "question": "x", "answer": "y"}]
        path = os.path.join(self.root, "study", "questions", "invented.json")
        with open(path, "w") as f:
            json.dump(bad, f)
        _, problems = rs.load_questions([path], self.root)
        text = "\n".join(problems)
        for needle in ("duplicate id Q1", "Q5: type", "Q6: no reference answer", "claim C9", "Q8: 'cross'"):
            self.assertIn(needle, text)

    def test_template_is_skipped(self):
        with open(os.path.join(self.root, "study", "questions", "_template.json"), "w") as f:
            f.write("{}")
        self.assertEqual(len(rs.question_files(None, self.root)), 1)

    def test_documents_per_condition(self):
        q1, q2, _ = self.questions()
        self.assertIn("[p8.1] Table 2", rs.document(q1, "paper", self.root))
        self.assertEqual(rs.document(q1, "claimset", self.root), VIEW)
        self.assertEqual(rs.document(q1, "bundle", self.root), "CLAIM C2 of invented\n")
        self.assertIsNone(rs.document(q2, "bundle", self.root))

    def test_tasks_skip_bundle_without_claims_and_are_shuffled(self):
        t = rs.tasks(self.questions(), list(rs.CONDITIONS), ["m1", "m2"], 2, seed=1)
        self.assertEqual(len(t), (3 * 2 + 1) * 2 * 2)
        self.assertEqual(len({x["key"] for x in t}), len(t))
        self.assertEqual([x["key"] for x in t], [x["key"] for x in rs.tasks(self.questions(), list(rs.CONDITIONS),
                                                                              ["m1", "m2"], 2, seed=1)])

    def test_run_resumes_and_refuses_changed_inputs(self):
        self.assertEqual(rs.cmd_run(args(out=self.out, max_calls=3), self.root), 0)
        self.assertEqual(len(rs.load_jsonl(os.path.join(self.out, "answers.jsonl"))), 3)
        self.assertEqual(rs.cmd_run(args(out=self.out), self.root), 0)
        answers = rs.load_jsonl(os.path.join(self.out, "answers.jsonl"))
        self.assertEqual(len(answers), 14)
        self.assertEqual(len({a["key"] for a in answers}), 14)
        a = answers[0]
        for field in ("doc_sha256", "input_tokens", "output_tokens", "latency_s", "not_stated", "cites"):
            self.assertIn(field, a)
        with open(rs.view_path("invented", self.root), "a") as f:
            f.write("changed\n")
        with self.assertRaises(SystemExit):
            rs.cmd_run(args(out=self.out), self.root)

    def test_failed_calls_are_recorded_and_retried(self):
        calls = []

        def flaky(model, system, blocks, schema, effort, max_tokens=16000):
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("HTTP 500")
            return rs.call_fake(model, system, blocks, schema, effort)
        rs.PROVIDERS["flaky"] = flaky
        try:
            self.assertEqual(rs.cmd_run(args(out=self.out, provider="flaky", reps=1, conditions=["paper"]), self.root), 1)
            self.assertEqual(rs.cmd_run(args(out=self.out, provider="flaky", reps=1, conditions=["paper"]), self.root), 0)
        finally:
            del rs.PROVIDERS["flaky"]
        answers = rs.load_jsonl(os.path.join(self.out, "answers.jsonl"))
        self.assertEqual(sum(bool(a.get("error")) for a in answers), 1)
        self.assertEqual(len({a["key"] for a in answers if not a.get("error")}), 3)

    def test_blind_removes_condition_markers_but_not_names(self):
        self.assertEqual(rs.blind("SEP scores 0.112 [p8.1] on [[D3:UCI-40]] (C2, E1.T1) and M4"),
                         "SEP scores 0.112 on UCI-40 and M4")

    def test_cites_are_checked_against_the_document(self):
        q = self.questions()[0]
        self.assertEqual(rs.cites_valid({"condition": "paper", "cites": ["p8.1", "[p4.2]", "p99.1"]}, q, self.root), (2, 3))
        self.assertEqual(rs.cites_valid({"condition": "claimset", "cites": ["C2", "E1.T1.r1", "C9"]}, q, self.root), (2, 3))

    def test_scores(self):
        lookup, absent = {"type": "lookup"}, {"type": "absent"}
        self.assertEqual([rs.score(lookup, g) for g in rs.GRADES], [1.0, 0.5, 0.0, 0.0])
        self.assertEqual([rs.score(absent, g) for g in rs.GRADES], [1.0, 0.0, 0.0, 1.0])

    def test_grade_sheet_import_and_report(self):
        rs.cmd_run(args(out=self.out), self.root)
        self.assertEqual(rs.cmd_grade(args(out=self.out), self.root), 0)
        grades = rs.load_jsonl(os.path.join(self.out, "grades.jsonl"))
        self.assertEqual(len(grades), 14)
        self.assertTrue(all(g["grade"] == "not_stated" for g in grades))   # the fake model never answers
        sheet = os.path.join(self.out, "sheet.csv")
        rs.cmd_grade(args(out=self.out, sheet=sheet), self.root)
        with open(sheet, newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 14)
        self.assertNotIn("condition", rows[0])
        rows[0]["human_grade"] = "correct"
        with open(sheet, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rs.SHEET)
            w.writeheader()
            w.writerows(rows)
        rs.cmd_grade(args(out=self.out, import_sheet=sheet), self.root)
        humans = [g for g in rs.load_jsonl(os.path.join(self.out, "grades.jsonl")) if g.get("human")]
        self.assertEqual(len(humans), 1)
        self.assertEqual(rs.cmd_report(args(out=self.out), self.root), 0)
        rep = json.load(open(os.path.join(self.out, "report.json")))
        correct = sum(s["correct"]["k"] for s in rep["by_model_and_condition"].values())
        self.assertEqual(correct, 0 if humans[0]["key"].startswith("invented:Q3|") else 1)   # the human grade counts
        self.assertEqual(rep["by_model_and_condition"]["m1 / paper"]["answered_absent_question"]["rate"], 0.0)
        self.assertIn("claimset - paper", rep["paired"])
        self.assertIn("bundle - paper", rep["paired"])
        self.assertTrue(os.path.exists(os.path.join(self.out, "report.md")))

    def test_dry_run_makes_no_calls(self):
        self.assertEqual(rs.cmd_run(args(out=self.out, dry_run=True, provider="anthropic"), self.root), 0)
        self.assertFalse(os.path.exists(self.out))


if __name__ == "__main__":
    unittest.main()
