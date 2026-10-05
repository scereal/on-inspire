"""Check the calculus curriculum (docs/calculus/curriculum.js) against walkthroughs, banks and concepts.
Spec: design/specs/2026-10-05-math-140-explorer-design.md §7.

    .venv/bin/python tests/check_curriculum.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
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


TERM = re.compile(r"\[\[([a-z0-9-]+)(?:\|[^\]]*)?\]\]")


def walkthrough_terms(walks):
    """Every concept id a walkthrough links to: these are entry points into the "Why?" network."""
    return {t for w in walks for step in w.get("steps", []) for t in TERM.findall(step.get("narration", ""))}


def walkthrough_problems(walks, concept_ids, known_ids):
    found, seen = [], set()
    for w in walks:
        wid = w.get("id", "?")
        if wid in seen:
            found.append(f"duplicate walkthrough '{wid}'")
        seen.add(wid)
        if w.get("subtopic") not in known_ids:
            found.append(f"{wid}: unknown subtopic '{w.get('subtopic')}'")
        if not w.get("steps"):
            found.append(f"{wid}: has no steps")
        if "\\$" in json.dumps(w):   # an escaped dollar sign: KaTeX would read it as a math delimiter
            found.append(f"{wid}: uses an escaped dollar sign; write amounts as '100 dollars'")
        for i, step in enumerate(w.get("steps", []), 1):
            where = f"{wid} step {i}"
            if not step.get("narration"):
                found.append(f"{where}: has no narration")
            for t in TERM.findall(step.get("narration", "")):
                if t not in concept_ids:
                    found.append(f"{where}: unknown concept '{t}'")
            for t in step.get("builds_on", []):
                ok = t.split(":", 1)[1] in concept_ids if t.startswith("foundation:") else t in known_ids
                if not ok:
                    found.append(f"{where}: unknown target '{t}'")
            ask = step.get("ask")
            if not ask:
                found.append(f"{where}: must ask a question before explaining")
                continue
            if ask.get("format") == "choice":
                options = ask.get("options", [])
                n = sum(bool(o.get("correct")) for o in options)
                if n != 1:
                    found.append(f"{where}: {n} correct options")
                for o in options:
                    if not o.get("correct") and not o.get("feedback"):
                        found.append(f"{where}: wrong option '{o.get('label')}' has no feedback")
            elif ask.get("format") == "number" and not ask.get("tolerance", 0) > 0:
                found.append(f"{where}: number step needs a tolerance")
    return found


def verify_walkthrough_claims(walks):
    from tests import check_concepts
    return check_concepts.verify_claims(walks)


def main():
    cur = load()
    walks = {w["id"] for w in load_js(WALKTHROUGHS)} if WALKTHROUGHS.exists() else set()
    bank = json.loads(BANK_INDEX.read_text())
    concepts = {c["id"] for c in load_js(CONCEPTS)}
    walk_list = load_js(WALKTHROUGHS) if WALKTHROUGHS.exists() else []
    known = {u["id"] for u in cur["units"]} | {o["id"] for u in cur["units"] for o in u["outcomes"]} | \
            {s["id"] for u in cur["units"] for o in u["outcomes"] for s in o.get("subtopics", [])}
    found = problems(cur, walks, bank, concepts) + walkthrough_problems(walk_list, concepts, known) + \
            verify_walkthrough_claims(walk_list)
    for line in found:
        print("FAIL", line)
    n_out = sum(len(u["outcomes"]) for u in cur["units"])
    n_sub = sum(len(o.get("subtopics", [])) for u in cur["units"] for o in u["outcomes"])
    print(f"curriculum: {len(cur['units'])} units, {n_out} outcomes, {n_sub} subtopics, {len(walk_list)} walkthroughs, {len(found)} problem(s)")
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main())
