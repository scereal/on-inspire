"""Shared helpers for the MECH 430 atlas content (forked from the MECH 559 and MECH 419 atlases).

Numeric answers are computed with content/gas.py (which checks itself against the notes) or SymPy,
never typed in by hand. Symbolic choices are graded by SymPy, and code exercises are run against
their own tests at build time, including deliberately wrong versions that the tests must reject.
"""
import math
import re
import sympy as sp

# ---- symbols ---------------------------------------------------------------------------------
M, M1, M2, Mx, My = sp.symbols("M M1 M2 Mx My", positive=True)
g = sp.Symbol("gamma", positive=True)
T, T0, p, p0, rho, V, A, Astar, R, cp, cv, h, q, x, c, dV, dA, dp, drho = sp.symbols(
    "T T0 p p0 rho V A Astar R c_p c_v h q x c dV dA dp drho", positive=True)
sigma, delta, theta, nu, alpha = sp.symbols("sigma delta theta nu alpha", positive=True)

NAMES = {g: r"\gamma", Astar: "A^*", rho: r"\rho", sigma: r"\sigma", delta: r"\delta", theta: r"\theta",
         nu: r"\nu", alpha: r"\alpha", T0: "T_0", p0: "p_0", M1: "M_1", M2: "M_2", Mx: "M_x", My: "M_y",
         dV: "dV", dA: "dA", dp: "dp", drho: r"d\rho"}


def tex(e):
    return sp.latex(e, symbol_names=NAMES) if not isinstance(e, str) else e


def same(a, b):
    return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0


# ---- step builders --------------------------------------------------------------------------
def opt(label, correct=False, why=""):
    return {"label": label, "correct": bool(correct), "why": why}


def choice(prompt, options, explain=""):
    n = sum(o["correct"] for o in options)
    assert n == 1, f"choice needs exactly one correct option, got {n}: {prompt}"
    assert all(o["why"] for o in options if not o["correct"]), f"every wrong option needs a reason: {prompt}"
    return {"type": "choice", "prompt": prompt, "options": options, "explain": explain}


def sym_choice(prompt, target, options, explain=""):
    """options = [(expr, why), ...]; SymPy decides which one equals the target."""
    built = []
    for e, why in options:
        ok = same(e, target)
        built.append(opt("$" + tex(sp.sympify(e)) + "$", ok, "" if ok else why))
    return choice(prompt, built, explain)


def num(prompt, answer, unit="", tol=0.01, explain="", hint=""):
    answer = float(answer)
    assert math.isfinite(answer), prompt
    return {"type": "num", "prompt": prompt, "answer": answer, "unit": unit, "tol": tol, "explain": explain, "hint": hint}


def blank(prompt, answers, explain="", hint="", mode="text", placeholder=""):
    """Type a short answer. mode="code": whitespace ignored, case-sensitive. mode="text": case and spacing ignored."""
    answers = [answers] if isinstance(answers, str) else list(answers)
    assert answers and all(a.strip() for a in answers), prompt
    return {"type": "blank", "prompt": prompt, "answers": answers, "mode": mode, "explain": explain, "hint": hint, "placeholder": placeholder}


def spot(prompt, lines, explain="", code=False):
    """Find the mistake: lines = [(text, is_wrong, why), ...], exactly one wrong."""
    assert sum(1 for _, w, _ in lines if w) == 1, f"spot needs exactly one wrong line: {prompt}"
    assert all(why for _, w, why in lines if w), "the wrong line needs an explanation"
    return {"type": "spot", "prompt": prompt, "code": code, "explain": explain,
            "lines": [{"text": t, "wrong": bool(w), "why": why} for t, w, why in lines]}


def order(prompt, items, explain=""):
    assert len(items) >= 3 and len(set(items)) == len(items), prompt
    return {"type": "order", "prompt": prompt, "items": list(items), "explain": explain}


EXPR_OK = re.compile(r"[0-9a-zA-Z_+\-*/(). ,]+")


def expr(prompt, answer, variables, explain="", hint="", ranges=None):
    """Type a math expression; the browser parses it (no eval) and compares it with `answer` at random points."""
    answer = sp.sympify(answer)
    names = [str(v) for v in variables]
    assert {str(s) for s in answer.free_symbols} <= set(names), f"{answer} uses symbols beyond {names}"
    typed = sp.sstr(answer)
    assert EXPR_OK.fullmatch(typed), typed
    return {"type": "expr", "prompt": prompt, "ref": typed, "vars": names, "tex": tex(answer),
            "ranges": ranges or {n: [0.5, 2.5] for n in names}, "explain": explain, "hint": hint}


# ---- dial: set a live model to hit a target ------------------------------------------------------
import gas as _gas  # noqa: E402

DIAL_MODELS = {
    # name: (python function of (x, args), what the readout shows)
    "A_Astar": (lambda x, a: _gas.A_Astar(x, a.get("g", 1.4)), "A/A*"),
    "p_p0": (lambda x, a: 1 / _gas.p0_p(x, a.get("g", 1.4)), "p/p₀"),
    "T_T0": (lambda x, a: 1 / _gas.T0_T(x, a.get("g", 1.4)), "T/T₀"),
    "mass_flux": (lambda x, a: _gas.mass_flux(x) / _gas.mass_flux(1.0), "ṁ/ṁ_max"),
    "ns_p2p1": (lambda x, a: _gas.ns_p2p1(x), "p₂/p₁"),
    "ns_p02p01": (lambda x, a: _gas.ns_p02p01(x), "p₀₂/p₀₁"),
    "fanno_fL": (lambda x, a: _gas.fanno_fL(x), "4fL*/D"),
    "ray_T0": (lambda x, a: _gas.ray_T0(x), "T₀/T₀*"),
    "pm_nu": (lambda x, a: _gas.pm_nu(x), "ν (degrees)"),
    "mach_angle": (lambda x, a: _gas.mach_angle(x), "μ (degrees)"),
    "ob_delta": (lambda x, a: _gas.ob_delta(a["M"], x), "deflection δ (degrees)"),
    "nozzle_shock": (lambda x, a: (_gas.nozzle(a["AeAt"], x).get("As") or float("nan")), "shock at A/A_t"),
    "piston": (lambda x, a: _gas.piston_shock_mach(x / a["c"]), "shock Mach number"),
}


def dial(prompt, model, target, lo, hi, step, answer, args=None, var="x", unit="", tol=0.01, explain=""):
    """Move a slider until the model's output hits `target`. `answer` is checked against the model here."""
    args = args or {}
    f, shows = DIAL_MODELS[model]
    got = f(answer, args)
    assert abs(got - target) <= 1e-3 * max(1, abs(target)), f"dial {model}({answer}) = {got}, not {target}"
    assert lo <= answer <= hi, (lo, answer, hi)
    return {"type": "dial", "prompt": prompt, "model": model, "args": args, "target": target, "lo": lo, "hi": hi,
            "step": step, "answer": float(answer), "var": var, "unit": unit, "tol": tol, "shows": shows, "explain": explain}


# ---- code: write a Python function that runs in the browser (Skulpt) -----------------------------
HARNESS = '''
_results = []
def check(label, got, want, tol=1e-3):
    try:
        ok = abs(got - want) <= tol * max(1.0, abs(want))
    except Exception:
        ok = False
    _results.append((label, ok, got, want))
'''
REPORT = '''
for _r in _results:
    print(("PASS " if _r[1] else "FAIL ") + _r[0] + " | got " + str(_r[2]) + " | want " + str(_r[3]))
'''


def run_tests(src, tests):
    ns = {}
    exec(compile(HARNESS + "\n" + src + "\n" + tests, "<exercise>", "exec"), ns)
    return ns["_results"]


def code(prompt, starter, solution, tests, wrong=(), hints=(), explain="", fn=""):
    """A coding step. The solution must pass every check; every wrong version must fail at least one.

    Restricted to what runs in Skulpt: plain Python 3, the math module, no numpy and no f-strings.
    """
    for label, src in (("solution", solution), *(("wrong", w) for w in wrong)):
        assert "f\"" not in src and "f'" not in src, "no f-strings (Skulpt)"
        assert "import numpy" not in src and "import scipy" not in src, "plain Python only (Skulpt)"
    res = run_tests(solution, tests)
    assert res and all(ok for _, ok, _, _ in res), f"reference solution fails its tests: {[r for r in res if not r[1]]}"
    for w in wrong:
        try:
            wr = run_tests(w, tests)
            assert not all(ok for _, ok, _, _ in wr), f"tests don't catch this wrong version:\n{w}"
        except AssertionError:
            raise
        except Exception:
            pass  # a crash also counts as caught
    assert wrong, "give at least one wrong version so the tests are known to bite"
    return {"type": "code", "prompt": prompt, "starter": starter.strip("\n"), "solution": solution.strip("\n"),
            "tests": tests.strip("\n"), "wrong": [w.strip("\n") for w in wrong], "hints": list(hints), "explain": explain,
            "fn": fn, "harness": HARNESS, "report": REPORT, "n_checks": len(res)}


# ---- problems and concepts ---------------------------------------------------------------------
def problem(pid, title, stem, steps, kind="", takeaway=""):
    """kind: '' (practice), 'notes' (a worked example from the notes), 'variant' (an assignment skill on new numbers)."""
    assert kind in ("", "notes", "variant"), kind
    return {"id": pid, "title": title, "stem": stem, "steps": steps, "kind": kind, "takeaway": takeaway, "fig": None}


def concept(cid, title, layer, group, body, deeper=(), math=(), analogy=None, exam="", widget=None,
            problems=(), source="", terms=()):
    return {"id": cid, "title": title, "layer": layer, "group": group, "body": body.strip(), "deeper": list(deeper),
            "math": list(math), "analogy": analogy, "exam": exam.strip(), "widget": widget, "problems": list(problems),
            "source": source, "terms": list(terms)}


def analogy(text, breaks):
    return {"text": text, "breaks": breaks}


def r3(v):
    return float(f"{v:.4g}")
