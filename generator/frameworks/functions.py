"""Functions and graphs (MATH 140, outcomes 140.1.1–140.1.3). Plan: design/plans/2026-10-05-math-140-functions.md.

Level 1: domain from a formula.
Level 2: composition.
Level 3: inverse functions.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x, y = sp.symbols("x y")
MAX_DEN = 20


def L(e):
    return sp.latex(e, ln_notation=True, inv_trig_style="full")


def tex(e):
    return f"${L(e)}$"


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):g}")


def key(e):
    return sp.sstr(sp.simplify(e))


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 100000


def plus(v):
    """' + 3', ' - 3' or '' for a constant term in worked arithmetic."""
    return "" if v == 0 else (f" + {v}" if v > 0 else f" - {-v}")


def same(a, b):
    return sp.simplify(a - b) == 0


def pick(right, candidates, n=2):
    kept = []
    for c in candidates:
        e = c[1]
        if same(e, right) or any(same(e, k[1]) for k in kept):
            continue
        kept.append(c)
        if len(kept) == n:
            break
    return kept


# Level 3 ----------------------------------------------------------------------------

def inverse_function(p):
    a, b, d = p["a"], p["b"], p["d"]
    if p["family"] == "linear":
        return a * x + b
    if p["family"] == "cube":
        return x**3 + b
    return (a * x + b) / (x + d)


def inverse_formula(p):
    a, b, d = p["a"], p["b"], p["d"]
    if p["family"] == "linear":
        return (x - b) / a
    if p["family"] == "cube":
        return sp.cbrt(x - b)
    return (b - d * x) / (x - a)


class Functions(Framework):
    id = "functions"
    title = "Functions and graphs"
    outcome = "Work with domains, compositions and inverses, transform graphs, and use exponentials, logarithms and trig values."
    levels = {
        1: Level("Domain", {"condition": 1, "domain": 1}),
        2: Level("Composition", {"inner": 1, "outer": 1, "formula": 1}),
        3: Level("Inverse functions", {"swap-and-solve": 1, "evaluate": 1}),
    }
    misconceptions = {
        "strict-for-root": "Excluded zero under a square root. √0 = 0 is fine.",
        "log-of-zero": "Allowed zero inside a log. log 0 is undefined: the inside must be strictly positive.",
        "only-zero-matters": "Only excluded the point where the inside is zero; negatives are the real problem.",
        "forgot-to-flip": "Divided an inequality by a negative number without flipping it.",
        "inequality-flip": "Flipped the inequality without dividing by a negative.",
        "forgot-negative-root": "Missed the negative root: x² = r² has two solutions.",
        "denominator-positive": "Required the bottom to be positive. It only has to be nonzero.",
        "forgot-denominator": "Forgot that the bottom can't be zero.",
        "order-swapped": "Composed in the wrong order: f(g(x)) means do g first.",
        "composition-is-product": "Multiplied the functions. Composition feeds one into the other.",
        "inverse-is-reciprocal": "Took 1/f(x). The −1 in f⁻¹ means 'undo', not a power.",
        "solved-wrong": "Slipped a sign while solving for y.",
    }
    targets = {1: 100, 2: 100, 3: 100}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        nz = lambda lo, hi: rng.choice([v for v in range(lo, hi + 1) if v])
        if level == 1:
            family = rng.choice(["sqrt", "ln", "recip", "combo"])
            if family == "recip":
                return {"family": family, "a": rng.randint(1, 6), "b": 0, "q": 0}
            if family == "combo":
                b = rng.randint(-6, 4)
                return {"family": family, "a": 1, "b": b, "q": -b + rng.randint(1, 6)}
            return {"family": family, "a": nz(-3, 3), "b": rng.randint(-8, 8), "q": 0}
        if level == 2:
            return {"a": nz(-3, 3), "b": rng.randint(-5, 5), "c": rng.choice([1, 2, -1, 3]), "d": rng.randint(-4, 4), "t": rng.randint(-3, 3)}
        family = rng.choice(["linear", "cube", "mobius"])
        if family == "mobius":
            return {"family": family, "a": nz(-3, 3), "b": rng.randint(-5, 5), "d": nz(-4, 4), "u": rng.randint(-3, 3)}
        return {"family": family, "a": nz(-5, 5) if family == "linear" else 1, "b": rng.randint(-8, 8), "d": 0, "u": rng.randint(-3, 3)}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._domain, self._composition, self._inverse][level](p)

    def _choice(self, prompt, right_label, right_value, wrongs):
        if len(wrongs) < 2:
            raise NoSolution("fewer than two distinct mistakes: a coin flip")
        labels = [right_label] + [w[1] for w in wrongs]
        if len(set(labels)) != len(labels):
            raise NoSolution("two options read the same")
        return Step(prompt, "choice", right_label, options=[Option(right_label, correct=True, value=right_value)] +
                    [Option(lbl, misconception=m, value=v, feedback=fb) for m, lbl, v, fb in wrongs])

    # Level 1 ----------------------------------------------------------------------------
    def _domain(self, p):
        fam, a, b, q = p["family"], p["a"], p["b"], p["q"]
        inside = a * x + b
        c = sp.Rational(-b, a)
        ineq = lambda op, val: f"$x {op} {L(val)}$"
        if fam in ("sqrt", "ln"):
            f = sp.sqrt(inside) if fam == "sqrt" else sp.log(inside)
            weak = fam == "sqrt"
            cond_ok, cond_strict = ("\\ge", ">") if weak else (">", "\\ge")
            cond = self._choice("What must be true of the inside?", f"${L(inside)} {cond_ok} 0$", "right", [
                ("strict-for-root" if weak else "log-of-zero", f"${L(inside)} {cond_strict} 0$", "strict",
                 "Zero is fine under a square root: $\\sqrt{0} = 0$." if weak else "$\\ln 0$ is undefined, so the inside must be strictly positive."),
                ("only-zero-matters", f"${L(inside)} \\ne 0$", "nonzero",
                 "Negative inputs are the problem: " + ("there's no real square root of a negative number." if weak else "logs of negative numbers aren't defined.")),
            ])
            up = a > 0
            op, flip = ((("\\ge" if weak else ">"), ("\\le" if weak else "<")) if up else (("\\le" if weak else "<"), ("\\ge" if weak else ">")))
            strict_op = (">" if up else "<") if weak else ("\\ge" if up else "\\le")
            wrongs = [("forgot-to-flip" if not up else "inequality-flip", ineq(flip, c), "flip",
                       (f"Dividing by ${a}$, a negative number, flips the inequality." if not up else "Dividing by a positive number keeps the inequality's direction.")),
                      ("strict-for-root" if weak else "log-of-zero", ineq(strict_op, c), "strict",
                       "$x = " + L(c) + "$ makes the inside 0, " + ("which is allowed under a root." if weak else "which a log can't take."))]
            dom = self._choice("So what is the domain?", ineq(op, c), "right", wrongs)
            checks = [("clean", clean(c), "boundary isn't clean")]
        elif fam == "recip":
            r = a
            f = 1 / (x**2 - r**2)
            cond = self._choice("What must be true of the bottom?", f"$x^2 - {r * r} \\ne 0$", "right", [
                ("denominator-positive", f"$x^2 - {r * r} > 0$", "pos", "The bottom only has to be nonzero; negative values are fine to divide by."),
                ("forgot-negative-root", f"$x \\ne {r}$", "half", f"$x^2 = {r * r}$ at both $x = {r}$ and $x = -{r}$."),
            ])
            dom = self._choice("So what is the domain?", f"All real $x$ except $x = \\pm {r}$", "right", [
                ("forgot-negative-root", f"All real $x$ except $x = {r}$", "half", f"$(-{r})^2 = {r * r}$ too, so $x = -{r}$ also makes the bottom 0."),
                ("denominator-positive", f"$x < -{r}$ or $x > {r}$", "pos", f"Between $-{r}$ and ${r}$ the bottom is negative, but you can still divide by it."),
            ])
            checks = []
        else:
            f = sp.sqrt(inside) / (x - q)
            cond = self._choice("What must be true?", f"${L(inside)} \\ge 0$ and $x \\ne {q}$", "right", [
                ("forgot-denominator", f"${L(inside)} \\ge 0$ only", "root-only", f"The bottom, ${L(x - q)}$, can't be 0 either."),
                ("strict-for-root", f"${L(inside)} > 0$ and $x \\ne {q}$", "strict", "Zero is fine under a square root: $\\sqrt{0} = 0$."),
            ])
            dom = self._choice("So what is the domain?", f"$x \\ge {L(c)}$, except $x = {q}$", "right", [
                ("forgot-denominator", f"$x \\ge {L(c)}$", "root-only", f"At $x = {q}$ the bottom is 0, so it must be left out."),
                ("strict-for-root", f"$x > {L(c)}$, except $x = {q}$", "strict", f"At $x = {L(c)}$ the top is $\\sqrt{{0}} = 0$ and the bottom isn't 0, so it's allowed."),
            ])
            checks = []
        story = f"What is the domain of $f(x) = {L(f)}$?"
        scene = {"type": "integral", "tex": f"f(x) = {L(f)}", "rule": "\\sqrt{u}: u \\ge 0, \\quad \\ln u: u > 0, \\quad \\tfrac{1}{u}: u \\ne 0"}
        return Solution([cond, dom], story, scene, ["condition", "domain"], {"_checks": checks})

    # Level 2 ----------------------------------------------------------------------------
    def _composition(self, p):
        a, b, c, d, t = p["a"], p["b"], p["c"], p["d"], p["t"]
        f, g = a * x + b, c * x**2 + d
        fg, gf, prod = sp.expand(f.subs(x, g)), sp.expand(g.subs(x, f)), sp.expand(f * g)
        gt = g.subs(x, t)
        fgt = f.subs(x, gt)
        wrongs = pick(fg, [("order-swapped", gf, "That's $g(f(x))$: it does $f$ first. $f(g(x))$ puts $g(x)$ inside $f$."),
                           ("composition-is-product", prod, "That's $f(x)\\cdot g(x)$. Composition feeds $g(x)$ into $f$.")])
        formula = self._choice("Which is the formula for $(f \\circ g)(x)$?", f"${L(fg)}$", "right",
                               [(m, f"${L(e)}$", f"w{i}", fb) for i, (m, e, fb) in enumerate(wrongs)])
        steps = [
            Step(f"What is $g({t})$?", "number", float(gt), tolerance=0.01, explain=f"$g({t}) = {c}({t})^2{plus(d)} = {gt}$"),
            Step(f"So what is $(f \\circ g)({t}) = f(g({t}))$?", "number", float(fgt), tolerance=0.01,
                 explain=f"$f({gt}) = {a}({gt}){plus(b)} = {fgt}$"),
            formula,
        ]
        story = f"Let $f(x) = {L(f)}$ and $g(x) = {L(g)}$."
        scene = {"type": "integral", "tex": "(f \\circ g)(x) = f(g(x))", "rule": "\\text{do } g \\text{ first, then } f"}
        return Solution(steps, story, scene, ["inner", "outer", "formula"], {"value": float(fgt), "_checks": []})

    # Level 3 ----------------------------------------------------------------------------
    def _inverse(self, p):
        f, inv, u = inverse_function(p), inverse_formula(p), p["u"]
        if same(f, inv):
            raise NoSolution("f is its own inverse: the swapped answer would equal f")
        if p["family"] == "mobius" and (u + p["d"] == 0 or p["a"] * p["d"] == p["b"]):
            raise NoSolution("undefined or constant function")
        a, b, d = p["a"], p["b"], p["d"]
        slip = {"linear": (x + b) / a, "cube": sp.cbrt(x + b), "mobius": (b + d * x) / (x - a)}[p["family"]]
        wrongs = pick(inv, [("inverse-is-reciprocal", 1 / f, "$f^{-1}$ means the function that undoes $f$, not $\\frac{1}{f(x)}$."),
                            ("solved-wrong", slip, "Swap $x$ and $y$, then undo each step in reverse order, flipping the sign of what you move across.")])
        v = f.subs(x, u)
        steps = [
            self._choice("Swap $x$ and $y$ in $y = f(x)$ and solve for $y$. What is $f^{-1}(x)$?", f"${L(inv)}$", "right",
                         [(m, f"${L(e)}$", f"w{i}", fb) for i, (m, e, fb) in enumerate(wrongs)]),
            Step(f"What is $f^{{-1}}({L(v)})$?", "number", float(u), tolerance=0.01,
                 explain=f"$f({u}) = {L(v)}$, so $f^{{-1}}({L(v)}) = {u}$: the inverse sends the output back to its input."),
        ]
        checks = [("exists", same(f.subs(x, inv), x), "the formula doesn't undo f"), ("clean", clean(v), "value isn't clean")]
        story = f"Let $f(x) = {L(f)}$."
        scene = {"type": "integral", "tex": f"y = {L(f)}", "rule": "\\text{swap } x \\text{ and } y, \\text{ then solve for } y"}
        return Solution(steps, story, scene, ["swap-and-solve", "evaluate"], {"_checks": checks})


FRAMEWORK = Functions()
