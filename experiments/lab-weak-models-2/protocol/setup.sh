#!/usr/bin/env bash
# Sets up one session of experiment lab-weak-models-2 (entrylib/claimset-eval).
# Usage: setup.sh lab|nolab ROOT
#        setup.sh claimset ROOT SOURCE_BARE_REPO
# Makes ROOT/venv, ROOT/runs/<run>/ (each a git repository whose remote is ROOT/runs/<run>.git)
# and, for the lab and claimset sessions, the claimset files (skills, AGENTS.md, guard hook) in ROOT itself.
set -euo pipefail
ARM=$1; ROOT=$(realpath -m "$2"); SRC=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PYTHON:-python3}
PKGS="smooth==1.2.0 statsforecast==2.1.1 numpy==2.5.4 pandas==2.3.3 scipy==1.18.1"
mkdir -p "$ROOT/runs"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then echo "ROOT must not be inside a git repository" >&2; exit 1; fi

"$PY" -m venv "$ROOT/venv"
mkdir -p "$ROOT/.claude" "$ROOT/log"
cat > "$ROOT/.claude/settings.local.json" <<'JSON'
{"permissions": {"allow": ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch"]}}
JSON
if [ "$ARM" = nolab ]; then
  "$ROOT/venv/bin/pip" install -q $PKGS
  printf '[global]\nno-index = true\n' > "$ROOT/venv/pip.conf"      # nothing more can be installed into it
  if "$ROOT/venv/bin/python" -c "import claimset" 2>/dev/null; then echo "claimset is importable in the control environment" >&2; exit 1; fi
else
  "$ROOT/venv/bin/pip" install -q $PKGS claimset==0.45.0
  ( cd "$ROOT" && "$ROOT/venv/bin/claimset" init --agent claude --guard >/dev/null )
fi

newrun() {  # newrun RUN BRIEF
  local d="$ROOT/runs/$1"
  git init -q --bare "$ROOT/runs/$1.git"
  git init -q -b main "$d"
  sed "s#/home/user/venv#$ROOT/venv#" "$2" > "$d/brief.md"
  printf '__pycache__/\n*.pyc\n' > "$d/.gitignore"
  if [ "$ARM" = lab ]; then ( cd "$d" && "$ROOT/venv/bin/claimset" init --agent claude --guard >/dev/null ); fi
  git -C "$d" add -A
  git -C "$d" -c user.name=Experiment -c user.email=experiment@localhost commit -qm "Start of run $1"
  git -C "$d" remote add origin "$ROOT/runs/$1.git"
  git -C "$d" push -q -u origin main
}

case "$ARM" in
  lab)   for r in lab-sonnet-1 lab-sonnet-2 lab-haiku-1 lab-haiku-2; do newrun "$r" "$HERE/brief-lab.md"; done ;;
  nolab) for r in nolab-sonnet-1 nolab-sonnet-2 nolab-haiku-1 nolab-haiku-2; do newrun "$r" "$HERE/brief-control.md"; done ;;
  claimset)
    [ -n "$SRC" ] || { echo "give the selected lab run's bare repository" >&2; exit 1; }
    for r in claimset-sonnet-1 claimset-sonnet-2 claimset-haiku-1 claimset-haiku-2; do
      git clone -q --bare "$SRC" "$ROOT/runs/$r.git"
      git -C "$ROOT/runs/$r.git" symbolic-ref HEAD refs/heads/main
      git clone -q "$ROOT/runs/$r.git" "$ROOT/runs/$r"
      ( cd "$ROOT/runs/$r" && "$ROOT/venv/bin/claimset" setup >/dev/null )
      for s in "$ROOT/runs/$r"/claimset/*/; do      # remove what the lab agent exported, so each agent exports afresh (as in the pilot)
        ( cd "$s" && git rm -q --ignore-unmatch -- *.claimset.json files/*.results.csv \
          && git -c user.name=Experiment -c user.email=experiment@localhost commit -qm "Remove the lab agent's export" 2>/dev/null \
          && git push -q ) || true
      done
      ( cd "$ROOT/runs/$r" && "$ROOT/venv/bin/claimset" lab verify --remote )
    done ;;
  *) echo "unknown arm $ARM" >&2; exit 1 ;;
esac
echo "set up $ARM in $ROOT"
