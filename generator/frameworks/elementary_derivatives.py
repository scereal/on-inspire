"""Differentiating elementary functions (MATH 140, outcomes 140.4.1–140.4.4). Plan: design/plans/2026-10-05-math-140-elementary.md.

Level 1: sin, cos and tan, with the chain rule.
Level 2: exponentials and logarithms.
Level 3: the derivative of an inverse function.
Level 4: inverse trig.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x = sp.Symbol("x")
MAX_DEN = 20


def L(e):
    """TeX the way a calculus course writes it: ln, arctan, arcsin."""
    return sp.latex(e, ln_notation=True, inv_trig_style="full")


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else L(v))


def tex(e):
    return f"${L(e)}$"


def key(e):
    return sp.sstr(sp.simplify(e))


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 400


def same(a, b):
    return sp.simplify(sp.expand_log(a - b, force=True)) == 0


def pick(right, candidates, n=2):
    """Keep up to n (misconception, expression) candidates that differ from the answer and from each other."""
    kept = []
    for name, e in candidates:
        if same(e, right) or any(same(e, k) for _, k in kept):
            continue
        kept.append((name, e))
        if len(kept) == n:
            break
    return kept


# Level 1 ----------------------------------------------------------------------------

def trig_function(p):
    k = p["k"]
    if p["family"] == "tan":
        return p["c"] * sp.tan(k * x)
    return p["a"] * sp.sin(k * x) + p["b"] * sp.cos(k * x)


def trig_point(p):
    if p["at"] == "0":
        return sp.Integer(0)
    return sp.pi / (2 * p["k"]) if p["family"] == "sincos" else sp.pi / (4 * p["k"])


# Level 4 ----------------------------------------------------------------------------

def inverse_trig(p):
    k, m = p["k"], p["m"]
    f = k * (sp.atan(m * x) if p["family"] == "atan" else sp.asin(m * x))
    point = sp.Rational(1, m) if p["at"] == "one" else sp.Integer(0)
    return f, point


FEEDBACK = {
    "cos-sign": "The derivative of $\\cos$ is $-\\sin$: cosine starts by falling as $x$ grows past 0.",
    "dropped-inner": "The chain rule multiplies by the derivative of the inside, $kx$, which is $k$.",
    "antiderivative": "That undoes the derivative instead of taking it: it's an antiderivative.",
    "sec-not-squared": "The derivative of $\\tan x$ is $\\sec^2 x$, from the quotient rule on $\\frac{\\sin x}{\\cos x}$.",
    "tan-sign": "$\\tan$ is increasing everywhere it's defined, so its derivative $\\sec^2$ is positive.",
    "exp-dropped-inner": "$e^{kx}$ needs the chain rule: its derivative is $k e^{kx}$.",
    "power-rule-on-exp": "The power rule is for a variable base and a fixed exponent. Here the exponent varies: $(e^{u})' = e^{u}u'$.",
    "dropped-power": "Differentiate the $x^2$ term too: $(x^2)' = 2x$.",
    "dropped-linear": "The $bx$ term has derivative $b$; don't drop it.",
    "ln-kept-k": "$\\ln(mx) = \\ln m + \\ln x$, and the constant $\\ln m$ has derivative 0. So $(\\ln mx)' = \\frac{1}{x}$, not $\\frac{m}{x}$.",
    "ln-reciprocal-inside": "The chain rule gives $\\frac{1}{mx}\\cdot m = \\frac{1}{x}$: the $m$ cancels.",
    "exp-rule-without-ln": "Only $e^x$ is its own derivative. For $2^x = e^{x\\ln 2}$, the chain rule brings out $\\ln 2$.",
    "used-b": "That's the output. You need the input $a$ that $f$ sends to the given value.",
    "solved-wrong": "Check by substituting: that input doesn't give the right output.",
    "forgot-to-flip": "The inverse's slope is the reciprocal of $f$'s slope: mirroring across $y = x$ swaps rise and run.",
    "wrong-point": "Evaluate $f'$ at the input $a$ (where $f(a) = b$), not at $b$.",
    "arctan-no-chain": "The chain rule multiplies by the derivative of the inside, $mx$, and squares it in the denominator.",
    "square-slip": "Inside $\\frac{1}{1 + u^2}$ the whole $u = mx$ is squared: $m^2x^2$.",
    "arcsin-confused": "That's the shape of the arcsin derivative. arctan gives $\\frac{1}{1 + u^2}$.",
    "arctan-confused": "That's the shape of the arctan derivative. arcsin gives $\\frac{1}{\\sqrt{1 - u^2}}$.",
    "sign-slip": "Check the sign inside: it comes from $1 + \\tan^2 = \\sec^2$ for arctan and $1 - \\sin^2 = \\cos^2$ for arcsin.",
    "arcsin-no-chain": "The chain rule multiplies by the derivative of the inside, $mx$, and the inside is squared under the root.",
}


class ElementaryDerivatives(Framework):
    id = "elementary-derivatives"
    title = "Derivatives of elementary functions"
    outcome = "Differentiate trig, exponential, logarithmic and inverse functions, implicitly defined curves, and higher derivatives."
    levels = {
        1: Level("Trig functions", {"differentiate": 1, "evaluate": 1}),
        2: Level("Exponentials and logarithms", {"differentiate": 1, "evaluate": 1}),
        3: Level("Inverse functions", {"find-input": 1, "slope": 1, "reciprocal": 1}),
        4: Level("Inverse trig", {"differentiate": 1, "evaluate": 1}),
    }
    misconceptions = {k: v.replace("$", "") for k, v in FEEDBACK.items()}
    targets = {1: 100, 2: 100, 3: 100, 4: 100}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        nz = lambda lo, hi: rng.choice([v for v in range(lo, hi + 1) if v])
        if level == 1:
            if rng.random() < 0.3:
                return {"family": "tan", "c": nz(-3, 4), "k": rng.randint(1, 3), "at": rng.choice(["0", "quarter"])}
            return {"family": "sincos", "a": nz(-3, 4), "b": nz(-3, 4), "k": rng.randint(1, 4), "at": rng.choice(["0", "quarter"])}
        if level == 2:
            family = rng.choice(["exp", "log", "log", "pow2"])
            if family == "exp":
                return {"family": family, "a": nz(-3, 4), "k": rng.choice([2, 3, 4, -1, -2]), "b": rng.randint(-4, 4)}
            if family == "log":
                return {"family": family, "c": nz(-3, 5), "m": rng.randint(2, 6), "b": nz(-3, 3)}
            return {"family": family, "a": nz(-3, 5)}
        if level == 3:
            return {"p": rng.randint(1, 5), "q": rng.randint(-5, 5), "a": nz(-3, 3)}
        family = rng.choice(["atan", "atan", "asin"])
        return {"family": family, "k": nz(-3, 4), "m": rng.randint(1, 5), "at": "zero" if family == "asin" else rng.choice(["zero", "one"])}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._trig, self._exp_log, self._inverse, self._inverse_trig][level](p)

    # Shared: a "which derivative" step from the right answer and named mistakes
    def _derivative_step(self, prompt, right, candidates):
        wrongs = pick(right, candidates)
        if not wrongs:
            raise NoSolution("every named mistake coincides with the answer")
        return Step(prompt, "choice", tex(right), options=[Option(tex(right), correct=True, value=key(right))] +
                    [Option(tex(e), misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in wrongs])

    # Level 1 ----------------------------------------------------------------------------
    def _trig(self, p):
        f, k = trig_function(p), p["k"]
        right = sp.diff(f, x)
        if p["family"] == "tan":
            c = p["c"]
            right = sp.Mul(c * k, sp.sec(k * x) ** 2, evaluate=False)     # same function, written as sec²
            cands = [("sec-not-squared", c * k * sp.sec(k * x)), ("dropped-inner", c * sp.sec(k * x) ** 2),
                     ("tan-sign", -c * k * sp.sec(k * x) ** 2)]
        else:
            a, b = p["a"], p["b"]
            cands = [("cos-sign", a * k * sp.cos(k * x) + b * k * sp.sin(k * x)),
                     ("dropped-inner", a * sp.cos(k * x) - b * sp.sin(k * x)),
                     ("antiderivative", sp.integrate(f, x))]
        point = trig_point(p)
        value = sp.nsimplify(right.subs(x, point))
        where = L(point)
        steps = [
            self._derivative_step("What is $f'(x)$?", right, cands),
            Step(f"Evaluate $f'({where})$.", "number", float(value), tolerance=0.01,
                 explain=f"$f'({where}) = {L(value)}$"),
        ]
        checks = [("clean", clean(value), "value isn't clean")]
        story = f"Let $f(x) = {L(f)}$."
        scene = {"type": "integral", "tex": f"\\frac{{d}}{{dx}}\\left[{L(f)}\\right]", "rule": "(\\sin u)' = u'\\cos u, \\quad (\\cos u)' = -u'\\sin u"}
        return Solution(steps, story, scene, ["differentiate", "evaluate"], {"value": float(value), "_checks": checks})

    # Level 2 ----------------------------------------------------------------------------
    def _exp_log(self, p):
        fam = p["family"]
        if fam == "exp":
            a, k, b = p["a"], p["k"], p["b"]
            f = a * sp.exp(k * x) + b * x
            cands = [("exp-dropped-inner", a * sp.exp(k * x) + b), ("power-rule-on-exp", a * k * x * sp.exp(k * x - 1) + b),
                     ("dropped-linear", a * k * sp.exp(k * x))]
            point = sp.Integer(0)
        elif fam == "log":
            c, m, b = p["c"], p["m"], p["b"]
            f = c * sp.log(m * x) + b * x**2
            cands = [("ln-kept-k", c * m / x + 2 * b * x), ("ln-reciprocal-inside", c / (m * x) + 2 * b * x),
                     ("dropped-power", c / x + b * x)]
            point = sp.Integer(1)
        else:
            a = p["a"]
            f = a * 2**x
            cands = [("exp-rule-without-ln", a * 2**x), ("power-rule-on-exp", a * x * 2 ** (x - 1))]
            point = sp.Integer(0)
        right = sp.diff(f, x)
        value = sp.nsimplify(right.subs(x, point))
        steps = [self._derivative_step("What is $f'(x)$?", right, cands)]
        if fam == "pow2":
            a = p["a"]
            steps.append(Step("Evaluate $f'(0)$.", "choice", tex(a * sp.log(2)), options=[
                Option(tex(a * sp.log(2)), correct=True, value="ln2"),
                Option(f"${a}$", misconception="exp-rule-without-ln", value="a", feedback=FEEDBACK["exp-rule-without-ln"]),
                Option("$0$", misconception="power-rule-on-exp", value="0", feedback=FEEDBACK["power-rule-on-exp"]),
            ]))
            checks = []
        else:
            steps.append(Step(f"Evaluate $f'({point})$.", "number", float(value), tolerance=0.01,
                              explain=f"$f'({point}) = {L(value)}$"))
            checks = [("clean", clean(value), "value isn't clean")]
        story = f"Let $f(x) = {L(f)}$."
        scene = {"type": "integral", "tex": f"\\frac{{d}}{{dx}}\\left[{L(f)}\\right]", "rule": "(e^{u})' = u'e^{u}, \\quad (\\ln u)' = \\frac{u'}{u}"}
        return Solution(steps, story, scene, ["differentiate", "evaluate"], {"_checks": checks})

    # Level 3 ----------------------------------------------------------------------------
    def _inverse(self, p):
        pp, q, a = p["p"], p["q"], p["a"]
        f = x**3 + pp * x + q
        b = f.subs(x, a)
        if b == a:
            raise NoSolution("a = b makes the wrong-point mistake give the right answer")
        fa = sp.diff(f, x).subs(x, a)
        fb = sp.diff(f, x).subs(x, b)
        guess = next(g for g in (a + 1, a - 1, a + 2, a - 2) if g not in (a, b) and f.subs(x, g) != b)
        steps = [
            Step(f"Which input $a$ has $f(a) = {b}$?", "choice", f"${a}$", options=[
                Option(f"$a = {a}$", correct=True, value=str(a)),
                Option(f"$a = {b}$", misconception="used-b", value=str(b), feedback=FEEDBACK["used-b"]),
                Option(f"$a = {guess}$", misconception="solved-wrong", value=str(guess),
                       feedback=f"$f({guess}) = {f.subs(x, guess)}$, not ${b}$."),
            ]),
            Step(f"What is $f'({a})$?", "number", float(fa), tolerance=0.01, explain=f"$f'(x) = 3x^2 + {pp}$, so $f'({a}) = {fa}$."),
            Step(f"What is $(f^{{-1}})'({b})$?", "choice", tex(1 / fa), options=[
                Option(tex(sp.Rational(1, 1) / fa), correct=True, value=num(1 / fa)),
                Option(tex(fa), misconception="forgot-to-flip", value=num(fa), feedback=FEEDBACK["forgot-to-flip"]),
                Option(tex(sp.Rational(1, 1) / fb), misconception="wrong-point", value=num(1 / fb), feedback=FEEDBACK["wrong-point"]),
            ]),
        ]
        story = f"$f(x) = {L(f)}$ is always increasing, so it has an inverse $f^{{-1}}$."
        scene = {"type": "integral", "tex": f"(f^{{-1}})'({b}) = \\frac{{1}}{{f'(a)}} \\quad \\text{{where }} f(a) = {b}", "rule": ""}
        return Solution(steps, story, scene, ["find-input", "slope", "reciprocal"], {"slope": float(1 / fa), "_checks": []})

    # Level 4 ----------------------------------------------------------------------------
    def _inverse_trig(self, p):
        f, point = inverse_trig(p)
        k, m = p["k"], p["m"]
        right = sp.diff(f, x)
        if p["family"] == "atan":
            cands = [("arctan-no-chain", k / (1 + x**2)), ("square-slip", k * m / (1 + m * x**2)),
                     ("arcsin-confused", k * m / sp.sqrt(1 - m**2 * x**2)), ("sign-slip", k * m / (1 - m**2 * x**2))]
        else:
            cands = [("arcsin-no-chain", k / sp.sqrt(1 - x**2)), ("arctan-confused", k * m / (1 + m**2 * x**2)),
                     ("sign-slip", k * m / sp.sqrt(1 + m**2 * x**2))]
        value = sp.nsimplify(right.subs(x, point))
        where = L(point)
        steps = [
            self._derivative_step("What is $f'(x)$?", right, cands),
            Step(f"Evaluate $f'({where})$.", "number", float(value), tolerance=0.01, explain=f"$f'({where}) = {L(value)}$"),
        ]
        story = f"Let $f(x) = {L(f)}$."
        scene = {"type": "integral", "tex": f"\\frac{{d}}{{dx}}\\left[{L(f)}\\right]", "rule": "(\\arctan u)' = \\frac{u'}{1 + u^2}, \\quad (\\arcsin u)' = \\frac{u'}{\\sqrt{1 - u^2}}"}
        checks = [("clean", clean(value), "value isn't clean")]
        return Solution(steps, story, scene, ["differentiate", "evaluate"], {"value": float(value), "_checks": checks})


FRAMEWORK = ElementaryDerivatives()
