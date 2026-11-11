"""Facts about a lab record for scoring: events by type, plans and approvals before runs, statuses, authorship.

python3 lab_summary.py LAB_DIR   (the folder holding lab.jsonl). Standard library only. Reads lab.jsonl only.
"""
import json, sys
from collections import Counter


def main(lab):
    ev = [json.loads(l) for l in open(f"{lab}/lab.jsonl")]
    by_id = {e["id"]: e for e in ev}
    types = Counter(e["type"] for e in ev)
    actors = {e["id"]: e["body"] for e in ev if e["type"] == "actor"}
    humans = {i for i, b in actors.items() if b.get("kind") == "human"}
    print(f"events: {len(ev)}; by type: {dict(types)}")
    for i, b in actors.items():
        print(f"  actor {i}: {b.get('kind')} {b.get('name')} model={b.get('model')} words={b.get('words')!r} given_at={b.get('given_at')} supersedes={by_id[i].get('supersedes')}")
    by_human = [e["id"] for e in ev if e.get("by") in humans]
    print(f"events written --by a human actor: {by_human}")
    for e in ev:
        if e["type"] == "hypothesis":
            b = e["body"]
            print(f"  {e['id']} seq {e['seq']} from_exploration={b.get('from_exploration')} prompted_by={b.get('prompted_by')}: {b.get('statement', '')[:160]}")
    plans = [e for e in ev if e["type"] == "plan"]
    for p in plans:
        b = p["body"]
        d = b.get("decision") or {}
        print(f"  {p['id']} seq {p['seq']} kind={b.get('kind')} hyps={b.get('hypotheses')} requires_approval={b.get('requires_approval')} framework={d.get('framework')} quantities={list((d.get('quantities') or {}).keys())} supersedes={p.get('supersedes')}")
    for e in ev:
        if e["type"] == "approval":
            print(f"  {e['id']} seq {e['seq']} target={e['body'].get('target')} words={e['body'].get('words')!r} given_at={e['body'].get('given_at')} by={e['by']} on_behalf_of={e['body'].get('on_behalf_of')}")
    for e in ev:
        if e["type"] == "run":
            b = e["body"]
            pl = b.get("plan")
            note = ""
            if pl:
                pseq = by_id[pl]["seq"]
                aps = [a for a in ev if a["type"] == "approval" and a["body"].get("target") == pl and a["seq"] < e["seq"]]
                note = f"plan {pl} seq {pseq} {'before' if pseq < e['seq'] else 'AFTER'} run; approvals before run: {[a['id'] for a in aps]}"
            print(f"  {e['id']} seq {e['seq']} by={e['by']} label={b.get('label')} exit={b.get('exit_status', b.get('exit'))} dirty={b.get('dirty')} seeds={b.get('seeds')} cmd={' '.join(b.get('command', []))[:120]} {note}")
    for e in ev:
        if e["type"] == "status":
            b = e["body"]
            print(f"  {e['id']} {b.get('target')} -> {b.get('to')} plan={b.get('plan')} evidence={b.get('evidence')[:6] if b.get('evidence') else None}: {b.get('rationale', '')[:150]}")
    for e in ev:
        if e["type"] in ("decision", "note", "deviation", "assumption"):
            b = e["body"]
            print(f"  {e['id']} {e['type']}: {(b.get('text') or b.get('statement') or b.get('decision') or '')[:220]}")
    anchors = sum(1 for _ in open(f"{lab}/anchors.jsonl")) if __import__('os').path.exists(f"{lab}/anchors.jsonl") else 0
    print(f"anchor receipts: {anchors}")


if __name__ == "__main__":
    main(sys.argv[1])
