#!/usr/bin/env bash
# Run by the person, in an empty folder BASE outside any git repository, before starting an orchestrator session.
# Usage: bash bootstrap.sh PROTO lab|nolab|claimset [SOURCE_BARE_REPO]
# Fetches the protocol into BASE/protocol-<session>/, checks that nothing will leak, and sets up BASE/<session>/.
set -euo pipefail
PROTO=$1; S=$2; SRC=${3:-}; BASE=$(pwd)
if git rev-parse --git-dir >/dev/null 2>&1; then echo "STOP: $BASE is inside a git repository" >&2; exit 1; fi
d=$BASE; while [ "$d" != / ]; do
  for f in CLAUDE.md AGENTS.md; do [ -e "$d/$f" ] && { echo "STOP: $d/$f would be read by the session" >&2; exit 1; }; done
  d=$(dirname "$d"); done
[ -e "$BASE/$S" ] && { echo "STOP: $BASE/$S exists already" >&2; exit 1; }
if [ "$S" = nolab ]; then
  hits=$(grep -rilE 'claimset|entrylib' ~/.claude/CLAUDE.md ~/.claude/skills ~/.claude/agents ~/.claude/commands \
         ~/.claude/plugins ~/.claude/settings*.json 2>/dev/null || true)
  [ -n "$hits" ] && { echo "STOP: these user-level Claude Code files mention claimset or EntryLib, and a control session would see them:"; echo "$hits"; exit 1; }
fi
P="$BASE/protocol-$S"; mkdir -p "$P"
for f in setup.sh archive.sh answers.md brief-lab.md brief-control.md ORCHESTRATOR.md; do curl -fsSL "$PROTO/$f" -o "$P/$f"; done
if [ "$S" = nolab ]; then rm "$P/brief-lab.md"; fi
bash "$P/setup.sh" "$S" "$BASE/$S" $SRC
echo "Now: cd $BASE/$S && claude --model opus --strict-mcp-config"
