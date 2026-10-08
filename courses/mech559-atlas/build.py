"""Build the MECH 559 atlas into one self-contained HTML page.

    ATLAS_PY=/path/to/python-with-scipy python3 build.py

Content modules verify every symbolic answer with SymPy as they import. This script then checks the
network (links resolve, prerequisites acyclic, every concept practised), runs every code snippet in a
Python that has numpy/scipy/scikit-learn/pandas (ATLAS_PY) and captures the real output and error
messages, and writes docs/optimization/mech-559/index.html (the site page) and mech559-atlas.html (the artifact
page, a body fragment).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent / "docs" / "optimization" / "mech-559"
sys.path.insert(0, str(HERE / "content"))

import prereqs, course_a, course_b, course_c, course_d, questions, exercises, codelab  # noqa: E402

SHORT = {
    "x-e1-stationary": "1.1 Stationary points", "x-e1-existence": "1.2 Max or min exists?", "x-e1-iterations": "1.3 Gradient vs Newton step",
    "x-e2-monotonicity": "2.1 Chain of active constraints", "x-e2-hyperplane": "2.2 Hyperplane is convex", "x-e2-closest-point": "2.3 / 4.3 Closest point on a plane",
    "x-e2-armijo-goldstein": "2.4 Armijo–Goldstein interval", "x-e2-backtracking": "2.5 Backtracking", "x-e2-bfgs": "2.6 One BFGS update", "x-e2-canal": "2.7 Canal cross-section",
    "x-e3-kkt-unbounded": "3.1 KKT point, no maximum", "x-e3-reduced-b": "3.2 Reduced gradient for every b",
    "x-e4-cusp": "4.1 Kuhn–Tucker cusp", "x-e4-ellipsoid": "4.2 Ellipsoid + inequality",
    "p-gradient": "Gradient", "p-hessian": "Hessian", "p-taylor-vector": "Taylor in vector form", "p-matrix-calculus": "Matrix calculus",
    "p-eigen-definiteness": "Eigenvalues and definiteness", "p-linear-systems": "Linear systems", "p-sets-compactness": "Compact sets, Weierstrass",
    "p-newton-raphson": "Newton–Raphson", "p-statistics": "Mean, variance, Gaussian", "p-chain-rule": "Chain rule",
    "p-numpy-shapes": "NumPy shapes", "p-python-functions": "Python functions and args", "p-lagrange-419": "Multipliers in MECH 419",
    "c-functions-of-interest": "Functions of interest", "c-variables-parameters": "Variables vs parameters", "c-pareto": "Pareto front, ε-constraint",
    "c-models-and-classes": "Models and problem classes", "c-analysis-to-synthesis": "Analysis to synthesis", "c-negative-null-form": "Negative null form",
    "c-boundedness": "Boundedness", "c-feasibility": "Feasibility", "c-relaxation": "Relaxation theorems", "c-constraint-activity": "Constraint activity",
    "c-monotonicity": "Monotonicity analysis", "c-topography": "Interior, boundary, local, global",
    "c-surrogates-why": "Why surrogates", "c-doe": "Design of experiments", "c-model-taxonomy": "Model taxonomy", "c-model-assessment": "Over/underfitting, CV",
    "c-error-metrics": "RMSE and R²", "c-least-squares": "Least squares", "c-conditioning-ridge": "Conditioning and ridge", "c-variable-scaling": "Variable scaling",
    "c-ann": "Neural networks", "c-rbf": "Radial basis functions", "c-kriging": "Kriging", "c-gpr-uncertainty": "Kriging uncertainty (GPR)",
    "c-surrogate-choice": "Choosing a surrogate", "c-surrogate-optimization": "Surrogate-based optimization",
    "c-unconstrained-why": "Why unconstrained", "c-fonc": "FONC", "c-sosc": "SOSC", "c-quadratic-functions": "Quadratic functions", "c-convexity": "Convexity",
    "c-descent": "Descent directions", "c-gradient-method": "Gradient method", "c-exact-line-search": "Exact line search", "c-armijo": "Armijo line search",
    "c-newton": "Newton's method", "c-quasi-newton": "Quasi-Newton (BFGS)", "c-conjugate-gradients": "Conjugate gradients", "c-stabilization": "Stabilization",
    "c-scaling": "Scaling", "c-trust-region": "Trust regions",
    "c-lp-standard-form": "LP standard form", "c-basic-solutions": "Basic solutions", "c-lp-theory": "LP theory: vertices", "c-simplex": "Simplex method",
    "c-dof-regularity": "DOF and regularity", "c-tangent-normal": "Tangent and normal spaces", "c-reduced-gradient": "Reduced gradient",
    "c-lagrangian-equality": "Lagrangian, multipliers", "c-constrained-sosc": "Constrained SOSC", "c-kkt": "KKT conditions",
    "c-grg": "GRG", "c-active-set": "Active-set strategy", "c-penalty-barrier": "Penalty and barrier", "c-augmented-lagrangian": "Augmented Lagrangian",
    "c-sqp": "SQP", "c-convergence-termination": "Convergence and reporting",
    "q-active-means-tradeoff": "Active constraint = trade-off", "q-monotonicity-vs-kkt": "Monotonicity vs KKT", "q-knob-by-cv": "Knobs by CV",
    "q-conditioning-everywhere": "Ill-conditioning everywhere", "q-newton-vs-gradient": "Newton vs gradient", "q-lp-vertex-nlp": "LP vertex vs NLP",
    "q-multiplier-two-courses": "Multipliers in two courses", "q-multistart": "Why answers differ by start",
}

SUBJECTS = ["Multivariable calculus", "Linear algebra", "Analysis and numerics", "Python and NumPy", "From MECH 419"]

SOURCES = [
    ("MECH 559 lecture slides (Bayoumy; originally Kokkolaras), Lectures 1–9", "", "The structure, examples and every equation follow these slides."),
    ("MECH 559 course notebooks (public GitHub repository)", "https://github.com/Ahmed-Bayoumy/MECH559", "Companion notebooks for every lecture; used to match the library calls the course uses."),
    ("Papalambros & Wilde, Principles of Optimal Design (3rd ed.)", "https://doi.org/10.1017/9781316451038", "The textbook behind the formulation, monotonicity and algorithm chapters (drive screw, modified Cholesky)."),
    ("Martins & Ning, Engineering Design Optimization (free online)", "https://mdobook.github.io/", "Clear modern treatment of KKT geometry, regularity, SQP and surrogate models; cited in Lecture 8."),
    ("Nocedal & Wright, Numerical Optimization (2nd ed.)", "https://doi.org/10.1007/978-0-387-40065-5", "The standard reference for line searches, trust regions, quasi-Newton methods and SQP."),
    ("SciPy optimize documentation", "https://docs.scipy.org/doc/scipy/reference/optimize.html", "Authoritative signatures and method capabilities for minimize, linprog and root finders."),
    ("scikit-learn user guide: Gaussian processes, linear models, model selection", "https://scikit-learn.org/stable/user_guide.html", "Kernel parameterization, normalize_y, Ridge's intercept, and KFold."),
    ("Forrester, Sóbester & Keane, Engineering Design via Surrogate Modelling", "https://doi.org/10.1002/9780470770801", "Design of experiments, RBFs and Kriging for engineers."),
]

LINK_RE = re.compile(r"\[\[([a-z][a-z0-9]*-[a-z0-9-]+)")


def collect():
    concepts = prereqs.CONCEPTS + course_a.CONCEPTS + course_b.CONCEPTS + course_c.CONCEPTS + course_d.CONCEPTS + questions.CONCEPTS + exercises.CONCEPTS
    by = {c["id"]: c for c in concepts}
    assert len(by) == len(concepts), "duplicate concept id"
    lib = {e["id"]: e for e in codelab.LIBRARY}
    bugs = {e["id"]: e for e in codelab.ERRORS}
    flows = {w["id"]: w for w in codelab.WORKFLOWS}
    every = set(by) | set(lib) | set(bugs) | set(flows)
    assert len(every) == len(by) + len(lib) + len(bugs) + len(flows), "an id is used twice across sections"

    def check_links(owner, blob):
        for link in LINK_RE.findall(json.dumps(blob)):
            assert link in every, f"{owner} links to unknown [[{link}]]"

    pids = set()
    for c in concepts:
        assert c["id"] in SHORT, f"no short label for {c['id']}"
        c["short"] = SHORT[c["id"]]
        for d in c["deeper"]:
            assert d in by, f"{c['id']} builds on unknown {d}"
            assert by[d]["layer"] <= c["layer"], f"{c['id']} builds on a higher layer"
        assert c["problems"], f"{c['id']} has no practice"
        for p in c["problems"]:
            assert p["id"] not in pids, f"duplicate problem id {p['id']}"
            pids.add(p["id"])
        check_links(c["id"], c)
    for e in codelab.LIBRARY:
        for k in e["concepts"]:
            assert k in by, f"{e['id']} -> unknown concept {k}"
        for k in e["errors"]:
            assert k in bugs, f"{e['id']} -> unknown bug {k}"
        check_links(e["id"], e)
    for e in codelab.ERRORS:
        for k in e["concepts"]:
            assert k in by, f"{e['id']} -> unknown concept {k}"
        assert e["kind"] in ("crash", "warning", "silent")
        check_links(e["id"], e)
    for w in codelab.WORKFLOWS:
        for k in w["concepts"]:
            assert k in by, f"{w['id']} -> unknown concept {k}"
    for p in codelab.CODE_PROBLEMS:
        assert p["id"] not in pids
        pids.add(p["id"])
    # acyclic prerequisites
    state = {}
    def visit(i, path):
        if state.get(i) == 1:
            raise AssertionError("cycle: " + " -> ".join(path + [i]))
        if state.get(i) == 2:
            return
        state[i] = 1
        for d in by[i]["deeper"]:
            visit(d, path + [i])
        state[i] = 2
    for i in by:
        visit(i, [])
    used = {d for c in concepts for d in c["deeper"]}
    for c in concepts:
        if c["layer"] == 0:
            assert c["id"] in used, f"foundation {c['id']} isn't used by anything"
    return concepts


def code_tasks():
    tasks = []
    for e in codelab.LIBRARY:
        if e["code"]:
            tasks.append({"kind": "example", "id": e["id"], "code": e["code"]})
    for b in codelab.ERRORS:
        tasks.append({"kind": "bug", "id": b["id"], "bad": b["bad"], "good": b["good"], "verify": list(b["verify"]),
                      "good_check": b["good_check"], "show": b.get("show")})
    for w in codelab.WORKFLOWS:
        tasks.append({"kind": "workflow", "id": w["id"], "steps": [s[1] for s in w["steps"]]})
    return tasks


def verify_code(tasks):
    """Run snippets in ATLAS_PY (cached by content hash). Returns the results dict."""
    blob = json.dumps(tasks, sort_keys=True).encode()
    key = hashlib.sha256(blob).hexdigest()[:16]
    cache = HERE / "code" / "results.json"
    if cache.exists():
        cached = json.loads(cache.read_text())
        if cached.get("key") == key and not cached.get("failures"):
            return cached["results"]
    py = os.environ.get("ATLAS_PY", sys.executable)
    tasks_path = HERE / "code" / "_tasks.json"
    out_path = HERE / "code" / "_results.json"
    tasks_path.write_text(blob.decode())
    proc = subprocess.run([py, str(HERE / "code" / "run_snippets.py"), str(tasks_path), str(out_path)], capture_output=True, text=True)
    print(proc.stdout.strip())
    if proc.returncode != 0 or not out_path.exists():
        print(proc.stderr[-2000:])
        raise SystemExit("code verification failed (set ATLAS_PY to a Python with numpy, scipy, scikit-learn and pandas)")
    data = json.loads(out_path.read_text())
    cache.write_text(json.dumps({"key": key, **data}, indent=1))
    tasks_path.unlink()
    out_path.unlink()
    return data["results"]


def main():
    concepts = collect()
    results = verify_code(code_tasks())
    library = []
    for e in codelab.LIBRARY:
        library.append({**e, "output": results.get(e["id"], {}).get("output", "")})
    bugs = []
    for e in codelab.ERRORS:
        r = results[e["id"]]
        bugs.append({k: v for k, v in e.items() if k not in ("verify", "good_check", "show")} | {
            "symptom": r["symptom"], "bad_show": r["bad_show"], "good_show": r["good_show"]})
    flows = []
    for w in codelab.WORKFLOWS:
        outs = results[w["id"]]["outputs"]
        flows.append({"id": w["id"], "title": w["title"], "summary": w["summary"], "concepts": w["concepts"],
                      "steps": [{"text": t, "code": c, "output": o} for (t, c), o in zip(w["steps"], outs)]})
    code_problems = list(codelab.CODE_PROBLEMS)
    for e in codelab.ERRORS:
        q = e.get("quiz")
        if q:
            code_problems.append({"id": "q-" + e["id"], "title": e["title"], "stem": f"From the bug library: **{e['title']}**.",
                                  "fig": None, "steps": [q], "takeaway": "", "bug": e["id"]})
    data = {"concepts": concepts, "subjects": SUBJECTS, "library": library, "bugs": bugs, "workflows": flows,
            "codeProblems": code_problems, "versions": results.get("_versions", {}),
            "sources": [{"title": t, "url": u, "note": n} for t, u, n in SOURCES]}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "src/page.html").read_text()
    for name in ("style.css", "figures.js", "widgets.js", "app.js"):
        page = page.replace("/*@" + name + "@*/", (HERE / "src" / name).read_text())
    page = page.replace("/*@data@*/", "window.ATLAS = " + payload + ";")
    # Artifact page: a body fragment (the artifact host supplies the document skeleton).
    out = HERE / "mech559-atlas.html"
    out.write_text(page.replace("<!--@home@-->", ""))
    # Site page: a full document, with a way back to the rest of on inspire.
    site = SITE / "index.html"
    site.parent.mkdir(parents=True, exist_ok=True)
    head, body = page.split('<a class="skip"', 1)
    site.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                    + head.replace("<title>MECH 559 Atlas</title>", "<title>MECH 559 Atlas · on inspire</title>")
                    + '</head>\n<body>\n<a class="skip"' + body.replace("<!--@home@-->", '<a class="home-link" href="../../">on inspire</a>') + "\n</body>\n</html>\n")
    n_prob = sum(len(c["problems"]) for c in concepts)
    print(f"built {site.relative_to(HERE.parent.parent)} and {out.name}: {len(concepts)} concepts, {n_prob} concept problems, {len(code_problems)} code problems, "
          f"{len(library)} library guides, {len(bugs)} bugs, {len(flows)} workflows, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
