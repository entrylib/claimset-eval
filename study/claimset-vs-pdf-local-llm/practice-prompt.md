# Practice run of the local models: a prompt for Claude Code on the supervisor's PC

Give the text below to Claude Code running on the PC with the GPU and Ollama, inside a clone of `entrylib/claimset-eval`. It is the practice run of the study in `plan.md`: it fixes the models, their digests and the context length, and checks the script, before anything counts as data. Paste the report it writes back into the study's conversation.

````text
Practice run for the claimset-vs-pdf-local-llm study's local models. This is a practice run, not data collection: do not run `local_models.py run`, do not put any of the study's questions to a model, and do not commit or push anything.

Setup
1. In this clone of entrylib/claimset-eval, fetch and check out branch `claimset-vs-pdf-local-llm` (the script is claimset-code/claimset-vs-pdf/local_models.py; read its docstring and study/claimset-vs-pdf-local-llm/plan.md first). Run `python3 -m unittest tests.test_local_models` and confirm it passes.
2. Report `nvidia-smi` (GPU, memory), `ollama --version`, and the Ollama service's environment (`systemctl show ollama --property=Environment`). If Ollama is older than the newest release, update it with `curl -fsSL https://ollama.com/install.sh | sh` and report the new version. Do not change OLLAMA_KV_CACHE_TYPE or other settings that change the computation without asking me; note any already set.

Models
3. Look up the current tags on https://ollama.com/library (qwen3.5, qwen3.6, qwen3.8, or whichever is newest; gemma4; gpt-oss). Choose:
   - Qwen: the newest version, size between 8B and 14B, default quantisation;
   - gpt-oss: `gpt-oss:20b`;
   - Gemma 4: the ~12B model, default quantisation.
   Tell me which tags you chose and why before pulling, and wait for my OK.
4. `ollama rm qwen3:8b`, then `ollama pull` the three. Report `ollama list` (with digests: `curl -s localhost:11434/api/tags`) and, for each, `ollama show <tag>` (capabilities: does it list "thinking"? context length; quantisation).

Context
5. For each model, find the largest context from 32768, 40960, 49152, 65536 that runs entirely on the GPU: load it with
   curl -s localhost:11434/api/chat -d '{"model":"<tag>","messages":[{"role":"user","content":"Hi"}],"stream":false,"keep_alive":"5m","options":{"num_ctx":<N>}}'
   then `ollama ps` (the PROCESSOR column must say 100% GPU), then unload with `ollama stop <tag>`.
6. With the smallest of those maxima across the three models as N, run the script's size check:
   python3 claimset-code/claimset-vs-pdf/local_models.py sizes --num-ctx N --model <qwen>=false --model gpt-oss:20b=low --model <gemma>
   (for Gemma add `=false` only if `ollama show` lists thinking). It prints each document's prompt tokens and FITS or TOO LONG. If any document is TOO LONG, tell me and stop.

Prompt cache
7. Write an invented document of about 3,000 words to ~/claimset-practice/invented.txt: a made-up paper on a made-up forecasting method, with a small results table and two formulas. Use nothing from the study's papers, questions or claimsets. Then:
   python3 claimset-code/claimset-vs-pdf/local_models.py practice --num-ctx N --model ... (same three) --document ~/claimset-practice/invented.txt --question "Which method had the lowest error, and on which data?"
   For each model, check that attempt 2's prompt_eval_count equals attempt 1's and its prompt_eval_duration is of the same order (not much smaller): if it is much smaller, a cached prompt was reused, so tell me. Also report whether a `thinking` text came back for each model.

Report
8. Write everything to ~/claimset-practice/report.md: GPU and Ollama version, the service's environment, the three tags with digests, quantisation and thinking capability, the context N and how you chose it, the full output of `sizes` and `practice` (answers included), how long each call took, and anything that went wrong. Then show me the report.
````
