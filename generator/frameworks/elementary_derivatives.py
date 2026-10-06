"""Differentiating elementary functions (MATH 140, outcomes 140.4.1–140.4.4). Plan: design/plans/2026-10-05-math-140-elementary.md.

Level 1: sin, cos and tan, with the chain rule.
Level 2: exponentials and logarithms.
Level 3: the derivative of an inverse function.
Level 4: inverse trig.
Level 5: implicit differentiation.
Level 6: logarithmic differentiation.
Level 7: higher derivatives (velocity, acceleration, concavity).
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x, y, t = sp.symbols("x y t")
yp = sp.Symbol("y'")
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


# Level 5 ----------------------------------------------------------------------------

LATTICE = {5: [(3, 4), (4, 3)], 10: [(6, 8), (8, 6)], 13: [(5, 12), (12, 5)]}


def implicit_curve(p):
    """F(x, y) with the curve F = 0."""
    if p["family"] == "circle":
        return x**2 + y**2 - p["r"] ** 2
    if p["family"] == "hyperbola":
        return x * y - p["c"]
    return x**2 + x * y + y**2 - (p["px"] ** 2 + p["px"] * p["py"] + p["py"] ** 2)


# Level 6 ----------------------------------------------------------------------------

def log_diff_function(p):
    a, b, c = p["a"], p["b"], p["c"]
    if p["family"] == "power":
        return x ** (a * x**2 + b * x + c)
    if p["family"] == "product":
        return x**a * (x + 1) ** b * (x + 3) ** c
    return x**a * (x + 1) ** b / (x + 3) ** c


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
    "forgot-chain-on-y": "$y$ depends on $x$, so the chain rule applies: $(y^2)' = 2y\\,y'$, not $2y$.",
    "chain-dropped-outer": "The chain rule keeps the outer derivative too: $(y^2)' = 2y\\cdot y'$, not just $2y'$.",
    "treated-y-as-x": "$y$ changes with $x$, so its derivative is $y'$, not 1: $(xy)' = y + x\\,y'$, and every $y$-term picks up a factor $y'$.",
    "forgot-product-rule": "$xy$ is a product of two things that change with $x$: $(xy)' = y + x\\,y'$.",
    "implicit-sign-slip": "Moving the $x$-terms to the other side flips their sign.",
    "implicit-swapped": "Solve for $y'$: it's the $x$-derivative over the $y$-derivative, with a minus sign, not the other way up.",
    "exponent-not-down": "The point of the log is that it brings the exponent down: $\\ln(x^{p}) = p\\ln x$.",
    "log-of-exponent": "The log brings the exponent down as a factor: $\\ln(x^{p}) = p\\ln x$, not $\\ln p\\cdot\\ln x$.",
    "logs-multiply": "Logs turn products into sums, not products of logs: $\\ln(AB) = \\ln A + \\ln B$.",
    "forgot-y": "That's $\\frac{y'}{y}$. Multiply both sides by $y$ to get $y'$ itself.",
    "power-rule-on-variable-exponent": "The power rule needs a fixed exponent. Here the exponent changes with $x$, which is why you take logs.",
    "differentiated-each-factor": "You can't differentiate a product factor by factor. Logs turn it into a sum first.",
    "constant-not-zero": "The constant term's derivative is 0.",
    "exponent-unchanged": "The power rule lowers each exponent by one.",
    "dropped-coefficient": "The power rule brings the exponent down as a coefficient: $(t^3)' = 3t^2$.",
    "acceleration-is-velocity": "That's the velocity again. Acceleration is the derivative of velocity: differentiate once more.",
    "forgot-to-double": "$(t^2)'' = 2$: differentiate $2bt$ to get $2b$.",
    "concavity-from-f-prime": "Concavity comes from the sign of the second derivative, not the first.",
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
        5: Level("Implicit differentiation", {"differentiate-both-sides": 1, "solve-for-y'": 1, "evaluate": 1}),
        6: Level("Logarithmic differentiation", {"take-logs": 1, "differentiate": 1, "evaluate": 1}),
        7: Level("Higher derivatives", {"velocity": 1, "acceleration": 1, "evaluate": 1, "concavity": 1}),
    }
    misconceptions = {k: v.replace("$", "") for k, v in FEEDBACK.items()}
    targets = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}

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
        if level == 4:
            family = rng.choice(["atan", "atan", "asin"])
            return {"family": family, "k": nz(-3, 4), "m": rng.randint(1, 5), "at": "zero" if family == "asin" else rng.choice(["zero", "one"])}
        if level == 5:
            family = rng.choice(["circle", "circle", "hyperbola", "mixed"])
            if family == "circle":
                r = rng.choice(list(LATTICE))
                px, py = rng.choice(LATTICE[r])
                return {"family": family, "r": r, "px": px * rng.choice([1, -1]), "py": py * rng.choice([1, -1])}
            if family == "hyperbola":
                px, py = nz(-4, 4), nz(-4, 4)
                return {"family": family, "c": px * py, "px": px, "py": py}
            return {"family": family, "px": nz(-3, 3), "py": nz(-3, 3)}
        if level == 6:
            family = rng.choice(["power", "power", "product", "quotient"])
            if family == "power":
                return {"family": family, "a": rng.randint(-2, 2), "b": rng.randint(-3, 3), "c": rng.randint(-3, 3)}
            return {"family": family, "a": rng.randint(1, 3), "b": rng.randint(1, 3), "c": rng.randint(1, 2) if family == "product" else 1}
        return {"a": nz(-2, 2), "b": rng.randint(-6, 6), "c": rng.randint(-5, 5), "d": rng.randint(-5, 5), "t0": rng.randint(0, 4)}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._trig, self._exp_log, self._inverse, self._inverse_trig,
                self._implicit, self._log_diff, self._higher][level](p)

    # Shared: a "which derivative" step from the right answer and named mistakes
    def _derivative_step(self, prompt, right, candidates, overrides=None):
        wrongs = pick(right, candidates)
        if len(wrongs) < 2:
            raise NoSolution("fewer than two distinct named mistakes: the step would be a coin flip")
        fb = {**FEEDBACK, **(overrides or {})}
        return Step(prompt, "choice", tex(right), options=[Option(tex(right), correct=True, value=key(right))] +
                    [Option(tex(e), misconception=m, feedback=fb[m], value=key(e)) for m, e in wrongs])

    # Level 1 ----------------------------------------------------------------------------
    def _trig(self, p):
        f, k = trig_function(p), p["k"]
        right = sp.diff(f, x)
        if p["family"] == "tan":
            c = p["c"]
            right = sp.Mul(c * k, sp.sec(k * x) ** 2, evaluate=abs(c * k) == 1)     # same function, written as sec²
            cands = [("sec-not-squared", c * k * sp.sec(k * x)), ("dropped-inner", c * sp.sec(k * x) ** 2),
                     ("tan-sign", -c * k * sp.sec(k * x) ** 2)]
            overrides = {"tan-sign": f"$\\sec^2$ is always positive, so $f'$ has the sign of its coefficient ${c * k}$."}
        else:
            a, b = p["a"], p["b"]
            cands = [("cos-sign", a * k * sp.cos(k * x) + b * k * sp.sin(k * x)),
                     ("dropped-inner", a * sp.cos(k * x) - b * sp.sin(k * x)),
                     ("antiderivative", sp.integrate(f, x))]
        point = trig_point(p)
        value = sp.nsimplify(right.subs(x, point))
        where = L(point)
        steps = [
            self._derivative_step("What is $f'(x)$?", right, cands, overrides if p["family"] == "tan" else None),
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


    # Level 5 ----------------------------------------------------------------------------
    def _implicit(self, p):
        F, px, py = implicit_curve(p), p["px"], p["py"]
        point = {x: px, y: py}
        if F.subs(point) != 0:
            raise NoSolution("the point isn't on the curve")
        Fx, Fy = sp.diff(F, x), sp.diff(F, y)
        if Fy.subs(point) == 0:
            raise NoSolution("vertical tangent at the point")
        left = sp.expand(Fx + Fy * yp)                       # d/dx of F(x, y(x))
        rhs = sp.Integer(0)
        slope_expr = -Fx / Fy
        slope = slope_expr.subs(point)
        if p["family"] == "circle":
            show = x**2 + y**2
            cands = [("forgot-chain-on-y", 2 * x + 2 * y), ("chain-dropped-outer", 2 * x + 2 * yp)]
            rhs = sp.Integer(p["r"] ** 2)
        elif p["family"] == "hyperbola":
            show = x * y
            cands = [("forgot-product-rule", x * yp), ("treated-y-as-x", y + x)]
            rhs = sp.Integer(p["c"])
        else:
            show = x**2 + x * y + y**2
            cands = [("forgot-product-rule", 2 * x + x * yp + 2 * y * yp), ("treated-y-as-x", 2 * x + y + x + 2 * y),
                     ("chain-dropped-outer", 2 * x + y + x * yp + 2 * yp)]
            rhs = show.subs(point)
        lw = pick(left, cands)
        d_step = Step("Differentiate both sides with respect to $x$. The left side becomes:", "choice", tex(left),
                      options=[Option(tex(left), correct=True, value=key(left))] +
                      [Option(tex(e), misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in lw])
        sw = pick(slope_expr, [("implicit-sign-slip", Fx / Fy), ("implicit-swapped", -Fy / Fx)])
        s_step = Step("Solve for $y'$.", "choice", f"$y' = {L(slope_expr)}$",
                      options=[Option(f"$y' = {L(slope_expr)}$", correct=True, value=key(slope_expr))] +
                      [Option(f"$y' = {L(e)}$", misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in sw])
        steps = [d_step, s_step,
                 Step(f"What is the slope at $({px}, {py})$?", "number", float(slope), tolerance=0.01,
                      explain=f"$y' = {L(slope_expr.subs(point))}$ at $({px}, {py})$.")]
        checks = [("exists", sp.idiff(F, y, x).subs(point) == slope, "idiff disagrees"),
                  ("clean", clean(slope), "slope isn't clean")]
        story = f"The curve ${L(show)} = {rhs}$ passes through $({px}, {py})$. Find the slope of its tangent there."
        scene = {"type": "integral", "tex": f"{L(show)} = {rhs}", "rule": "\\frac{d}{dx}\\left[y^2\\right] = 2y\\,y'"}
        return Solution(steps, story, scene, ["differentiate-both-sides", "solve-for-y'", "evaluate"], {"slope": float(slope), "_checks": checks})

    # Level 6 ----------------------------------------------------------------------------
    def _log_diff(self, p):
        f, fam = log_diff_function(p), p["family"]
        a, b, c = p["a"], p["b"], p["c"]
        if fam == "power":
            q = a * x**2 + b * x + c
            if sp.degree(q, x) < 1:
                raise NoSolution("a constant exponent needs only the power rule")
            ln_y = q * sp.log(x)
            ln_cands = [("exponent-not-down", sp.log(x) ** q), ("log-of-exponent", sp.log(q) * sp.log(x))]
            ratio = sp.diff(ln_y, x)
            d_cands = [("forgot-y", ratio), ("power-rule-on-variable-exponent", q * x ** (q - 1))]
        else:
            sign = 1 if fam == "product" else -1
            ln_y = a * sp.log(x) + b * sp.log(x + 1) + sign * c * sp.log(x + 3)
            ln_cands = [("logs-multiply", a * sp.log(x) * b * sp.log(x + 1) * (c * sp.log(x + 3)) ** sign),
                        ("exponent-not-down", sp.log(x) ** a + sp.log(x + 1) ** b + sign * sp.log(x + 3) ** c)]
            ratio = sp.diff(ln_y, x)
            each = a * x ** (a - 1) * b * (x + 1) ** (b - 1) * (c * (x + 3) ** (c - 1)) ** sign
            d_cands = [("forgot-y", ratio), ("differentiated-each-factor", each)]
        right = f * ratio
        value = sp.nsimplify(right.subs(x, 1))
        if same(ratio.subs(x, 1), value) and fam != "power":
            raise NoSolution("y(1) = 1 hides the forgot-y mistake in the number step")
        lw = pick(ln_y, ln_cands)
        dw = pick(right, d_cands)
        if len(lw) < 2 or len(dw) < 2:
            raise NoSolution("a step would be a coin flip")
        steps = [
            Step("Take the natural log of both sides. $\\ln y = $", "choice", tex(ln_y),
                 options=[Option(tex(ln_y), correct=True, value=key(ln_y))] +
                 [Option(tex(e), misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in lw]),
            Step("Differentiate both sides and solve for $y'$.", "choice", f"$y' = {L(right)}$",
                 options=[Option(f"$y' = {L(right)}$", correct=True, value=key(right))] +
                 [Option(f"$y' = {L(e)}$", misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in dw]),
            Step("Evaluate $y'(1)$.", "number", float(value), tolerance=0.01, explain=f"$y'(1) = {L(value)}$"),
        ]
        checks = [("exists", sp.simplify(sp.diff(f, x) - right) == 0, "log-derivative disagrees with diff"),
                  ("clean", clean(value), "value isn't clean")]
        story = f"Let $y = {L(f)}$."
        scene = {"type": "integral", "tex": f"y = {L(f)}", "rule": "\\ln y \\implies \\frac{y'}{y}"}
        return Solution(steps, story, scene, ["take-logs", "differentiate", "evaluate"], {"value": float(value), "_checks": checks})

    # Level 7 ----------------------------------------------------------------------------
    def _higher(self, p):
        a, b, c, d, t0 = p["a"], p["b"], p["c"], p["d"], p["t0"]
        s_ = a * t**3 + b * t**2 + c * t + d
        v, acc = sp.expand(sp.diff(s_, t)), sp.expand(sp.diff(s_, t, 2))   # expanded, like the distractors
        at = acc.subs(t, t0)
        if at == 0:
            raise NoSolution("inflection point: concavity is undefined there")
        vw = pick(v, [("constant-not-zero", v + d), ("exponent-unchanged", 3 * a * t**3 + 2 * b * t**2 + c * t),
                      ("dropped-coefficient", a * t**2 + b * t + c)])
        aw = pick(acc, [("acceleration-is-velocity", v), ("forgot-to-double", 6 * a * t + b)])
        if len(vw) < 2 or len(aw) < 2:
            raise NoSolution("a step would be a coin flip")
        up = at > 0
        steps = [
            Step("What is the velocity $v(t) = s'(t)$?", "choice", tex(v),
                 options=[Option(tex(v), correct=True, value=key(v))] + [Option(tex(e), misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in vw]),
            Step("What is the acceleration $a(t) = s''(t)$?", "choice", tex(acc),
                 options=[Option(tex(acc), correct=True, value=key(acc))] + [Option(tex(e), misconception=m, feedback=FEEDBACK[m], value=key(e)) for m, e in aw]),
            Step(f"What is the acceleration at $t = {t0}$, in m/s²?", "number", float(at), tolerance=0.01,
                 explain=f"$a({t0}) = {at}$ m/s²."),
            Step(f"At $t = {t0}$, is the graph of $s(t)$ concave up or concave down?", "choice", "up" if up else "down", options=[
                Option("Concave up" if up else "Concave down", correct=True, value="up" if up else "down"),
                Option("Concave down" if up else "Concave up", misconception="concavity-from-f-prime", value="down" if up else "up",
                       feedback=f"$s''({t0}) = {at}$ is {'positive' if up else 'negative'}, so the graph bends {'upward' if up else 'downward'}. Concavity follows the sign of $s''$."),
            ]),
        ]
        story = f"A particle moves along a line. Its position after $t$ seconds is $s(t) = {L(s_)}$ metres."
        scene = {"type": "integral", "tex": f"s(t) = {L(s_)}", "rule": "v = s', \\quad a = s''"}
        return Solution(steps, story, scene, ["velocity", "acceleration", "evaluate", "concavity"], {"acc": float(at), "_checks": []})


FRAMEWORK = ElementaryDerivatives()
