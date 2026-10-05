"""The derivative from its definition (MATH 140, outcome 140.3.1). Spec: design/specs/2026-10-05-math-140-explorer-design.md §5.1.

Level 1: average vs instantaneous rate, from a story.
Level 2: the limit of the difference quotient.
Level 3: continuous vs differentiable (corners, kinks, jumps, smooth joins).
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x, h, t = sp.symbols("x h t")
MAX_DEN = 20


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else f"{float(v):g}"


def tex(e):
    return f"${sp.latex(e)}$"


def key(e):
    return sp.sstr(sp.expand(e))


def poly(p):
    a, b, c = sp.Rational(p["a"]), sp.Rational(p["b"]), sp.Rational(p["c"])
    return a * x**3 + b * x + c if p.get("kind") == "cubic" else a * x**2 + b * x + c


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 2000


# Level 3: the families of functions at x = a ---------------------------------------

def pieces(p):
    """(left expression, right expression) around x = a."""
    a, k, m1, m2 = (sp.Integer(p[n]) for n in ("a", "k", "m1", "m2"))
    u = x - a
    if p["kind"] == "abs":
        return -u + k, u + k
    if p["kind"] == "kink":
        return m1 * u + k, m2 * u + k
    if p["kind"] == "jump":
        return m1 * u + k, m1 * u + k + 2
    return u**2 + m2 * u + k, m2 * u + k          # smooth: same value and slope at a


def classify(p):
    a = sp.Integer(p["a"])
    left, right = pieces(p)
    value = right.subs(x, a)                         # f(a) uses the right-hand piece (x ≥ a)
    lim_left, lim_right = sp.limit(left, x, a, "-"), sp.limit(right, x, a, "+")
    continuous = lim_left == lim_right == value
    left_slope = sp.limit((left.subs(x, a + h) - value) / h, h, 0, "-") if continuous else None
    right_slope = sp.limit((right.subs(x, a + h) - value) / h, h, 0, "+")
    differentiable = bool(continuous and left_slope == right_slope)
    return {"continuous": bool(continuous), "differentiable": differentiable,
            "left_slope": left_slope, "right_slope": right_slope}


def piecewise_tex(p):
    left, right = pieces(p)
    if p["kind"] == "abs":
        return f"$f(x) = |{sp.latex(x - p['a'])}| + {p['k']}$".replace("+ -", "- ")
    return f"$f(x) = \\begin{{cases}} {sp.latex(sp.expand(left))} & x < {p['a']} \\\\ {sp.latex(sp.expand(right))} & x \\ge {p['a']} \\end{{cases}}$"


class DerivativeDefinition(Framework):
    id = "derivative-definition"
    title = "The derivative from its definition"
    outcome = "Understand the derivative as an instantaneous rate and compute it from the limit definition."
    levels = {
        1: Level("Slope as a rate of change", {"average-rate": 1, "shrink-interval": 1, "units": 1}),
        2: Level("The limit definition", {"expand": 1, "limit": 1, "generalize": 1}),
        3: Level("Differentiable versus continuous", {"continuity": 1, "one-sided-slopes": 1}),
    }
    misconceptions = {
        "change-not-rate": "Gave the change in the quantity, not the rate (change per unit of time).",
        "upside-down": "Divided time by change instead of change by time.",
        "value-over-time": "Divided the value by the time instead of the change by the elapsed time.",
        "average-is-instant": "Used the average over the whole interval as the rate at one instant.",
        "units-no-time": "Left out the 'per unit of time' that every rate has.",
        "units-flipped": "Wrote the units of time per quantity, upside down.",
        "dropped-cross-term": "Expanded (p + h)² as p² + h², losing the 2ph term.",
        "forgot-to-divide": "Simplified the numerator but didn't divide by h.",
        "early-substitution": "Put h = 0 in before simplifying, which only ever gives 0/0.",
        "zero-over-zero": "Stopped at 0/0, which is a reason to simplify, not an answer.",
        "value-not-function": "Gave the derivative's value at one point instead of the function f′(x).",
        "dropped-linear-term": "Lost the derivative of the bx term.",
        "same-as-f": "Copied f(x) instead of differentiating.",
        "continuous-means-differentiable": "Assumed an unbroken graph must have a derivative; corners don't.",
        "jump-continuous": "Missed the jump: the two sides don't meet.",
        "corner-smooth": "Called a corner smooth, but the one-sided slopes disagree.",
        "slopes-swapped": "Swapped the left and right slopes.",
    }
    targets = {1: 100, 2: 110, 3: 100}
    STORY_FIELDS = {1: {"t", "f_tex"}}

    def themes_for(self, level):
        return super().themes_for(level) if level == 1 else []

    def sample(self, rng, level, theme):
        if level == 1:
            co = theme["coefficients"]
            t1 = rng.randint(1, 5)
            return {"a": str(rng.choice(co["a"])), "b": rng.choice(co["b"]), "c": rng.choice(co["c"]),
                    "t1": t1, "t2": t1 + rng.choice([2, 3])}   # over a 1-unit interval, change = rate, so that mistake would be invisible
        if level == 2:
            kind = rng.choice(["quad", "quad", "cubic"])
            return {"kind": kind, "a": rng.choice([1, 2, 3, -1, -2]), "b": rng.randint(-5, 5),
                    "c": rng.randint(-5, 5), "p": rng.randint(-3, 3)}
        return {"kind": rng.choice(["abs", "kink", "jump", "smooth"]), "a": rng.randint(-2, 3),
                "k": rng.randint(-3, 3), "m1": rng.randint(-3, 3), "m2": rng.randint(-3, 3)}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def plausibility(self, p, level, theme):
        if level != 1:
            return []
        f = sp.Rational(p["a"]) * t**2 + p["b"] * t + p["c"]
        # The rate is linear in t, so checking both ends of the drawn window [0, t2 + 1] covers all of it:
        # the quantity never turns around on the graph (coffee warming up by itself, say).
        rate = sp.diff(f, t)
        return [("rate", float(rate.subs(t, at))) for at in (0, p["t1"], p["t2"] + 1)]

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        if level == 1:
            return self._rate(p, theme)
        if level == 2:
            return self._definition(p)
        return self._continuity(p)

    # Level 1 ----------------------------------------------------------------------
    def _rate(self, p, theme):
        a, b, c, t1, t2 = sp.Rational(p["a"]), sp.Integer(p["b"]), sp.Integer(p["c"]), p["t1"], p["t2"]
        f = a * t**2 + b * t + c
        f1, f2 = f.subs(t, t1), f.subs(t, t2)
        avg = (f2 - f1) / (t2 - t1)
        inst = sp.diff(f, t).subs(t, t1)
        sym, unit, tu = theme["symbol"], theme["unit"], theme["time_unit"]
        story = theme["stories"][1][0].format(t="$t$", f_tex=sp.latex(f))
        val = lambda v: float(sp.nsimplify(v))
        steps = [
            Step(f"What is the average rate of change of ${sym}$ from $t = {t1}$ to $t = {t2}$?", "choice", f"{num(avg)} {unit}/{tu}", options=[
                Option(f"{num(avg)} {unit}/{tu}", correct=True, value=val(avg)),
                Option(f"{num(f2 - f1)} {unit}", misconception="change-not-rate",
                       feedback=f"That's how much ${sym}$ changed. A rate is change ÷ time: divide by {t2 - t1}.", value=val(f2 - f1)),
                Option(f"{num(f2 / t2)} {unit}/{tu}", misconception="value-over-time",
                       feedback=f"That divides the value at $t = {t2}$ by {t2}. Use the change between the two times.", value=val(f2 / t2) if t2 else 0),
            ], explain=f"$\\frac{{{sym}({t2}) - {sym}({t1})}}{{{t2} - {t1}}} = \\frac{{{num(f2)} - {num(f1)}}}{{{t2 - t1}}} = {num(avg)}$"),
            Step(f"Shrink the interval toward $t = {t1}$. What is the instantaneous rate at $t = {t1}$? (in {unit}/{tu})", "number",
                 val(inst), tolerance=0.01, unit=f"{unit}/{tu}",
                 explain=f"Over $[{t1}, {t1} + h]$ the average is ${sp.latex(sp.expand(sp.simplify((f.subs(t, t1 + h) - f1) / h)))}$, which goes to {num(inst)} as $h \\to 0$."),
            Step("What are the units of a rate of change here?", "choice", f"{unit} per {tu}", options=[
                Option(f"{unit} per {tu}", correct=True, value="right"),
                Option(f"{unit}", misconception="units-no-time", feedback="A rate always says per what: here, per unit of time.", value="no-time"),
                Option(f"{tu} per {unit}", misconception="units-flipped", feedback="Change in the quantity goes on top; time goes underneath.", value="flipped"),
            ]),
        ]
        checks = [("clean", clean(avg) and clean(inst), "rates aren't clean numbers"),
                  ("distinct", abs(val(avg) - val(inst)) > 1e-9, "average equals instantaneous: the lesson needs them to differ")]
        span = t2 + 1
        curve = [[k * span / 40, float(f.subs(t, sp.Rational(k * span, 40)))] for k in range(41)]
        scene = {"type": "rate", "f": sp.sstr(f), "tex": sp.latex(f), "t1": t1, "t2": t2, "y1": val(f1), "y2": val(f2),
                 "symbol": sym, "unit": unit, "time_unit": tu, "curve": curve}
        return Solution(steps, story, scene, ["average-rate", "shrink-interval", "units"],
                        {"average": val(avg), "instant": val(inst), "_checks": checks})

    # Level 2 ----------------------------------------------------------------------
    def _definition(self, p):
        f, pt = poly(p), sp.Integer(p["p"])
        quotient = sp.expand(sp.cancel((f.subs(x, pt + h) - f.subs(x, pt)) / h))
        numerator = sp.expand(f.subs(x, pt + h) - f.subs(x, pt))
        value = sp.diff(f, x).subs(x, pt)
        fprime = sp.diff(f, x)
        a, b = sp.Integer(p["a"]), sp.Integer(p["b"])
        if p["kind"] == "quad":
            no_cross = sp.expand((a * (pt**2 + h**2) + b * (pt + h) - a * pt**2 - b * pt) / h)
            wrong_fprime = [("dropped-linear-term", 2 * a * x), ("same-as-f", f)]
        else:
            no_cross = sp.expand((a * (pt**3 + h**3) + b * (pt + h) - a * pt**3 - b * pt) / h)
            wrong_fprime = [("dropped-linear-term", 3 * a * x**2), ("same-as-f", f)]
        steps = [
            Step(f"Simplify $\\dfrac{{f({pt} + h) - f({pt})}}{{h}}$ for $f(x) = {sp.latex(f)}$.", "choice", tex(quotient), options=[
                Option(tex(quotient), correct=True, value=key(quotient)),
                Option(tex(no_cross), misconception="dropped-cross-term",
                       feedback=("$(p+h)^2 = p^2 + 2ph + h^2$: the cross term $2ph$ matters." if p["kind"] == "quad"
                                 else "$(p+h)^3 = p^3 + 3p^2h + 3ph^2 + h^3$: the middle terms matter."), value=key(no_cross)),
                Option(tex(numerator), misconception="forgot-to-divide", feedback="That's just the top. Divide every term by $h$.", value=key(numerator)),
            ]),
            Step("Now let $h \\to 0$. What is $f'(" + str(pt) + ")$?", "choice", num(value), options=[
                Option(f"${num(value)}$", correct=True, value=float(value)),
                Option("$0$ (put $h = 0$ in first)", misconception="early-substitution",
                       feedback="Putting $h = 0$ into the original fraction gives $0/0$. Simplify first, then let $h$ shrink.", value=0.0),
                Option("Undefined: it's $0/0$", misconception="zero-over-zero",
                       feedback="$0/0$ only means \"simplify first\". After simplifying, the $h$ in the denominator is gone.", value="undefined"),
            ], explain=f"Every term with $h$ vanishes, leaving ${num(value)}$."),
            Step("Repeat the same steps at any $x$. What is $f'(x)$?", "choice", tex(fprime), options=[
                Option(tex(fprime), correct=True, value=key(fprime)),
                *[Option(tex(e), misconception=m, value=key(e),
                         feedback=("The $bx$ term has slope $b$ everywhere: keep it." if m == "dropped-linear-term" else "That's $f(x)$ itself. Differentiate it."))
                  for m, e in wrong_fprime if key(e) != key(fprime)],
                Option(f"${num(value)}$", misconception="value-not-function",
                       feedback=f"That's the slope at $x = {pt}$ only. The derivative is a function of $x$.", value=f"const:{num(value)}"),
            ]),
        ]
        checks = [("exists", sp.limit(quotient, h, 0) == value, "difference quotient limit disagrees with diff")]
        scene = {"type": "integral", "tex": f"\\lim_{{h\\to 0}}\\frac{{f({pt}+h) - f({pt})}}{{h}}", "rule": f"f(x) = {sp.latex(f)}"}
        return Solution(steps, f"Find the derivative of $f(x) = {sp.latex(f)}$ at $x = {pt}$ from the definition.", scene,
                        ["expand", "limit", "generalize"], {"value": float(value), "_checks": checks})

    # Level 3 ----------------------------------------------------------------------
    def _continuity(self, p):
        if p["kind"] == "kink" and p["m1"] == p["m2"]:
            raise NoSolution("equal slopes make a straight line, not a kink")
        got = classify(p)
        a = p["a"]
        yes_no = lambda flag: "Yes" if flag else "No"
        cont, diff = got["continuous"], got["differentiable"]
        steps = [
            Step(f"Is $f$ continuous at $x = {a}$?", "choice", yes_no(cont), options=[
                Option("Yes", correct=cont, value="yes", misconception=None if cont else "jump-continuous",
                       feedback="" if cont else "Compare the two sides as $x \\to " + str(a) + "$: they approach different values."),
                Option("No", correct=not cont, value="no", misconception=None if not cont else "jump-continuous",
                       feedback="" if not cont else "Both sides approach the same value, and it equals $f(" + str(a) + ")$: no break."),
            ]),
            Step(f"Is $f$ differentiable at $x = {a}$?", "choice", yes_no(diff), options=[
                Option("Yes", correct=diff, value="yes",
                       misconception=None if diff else ("continuous-means-differentiable" if cont else "jump-continuous"),
                       feedback="" if diff else ("Unbroken isn't enough: check the slope from each side." if cont else "A graph that jumps can't have a slope there.")),
                Option("No", correct=not diff, value="no", misconception=None if not diff else "corner-smooth",
                       feedback="" if not diff else "Both one-sided slopes agree, so the derivative exists."),
            ]),
        ]
        if cont:
            L, R = got["left_slope"], got["right_slope"]
            opts = [Option(f"left ${num(L)}$, right ${num(R)}$", correct=True, value=f"{L},{R}")]
            if L != R:
                opts.append(Option(f"left ${num(R)}$, right ${num(L)}$", misconception="slopes-swapped",
                                   feedback="Read each piece's slope from its own side of $x = " + str(a) + "$.", value=f"{R},{L}"))
                opts.append(Option(f"both ${num((L + R) / 2)}$", misconception="corner-smooth",
                                   feedback="There's no single slope at a corner; each side keeps its own.", value=f"avg{(L + R) / 2}"))
            else:
                opts.append(Option(f"left ${num(L + 1)}$, right ${num(R)}$", misconception="corner-smooth",
                                   feedback="The pieces were built to join smoothly: same value and same slope.", value=f"{L + 1},{R}"))
            steps.append(Step("What are the slopes approaching $x = " + str(a) + "$ from each side?", "choice", opts[0].label, options=opts))
        story = f"Consider {piecewise_tex(p)}."
        scene = {"type": "integral", "tex": piecewise_tex(p).strip("$"), "rule": f"x = {a}"}
        return Solution(steps, story, scene, ["continuity", "one-sided-slopes"],
                        {"continuous": cont, "differentiable": diff, "_checks": []})


FRAMEWORK = DerivativeDefinition()
