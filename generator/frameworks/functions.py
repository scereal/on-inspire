"""Functions and graphs (MATH 140, outcomes 140.1.1–140.1.3). Plan: design/plans/2026-10-05-math-140-functions.md.

Level 1: domain from a formula.
Level 2: composition.
Level 3: inverse functions.
Level 4: graph transformations.
Level 5: exponential and logarithmic equations.
Level 6: exact trig values.
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


# Level 4 ----------------------------------------------------------------------------

BASES = {"square": x**2, "sqrt": sp.sqrt(x), "abs": sp.Abs(x), "recip": 1 / x}
BASE_TEX = {"square": "x^2", "sqrt": "\\sqrt{x}", "abs": "|x|", "recip": "\\frac{1}{x}"}
NICE_T = {"square": [1, 2, -1, -2], "sqrt": [1, 4, 9], "abs": [2, -3, 1], "recip": [1, 2, -1]}


def base_tex(name, inner):
    if name == "square":
        return "x^2" if inner == "x" else f"({inner})^2"
    return {"sqrt": f"\\sqrt{{{inner}}}", "abs": f"|{inner}|", "recip": f"\\frac{{1}}{{{inner}}}"}[name]


def inner_tex(h):
    return "x" if h == 0 else (f"x - {h}" if h > 0 else f"x + {-h}")


def coef_tex(a):
    a = sp.Rational(a)
    if a == 1:
        return ""
    if a == -1:
        return "-"
    return L(a)


def transformed(p):
    a = sp.Rational(p["a"])
    return a * BASES[p["base"]].subs(x, x - p["h"]) + p["k"]


def transform_tex(name, a, h, k):
    return f"{coef_tex(a)}{base_tex(name, inner_tex(h))}{plus(k)}"


# Level 5 ----------------------------------------------------------------------------

LOG_PAIRS = [(b, b**i, b**j) for b, top in ((2, 10), (3, 6), (5, 4), (10, 4))
             for i in range(1, top + 1) for j in range(0, i) if i + j <= top]


class Functions(Framework):
    id = "functions"
    title = "Functions and graphs"
    outcome = "Work with domains, compositions and inverses, transform graphs, and use exponentials, logarithms and trig values."
    levels = {
        1: Level("Domain", {"condition": 1, "domain": 1}),
        2: Level("Composition", {"inner": 1, "outer": 1, "formula": 1}),
        3: Level("Inverse functions", {"swap-and-solve": 1, "evaluate": 1}),
        4: Level("Transforming graphs", {"formula": 1, "evaluate": 1}),
        5: Level("Exponential and log equations", {"rewrite": 1, "solve": 1}),
        6: Level("Exact trig values", {"quadrant": 1, "value": 1}),
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
        "shift-sign": "Shifted the wrong way: (x − h) moves the graph right by h.",
        "horizontal-as-vertical": "Turned a sideways shift into an up/down shift.",
        "vertical-sign": "Shifted down instead of up (or the reverse).",
        "stretch-inside": "Put the stretch inside the function, which squeezes the graph sideways instead.",
        "miscounted-power": "Miscounted the power: check by multiplying it out.",
        "log-of-sum": "Added the arguments. log A + log B = log(AB), a product.",
        "logs-multiply": "Multiplied the logs. log A + log B = log(AB).",
        "kept-extraneous": "Kept a root that makes a log's argument negative. Logs only take positive inputs.",
        "picked-wrong-root": "Kept the root that makes a log's argument negative and dropped the valid one.",
        "quadrant-sign": "Got the sign wrong for that quadrant.",
        "wrong-quadrant": "Placed the angle in the wrong quadrant.",
        "cofunction-swap": "Swapped sine and cosine (or tangent and cotangent).",
        "special-value-mixup": "Mixed up the special values (1/2, √2/2, √3/2 belong to different angles).",
        "reference-slip": "Used the wrong reference angle (π/6 and π/3 swap their sine and cosine).",
    }
    targets = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100}

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
        if level == 4:
            base = rng.choice(list(BASES))
            return {"base": base, "a": rng.choice(["1", "1", "1", "2", "-1", "3", "1/2", "-2"]), "h": rng.randint(-4, 4),
                    "k": rng.randint(-4, 4), "t": rng.choice(NICE_T[base])}
        if level == 5:
            if rng.random() < 0.45:
                b, X, Y = rng.choice(LOG_PAIRS)
                return {"family": "log", "b": b, "p": 0, "q": 0, "x0": X, "d": X - Y}
            return {"family": "exp", "b": rng.choice([2, 3, 5, 10]), "p": rng.randint(1, 3), "q": rng.randint(-3, 3),
                    "x0": rng.randint(-2, 5), "d": 0}
        if level == 6:
            den = rng.choice([6, 4, 3])
            nums = {6: [1, 5, 7, 11, 13, 17], 4: [1, 3, 5, 7, 9, 11], 3: [1, 2, 4, 5, 7, 8]}[den]   # includes coterminal angles past 2π
            return {"func": rng.choice(["sin", "cos", "tan"]), "num": rng.choice(nums) * rng.choice([1, -1]), "den": den}
        family = rng.choice(["linear", "cube", "mobius"])
        if family == "mobius":
            return {"family": family, "a": nz(-3, 3), "b": rng.randint(-5, 5), "d": nz(-4, 4), "u": rng.randint(-3, 3)}
        return {"family": family, "a": nz(-5, 5) if family == "linear" else 1, "b": rng.randint(-8, 8), "d": 0, "u": rng.randint(-3, 3)}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._domain, self._composition, self._inverse, self._transform, self._exp_log, self._trig][level](p)

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


    # Level 4 ----------------------------------------------------------------------------
    def _transform(self, p):
        name, a, h, k, t = p["base"], sp.Rational(p["a"]), p["h"], p["k"], p["t"]
        if a == 1 and h == 0 and k == 0:
            raise NoSolution("nothing to transform")
        base = BASES[name]
        g = transformed(p)
        parts = []
        if a < 0:
            parts.append("reflected in the $x$-axis")
        if abs(a) > 1:
            parts.append(f"stretched vertically by a factor of {abs(a)}")
        elif 0 < abs(a) < 1:
            parts.append(f"compressed vertically by a factor of {L(1 / abs(a))}")
        if h:
            parts.append(f"shifted {abs(h)} unit{'s' if abs(h) > 1 else ''} {'right' if h > 0 else 'left'}")
        if k:
            parts.append(f"shifted {abs(k)} unit{'s' if abs(k) > 1 else ''} {'up' if k > 0 else 'down'}")
        desc = ", then ".join(parts)
        cands = []
        if h:
            cands.append(("shift-sign", a * base.subs(x, x + h) + k, transform_tex(name, a, -h, k),
                          f"$(x - {h})$ moves the graph right by {h}: the old $x = 0$ behaviour now happens at $x = {h}$." if h > 0 else
                          f"$(x + {-h})$ moves the graph left by {-h}: the old $x = 0$ behaviour now happens at $x = {h}$."))
            cands.append(("horizontal-as-vertical", a * base + k - h, f"{coef_tex(a)}{base_tex(name, 'x')}{plus(k - h)}",
                          f"A sideways shift changes the input, so it goes inside the function: ${inner_tex(h)}$."))
        if k:
            cands.append(("vertical-sign", a * base.subs(x, x - h) - k, transform_tex(name, a, h, -k),
                          f"Adding ${k}$ outside the function moves every point {'up' if k > 0 else 'down'} by {abs(k)}."))
        if a != 1:
            inside = f"{coef_tex(a) if a != -1 else '-'}({inner_tex(h)})" if h else f"{coef_tex(a)}x"
            cands.append(("stretch-inside", base.subs(x, a * (x - h)) + k, f"{base_tex(name, inside)}{plus(k)}",
                          "A vertical stretch multiplies the outputs, so the factor goes outside the function."))
        wrongs = pick(g, cands)
        steps = [
            self._choice(f"Which equation gives the new graph?", f"$y = {transform_tex(name, a, h, k)}$", "right",
                         [(m, f"$y = {lbl}$", f"w{i}", fb) for i, (m, e, lbl, fb) in enumerate(wrongs)]),
            Step(f"What is $y$ at $x = {h + t}$?", "number", float(g.subs(x, h + t)), tolerance=0.01,
                 explain=f"$y({h + t}) = {transform_tex(name, a, h, k).replace('x', '(' + str(h + t) + ')')} = {L(g.subs(x, h + t))}$"),
        ]
        story = f"The graph of $y = {BASE_TEX[name]}$ is {desc}."
        scene = {"type": "integral", "tex": "y = a\\,f(x - h) + k", "rule": "\\text{inside: sideways and backwards; outside: up/down as written}"}
        checks = [("clean", clean(g.subs(x, h + t)), "value isn't clean")]
        return Solution(steps, story, scene, ["formula", "evaluate"], {"_checks": checks})

    # Level 5 ----------------------------------------------------------------------------
    def _exp_log(self, p):
        b = p["b"]
        if p["family"] == "exp":
            pp, q, x0 = p["p"], p["q"], p["x0"]
            n = pp * x0 + q
            if n < 1 or b**n > 100000:
                raise NoSolution("the right side must be a modest whole power")
            power = f"{b}^{{{L(pp * x + q)}}}"
            rewrite = self._choice(f"Write {b**n} as a power of {b}:", f"${b}^{{{n}}}$", "right", [
                ("miscounted-power", f"${b}^{{{n + 1}}}$", "up", f"${b}^{{{n + 1}}} = {b**(n + 1)}$, not {b**n}."),
                ("miscounted-power", f"${b}^{{{n - 1}}}$", "down", f"${b}^{{{n - 1}}} = {b**(n - 1)}$, not {b**n}."),
            ])
            steps = [rewrite,
                     Step("Set the exponents equal. What is $x$?", "number", float(x0), tolerance=0.01,
                          explain=f"${L(pp * x + q)} = {n}$, so $x = {x0}$.")]
            story = f"Solve ${power} = {b**n}$."
            scene = {"type": "integral", "tex": f"{power} = {b**n}", "rule": "b^{u} = b^{v} \\implies u = v"}
        else:
            X, d = p["x0"], p["d"]
            Y = X - d
            n = sp.log(X * Y, b)
            n = int(sp.nsimplify(n))
            lg = f"\\log_{{{b}}}"
            combine = self._choice("Combine the logs on the left:", f"${lg}\\big(x(x - {d})\\big) = {n}$", "right", [
                ("log-of-sum", f"${lg}(2x - {d}) = {n}$", "sum", f"Logs add when their arguments multiply: ${lg} A + {lg} B = {lg}(AB)$."),
                ("logs-multiply", f"${lg} x \\cdot {lg}(x - {d}) = {n}$", "times", "The sum of logs becomes the log of a product, not a product of logs."),
            ])
            roots = f"$x = {X}$"
            solve = self._choice(f"So $x(x - {d}) = {b}^{{{n}}} = {X * Y}$. Which solutions are valid?", roots, "right", [
                ("kept-extraneous", f"$x = {X}$ or $x = {-Y}$", "both", f"$x = {-Y}$ makes $x$ negative, and $\\log_{{{b}}}$ of a negative number is undefined."),
                ("picked-wrong-root", f"$x = {-Y}$", "neg", f"$x = {-Y}$ gives a negative argument; $x = {X}$ works: ${lg} {X} + {lg} {Y} = {n}$."),
            ])
            steps = [combine, solve]
            story = f"Solve ${lg} x + {lg}(x - {d}) = {n}$."
            scene = {"type": "integral", "tex": f"{lg} x + {lg}(x - {d}) = {n}", "rule": "\\log_b A + \\log_b B = \\log_b(AB)"}
        return Solution(steps, story, scene, ["rewrite", "solve"], {"_checks": []})

    # Level 6 ----------------------------------------------------------------------------
    def _trig(self, p):
        fname, num, den = p["func"], p["num"], p["den"]
        theta = sp.pi * sp.Rational(num, den)
        F = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
        v = sp.nsimplify(F[fname](theta))
        if v == 0 or v.has(sp.zoo):
            raise NoSolution("axis angle or undefined")
        frac = (sp.Rational(num, den) % 2)                      # position in [0, 2) half-turns
        quad = int(frac * 2) + 1
        sign = "positive" if v > 0 else "negative"
        other = lambda s_: "negative" if s_ == "positive" else "positive"
        q2 = quad % 4 + 1
        v2 = sp.nsimplify(F[fname](sp.pi * (sp.Rational(2 * q2 - 1, 4))))
        roman = {1: "I", 2: "II", 3: "III", 4: "IV"}
        quad_step = self._choice(f"Which quadrant is ${L(theta)}$ in, and what sign does $\\{fname}$ have there?",
                                 f"Quadrant {roman[quad]}, where $\\{fname}$ is {sign}", "right", [
            ("quadrant-sign", f"Quadrant {roman[quad]}, where $\\{fname}$ is {other(sign)}", "sign",
             "Recall the signs by quadrant: all positive in I, only sine in II, only tangent in III, only cosine in IV."),
            ("wrong-quadrant", f"Quadrant {roman[q2]}, where $\\{fname}$ is {'positive' if v2 > 0 else 'negative'}", "quad",
             f"${L(theta)}$ is ${L(sp.Rational(num, den))}$ of a half-turn: measure from the positive $x$-axis, counterclockwise for positive angles."),
        ])
        co = {"sin": sp.cos, "cos": sp.sin, "tan": lambda u: 1 / sp.tan(u)}[fname]
        refang = sp.Abs(sp.Rational(num, den) - sp.Rational(round(float(sp.Rational(num, den))), 1)) * sp.pi
        swapped_ref = sp.pi / 2 - refang
        cands = [("quadrant-sign", -v, "Right size, wrong sign: check which quadrant the angle is in."),
                 ("cofunction-swap", sp.nsimplify(co(theta)), f"That's the value of the co-function. ${'\\sin' if fname == 'sin' else ('\\cos' if fname == 'cos' else '\\tan')}$ is the {'height' if fname == 'sin' else ('width' if fname == 'cos' else 'slope')} on the unit circle."),
                 ("reference-slip", sp.nsimplify((1 if v > 0 else -1) * abs(F[fname](swapped_ref))), f"The reference angle is ${L(refang)}$, not ${L(swapped_ref)}$.")]
        sgn = 1 if v > 0 else -1
        table = {"sin": [sp.Rational(1, 2), sp.sqrt(2) / 2, sp.sqrt(3) / 2], "cos": [sp.Rational(1, 2), sp.sqrt(2) / 2, sp.sqrt(3) / 2],
                 "tan": [sp.sqrt(3) / 3, 1, sp.sqrt(3)]}[fname]
        for w in table:                                       # the other special values, with the right sign
            cands.append(("special-value-mixup", sp.sympify(sgn * w),
                          f"That's the value at a different special angle. At reference angle ${L(refang)}$, $|\\{fname}| = {L(abs(v))}$."))
        wrongs = pick(v, [(m, e, fb) for m, e, fb in cands if e.is_finite])
        value_step = self._choice(f"What is $\\{fname}\\left({L(theta)}\\right)$?", f"${L(v)}$", sp.sstr(v),
                                  [(m, f"${L(e)}$", sp.sstr(e), fb) for m, e, fb in wrongs])
        story = f"Find the exact value of $\\{fname}\\left({L(theta)}\\right)$."
        scene = {"type": "integral", "tex": f"\\{fname}\\left({L(theta)}\\right)", "rule": "\\text{reference angle, then the quadrant's sign}"}
        return Solution([quad_step, value_step], story, scene, ["quadrant", "value"], {"_checks": []})


FRAMEWORK = Functions()
