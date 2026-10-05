"""Limits (MATH 140, outcomes 140.2.1–140.2.3). Plan: design/plans/2026-10-05-math-140-limits.md.

Level 1: read a limit from a table of values (sin kx / x and friends).
Level 2: one-sided limits from a graph (jumps and holes).
Level 3: 0/0 by factoring and cancelling.
Level 4: 0/0 with a square root, by the conjugate.
Level 5: the squeeze theorem (bounded oscillation times something that vanishes).
Level 6: limits at infinity of rational functions.
Level 7: vertical asymptotes and infinite one-sided limits.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x = sp.Symbol("x")
MAX_DEN = 20


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):g}")


def tex(e):
    return f"${sp.latex(e)}$"


def key(e):
    return sp.sstr(sp.simplify(e))


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 200


def factor(v):
    """The factor that vanishes at x = v, as TeX: (x - 3), (x + 4), or x."""
    return f"({sp.latex(x - v)})" if v else "x"


def tolerance(v):
    return 0.005 if abs(float(v)) < 1 else 0.01


# Level 1 ----------------------------------------------------------------------------

def table_function(p):
    u, k, m = x - p["a"], p["k"], p["m"]
    inner = {
        "sin": sp.sin(k * u) / u,
        "tan": sp.tan(k * u) / u,
        "exp": (sp.exp(k * u) - 1) / u,
        "pow": ((1 + u) ** k - 1) / u,
        "root": (sp.sqrt(u + k**2) - k) / u,
    }[p["kind"]]
    return m * inner


def table_limit(p):
    k, m = sp.Integer(p["k"]), sp.Integer(p["m"])
    return m / (2 * k) if p["kind"] == "root" else m * k


def table_tex(p):
    f = table_function(p)
    a = sp.Integer(p["a"])
    rows = []
    for d in ["-0.1", "-0.01", "-0.001", None, "0.001", "0.01", "0.1"]:
        if d is None:
            rows.append(f"{a} & \\text{{undefined}}")
            continue
        xv = a + sp.Rational(d)
        rows.append(f"{float(xv):g} & {float(f.subs(x, xv)):.6g}")
    return "\\begin{array}{c|c} x & f(x) \\\\ \\hline " + " \\\\ ".join(rows) + " \\end{array}"


# Level 2 ----------------------------------------------------------------------------

def sides(p):
    a = p["a"]
    return p["m1"] * a + p["b1"], p["m2"] * a + p["b2"]


def value_at(p):
    left, right = sides(p)
    if p["family"] == "removable":
        return p.get("c")
    return {"left": left, "right": right}.get(p.get("dot"), p.get("c"))


def graph_scene(p):
    a = p["a"]
    left, right = sides(p)
    fa = value_at(p)
    lo, hi = a - 3, a + 3
    ys = [p["m1"] * lo + p["b1"], left, right, p["m2"] * hi + p["b2"]] + ([fa] if fa is not None else [])
    dots = []
    for y in {left, right}:
        if y != fa:
            dots.append({"x": a, "y": y, "open": True})
    if fa is not None:
        dots.append({"x": a, "y": fa, "open": False})
    return {"type": "graph", "xmin": lo, "xmax": hi, "ymin": min(-1, min(ys) - 1), "ymax": max(1, max(ys) + 1), "mark": a,
            "pieces": [[[lo, p["m1"] * lo + p["b1"]], [a, left]], [[a, right], [hi, p["m2"] * hi + p["b2"]]]],
            "dots": dots, "label": f"Graph of f near x = {a}"}


# Level 4 ----------------------------------------------------------------------------

def root_parts(p):
    d, a, m = sp.Integer(p["d"]), sp.Integer(p["a"]), sp.Integer(p["m"])
    root = sp.sqrt(x + d**2 - a)
    return root, d, a, m


# Level 5 ----------------------------------------------------------------------------

def squeeze_function(p):
    trig = {"sin": sp.sin, "cos": sp.cos}[p["trig"]]
    c, k = sp.Integer(p["c"]), sp.Integer(p["k"])
    if p["family"] == "zero":
        return c + x ** p["n"] * trig(k / x)
    return (c * x + trig(k * x)) / x


# Level 6 ----------------------------------------------------------------------------

def rational_parts(p):
    top = sum(sp.Integer(cf) * x ** (2 - i) for i, cf in enumerate(p["a"]))
    bottom = sum(sp.Integer(cf) * x ** (2 - i) for i, cf in enumerate(p["b"]))
    return top, bottom


def show_limit(v):
    return {sp.oo: "\\infty", -sp.oo: "-\\infty"}.get(v, sp.latex(v))


def value_key(v):
    return {sp.oo: "oo", -sp.oo: "-oo"}.get(v, num(v))


class Limits(Framework):
    id = "limits"
    title = "Limits"
    outcome = "Find limits from tables and graphs, compute them with algebra, and handle infinity."
    levels = {
        1: Level("Limits from a table", {"read-table": 1, "value-not-needed": 1}),
        2: Level("One-sided limits", {"one-sided": 1, "two-sided": 1}),
        3: Level("Factor and cancel", {"substitute": 1, "factor-cancel": 1, "evaluate": 1}),
        4: Level("Rationalize with the conjugate", {"conjugate": 1, "simplify": 1, "evaluate": 1}),
        5: Level("The squeeze theorem", {"why-not-split": 1, "bounds": 1, "squeeze": 1}),
        6: Level("Limits at infinity", {"dominant-terms": 1, "horizontal-asymptote": 1}),
        7: Level("Vertical asymptotes", {"locate-asymptote": 1, "one-sided-infinite": 2}),
    }
    misconceptions = {
        "limit-needs-value": "Thought a limit needs a value at the point itself. It only uses values near the point.",
        "top-is-zero": "Took the limit to be 0 because the top is 0 at the point, ignoring the bottom.",
        "sides-swapped": "Swapped the left-hand and right-hand limits.",
        "limit-is-value": "Read the limit off the filled dot (the value f(a)) instead of where the graph is heading.",
        "dot-is-right-side": "Used the filled dot as one side's limit.",
        "average-of-sides": "Averaged two different one-sided limits. When they disagree, there is no limit.",
        "hole-means-no-limit": "Thought a hole at the point stops the limit. Both sides still head to the same height.",
        "zero-over-zero-is-0": "Took 0/0 to be 0. It's a signal to simplify, not a value.",
        "zero-over-zero-dne": "Took 0/0 to mean no limit. It means the algebra isn't finished.",
        "wrong-root-sign": "Factored with the wrong signs: a root at x = r gives the factor (x − r).",
        "kept-cancelled-factor": "Kept the factor that cancels and dropped the one that stays.",
        "dropped-denominator": "Removed the bottom without dividing the top by it.",
        "same-not-conjugate": "Multiplied by the same expression instead of the conjugate (flip the sign in the middle).",
        "wrong-factor": "Multiplied by a factor that doesn't remove the square root.",
        "blamed-wrong-factor": "Blamed the factor that behaves well; the trouble is the oscillating one.",
        "oscillation-has-limit": "Assumed an oscillating function settles down. sin and cos of something growing never do.",
        "bounds-dont-meet": "Used bounds that are true but approach different values, so they squeeze nothing.",
        "lower-bound-too-high": "Picked a lower bound the function actually dips below.",
        "constant-terms": "Divided the constant terms. Far out, the highest powers dominate.",
        "top-grows-so-infinity": "Saw the top grow and concluded infinity, forgetting the bottom grows too.",
        "ratio-regardless-of-degree": "Divided the leading coefficients even though the degrees differ.",
        "sign-of-infinity": "Got the sign of infinity wrong: check the sign of each leading term for that direction.",
        "top-zero-is-asymptote": "Put the asymptote where the top is zero. That's where the graph crosses the axis.",
        "hole-is-asymptote": "Called a cancelling factor an asymptote. It leaves a hole instead.",
        "sign-of-root": "Got the sign of the root wrong: (x − a) is zero at x = a.",
        "tiny-bottom-small-answer": "Thought dividing by a tiny number gives something tiny. It gives something huge.",
        "sign-slip": "Lost track of the sign in the conjugate after simplifying.",
        "flipped": "Put the simplified expression on the wrong side of the fraction bar.",
    }
    targets = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        if level == 1:
            kind = rng.choice(["sin", "tan", "exp", "pow", "root"])
            k = rng.randint(2, 6) if kind in ("sin", "pow") else rng.randint(1, 5) if kind in ("exp", "root") else rng.randint(2, 5)
            return {"kind": kind, "k": k, "a": rng.randint(-2, 3), "m": rng.choice([1, 1, -1, 2])}
        if level == 2:
            family = rng.choice(["jump", "jump", "removable"])
            p = {"family": family, "a": rng.randint(-2, 2), "m1": rng.randint(-2, 2), "b1": rng.randint(-2, 4),
                 "m2": rng.randint(-2, 2), "b2": rng.randint(-2, 4)}
            if family == "jump":
                p["dot"] = rng.choice(["left", "right", "other"])
                p["c"] = rng.randint(-2, 5)
            else:
                left, _ = sides(p)
                p["b2"] = left - p["m2"] * p["a"]           # make the pieces meet
                p["c"] = rng.choice([None, rng.randint(-2, 5)])
            return p
        if level == 3:
            family = rng.choice(["lin", "lin", "quad"])
            return {"family": family, "k": rng.choice([1, 1, 2, 3, -1, -2]), "a": rng.randint(-4, 4),
                    "r": rng.randint(-5, 5), "s": rng.randint(-5, 5) if family == "quad" else None}
        if level == 4:
            return {"family": rng.choice(["top", "top", "bottom"]), "d": rng.randint(1, 5), "a": rng.randint(-3, 5),
                    "m": rng.choice([1, 1, 2, 3])}
        if level == 5:
            family = rng.choice(["zero", "zero", "inf"])
            return {"family": family, "n": rng.randint(1, 3) if family == "zero" else None, "k": rng.randint(1, 5),
                    "trig": rng.choice(["sin", "cos"]), "c": rng.randint(-3, 3)}
        if level == 6:
            case = rng.choice(["equal", "smaller", "bigger"])
            lead = lambda: rng.choice([1, 2, 3, 4, 5, -1, -2, -3])
            coef = lambda: rng.randint(-6, 6)
            if case == "equal":
                a, b = [lead(), coef(), coef()], [lead(), coef(), coef()]
            elif case == "smaller":
                a, b = [0, lead(), coef()], [lead(), coef(), coef()]
            else:
                a, b = [lead(), coef(), coef()], [0, lead(), coef()]
            return {"case": case, "dir": rng.choice(["+", "+", "-"]), "a": a, "b": b}
        family = rng.choice(["single", "single", "hole"])
        return {"family": family, "k": rng.choice([1, 2, 3, -1, -2]), "r": rng.randint(-4, 4), "a": rng.randint(-4, 4),
                "m": rng.choice([1, 1, 2]) if family == "single" else 1, "b": rng.randint(-4, 4) if family == "hole" else None}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._table, self._one_sided, self._factor, self._rationalize,
                self._squeeze, self._infinity, self._asymptote][level](p)

    # Level 1 ----------------------------------------------------------------------------
    def _table(self, p):
        f, a = table_function(p), p["a"]
        L = table_limit(p)
        steps = [
            Step(f"The table shows $f(x)$ as $x$ closes in on ${a}$ from both sides. What value is $f(x)$ approaching?",
                 "number", float(L), tolerance=tolerance(L),
                 explain=f"From both sides the values crowd in on ${num(L)}$, so $\\lim_{{x\\to {a}}} f(x) = {num(L)}$."),
            Step(f"At $x = {a}$ itself, $f$ is $\\frac{{0}}{{0}}$: undefined. Does that stop the limit from existing?", "choice",
                 "No", options=[
                     Option("No: a limit only uses the values near the point, never at it", correct=True, value="no"),
                     Option("Yes: with no value at the point, there's no limit", misconception="limit-needs-value", value="yes",
                            feedback="A limit asks where $f(x)$ is heading as $x$ gets close, not what happens at the point. The table shows a clear destination."),
                     Option("The limit is 0, because the top is 0 there", misconception="top-is-zero", value="zero",
                            feedback="The bottom is 0 too. $\\frac{0}{0}$ says nothing on its own; the table shows where the values actually go."),
                 ]),
        ]
        checks = [("exists", sp.limit(f, x, a) == L, "SymPy disagrees with the limit"),
                  ("clean", clean(L), "limit isn't a clean number")]
        story = f"Here's $f(x) = {sp.latex(f)}$, which can't be evaluated at $x = {a}$."
        scene = {"type": "integral", "tex": table_tex(p), "rule": ""}
        return Solution(steps, story, scene, ["read-table", "value-not-needed"], {"limit": float(L), "_checks": checks})

    # Level 2 ----------------------------------------------------------------------------
    def _one_sided(self, p):
        a = p["a"]
        left, right = sides(p)
        fa = value_at(p)
        removable = p["family"] == "removable"
        if removable and left != right:
            raise NoSolution("a removable discontinuity needs the pieces to meet")
        if not removable and left == right:
            raise NoSolution("a jump needs the pieces to miss each other")
        if removable and fa == left:
            raise NoSolution("the dot fills the hole: that's continuous, not removable")
        if p["m1"] == 0 and p["m2"] == 0 and removable:
            raise NoSolution("two flat pieces at the same height are one line")
        pair = lambda l, r: f"$\\lim_{{x\\to {a}^-}} f(x) = {num(l)}$ and $\\lim_{{x\\to {a}^+}} f(x) = {num(r)}$"
        read = [Option(pair(left, right), correct=True, value=f"{left},{right}")]
        if not removable:
            read.append(Option(pair(right, left), misconception="sides-swapped", value=f"{right},{left}",
                               feedback="The left-hand limit comes from the piece to the left of the dashed line."))
            if fa is not None:
                read.append(Option(pair(fa, fa), misconception="limit-is-value", value=f"{fa},{fa}",
                                   feedback="The filled dot is $f(" + str(a) + ")$. A limit follows each piece toward the line, ignoring the dot."))
        elif fa is not None:
            read.append(Option(pair(fa, fa), misconception="limit-is-value", value=f"{fa},{fa}",
                               feedback="The filled dot is $f(" + str(a) + ")$, off on its own. Both pieces head to the open circle."))
            read.append(Option(pair(left, fa), misconception="dot-is-right-side", value=f"{left},{fa}",
                               feedback="The right-hand limit follows the right piece toward the line, which ends at the open circle, not the dot."))
        else:
            read.append(Option("Neither exists, because $f(" + str(a) + ")$ is undefined", misconception="limit-needs-value", value="none",
                               feedback="There's no dot, so $f(" + str(a) + ")$ is undefined, but both pieces still head somewhere."))
        if removable:
            exist = [Option(f"Yes, it's ${num(left)}$", correct=True, value=f"yes:{left}")]
            if fa is not None:
                exist.append(Option(f"Yes, it's ${num(fa)}$", misconception="limit-is-value", value=f"yes:{fa}",
                                    feedback=f"That's the value $f({a})$. The limit is where the graph is heading: both sides head to ${num(left)}$."))
            exist.append(Option(f"No: the graph has a hole at $x = {a}$", misconception="hole-means-no-limit", value="dne",
                                feedback="A hole doesn't matter: both one-sided limits exist and agree."))
        else:
            exist = [Option("No: the one-sided limits disagree", correct=True, value="dne")]
            if fa is not None:
                exist.append(Option(f"Yes, it's ${num(fa)}$", misconception="limit-is-value", value=f"yes:{fa}",
                                    feedback=f"$f({a}) = {num(fa)}$ is a value, not a limit. The two sides head to different heights."))
            exist.append(Option(f"Yes, it's ${num(sp.Rational(left + right, 2))}$", misconception="average-of-sides",
                                value=f"yes:{sp.Rational(left + right, 2)}",
                                feedback="Averaging doesn't help: the two-sided limit exists only when both sides agree."))
        steps = [
            Step(f"Read the one-sided limits at $x = {a}$.", "choice", read[0].label, options=read),
            Step(f"Does $\\lim_{{x\\to {a}}} f(x)$ exist?", "choice", exist[0].label, options=exist),
        ]
        story = f"The graph shows $y = f(x)$ near $x = {a}$. An open circle is a point the graph leaves out; a filled dot is the value $f({a})$."
        return Solution(steps, story, graph_scene(p), ["one-sided", "two-sided"],
                        {"left": left, "right": right, "_checks": []})

    # Level 3 ----------------------------------------------------------------------------
    def _factor(self, p):
        k, a, r, s = p["k"], p["a"], p["r"], p.get("s")
        if r == a or (s is not None and s in (a, r)):
            raise NoSolution("needs distinct roots")
        top = sp.expand(k * (x - a) * (x - r))
        bottom = sp.expand((x - a) * (x - s)) if s is not None else x - a
        stays = k * (x - r) / (x - s) if s is not None else k * (x - r)
        wrong = k * (x + r) / (x + s) if s is not None else k * (x + r)
        kept = k * (x - a) / (x - s) if s is not None else k * (x - a)
        kept_name, kept_feedback = "kept-cancelled-factor", f"${factor(a)}$ is the factor that cancels. What's left is the other one."
        if key(kept) == key(wrong):          # r = −a: the two slips look identical, so offer a different one
            kept = top / (x - s) if s is not None else top
            kept_name, kept_feedback = "dropped-denominator", f"The bottom's ${factor(a)}$ cancels against a factor of the top; it doesn't just disappear."
        L = stays.subs(x, a)
        f = top / bottom
        steps = [
            Step(f"What do you get by substituting $x = {a}$ straight in?", "choice", "0/0", options=[
                Option("$\\frac{0}{0}$, so simplify first", correct=True, value="0/0"),
                Option("$0$", misconception="zero-over-zero-is-0", value="0",
                       feedback="The top is 0, but so is the bottom. $\\frac{0}{0}$ isn't 0; it's a sign to simplify."),
                Option("Undefined, so there's no limit", misconception="zero-over-zero-dne", value="dne",
                       feedback="$\\frac{0}{0}$ means the algebra isn't finished. Factor and cancel, then try again."),
            ]),
            Step(f"Factor and cancel the common factor ${factor(a)}$.",
                 "choice", tex(stays), options=[
                     Option(tex(stays), correct=True, value=key(stays)),
                     Option(tex(wrong), misconception="wrong-root-sign", value=key(wrong),
                            feedback=f"The top is 0 at $x = {r}$, so its factor is ${factor(r)}$, not ${factor(-r)}$."),
                     Option(tex(kept), misconception=kept_name, value=key(kept), feedback=kept_feedback),
                 ]),
            Step(f"Now substitute $x = {a}$. What is the limit?", "number", float(L), tolerance=tolerance(L),
                 explain=f"$\\lim_{{x\\to {a}}} f(x) = {sp.latex(L)}$"),
        ]
        checks = [("exists", sp.limit(f, x, a) == L, "SymPy disagrees with the limit"),
                  ("clean", clean(L), "limit isn't a clean number")]
        story = f"Find $\\lim_{{x\\to {a}}} \\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}$."
        scene = {"type": "integral", "tex": f"\\lim_{{x\\to {a}}} \\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}", "rule": "\\text{factor, cancel, substitute}"}
        return Solution(steps, story, scene, ["substitute", "factor-cancel", "evaluate"], {"limit": float(L), "_checks": checks})

    # Level 4 ----------------------------------------------------------------------------
    def _rationalize(self, p):
        root, d, a, m = root_parts(p)
        conj, same = root + d, root - d
        if p["family"] == "top":
            f = m * (root - d) / (x - a)
            right, slip, flip = m / conj, m / same, m * conj
        else:
            f = m * (x - a) / (root - d)
            right, slip, flip = m * conj, m * same, m / conj
        L = right.subs(x, a)
        steps = [
            Step("Substituting gives $\\frac{0}{0}$. What should you multiply the top and bottom by?", "choice", tex(conj), options=[
                Option(tex(conj), correct=True, value="conj"),
                Option(tex(same), misconception="same-not-conjugate", value="same",
                       feedback=f"Multiplying by the same expression squares it and keeps the root. Flip the middle sign: $(A - B)(A + B) = A^2 - B^2$."),
                Option(tex(x - a), misconception="wrong-factor", value="xa",
                       feedback=f"That doesn't touch the square root. The conjugate turns ${sp.latex(same)}$ into a difference of squares."),
            ]),
            Step("After multiplying and cancelling, what's left?", "choice", tex(right), options=[
                Option(tex(right), correct=True, value=key(right)),
                Option(tex(slip), misconception="sign-slip", value=key(slip),
                       feedback="The conjugate you multiplied by has a plus sign, and that's the factor that survives."),
                Option(tex(flip), misconception="flipped", value=key(flip),
                       feedback="Track where the conjugate went: it multiplied the side without the square root."),
            ]),
            Step(f"Substitute $x = {a}$. What is the limit?", "number", float(L), tolerance=tolerance(L),
                 explain=f"$\\lim_{{x\\to {a}}} f(x) = {sp.latex(L)}$"),
        ]
        checks = [("exists", sp.limit(f, x, a) == L, "SymPy disagrees with the limit"),
                  ("clean", clean(L), "limit isn't a clean number")]
        story = f"Find $\\lim_{{x\\to {a}}} {sp.latex(f)}$."
        scene = {"type": "integral", "tex": f"\\lim_{{x\\to {a}}} {sp.latex(f)}", "rule": "\\text{multiply by the conjugate}"}
        return Solution(steps, story, scene, ["conjugate", "simplify", "evaluate"], {"limit": float(L), "_checks": checks})


    # Level 5 ----------------------------------------------------------------------------
    def _squeeze(self, p):
        f, c, k = squeeze_function(p), p["c"], p["k"]
        trig = f"\\{p['trig']}"
        if p["family"] == "zero":
            n = p["n"]
            power = f"x^{{{n}}}" if n > 1 else "x"
            size = f"|x|^{{{n}}}" if n % 2 else power                     # x² is already non-negative
            if n == 1:
                size = "|x|"
            wild, tame, where = f"{trig}\\left(\\frac{{{k}}}{{x}}\\right)" if k > 1 else f"{trig}\\left(\\frac{{1}}{{x}}\\right)", power, "0"
        else:
            size = "\\frac{1}{x}"
            wild, tame, where = f"{trig}({k if k > 1 else ''}x)", "\\frac{1}{x}", "\\infty"
        cs = "" if c == 0 else f"{c} "
        lo = f"{c} - {size}" if c else f"-{size}"
        hi = f"{c} + {size}" if c else size
        steps = [
            Step(f"Why can't you just take the limit of each piece and combine them?", "choice", "osc", options=[
                Option(f"${wild}$ has no limit: it keeps oscillating", correct=True, value="osc"),
                Option(f"${tame}$ has no limit as $x \\to {where}$", misconception="blamed-wrong-factor", value="tame",
                       feedback=f"${tame}$ behaves perfectly: it goes to 0. The problem is the other piece."),
                Option(f"Nothing stops you: ${wild}$ settles to 0", misconception="oscillation-has-limit", value="settles",
                       feedback=f"${wild}$ swings between $-1$ and $1$ forever{', faster and faster' if p['family'] == 'zero' else ''}. It never settles."),
            ]),
            Step("Which pair of bounds squeezes $f(x)$ to a limit?", "choice", "tight", options=[
                Option(f"${lo} \\le f(x) \\le {hi}$", correct=True, value="tight"),
                Option(f"${c - 1} \\le f(x) \\le {c + 1}$", misconception="bounds-dont-meet", value="loose",
                       feedback=f"True near ${where}$, but the bounds stay 2 apart. A squeeze needs bounds that approach the same value."),
                Option(f"${c} \\le f(x) \\le {hi}$", misconception="lower-bound-too-high", value="high",
                       feedback=f"${wild}$ goes negative too, so $f(x)$ dips below ${c}$. The lower bound has to mirror the upper one."),
            ]),
            Step("Both bounds approach the same value. What is the limit?", "number", float(c), tolerance=0.01,
                 explain=f"Squeezed between ${lo}$ and ${hi}$, both heading to ${c}$, $f(x) \\to {c}$."),
        ]
        point = sp.oo if p["family"] == "inf" else 0
        checks = [("exists", sp.limit(f, x, point) == c, "SymPy disagrees with the limit")]
        story = f"Find $\\lim_{{x\\to {where}}} {sp.latex(f)}$."
        scene = {"type": "integral", "tex": f"\\lim_{{x\\to {where}}} {sp.latex(f)}", "rule": f"-1 \\le {wild} \\le 1"}
        return Solution(steps, story, scene, ["why-not-split", "bounds", "squeeze"], {"limit": c, "_checks": checks})

    # Level 6 ----------------------------------------------------------------------------
    def _infinity(self, p):
        top, bottom = rational_parts(p)
        if sp.Poly(top, x).degree() < 1 or sp.gcd(top, bottom) != 1:
            raise NoSolution("needs a genuine rational function with no common factor")
        point = sp.oo if p["dir"] == "+" else -sp.oo
        L = sp.limit(top / bottom, x, point)
        where = "\\infty" if p["dir"] == "+" else "-\\infty"
        lt, lb = sp.LT(top, x), sp.LT(bottom, x)
        lead = sp.cancel(lt / lb)
        a0, b0 = sp.Integer(p["a"][2]), sp.Integer(p["b"][2])
        opt = lambda v, **kw: Option(f"${show_limit(v)}$", value=value_key(v), **kw)
        if p["case"] == "equal":
            limit_opts = [opt(L, correct=True)]
            if b0 != 0:
                limit_opts.append(opt(a0 / b0, misconception="constant-terms",
                                      feedback=f"Far out, ${sp.latex(lt)}$ and ${sp.latex(lb)}$ dwarf everything else. Divide by $x^{{{sp.degree(bottom, x)}}}$ and only their coefficients survive."))
            limit_opts.append(opt(sp.oo if L > 0 else -sp.oo, misconception="top-grows-so-infinity",
                                  feedback="The top grows, but the bottom grows just as fast. Same degree means the leading coefficients decide."))
            asym = [Option(f"$y = {sp.latex(L)}$", correct=True, value=f"y={num(L)}")]
            if b0 != 0:
                asym.append(Option(f"$y = {sp.latex(a0 / b0)}$", misconception="constant-terms", value=f"y={num(a0 / b0)}",
                                   feedback="The constant terms matter near $x = 0$, not far out."))
            asym.append(Option("None", misconception="top-grows-so-infinity", value="none",
                               feedback="The function settles to a finite value, so that value is a horizontal asymptote."))
        elif p["case"] == "smaller":
            limit_opts = [opt(L, correct=True),
                          opt(sp.Rational(p["a"][1], p["b"][0]), misconception="ratio-regardless-of-degree",
                              feedback="The leading coefficients only decide when the degrees match. Here the bottom has the higher degree and wins."),
                          opt(sp.oo if sp.Rational(p["a"][1], p["b"][0]) > 0 else -sp.oo, misconception="top-grows-so-infinity",
                              feedback="The top grows, but the bottom grows faster: a degree-2 bottom beats a degree-1 top.")]
            asym = [Option("$y = 0$", correct=True, value="y=0"),
                    Option("None", misconception="top-grows-so-infinity", value="none", feedback="The function settles to 0, so $y = 0$ is a horizontal asymptote."),
                    Option(f"$y = {sp.latex(sp.Rational(p['a'][1], p['b'][0]))}$", misconception="ratio-regardless-of-degree",
                           value=f"y={num(sp.Rational(p['a'][1], p['b'][0]))}", feedback="With a higher-degree bottom, the values shrink to 0.")]
        else:
            ratio = sp.Rational(p["a"][0], p["b"][1])
            limit_opts = [opt(L, correct=True),
                          opt(-L, misconception="sign-of-infinity",
                              feedback=f"For large {'negative' if p['dir'] == '-' else 'positive'} $x$, ${sp.latex(lt)}$ and ${sp.latex(lb)}$ have signs that make the ratio {'positive' if L == sp.oo else 'negative'}."),
                          opt(ratio, misconception="ratio-regardless-of-degree",
                              feedback="The leading coefficients only decide when the degrees match. Here the top has the higher degree, so the values grow without bound.")]
            asym = [Option("None", correct=True, value="none"),
                    Option(f"$y = {sp.latex(ratio)}$", misconception="ratio-regardless-of-degree", value=f"y={num(ratio)}",
                           feedback="The values grow without bound, so there's no horizontal line to approach."),
                    Option("$y = 0$", misconception="constant-terms", value="y=0",
                           feedback="The values grow without bound, so there's no horizontal asymptote.")]
        steps = [
            Step(f"What is $\\lim_{{x\\to {where}}} f(x)$?", "choice", limit_opts[0].label, options=limit_opts),
            Step("What horizontal asymptote does that give?", "choice", asym[0].label, options=asym),
        ]
        story = f"Let $f(x) = \\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}$."
        scene = {"type": "integral", "tex": f"\\lim_{{x\\to {where}}} \\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}", "rule": "\\text{divide top and bottom by the highest power of } x \\text{ in the bottom}"}
        checks = [("clean", L in (sp.oo, -sp.oo) or clean(L), "limit isn't clean")]
        return Solution(steps, story, scene, ["dominant-terms", "horizontal-asymptote"], {"limit": value_key(L), "_checks": checks})

    # Level 7 ----------------------------------------------------------------------------
    def _asymptote(self, p):
        k, r, a, m, b = p["k"], p["r"], p["a"], p["m"], p.get("b")
        if r == a or (b is not None and b in (a, r)):
            raise NoSolution("needs distinct roots")
        if b is None:
            top, bottom = sp.expand(k * (x - r)), sp.expand((x - a) ** m)
        else:
            top, bottom = sp.expand(k * (x - r) * (x - b)), sp.expand((x - a) * (x - b))
        f = top / bottom
        right, left = sp.limit(f, x, a, "+"), sp.limit(f, x, a, "-")
        if not {right, left} <= {sp.oo, -sp.oo}:
            raise NoSolution("not a vertical asymptote")
        line = lambda v: f"$x = {v}$"
        where = [Option(line(a), correct=True, value=f"x={a}"),
                 Option(line(r), misconception="top-zero-is-asymptote", value=f"x={r}",
                        feedback=f"At $x = {r}$ the top is 0, so the graph crosses the axis there. An asymptote needs the bottom to be 0 and the top not."),]
        if b is not None:
            where.append(Option(f"$x = {a}$ and $x = {b}$", misconception="hole-is-asymptote", value=f"x={a},{b}",
                                feedback=f"${factor(b)}$ is on the top and the bottom, so it cancels: $x = {b}$ is a hole, not an asymptote."))
        elif a != 0 and -a != r:
            where.append(Option(line(-a), misconception="sign-of-root", value=f"x={-a}",
                                feedback=f"The bottom is zero where ${sp.latex(x - a)} = 0$, at $x = {a}$."))
        side = lambda v, **kw: Option(f"${show_limit(v)}$", value=value_key(v), **kw)
        top_sign = "positive" if k * (a - r) > 0 else "negative"     # the surviving top, k(x − r), near x = a
        lead = f"after cancelling ${factor(b)}$, " if b is not None else ""   # signs refer to the cancelled form
        sided = []
        for s_name, v in (("+", right), ("-", left)):
            bottom_sign = "positive" if (s_name == "+" or m % 2 == 0) else "negative"
            sided.append([side(v, correct=True),
                          side(-v, misconception="sign-slip",
                               feedback=f"Check the signs just {'right' if s_name == '+' else 'left'} of ${a}$: {lead}the top ${sp.latex(k * (x - r))}$ is {top_sign} and the bottom ${sp.latex((x - a) ** m)}$ is a tiny {bottom_sign} number."),
                          Option("$0$", misconception="tiny-bottom-small-answer", value="0",
                                 feedback="Dividing by a tiny number makes the result huge, not tiny.")])
        steps = [
            Step("Where is the vertical asymptote?", "choice", where[0].label, options=where),
            Step(f"What is $\\lim_{{x\\to {a}^+}} f(x)$?", "choice", sided[0][0].label, options=sided[0]),
            Step(f"What is $\\lim_{{x\\to {a}^-}} f(x)$?", "choice", sided[1][0].label, options=sided[1]),
        ]
        story = f"Let $f(x) = \\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}$."
        scene = {"type": "integral", "tex": f"f(x) = \\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}", "rule": ""}
        return Solution(steps, story, scene, ["locate-asymptote", "one-sided-infinite", "one-sided-infinite"],
                        {"right": value_key(right), "left": value_key(left), "_checks": []})


FRAMEWORK = Limits()
