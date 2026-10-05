"""Check the calculus curriculum (docs/calculus/curriculum.js) against walkthroughs, banks and concepts.
Spec: design/specs/2026-10-05-math-140-explorer-design.md §7.

    .venv/bin/python tests/check_curriculum.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "docs/calculus/curriculum.js"
WALKTHROUGHS = ROOT / "docs/calculus/learn/walkthroughs.js"
BANK_INDEX = ROOT / "docs/math/bank/index.json"
CONCEPTS = ROOT / "docs/math/why/concepts.js"
OFFICIAL = ("Review of functions and graphs. Limits, continuity, derivative. Differentiation of elementary functions. "
            "Antidifferentiation. Applications.")


def load_js(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(re.search(r"=\s*([\[{].*[\]}])\s*;?\s*$", text, re.S).group(1))


def load():
    return load_js(CURRICULUM)


def problems(cur, walkthrough_ids, bank_index, concept_ids):
    found, ids, edges = [], [], {}
    if cur.get("official") != OFFICIAL:
        found.append("official description doesn't match McGill's text verbatim")

    def practice_ok(where, ref):
        if ref is None:
            return
        fw, level = ref.get("framework"), ref.get("level")
        if fw not in bank_index or str(level) not in bank_index[fw].get("levels", {}):
            found.append(f"{where}: no practice bank {fw} level {level}")

    for unit in cur.get("units", []):
        ids.append(unit["id"])
        for outcome in unit.get("outcomes", []):
            oid = outcome["id"]
            ids.append(oid)
            if not oid.startswith(unit["id"] + "."):
                found.append(f"outcome {oid} isn't inside unit {unit['id']}")
            practice_ok(oid, outcome.get("practice"))
            edges.setdefault(oid, [])
            for sub in outcome.get("subtopics", []):
                sid = sub["id"]
                ids.append(sid)
                if not sid.startswith(oid + "."):
                    found.append(f"subtopic {sid} isn't inside outcome {oid}")
                if sub.get("learn") is not None and sub["learn"] not in walkthrough_ids:
                    found.append(f"{sid}: unknown walkthrough '{sub['learn']}'")
                practice_ok(sid, sub.get("practice"))
                edges[oid].append(sid)                       # knowing an outcome means knowing its subtopics
                edges[sid] = list(sub.get("builds_on", []))

    for i in sorted({i for i in ids if ids.count(i) > 1}):
        found.append(f"duplicate id '{i}'")
    known = set(ids)
    for node, targets in edges.items():
        for t in targets:
            if t.startswith("foundation:"):
                if t.split(":", 1)[1] not in concept_ids:
                    found.append(f"{node}: unknown target '{t}'")
            elif t not in known:
                found.append(f"{node}: unknown target '{t}'")

    state = {}

    def visit(n, path):
        if state.get(n) == "done" or n not in edges:
            return
        if state.get(n) == "active":
            found.append(f"builds_on loop: {' -> '.join(path + [n])}")
            return
        state[n] = "active"
        for t in edges[n]:
            visit(t, path + [n])
        state[n] = "done"

    for n in list(edges):
        visit(n, [])
    return found


def main():
    cur = load()
    walks = {w["id"] for w in load_js(WALKTHROUGHS)} if WALKTHROUGHS.exists() else set()
    bank = json.loads(BANK_INDEX.read_text())
    concepts = {c["id"] for c in load_js(CONCEPTS)}
    found = problems(cur, walks, bank, concepts)
    for line in found:
        print("FAIL", line)
    n_out = sum(len(u["outcomes"]) for u in cur["units"])
    n_sub = sum(len(o.get("subtopics", [])) for u in cur["units"] for o in u["outcomes"])
    print(f"curriculum: {len(cur['units'])} units, {n_out} outcomes, {n_sub} subtopics, {len(found)} problem(s)")
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main())
