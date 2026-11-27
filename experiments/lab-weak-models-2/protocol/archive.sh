#!/usr/bin/env bash
# Archives one session: every run folder (files, and its full git history including study branches, as repo.bundle),
# the session's transcripts (the orchestrator's and every subagent's) and the session's log/.
# Usage: archive.sh ROOT   -> ROOT.tar.gz
set -euo pipefail
ROOT=$(realpath "$1"); OUT="$ROOT-archive"; rm -rf "$OUT"; mkdir -p "$OUT/runs" "$OUT/transcripts"
for d in "$ROOT"/runs/*/; do
  r=$(basename "$d"); mkdir -p "$OUT/runs/$r"
  git -C "$ROOT/runs/$r.git" bundle create -q "$OUT/runs/$r/repo.bundle" --all
  rsync -a --exclude .git --exclude __pycache__ "$d" "$OUT/runs/$r/tree/"
done
P="$HOME/.claude/projects/$(echo "$ROOT" | sed 's#[^A-Za-z0-9]#-#g')"
[ -d "$P" ] && cp -r "$P"/. "$OUT/transcripts/" || echo "no transcripts found at $P" >&2
[ -d "$ROOT/log" ] && cp -r "$ROOT/log" "$OUT/log"
{ uname -a; nproc; claude --version 2>/dev/null; "$ROOT/venv/bin/python" --version; "$ROOT/venv/bin/pip" freeze; } > "$OUT/environment.txt" 2>&1
tar -czf "$ROOT.tar.gz" -C "$(dirname "$OUT")" "$(basename "$OUT")"
echo "$ROOT.tar.gz"
