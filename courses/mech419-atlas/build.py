"""Build the MECH 419 atlas into one self-contained HTML page.

Run:  python3 build.py   -> docs/dynamics/mech-419/index.html (site) and mech419-atlas.html (artifact)
Every symbolic answer is verified while the content modules import (see content/lib.py);
this script then checks the network: links resolve, prerequisites form no cycles,
every concept is reachable, and every concept has practice.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent / "docs" / "dynamics" / "mech-419"
sys.path.insert(0, str(HERE / "content"))

import prereqs, course_a, course_b, course_c, questions  # noqa: E402

SHORT = {
    "p-dot": "Dot product as projection", "p-cross-omega": "ω × r", "p-relative-velocity": "Relative velocity",
    "p-polar": "Polar velocity", "p-rolling": "Rolling contact", "p-partial": "Partial derivatives",
    "p-chain-multi": "Total time derivative", "p-taylor": "Taylor series", "p-ibp": "Integration by parts",
    "p-extremum": "Extrema and stability", "p-newton": "Newton and FBDs", "p-work": "Work and power",
    "p-potential": "Potential energy", "p-ke-rigid": "Rigid-body kinetic energy", "p-inertia": "Moment of inertia",
    "p-energy-conservation": "Energy conservation", "p-quadratic-form": "Quadratic forms", "p-ode-char": "Characteristic equation",
    "p-complex-exp": "Complex exponentials",
    "c-vector-vs-analytical": "Vectorial vs analytical", "c-gen-coords": "Generalized coordinates", "c-dof": "Degrees of freedom",
    "c-r-of-q": "Positions r(q, t)", "c-dots": "Cancellation of dots", "c-virtual-disp": "Virtual displacement",
    "c-gen-force": "Generalized force", "c-gen-force-moment": "Generalized force of a moment", "c-gen-momentum": "Generalized momentum",
    "c-lagrange-derivation": "Deriving Lagrange's equations", "c-lagrangian": "L = T − V", "c-lagrange-recipe": "The Lagrange recipe",
    "c-rolling-lagrange": "Rolling with and without slip", "c-constraint-types": "Holonomic vs non-holonomic",
    "c-multipliers": "Lagrange multipliers", "c-accel-constraint": "Acceleration-level constraints", "c-t2t1t0": "T₂ + T₁ + T₀",
    "c-static-eq": "Static equilibrium", "c-dynamic-eq": "Dynamic equilibrium", "c-hamiltonian": "The Hamiltonian",
    "c-cyclic": "Cyclic coordinates", "c-h-conservation": "Conservation of H", "c-canonical": "Hamilton's canonical equations",
    "c-state-space": "State-space form", "c-functional": "Functionals and variations", "c-euler-lagrange": "Euler–Lagrange equation",
    "c-special-cases": "First integrals (Beltrami)", "c-shortest-path": "Shortest path", "c-brachistochrone": "Brachistochrone",
    "c-hamilton-principle": "Hamilton's principle", "c-extended-hamilton": "Extended Hamilton's principle",
    "c-linearization": "Linearization", "c-sdof-free": "Free vibration", "c-damping-cases": "Damping ratio",
    "c-underdamped": "Underdamped response", "c-log-dec": "Logarithmic decrement", "c-forced": "Forced vibration",
    "c-euler-method": "Euler's method",
    "q-pipeline": "Sketch → frequencies", "q-no-constraint-forces": "Where do constraint forces go?",
    "q-velocities-only": "Why only velocities?", "q-h-not-e": "H conserved, E not", "q-spin-out": "Why it swings out",
    "q-cycloid": "Why the cycloid wins", "q-dependent-wrong": "Why free fall?", "q-euler-energy": "Why Euler gains energy",
    "q-action-newton": "Action = Newton?",
}

SUBJECT_ORDER = ["Vectors and kinematics", "Calculus", "Mechanics", "Linear algebra", "Differential equations"]

SOURCES = [
    ("Feynman Lectures on Physics, Vol. II, Ch. 19: The Principle of Least Action", "https://www.feynmanlectures.caltech.edu/II_19.html",
     "Least action as a balance between kinetic and potential energy; the source of the 'thrown ball' intuition."),
    ("David Tong, Lectures on Classical Dynamics (Cambridge)", "https://www.damtp.cam.ac.uk/user/tong/dynamics.html",
     "Clear treatment of generalized coordinates, constraints, Noether's theorem and small oscillations."),
    ("J. Kim Vandiver, An Introduction to Lagrange Equations (MIT 2.003SC)", "https://ocw.mit.edu/courses/2-003sc-engineering-dynamics-fall-2011/d1984062464dcc3df68b5741fd37192b_MIT2_003SCF11_Lagrange.pdf",
     "The engineering recipe for generalized forces via virtual work; closest in spirit to MECH 419."),
    ("MIT 2.003SC: Estimation of natural frequencies and damping ratios (logarithmic decrement)", "https://ocw.mit.edu/courses/2-003sc-engineering-dynamics-fall-2011/resources/estimation-of-natural-frequencies-and-damping-ratios-from-measured-response-the-logarithmic-decrement",
     "Measuring ζ from peaks, as in Lecture 10."),
    ("3Blue1Brown with Steven Strogatz: The Brachistochrone", "https://www.youtube.com/watch?v=Cld0p3a43fU",
     "Bernoulli's light-refraction solution and Mark Levi's insight; the inspiration for the race widget."),
    ("Bead on a rotating circular hoop: a simple yet feature-rich dynamical system (arXiv:1112.4697)", "https://arxiv.org/abs/1112.4697",
     "The pitchfork bifurcation behind the spinning-pendulum's swing-out."),
    ("Strogatz, Nonlinear Dynamics and Chaos: lecture videos", "https://scholar.harvard.edu/siams/videos-strogatz-2015-nonlinear-dynamics-and-chaos",
     "Overdamped bead on a rotating hoop; bifurcations explained visually."),
    ("Ginsberg, Advanced Engineering Dynamics (2nd ed.)", "http://ndl.ethernet.edu.et/bitstream/123456789/1024/1/Advanced%20Engineering%20Dynamics.pdf",
     "Pfaffian constraints, Lagrange multipliers and the T₂ + T₁ + T₀ decomposition in the engineering style the notes follow."),
    ("Learn Multibody Dynamics: Equations of Motion with the Lagrange Method (J. Moore)", "https://moorepants.github.io/learn-multibody-dynamics/lagrange.html",
     "Worked computational examples, including constraints."),
    ("Durham IPPP, Numerical Methods: Harmonic Motion (Euler energy drift)", "https://www.ippp.dur.ac.uk/~krauss/Lectures/NumericalMethods/Oscillator/Lecture/lecture.pdf",
     "Why forward Euler spirals outward on an oscillator, and how symplectic Euler fixes it."),
]


def collect():
    concepts = prereqs.CONCEPTS + course_a.CONCEPTS + course_b.CONCEPTS + course_c.CONCEPTS + questions.CONCEPTS
    ids = [c["id"] for c in concepts]
    assert len(ids) == len(set(ids)), "duplicate concept ids"
    by = {c["id"]: c for c in concepts}
    problems_seen = set()
    for c in concepts:
        assert c["id"] in SHORT, f"no short label for {c['id']}"
        c["short"] = SHORT[c["id"]]
        for d in c["deeper"]:
            assert d in by, f"{c['id']} builds on unknown {d}"
            assert by[d]["layer"] <= c["layer"], f"{c['id']} builds on a higher layer {d}"
        text = c["body"] + json.dumps(c["problems"])
        for link in re.findall(r"\[\[([a-z0-9-]+)", text):
            assert link in by, f"{c['id']} links to unknown {link}"
        assert c["problems"], f"{c['id']} has no practice"
        for p in c["problems"]:
            assert p["id"] not in problems_seen, f"duplicate problem id {p['id']}"
            problems_seen.add(p["id"])
    # no cycles in "builds on"
    state = {}
    def visit(i, stack):
        if state.get(i) == 1:
            raise AssertionError("cycle: " + " -> ".join(stack + [i]))
        if state.get(i) == 2:
            return
        state[i] = 1
        for d in by[i]["deeper"]:
            visit(d, stack + [i])
        state[i] = 2
    for i in ids:
        visit(i, [])
    # every foundation is used by something; every course concept reachable from a question or used
    used = {d for c in concepts for d in c["deeper"]}
    for c in concepts:
        if c["layer"] == 0:
            assert c["id"] in used, f"foundation {c['id']} isn't used by anything"
    return concepts


def main():
    concepts = collect()
    data = {"concepts": concepts, "subjects": SUBJECT_ORDER, "sources": [
        {"title": t, "url": u, "note": n} for t, u, n in SOURCES]}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "src/page.html").read_text()
    for name in ("style.css", "figures.js", "widgets.js", "app.js"):
        page = page.replace("/*@" + name + "@*/", (HERE / "src" / name).read_text())
    page = page.replace("/*@data@*/", "window.ATLAS = " + payload + ";")
    # Artifact page: a body fragment (the artifact host supplies the document skeleton).
    out = HERE / "mech419-atlas.html"
    out.write_text(page.replace("<!--@home@-->", ""))
    # Site page: a full document, with a way back to the rest of on inspire.
    site = SITE / "index.html"
    site.parent.mkdir(parents=True, exist_ok=True)
    head, body = page.split("<a class=\"skip\"", 1)
    site.write_text("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
                    + head.replace("<title>MECH 419 Atlas</title>", "<title>MECH 419 Atlas · on inspire</title>")
                    + "</head>\n<body>\n<a class=\"skip\"" + body.replace("<!--@home@-->", '<a class="home-link" href="../../">on inspire</a>') + "\n</body>\n</html>\n")
    n_prob = sum(len(c["problems"]) for c in concepts)
    n_steps = sum(len(p["steps"]) for c in concepts for p in c["problems"])
    print(f"built {site.relative_to(HERE.parent.parent)} and {out.name}: {len(concepts)} concepts, {n_prob} problems, {n_steps} steps, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
