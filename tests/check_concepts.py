"""Check the "Why?" concept network (docs/math/why/concepts.js). Spec: design/specs/2026-10-04-why-network-design.md §6.

    .venv/bin/python tests/check_concepts.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONCEPTS = ROOT / "docs/math/why/concepts.js"
PAGES = [ROOT / "docs/math/square-wave/index.html", ROOT / "docs/math/two-cups/index.html",
         ROOT / "docs/math/integration-by-parts/index.html"]
WIDGETS = {"secant", "limit-zoom", "riemann", "accumulator", "unit-circle", "wave-mixer", "parabola-min",
           "product-rectangle", "chain-stretch", "derivative-ladder", "fraction-bar"}
REQUIRED = ("id", "title", "body", "deeper", "related", "foundation")
TERM = re.compile(r"\[\[([a-z0-9-]+)(?:\|[^\]]*)?\]\]")
VAR = re.compile(r"\{\{([A-Za-z_]\w*)\}\}")  # {{name}}: single braces belong to LaTeX


def load(path=CONCEPTS):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(re.search(r"=\s*(\[.*\])\s*;?\s*$", text, re.S).group(1))


def attach_calls(page_paths=PAGES):
    calls = {}
    pattern = re.compile(r'Why\.attach\(\s*[^,]+,\s*"([^"]+)"\s*(?:,\s*\{([^}]*)\})?')
    for path in page_paths:
        text = Path(path).read_text(encoding="utf-8")
        for entry, obj in pattern.findall(text):
            calls.setdefault(entry, set()).update(re.findall(r"([A-Za-z_]\w*)\s*:", obj or ""))
        # Step data that names its entry (why: "id"), attached by a generic Why.attach(el, step.why) call.
        # The data may live in the page or in a script beside it (e.g. items.js).
        if re.search(r"Why\.attach\(\s*[^,]+,\s*[A-Za-z_][\w.]*\.why\s*\)", text):
            sources = [text] + [p.read_text(encoding="utf-8") for p in sorted(Path(path).parent.glob("*.js"))]
            for source in sources:
                for entry in re.findall(r'"?\bwhy"?\s*:\s*"([^"]+)"', source):
                    calls.setdefault(entry, set())
    return calls


def used_by(concepts):
    out = {c["id"]: [] for c in concepts}
    for c in concepts:
        for d in c.get("deeper", []):
            out.setdefault(d, []).append(c["id"])
    return out


def problems(concepts, attach, require_reachable=True):
    found = []
    ids = [c.get("id") for c in concepts]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        found.append(f"duplicate id '{i}'")
    by_id = {c.get("id"): c for c in concepts}

    for c in concepts:
        cid = c.get("id", "?")
        for field in REQUIRED:
            if field not in c:
                found.append(f"'{cid}' is missing '{field}'")
        if "widget" not in c:
            found.append(f"'{cid}' has no widget")
        elif c["widget"].get("type") not in WIDGETS:
            found.append(f"'{cid}' uses unknown widget '{c['widget'].get('type')}'")
        for link in c.get("deeper", []) + c.get("related", []):
            if link not in by_id:
                found.append(f"'{cid}' links to unknown concept '{link}'")
        links = set(c.get("deeper", [])) | set(c.get("related", []))
        for term in TERM.findall(c.get("body", "")):
            if term not in links:
                found.append(f"'{cid}': [[{term}]] is not in its deeper or related links")
        if c.get("foundation") and c.get("deeper"):
            found.append(f"foundation '{cid}' links deeper")
        if not c.get("foundation") and not c.get("deeper"):
            found.append(f"'{cid}' is not a foundation but has no deeper links")
        if c.get("entry"):
            for var in sorted(set(VAR.findall(c.get("body", "")))):
                if var not in attach.get(cid, set()):
                    found.append(f"entry '{cid}': variable '{var}' is not supplied by its page")

    for entry in sorted(attach):
        if entry not in by_id or not by_id[entry].get("entry"):
            found.append(f"page attaches unknown entry '{entry}'")

    # Deeper links: no loops, and every concept reaches a foundation
    state = {}

    def visit(cid, path):
        if state.get(cid) == "done" or cid not in by_id:
            return
        if state.get(cid) == "active":
            found.append(f"deeper loop: {' -> '.join(path + [cid])}")
            return
        state[cid] = "active"
        for d in by_id[cid].get("deeper", []):
            visit(d, path + [cid])
        state[cid] = "done"

    for cid in by_id:
        visit(cid, [])

    def reaches_foundation(cid, seen=()):
        c = by_id.get(cid)
        if not c or cid in seen:
            return False
        return c.get("foundation", False) or any(reaches_foundation(d, seen + (cid,)) for d in c.get("deeper", []))

    for cid in by_id:
        if not reaches_foundation(cid):
            found.append(f"'{cid}' never reaches a foundation")

    # Every concept is reachable from an entry
    entries = [cid for cid, c in by_id.items() if c.get("entry")]
    if entries and require_reachable:
        seen, stack = set(entries), list(entries)
        while stack:
            c = by_id.get(stack.pop(), {})
            for link in c.get("deeper", []) + c.get("related", []):
                if link in by_id and link not in seen:
                    seen.add(link)
                    stack.append(link)
        for cid in by_id:
            if cid not in seen:
                found.append(f"orphan '{cid}': not reachable from any entry")
        for cid in entries:
            if cid not in attach:
                found.append(f"entry '{cid}' isn't attached to any page")
    return found


def verify_claims(concepts):
    import sympy as sp

    names = {s: sp.Symbol(s) for s in ("x", "t", "h", "u", "a", "b")}
    names["n"] = sp.Symbol("n", positive=True, integer=True)
    names.update({"Si": sp.Si, "E": sp.E, "pi": sp.pi, "Rational": sp.Rational})
    found = []
    for c in concepts:
        for claim in c.get("claims", []):
            try:
                value = sp.sympify(claim["sympy"], locals=names)
                value = value.doit() if hasattr(value, "doit") else value
                if "approx" in claim:
                    ok = abs(float(value) - claim["approx"]) <= claim.get("tol", 1e-6)
                else:
                    ok = sp.simplify(value - sp.sympify(claim["equals"], locals=names)) == 0
            except Exception as e:  # a claim that can't be evaluated is a failed claim
                ok, value = False, f"error: {e}"
            if not ok:
                found.append(f"'{c['id']}': claim {claim['sympy']} = {claim.get('equals', claim.get('approx'))} is false (got {value})")
    return found


def main():
    concepts = load()
    calls = attach_calls()
    # Orphans can only be judged once every page has wired in its entries
    pages_wired = all(attach_calls([page]) for page in PAGES)
    found = problems(concepts, calls, require_reachable=pages_wired) + verify_claims(concepts)
    if not pages_wired:
        print("note: orphan check skipped until all three pages attach their entries")
    for line in found:
        print("FAIL", line)
    entries = sum(1 for c in concepts if c.get("entry"))
    print(f"concept network: {len(concepts) - entries} concepts, {entries} entries, {len(found)} problem(s)")
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main())
