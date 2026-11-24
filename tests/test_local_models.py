import csv
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "claimset-code", "claimset-vs-pdf"))
import local_models as lm  # noqa: E402

MODELS = ["qwen:9b=false", "gpt-oss:20b=low", "gemma:12b"]


class FakeOllama(BaseHTTPRequestHandler):
    """Counts a prompt as one token per 4 characters; fails the call numbered in `fail`."""
    bodies = []
    fail = set()

    def log_message(self, *args):
        pass

    def send(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/version":
            self.send({"version": "0.40.16"})
        else:
            self.send({"models": [{"name": m.split("=")[0], "digest": "d-" + m.split("=")[0]} for m in MODELS]})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeOllama.bodies.append(body)
        if len(FakeOllama.bodies) in FakeOllama.fail:
            self.send({"error": "model crashed"}, status=500)
            return
        prompt = len(body["messages"][0]["content"]) // 4
        ctx = body["options"]["num_ctx"]
        self.send({"model": body["model"], "message": {"role": "assistant", "content": "an answer"},
                   "done_reason": "stop", "prompt_eval_count": min(prompt, ctx), "prompt_eval_duration": 2 * 10**9,
                   "eval_count": 10, "eval_duration": 10**9, "load_duration": 10**8, "total_duration": 3 * 10**9})


class LocalModelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOllama)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.host = f"127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.out = tempfile.mkdtemp()
        FakeOllama.bodies, FakeOllama.fail = [], set()

    def tearDown(self):
        shutil.rmtree(self.out)

    def main(self, *argv):
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()) as out:
            lm.main(list(argv))
        return out.getvalue()

    def run_args(self, *extra, num_ctx="40960"):
        args = ["run", "--out", self.out, "--host", self.host, "--num-ctx", num_ctx]
        for m in MODELS:
            args += ["--model", m]
        return self.main(*args, *extra)

    def replies(self):
        with open(os.path.join(self.out, "replies.jsonl")) as f:
            return [json.loads(line) for line in f]

    def test_plan_covers_every_question_model_and_condition_once(self):
        calls = lm.plan_calls([lm.parse_model(m) for m in MODELS])
        self.assertEqual(len(calls), 5 * 20 * 2 * 3)
        keys = {(c["model"], c["paper"], c["condition"], c["question_id"]) for c in calls}
        self.assertEqual(len(keys), len(calls))
        self.assertEqual([c["call"] for c in calls], list(range(1, len(calls) + 1)))
        self.assertEqual(calls, lm.plan_calls([lm.parse_model(m) for m in MODELS]))  # the seed fixes the order

    def test_request_is_one_new_chat_with_the_document_and_settings(self):
        self.run_args("--limit", "3")
        body = FakeOllama.bodies[0]
        self.assertEqual(len(body["messages"]), 1)
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertIn("\n\nI'm reading this paper.\n", body["messages"][0]["content"])
        self.assertEqual(body["keep_alive"], 0)
        self.assertEqual(body["options"], {"num_ctx": 40960, "seed": lm.SEED, "num_predict": lm.NUM_PREDICT})
        think = {b["model"]: b.get("think", "absent") for b in FakeOllama.bodies}
        expected = {"qwen:9b": False, "gpt-oss:20b": "low", "gemma:12b": "absent"}
        for model, value in think.items():
            self.assertEqual(value, expected[model])

    def test_document_is_the_condition_s_file(self):
        self.run_args("--limit", "6")
        for body, reply in zip(FakeOllama.bodies, self.replies()):
            document = lm.read(lm.document_path(reply["paper"], reply["condition"])).rstrip("\n")
            self.assertTrue(body["messages"][0]["content"].startswith(document))

    def test_run_resumes_without_repeating_calls_and_records_errors(self):
        FakeOllama.fail = {2}
        self.run_args("--limit", "4")
        self.run_args("--limit", "3")
        replies = self.replies()
        self.assertEqual([r["call"] for r in replies], list(range(1, 8)))
        self.assertIn("error", replies[1])
        self.assertEqual(replies[0]["prompt_eval_duration"], 2 * 10**9)
        with open(os.path.join(self.out, "manifest.json")) as f:
            manifest = json.load(f)
        self.assertEqual(manifest["models"][1], {"name": "gpt-oss:20b", "think": "low", "digest": "d-gpt-oss:20b"})
        self.assertEqual(len(manifest["files"]), 15)

    def test_resume_with_other_settings_is_refused(self):
        self.run_args("--limit", "1")
        with self.assertRaises(SystemExit):
            self.run_args("--limit", "1", num_ctx="8192")

    def test_prompt_filling_the_context_is_cut(self):
        self.run_args("--limit", "2", num_ctx="1000")
        self.assertTrue(all(r["cut"] for r in self.replies()))
        self.assertFalse(lm.is_cut({"prompt_eval_count": 900, "eval_count": 50, "done_reason": "stop"}, 1000))
        self.assertTrue(lm.is_cut({"prompt_eval_count": 900, "eval_count": 60, "done_reason": "length"}, 2000))
        self.assertFalse(lm.is_cut({"prompt_eval_count": 900, "eval_count": lm.NUM_PREDICT,
                                    "done_reason": "length"}, 100000))

    def test_summary_gives_medians_per_model_paper_condition(self):
        FakeOllama.fail = {1}
        self.run_args("--limit", "12")
        path = self.main("summary", "--out", self.out).strip()
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(sum(int(r["replies"]) for r in rows), 12)
        self.assertEqual(sum(int(r["errors"]) for r in rows), 1)
        ok = [r for r in rows if r["replies"] != r["errors"]]
        self.assertTrue(all(r["median prompt seconds"] == "2.0" for r in ok))

    def test_missing_model_is_refused(self):
        with self.assertRaises(SystemExit):
            self.main("run", "--out", self.out, "--host", self.host, "--num-ctx", "40960", "--model", "llama:8b")

    def test_bad_think_value_is_refused(self):
        with self.assertRaises(SystemExit):
            lm.parse_model("qwen:9b=off")


if __name__ == "__main__":
    unittest.main()
