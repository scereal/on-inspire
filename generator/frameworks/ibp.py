"""Integration by parts (spec section 5.1).

Level 1: c·x·g(ax), one round.            Level 2: c·xⁿ·g(ax), n rounds (the polynomial must be u).
Level 3: c·eᵃˣ·sin/cos(bx), the loop.     Level 4: c·xⁿ·ln(kx), ln must be u.
"""
from functools import lru_cache

import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x = sp.Symbol("x", positive=True)
G = {"exp": sp.exp, "sin": sp.sin, "cos": sp.cos}
A_VALUES = ["1", "2", "3", "4", "1/2", "1/3"]
TRANSCENDENTAL = (sp.exp, sp.sin, sp.cos, sp.log)
MAX_NUMERATOR, MAX_DENOMINATOR = 200, 60


def tex(e):
    return f"${sp.latex(e)}$"


def tex_anti(e):
    return f"${sp.latex(e)} + C$"


def key(e):
    """Canonical string for an expression: also parseable with sympify."""
    return sp.sstr(sp.expand(sp.simplify(e)))


def integrand(level, p):
    c = sp.Integer(p["c"])
    if level == 1:
        return c * x * G[p["g"]](sp.Rational(p["a"]) * x)
    if level == 2:
        return c * x ** p["n"] * G[p["g"]](sp.Rational(p["a"]) * x)
    if level == 3:
        return c * sp.exp(p["a"] * x) * G[p["t"]](p["b"] * x)
    return c * x ** p["n"] * sp.log(p["k"] * x)


# Structural helpers ---------------------------------------------------------------

def xpow(term):
    return sum(int(e) for b, e in (f.as_base_exp() for f in sp.Mul.make_args(term)) if b == x)


def has_func(term, funcs):
    return any(f.func in funcs for f in sp.Mul.make_args(term))


def basic(expr):
    """Integrable on sight: polynomial terms, or constant × exp/sin/cos of a linear argument."""
    for term in sp.Add.make_args(sp.expand(expr)):
        if has_func(term, (sp.log,)):
            return False
        if xpow(term) and has_func(term, (sp.exp, sp.sin, sp.cos)):
            return False
    return True


def one_round(f, u):
    """Integrate by parts once: returns (u·v, new integrand v·du), or None if dv can't be integrated."""
    dv = sp.simplify(f / u)
    v = sp.integrate(dv, x)
    if v.has(sp.Integral):
        return None
    return sp.simplify(u * v), sp.simplify(v * sp.diff(u, x))


def finishes(f, u, max_rounds=1):
    step = one_round(f, u)
    return bool(step) and basic(step[1]) if max_rounds == 1 else bool(step)


def rounds_needed(f, limit=6):
    """Repeated parts with u = the polynomial part each time; counts rounds until basic."""
    cur, rounds = sp.expand(f), 0
    while not basic(cur):
        if rounds >= limit:
            return None
        u = x ** xpow(cur)
        step = one_round(cur, u)
        if not step:
            return None
        cur, rounds = sp.expand(step[1]), rounds + 1
    return rounds


def gets_simpler(f, u):
    step = one_round(f, u)
    return bool(step) and xpow(sp.expand(step[1])) < xpow(sp.expand(f)) and not has_func(step[1], (sp.log,))


def tabular(u, dv, n_terms, signs=True, scale_integrals=None):
    """Σ (−1)^k u^(k) V_(k+1). scale_integrals rescales each integral (misconception models)."""
    total, d, V = 0, u, dv
    for k in range(n_terms):
        V = sp.integrate(V, x)
        if scale_integrals:
            V = V * scale_integrals
        total += (-1) ** k * d * V if signs else d * V
        d = sp.diff(d, x)
    return sp.simplify(total)


def rationals_clean(expr):
    for r in sp.preorder_traversal(expr):
        if isinstance(r, sp.Rational) and (abs(r.p) > MAX_NUMERATOR or r.q > MAX_DENOMINATOR):
            return False
    return True


# The framework ---------------------------------------------------------------------

class IntegrationByParts(Framework):
    id = "ibp"
    title = "Integration by parts"
    outcome = "Choose u so the integral gets simpler, know when repeated parts ends, and handle the loop."
    levels = {
        1: Level("One round", {"parts": 1}),
        2: Level("Repeated parts", {"parts": 3}),
        3: Level("The loop", {"parts": 2, "solve-for-I": 1}),
        4: Level("Logarithms", {"parts": 1}),
    }
    misconceptions = {
        "u-gets-harder": "Picked the u whose derivative doesn't get simpler, so the new integral is harder.",
        "whole-product-as-u": "Took the whole product as u, which leaves an even messier integral.",
        "differentiated-for-v": "Differentiated dv instead of integrating it.",
        "dropped-1-over-a": "Forgot the 1/a that integrating g(ax) brings out.",
        "trig-sign": "Got the sign of the trig integral wrong.",
        "power-rule-on-exp": "Used the power rule on an exponential.",
        "parts-sign": "Used uv + ∫v du instead of uv − ∫v du.",
        "stopped-early": "Stopped before the integral was finished.",
        "rounds-too-few": "Undercounted the rounds: each round lowers the power by one.",
        "rounds-too-many": "Overcounted the rounds: it ends when the power reaches zero.",
        "loop-confusion": "Thought repeated parts never ends here.",
        "tabular-sign": "Forgot that the signs alternate.",
        "loop-vanishes": "Expected the integral to disappear after two rounds.",
        "loop-grows": "Expected a new, harder integral.",
        "loop-sign": "Got the sign of the reappearing integral wrong.",
        "forgot-to-divide": "Didn't divide out the reappearing integral.",
        "swapped-trig": "Swapped sin and cos in the result.",
        "polynomial-habit": "Made the polynomial u out of habit, but ln x has no easy antiderivative.",
        "forgot-square": "Divided by (n+1) once instead of (n+1)².",
    }
    targets = {1: 70, 2: 100, 3: 100, 4: 40}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        if level == 1:
            return {"g": rng.choice(sorted(G)), "a": rng.choice(A_VALUES), "c": rng.randint(1, 6)}
        if level == 2:
            return {"g": rng.choice(sorted(G)), "a": rng.choice(A_VALUES), "c": rng.randint(1, 6), "n": rng.choice([2, 3])}
        if level == 3:
            return {"t": rng.choice(["sin", "cos"]), "a": rng.randint(1, 4), "b": rng.randint(1, 4), "c": rng.randint(1, 5)}
        return {"n": rng.choice([1, 2, 3]), "k": rng.choice([1, 2, 3]), "c": rng.randint(1, 6)}

    def canonical(self, p, level):
        return f"{level}:{sp.srepr(integrand(level, p))}"

    def solve(self, p, level, theme):
        return _solve(level, tuple(sorted(p.items())))

    def count_solutions(self, p, level):
        return _count(level, tuple(sorted(p.items())))

    def checks(self, p, level, theme, solution):
        f = integrand(level, p)
        F = sp.sympify(solution.answers["F"], locals={"x": x})
        results = [("clean", rationals_clean(F), "coefficients too large for mental arithmetic")]
        if sp.simplify(sp.diff(F, x) - f) != 0:
            results.append(("exists", False, "answer does not differentiate back to the integrand"))
        for step in solution.steps:
            for o in step.options:
                if o.correct or not isinstance(o.value, str) or "x" not in o.value:
                    continue
                w = sp.sympify(o.value, locals={"x": x})
                if step is solution.steps[-1] and sp.simplify(sp.diff(w, x) - f) == 0:
                    results.append(("distinct", False, f"'{o.misconception}' is also a correct antiderivative"))
        if level == 2 and solution.answers.get("rounds") != p["n"]:
            results.append(("taught_tools", False, "round count doesn't match the degree"))
        return results


def _choice(prompt, options, explain=""):
    answer = next(o.label for o in options if o.correct)
    return Step(prompt, "choice", answer, options=options, explain=explain)


def _antiderivative_options(F, wrongs):
    opts = [Option(tex_anti(F), correct=True, value=key(F))]
    for misconception, expr, feedback in wrongs:
        opts.append(Option(tex_anti(expr), misconception=misconception, feedback=feedback, value=key(expr)))
    return opts


@lru_cache(maxsize=None)
def _solve(level, items):
    p = dict(items)
    f = integrand(level, p)
    F = sp.simplify(sp.integrate(f, x))
    if F.has(sp.Integral):
        raise NoSolution("no closed form")
    story = f"Find {tex(sp.Integral(f, x))}."
    scene = {"type": "integral", "tex": sp.latex(sp.Integral(f, x)), "rule": r"\int u\,dv = uv - \int v\,du"}

    if level in (1, 2):
        a, g, c = sp.Rational(p["a"]), G[p["g"]], sp.Integer(p["c"])
        n = 1 if level == 1 else p["n"]
        poly, trig = c * x**n, g(a * x)
        steps, answers = [], {"F": str(F)}
        if level == 2:
            rounds = rounds_needed(f)
            answers["rounds"] = rounds
            steps.append(_choice(
                f"With $u = {sp.latex(x**n)}$, how many rounds of parts until the integral is easy?",
                [Option(str(rounds), correct=True, value=rounds),
                 Option(str(rounds - 1), misconception="rounds-too-few",
                        feedback="Each round lowers the power of x by one. Count down to x⁰.", value=rounds - 1),
                 Option(str(rounds + 1), misconception="rounds-too-many",
                        feedback="It ends as soon as the power reaches zero.", value=rounds + 1),
                 Option("It never finishes", misconception="loop-confusion",
                        feedback="The power of x drops every round, so it must reach zero.", value="never")],
                explain=f"Each round differentiates the polynomial once, so after {rounds} rounds it's a constant."))
        steps.append(_choice(
            "Which choice of u makes the integral easier?",
            [Option(f"$u = {sp.latex(poly if level == 1 else x**n)}$, $dv = {sp.latex(trig)}\\,dx$", correct=True, value="poly"),
             Option(f"$u = {sp.latex(trig)}$, $dv = {sp.latex(poly if level == 1 else x**n)}\\,dx$", misconception="u-gets-harder",
                    feedback=f"Then v = {sp.latex(sp.integrate(x**n, x))} and the power of x goes up, not down.", value="trig")]
            + ([Option(f"$u = {sp.latex(f)}$, $dv = dx$", misconception="whole-product-as-u",
                       feedback="Then v = x and the new integral is messier than the original.", value="whole")] if level == 1 else []),
            explain="The polynomial gets simpler every time you differentiate it."))
        if level == 1:
            v = sp.integrate(trig, x)
            wrong_v = [("differentiated-for-v", sp.diff(trig, x), "v must be an antiderivative of dv, not its derivative."),
                       ("dropped-1-over-a", sp.simplify(v * a), "Integrating g(ax) brings out a factor of 1/a.")]
            if p["g"] == "exp":
                wrong_v.append(("power-rule-on-exp", sp.exp(a * x + 1) / (a * x + 1), "The power rule is for xⁿ, not eˣ."))
            else:
                wrong_v.append(("trig-sign", -v, "Check the sign: d/dx of cos is −sin."))
            steps.append(_choice(
                f"With $dv = {sp.latex(trig)}\\,dx$, what is v?",
                [Option(tex(v), correct=True, value=key(v))]
                + [Option(tex(e), misconception=m, feedback=fb, value=key(e)) for m, e, fb in wrong_v]))
            uv = sp.simplify(poly * v)
            rest = sp.simplify(v * sp.diff(poly, x))
            wrongs = [("parts-sign", uv + sp.integrate(rest, x), "The rule is uv − ∫v du: the second part is subtracted."),
                      ("stopped-early", uv, "That's only uv. You still need to subtract ∫v du."),
                      ("dropped-1-over-a", uv - sp.integrate(rest, x) * a, "The second integral also brings out a 1/a.")]
            tools = ["parts"]
        else:
            wrongs = [("tabular-sign", tabular(poly, trig, n + 1, signs=False), "The signs alternate: + − + …"),
                      ("stopped-early", tabular(poly, trig, n), "One more round is needed before the polynomial is gone."),
                      ("dropped-1-over-a", tabular(poly, trig, n + 1, scale_integrals=a), "Every integral of g(ax) brings out a 1/a.")]
            tools = ["parts"] * answers["rounds"]
        steps.append(_choice("So the integral is:", _antiderivative_options(F, wrongs)))
        return Solution(steps=steps, story=story, scene=scene, tools=tools, answers=answers)

    if level == 3:
        a, b, c = p["a"], p["b"], sp.Integer(p["c"])
        T, e = G[p["t"]], sp.exp(p["a"] * x)
        u1 = c * T(b * x)
        v1 = e / a
        r1 = sp.simplify(v1 * sp.diff(u1, x))
        u2 = sp.simplify(r1 / e)
        v2 = v1
        r2 = sp.simplify(v2 * sp.diff(u2, x))
        k = sp.simplify(r2 / f)
        if k.has(x):
            raise NoSolution("integral doesn't reappear")
        boundary = sp.factor_terms(sp.expand(u1 * v1 - u2 * v2))
        # Textbook form, so sin(bx) and cos(bx) stay visible (SymPy may fold them into √2·sin(bx − π/4))
        S, C = sp.sin(b * x), sp.cos(b * x)
        numer = (a * S - b * C) if p["t"] == "sin" else (a * C + b * S)
        F = c * e * numer / (a**2 + b**2)
        swap = c * e * numer.subs({S: C, C: S}, simultaneous=True) / (a**2 + b**2)
        steps = [
            _choice(
                f"Take $u = {sp.latex(T(b * x))}$ and $dv = {sp.latex(e)}\\,dx$, then do parts twice. What's left over?",
                [Option(f"${sp.latex(k)}$ times the original integral", correct=True, value=float(k)),
                 Option("Nothing: the integral disappears", misconception="loop-vanishes",
                        feedback="Differentiating sin or cos never reaches zero; it cycles back.", value="vanishes"),
                 Option(f"${sp.latex(-k)}$ times the original integral", misconception="loop-sign",
                        feedback="Track both minus signs from uv − ∫v du.", value=float(-k)),
                 Option("A new, harder integral", misconception="loop-grows",
                        feedback="sin → cos → −sin: after two rounds you're back where you started.", value="grows")],
                explain="Call the integral I. Then I = (boundary terms) + k·I, and you can solve for I."),
        ]
        wrongs = [("forgot-to-divide", boundary, "I appears on both sides: move it over and divide by (1 − k).")]
        if k != 1 and k != -1:
            wrongs.append(("loop-sign", sp.factor_terms(sp.expand(boundary / (1 + k))), "Moving kI to the left gives (1 − k)I, not (1 + k)I."))
        wrongs.append(("swapped-trig", swap, "Check which of sin and cos goes with which coefficient."))
        steps.append(_choice("Solve for I:", _antiderivative_options(F, wrongs)))
        return Solution(steps=steps, story=story, scene=scene, tools=["parts", "parts", "solve-for-I"],
                        answers={"F": str(F), "k": str(k)})

    n, kk, c = p["n"], p["k"], sp.Integer(p["c"])
    lg = sp.log(kk * x)
    steps = [_choice(
        "Which choice of u makes the integral easier?",
        [Option(f"$u = {sp.latex(lg)}$, $dv = {sp.latex(c * x**n)}\\,dx$", correct=True, value="log"),
         Option(f"$u = {sp.latex(c * x**n)}$, $dv = {sp.latex(lg)}\\,dx$", misconception="polynomial-habit",
                feedback="Then you need ∫ln x dx first, and the new integral still contains ln x.", value="poly")],
        explain="ln x is easy to differentiate (1/x) but awkward to integrate, so it should be u.")]
    m = n + 1
    wrongs = [("forgot-square", c * x**m * lg / m - c * x**m / m, "∫ xⁿ/(n+1) dx brings another factor of 1/(n+1)."),
              ("parts-sign", c * x**m * lg / m + c * x**m / m**2, "The rule is uv − ∫v du.")]
    steps.append(_choice("So the integral is:", _antiderivative_options(F, wrongs)))
    return Solution(steps=steps, story=story, scene=scene, tools=["parts"], answers={"F": str(F)})


@lru_cache(maxsize=None)
def _count(level, items):
    """For 'which u?' steps: how many offered choices actually lead to an easier integral."""
    p = dict(items)
    f = integrand(level, p)
    if level == 1:
        a, g, c = sp.Rational(p["a"]), G[p["g"]], sp.Integer(p["c"])
        return sum(finishes(f, u) for u in (c * x, g(a * x), f))
    if level == 2:
        g, a = G[p["g"]], sp.Rational(p["a"])
        return sum(gets_simpler(f, u) for u in (x ** p["n"], g(a * x)))
    if level == 4:
        return sum(finishes(f, u) for u in (sp.log(p["k"] * x), sp.Integer(p["c"]) * x ** p["n"]))
    return 1  # level 3 asks about the loop, not about u


FRAMEWORK = IntegrationByParts()
