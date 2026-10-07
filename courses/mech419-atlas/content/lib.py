"""Shared helpers for the MECH 419 atlas content.

Every symbolic answer is checked here at build time: a choice step built with sym_choice marks an
option correct only if SymPy finds it equivalent to the target, and the build fails unless exactly
one option is. Numeric answers are computed in Python, never typed in by hand.
"""
import math
import sympy as sp

# ---- symbols ---------------------------------------------------------------------------------
t = sp.Symbol("t")
x, xd, xdd = sp.symbols("x xd xdd")
y, yd, ydd = sp.symbols("y yd ydd")
z, zd, zdd = sp.symbols("z zd zdd")
r, rd, rdd = sp.symbols("r rd rdd")
th, thd, thdd = sp.symbols("th thd thdd")
m, M, k, l, g, c, b, F, f, R, l0, Om, I, a, m1, m2 = sp.symbols(
    "m M k l g c b F f R l0 Omega I a m1 m2", positive=True)
lam = sp.Symbol("lam")
pr, pth, px = sp.symbols("p_r p_theta p_x")
yp, ypp = sp.symbols("yp ypp")
eps = sp.Symbol("epsilon")

NAMES = {
    xd: r"\dot{x}", xdd: r"\ddot{x}", yd: r"\dot{y}", ydd: r"\ddot{y}", zd: r"\dot{z}", zdd: r"\ddot{z}",
    rd: r"\dot{r}", rdd: r"\ddot{r}", th: r"\theta", thd: r"\dot{\theta}", thdd: r"\ddot{\theta}",
    Om: r"\Omega", lam: r"\lambda", l0: r"\ell_0", l: r"\ell", yp: "y'", ypp: "y''",
    pr: "p_r", pth: r"p_\theta", px: "p_x", eps: r"\epsilon",
}
STATE = {x, xd, xdd, y, yd, ydd, z, zd, zdd, r, rd, rdd, th, thd, thdd, lam, pr, pth, px, yp, ypp}


def tex(e):
    return sp.latex(e, symbol_names=NAMES, order="none") if not isinstance(e, str) else e


# ---- mechanics helpers ----------------------------------------------------------------------
def ddt(e, coords):
    """Total time derivative along coords = [(q, qd, qdd), ...]."""
    return sp.expand(sum(sp.diff(e, q) * qd + sp.diff(e, qd) * qdd for q, qd, qdd in coords))


def lagrange(T, V, coords, Q=None):
    """Lagrange's equations, each written as an expression that must equal zero."""
    L = T - V
    out = []
    for i, (q, qd, qdd) in enumerate(coords):
        e = ddt(sp.diff(L, qd), coords) - sp.diff(L, q) - (Q[i] if Q else 0)
        out.append(sp.simplify(e))
    return out


def equiv_eq(a, b):
    """a = 0 and b = 0 say the same thing: their ratio is nonzero and free of state variables."""
    a, b = sp.sympify(a), sp.sympify(b)
    if a == 0 or b == 0:
        return a == b
    ratio = sp.simplify(a / b)
    return ratio != 0 and not (ratio.free_symbols & STATE)


def same(a, b):
    return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0


# ---- step builders --------------------------------------------------------------------------
def opt(label, correct=False, why=""):
    return {"label": label, "correct": bool(correct), "why": why}


def choice(prompt, options, explain=""):
    n = sum(o["correct"] for o in options)
    assert n == 1, f"choice needs exactly one correct option, got {n}: {prompt}"
    return {"type": "choice", "prompt": prompt, "options": options, "explain": explain}


def sym_choice(prompt, target, options, explain="", eq=False):
    """options = [(expr, why), ...]. Correctness is decided by SymPy, not by the author.

    eq=True: options are equations (shown with '= 0'), equal up to a nonzero constant factor.
    eq=False: options are values that must be identical to the target.
    """
    test = equiv_eq if eq else same
    built = []
    for e, why in options:
        ok = test(e, target)
        label = "$" + tex(sp.sympify(e)) + (" = 0" if eq else "") + "$"
        built.append(opt(label, ok, "" if ok else why))
    labels = [o["label"] for o in built]
    assert len(set(labels)) == len(labels), f"duplicate option labels: {prompt}"
    return choice(prompt, built, explain)


def num(prompt, answer, unit="", tol=0.01, explain="", hint=""):
    answer = float(answer)
    assert math.isfinite(answer), prompt
    return {"type": "num", "prompt": prompt, "answer": answer, "unit": unit, "tol": tol,
            "explain": explain, "hint": hint}


def problem(pid, title, stem, steps, fig=None, takeaway=""):
    return {"id": pid, "title": title, "stem": stem, "fig": fig, "steps": steps, "takeaway": takeaway}


def concept(cid, title, layer, group, body, deeper=(), math=(), analogy=None, exam="", widget=None,
            problems=(), source="", beyond=False):
    return {"id": cid, "title": title, "layer": layer, "group": group, "body": body.strip(),
            "deeper": list(deeper), "math": list(math), "analogy": analogy, "exam": exam.strip(),
            "widget": widget, "problems": list(problems), "source": source, "beyond": beyond}


def analogy(text, breaks):
    return {"text": text, "breaks": breaks}


def deg(v):
    return math.degrees(v)
