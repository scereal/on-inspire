"""Build the MECH 430 atlas into one self-contained HTML page.

    python3 build.py

Importing the content runs every check: content/gas.py reproduces the worked examples in the notes,
numeric answers are computed (never typed), symbolic choices are graded by SymPy, dials are checked
against their models, and every coding exercise is run against its tests (the reference passes, the
deliberately wrong versions fail). This script then checks the concept network and writes
docs/fluids/mech-430/index.html (the site page), mech430-atlas.html (the artifact page, a body fragment)
and code/gas_checks.json (reference values the
browser test compares src/gas.js against).
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent / "docs" / "fluids" / "mech-430"
sys.path.insert(0, str(HERE / "content"))

import gas  # noqa: E402
import prereqs, ch_a, ch_b, ch_c, ch_d, ch_e, questions  # noqa: E402

SHORT = {
    "p-ideal-gas": "Ideal gas", "p-calorically-perfect": "Calorically perfect gas", "p-first-law": "First law, enthalpy",
    "p-entropy-isentropic": "Entropy, isentropic relations", "p-bernoulli": "Bernoulli", "p-momentum": "Momentum balance",
    "p-galilean": "Reference frames", "p-log-differentiation": "Log differentiation", "p-root-finding": "Root finding",
    "p-pdes": "PDE types", "p-python": "Python basics",
    "c-compressible-what": "What 'compressible' means", "c-control-volume": "Mass in a control volume", "c-cv-momentum": "Momentum and thrust",
    "c-cv-energy": "Energy, h + V²/2", "c-1d-terms": "Steady, uniform, stream tube", "c-1d-integral": "1-D integral forms",
    "c-1d-differential": "1-D differential forms", "c-sound-derivation": "Deriving the sound speed", "c-sound-ideal-gas": "c = √(γRT)",
    "c-mach-number": "Mach number", "c-mach-cone": "Mach cone",
    "c-area-velocity": "Area change, sub vs super", "c-stagnation": "Stagnation conditions", "c-sonic-reference": "Sonic conditions",
    "c-choking": "Choking", "c-area-ratio": "A/A*", "c-reference-state-method": "Reference-state method", "c-compressibility": "When Bernoulli breaks",
    "c-converging-nozzle": "Converging nozzle", "c-cd-nozzle-isentropic": "C-D nozzle, isentropic", "c-rocket-thrust": "Rocket thrust",
    "c-optimal-expansion": "Optimal expansion", "c-isp-max-velocity": "Maximum velocity, Isp", "c-altitude-compensation": "Altitude compensation",
    "c-shock-formation": "How shocks form", "c-normal-shock-relations": "Normal shock relations", "c-shock-entropy": "Entropy and p₀ loss",
    "c-strong-weak-shocks": "Strong and weak shocks", "c-shock-in-nozzle": "Shock in a nozzle", "c-back-pressure-regimes": "Back-pressure regimes",
    "c-moving-shocks": "Moving shocks, pistons", "c-pitot": "Pitot probes", "c-supersonic-inlet": "Supersonic inlets", "c-wind-tunnel": "Wind tunnels",
    "c-shinkansen": "Train in a tunnel",
    "c-fanno-effects": "Friction's effects", "c-fanno-relations": "Fanno relations, L*", "c-fanno-choking": "Frictional choking",
    "c-rayleigh-effects": "Heating's effects", "c-rayleigh-relations": "Rayleigh relations", "c-thermal-choking": "Thermal choking",
    "c-oblique-from-normal": "Oblique from normal", "c-theta-beta-mach": "δ–σ–M relation", "c-shock-reflection": "Regular reflection",
    "c-shock-polars": "Shock polars", "c-mach-reflection": "Mach reflection", "c-expansion-fan": "Expansion fans",
    "c-prandtl-meyer": "Prandtl–Meyer function", "c-over-under-expanded": "Over/underexpanded jets", "c-pde-types": "Elliptic vs hyperbolic",
    "c-characteristics": "Characteristics", "c-moc-unit-processes": "MOC unit processes", "c-moc-breakdown": "When MOC breaks",
    "q-three-chokes": "Three ways to choke", "q-what-survives": "What survives a shock", "q-frames": "Reference frames",
    "q-whole-nozzle": "The whole nozzle story", "q-p0-entropy": "p₀ loss is entropy", "q-information": "Can the flow hear?",
    "q-hysteresis": "Hysteresis twice",
}
SUBJECTS = ["Thermodynamics", "Fluids 1", "Mechanics", "Calculus and numerics", "Python"]
SOURCES = [
    ("A. J. Higgins, Compressible Fluids Notes (MECH 430 course notes package)", "",
     "The structure, notation, examples and every worked number follow these notes; the atlas reproduces each numerical example at build time."),
    ("MECH 430 Problem Sets 1–4 (2026)", "", "The skills each problem set exercises are taught here on different numbers and gases, so no problem-set answers appear."),
    ("J. D. Anderson, Modern Compressible Flow, 3rd ed.", "", "Recommended in the notes for its historical narratives; used to cross-check relations."),
    ("NASA Glenn Research Center, Beginner's Guide to Aeronautics: compressible flow and rocket thrust pages", "https://www.grc.nasa.gov/www/k-12/airplane/", "The thrust summary slide referenced in Problem Set 4."),
    ("Skulpt, Python in the browser", "https://skulpt.org/", "Runs the coding exercises on this page (loaded from cdn.jsdelivr.net only when you open one)."),
    ("M. Van Dyke, An Album of Fluid Motion", "", "Source of several photographs reproduced in the notes (schlieren, characteristics made visible)."),
]
LINK_RE = re.compile(r"\[\[([a-z][a-z0-9]*-[a-z0-9-]+)")


def collect():
    concepts = prereqs.CONCEPTS + ch_a.CONCEPTS + ch_b.CONCEPTS + ch_c.CONCEPTS + ch_d.CONCEPTS + ch_e.CONCEPTS + questions.CONCEPTS
    by = {c["id"]: c for c in concepts}
    assert len(by) == len(concepts), "duplicate concept id"
    pids = set()
    for c in concepts:
        assert c["id"] in SHORT, f"no short label for {c['id']}"
        c["short"] = SHORT[c["id"]]
        for d in c["deeper"]:
            assert d in by, f"{c['id']} builds on unknown {d}"
            assert by[d]["layer"] <= c["layer"], f"{c['id']} builds on a higher layer ({d})"
        assert c["problems"], f"{c['id']} has no practice"
        for p in c["problems"]:
            assert p["id"] not in pids, f"duplicate problem id {p['id']}"
            pids.add(p["id"])
        for link in LINK_RE.findall(json.dumps(c)):
            assert link in by, f"{c['id']} links to unknown [[{link}]]"
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


def gas_checks():
    """Reference values for the JS mirror, over the useful range of each function."""
    out = []
    Ms = [0.05, 0.2, 0.5, 0.8, 0.95, 1.0, 1.05, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0]
    Msup = [m for m in Ms if m > 1]
    for g in (1.4, 5 / 3, 1.25):
        for M in Ms:
            for fn in ("T0_T", "p0_p", "r0_r", "A_Astar", "mass_flux", "fanno_fL", "fanno_T", "fanno_p", "fanno_p0", "ray_p", "ray_T", "ray_T0", "ray_p0"):
                out.append([fn, [M, g], getattr(gas, fn)(M, g)])
        for M in Msup:
            for fn in ("ns_M2", "ns_p2p1", "ns_r2r1", "ns_T2T1", "ns_p02p01", "pitot_ratio", "pm_nu"):
                out.append([fn, [M, g], getattr(gas, fn)(M, g)])
        for ar in (1.2, 2.0, 5.0):
            out.append(["M_from_AR", [ar, False, g], gas.M_from_AR(ar, False, g)])
            out.append(["M_from_AR", [ar, True, g], gas.M_from_AR(ar, True, g)])
    for M in (1.5, 2.0, 3.0, 5.0):
        for d in (5.0, 10.0, 20.0):
            if d < gas.ob_max(M)[0]:
                out.append(["ob_sigma", [M, d, False], gas.ob_sigma(M, d)])
        out.append(["ob_max", [M], gas.ob_max(M)[0]])
    for nu in (10.0, 26.38, 60.0):
        out.append(["pm_M", [nu], gas.pm_M(nu)])
    for AeAt, pb in ((3.0, 0.7), (2.5, 0.75), (3.0, 0.98), (3.0, 0.2), (3.0, 0.02), (4.0, 0.5)):
        n = gas.nozzle(AeAt, pb)
        out.append(["nozzle.As" if n["regime"] == "shock" else "nozzle.pd", [AeAt, pb], n.get("As", n["pd"])])
    for v in (0.1, 0.5, 2.0):
        out.append(["piston_shock_mach", [v], gas.piston_shock_mach(v)])
    for fl in (0.1, 1.0):
        out.append(["fanno_M", [fl, False], gas.fanno_M(fl, False)])
    out.append(["fanno_M", [0.2, True], gas.fanno_M(0.2, True)])
    out.append(["ray_M", [0.8, False], gas.ray_M(0.8, False)])
    out.append(["ray_M", [0.8, True], gas.ray_M(0.8, True)])
    return out


def main():
    concepts = collect()
    code_steps = [{"concept": c["id"], "problem": p["id"], "index": i}
                  for c in concepts for p in c["problems"] for i, s in enumerate(p["steps"]) if s["type"] == "code"]
    data = {"concepts": concepts, "subjects": SUBJECTS, "codeSteps": code_steps,
            "sources": [{"title": t, "url": u, "note": n} for t, u, n in SOURCES],
            "notesDiscrepancy": {"deltaMaxLimitNotes": gas.DELTA_MAX_LIMIT_NOTES, "deltaMaxLimitExact": math.degrees(math.asin(1 / 1.4))}}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "src/page.html").read_text()
    for name in ("style.css", "gas.js", "widgets.js", "app.js"):
        page = page.replace("/*@" + name + "@*/", (HERE / "src" / name).read_text())
    page = page.replace("/*@data@*/", "window.ATLAS = " + payload + ";")
    out = HERE / "mech430-atlas.html"
    out.write_text(page.replace("<!--@home@-->", ""))
    # Site page: a full document, with a way back to the rest of on inspire.
    site = SITE / "index.html"
    site.parent.mkdir(parents=True, exist_ok=True)
    head, body = page.split('<a class="skip"', 1)
    site.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                    + head.replace("<title>MECH 430 Atlas</title>", "<title>MECH 430 Atlas · on inspire</title>")
                    + '</head>\n<body>\n<a class="skip"' + body.replace("<!--@home@-->", '<a class="home-link" href="../../">on inspire</a>') + "\n</body>\n</html>\n")
    (HERE / "code").mkdir(exist_ok=True)
    (HERE / "code" / "gas_checks.json").write_text(json.dumps(gas_checks()))
    steps = [s for c in concepts for p in c["problems"] for s in p["steps"]]
    kinds = {}
    for s in steps:
        kinds[s["type"]] = kinds.get(s["type"], 0) + 1
    n_prob = sum(len(c["problems"]) for c in concepts)
    print(f"built {site.relative_to(HERE.parent.parent)} and {out.name}: {len(concepts)} concepts, {n_prob} problems, {len(steps)} steps {kinds}, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
