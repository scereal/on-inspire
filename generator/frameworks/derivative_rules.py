"""Differentiation rules (MATH 140, outcome 140.3.2). Spec: design/specs/2026-10-05-math-140-explorer-design.md §5.2.

Levels: 1 sum and constant multiple · 2 power rule (roots, reciprocals) · 3 product · 4 quotient · 5 chain · 6 mixed.
Every problem: which rule first? → pick the derivative (wrong options from named mistakes) → evaluate at a point.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x = sp.Symbol("x")
MAX_DEN = 12
D = lambda e: sp.diff(e, x)
E = lambda s: sp.sympify(s, locals={"x": x})

RULES = {
    "sum": "Sum and constant-multiple rules",
    "power": "Power rule",
    "product": "Product rule",
    "quotient": "Quotient rule",
    "chain": "Chain rule",
}

# Named mistakes: each returns the wrong derivative a learner with that misconception would write
WRONG = {
    "product-of-derivatives": lambda f, g: D(f) * D(g),
    "dropped-second-term": lambda f, g: D(f) * g,
    "quotient-of-derivatives": lambda f, g: D(f) / D(g),
    "quotient-order": lambda f, g: (f * D(g) - D(f) * g) / g**2,
    "forgot-square": lambda f, g: (D(f) * g - f * D(g)) / g,
}
FEEDBACK = {
    "product-of-derivatives": "The derivative of a product isn't the product of derivatives. Each factor takes its turn: f′g + fg′.",
    "dropped-second-term": "That's only f′g. The product rule has two terms: f′g + fg′.",
    "quotient-of-derivatives": "Dividing the derivatives doesn't work. Use (f′g − fg′)/g².",
    "quotient-order": "The order on top is f′g − fg′ (derivative of the top first). Swapping them flips the sign.",
    "forgot-square": "The denominator is squared: g², not g.",
    "dropped-inner": "Multiply by the derivative of the inside: that's what the chain rule adds.",
    "power-up": "The power rule lowers the exponent by one: n xⁿ⁻¹, not n xⁿ⁺¹.",
    "exponent-unchanged": "Bring the power down and also subtract 1 from it.",
    "constant-to-1": "A constant's derivative is 0, not 1: it doesn't change.",
    "dropped-coefficient": "Constants multiply through: (c·f)′ = c·f′.",
}
RULE_FEEDBACK = {
    "sum": "This is a sum (or constant multiple) of simpler pieces: differentiate term by term.",
    "power": "This is a single power of x: no inner function, no product.",
    "product": "The outermost operation is multiplying two functions of x.",
    "quotient": "The outermost operation is dividing one function of x by another.",
    "chain": "There's a function inside another function, like (inside)ⁿ or √(inside).",
}


def power_up(c, n):
    return c * n * x ** (n + 1)


def dropped_inner(expr):
    """The chain-rule mistake: differentiate the outside, but forget to multiply by the inside's derivative."""
    base, exp = expr.as_base_exp()
    return exp * base ** (exp - 1)


def build(level, p):
    if level in (1, 2, 5):
        return E(p["f"])
    if level == 3:
        return sp.Integer(p.get("c", 1)) * sp.Mul(E(p["f"]), E(p["g"]), evaluate=False)
    if level == 4:
        return E(p["f"]) / E(p["g"])
    kind, f, g = p["kind"], E(p["f"]), E(p["g"])
    if kind == "product-chain":
        return f * g
    if kind == "quotient-chain":
        return g / f
    return sp.sqrt(f * g)                   # chain-of-product: √(f·g); SymPy can't split a square root, so the outer function stays visible


def outer_rule(level, p):
    if level in (1, 2, 3, 4, 5):
        return ["sum", "power", "product", "quotient", "chain"][level - 1]
    return {"product-chain": "product", "quotient-chain": "quotient", "chain-of-product": "chain"}[p["kind"]]


def nice(e):
    """One readable form for every derivative shown: a single factored fraction."""
    return sp.factor(sp.cancel(sp.together(e)))


def tex(e):
    return f"${sp.latex(e)}$"


def key(e):
    return sp.sstr(sp.simplify(e))


def lin(rng):
    return f"{rng.choice([1, 2, 3, -1, -2])}*x + {rng.choice([-3, -2, -1, 1, 2, 3])}"


def quad(rng):
    return f"{rng.choice([1, 2, -1])}*x**2 + {rng.randint(-3, 3)}*x + {rng.choice([-2, 1, 2, 3])}"


class DerivativeRules(Framework):
    id = "derivative-rules"
    title = "Differentiation rules"
    outcome = "Differentiate using the sum, constant-multiple, power, product, quotient and chain rules."
    levels = {
        1: Level("Sum and constant-multiple rules", {"choose-rule": 1, "sum": 1, "evaluate": 1}),
        2: Level("The power rule", {"choose-rule": 1, "power": 1, "evaluate": 1}),
        3: Level("The product rule", {"choose-rule": 1, "product": 1, "evaluate": 1}),
        4: Level("The quotient rule", {"choose-rule": 1, "quotient": 1, "evaluate": 1}),
        5: Level("The chain rule", {"choose-rule": 1, "chain": 1, "evaluate": 1}),
        6: Level("Mixed: which rule first?", {"choose-rule": 1, "product": 1, "quotient": 1, "chain": 1, "evaluate": 1}),
    }
    misconceptions = {**FEEDBACK, "wrong-rule": "Picked a rule that doesn't match the outermost structure."}
    targets = {1: 50, 2: 50, 3: 50, 4: 50, 5: 50, 6: 60}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        a = rng.choice([0, 1, 2, -1, 3])
        if level == 1:
            terms = [f"{rng.choice([1, 2, 3, 4, -2, -3])}*x**3", f"{rng.choice([-5, -4, 2, 3, 6])}*x**2",
                     f"{rng.choice([-7, -1, 4, 5])}*x", f"{rng.choice([-6, 2, 7, 9])}"]
            keep = sorted(rng.sample(range(4), 3)) if rng.random() < 0.5 else [0, 1, 2, 3]
            return {"f": " + ".join(terms[i] for i in keep), "a": a}
        if level == 2:
            n = rng.choice(["-1", "-2", "-3", "1/2", "-1/2", "3/2", "1/3"])
            return {"f": f"{rng.choice([1, 2, 3, 4, 6, -2])}*x**({n})", "a": rng.choice([1, 4, 8, 9])}
        if level == 3:
            return {"f": rng.choice([lin(rng), "x**2", "x**3", quad(rng)]), "g": rng.choice([lin(rng), quad(rng), "sqrt(x)"]),
                    "c": rng.choice([1, 1, 1, 2]), "a": rng.choice([1, 2, 4])}
        if level == 4:
            return {"f": rng.choice([lin(rng), quad(rng), "x**2"]), "g": lin(rng), "a": a}
        if level == 5:
            inner = rng.choice([lin(rng), lin(rng), quad(rng)])
            outer = rng.choice([f"({inner})**{rng.randint(2, 5)}", f"sqrt({inner})"])
            return {"f": outer, "a": a}
        kind = rng.choice(["product-chain", "quotient-chain", "chain-of-product"])
        if kind == "chain-of-product":
            return {"kind": kind, "f": "x", "g": lin(rng), "a": rng.choice([1, 2, 3, 4])}
        return {"kind": kind, "f": rng.choice(["x", "x**2"]), "g": f"({lin(rng)})**{rng.randint(2, 3)}", "a": rng.choice([1, 2, -1])}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def count_solutions(self, p, level):
        # A constant times a product reads as both "constant multiple" and "product": ambiguous
        return 2 if level == 3 and p.get("c", 1) != 1 else 1

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        expr = build(level, p)
        a = sp.Integer(p["a"])
        d = nice(D(expr))
        try:
            fx, value = expr.subs(x, a), d.subs(x, a)
        except Exception as e:
            raise NoSolution(str(e))
        if not (fx.is_finite and value.is_finite and value.is_real):
            raise NoSolution(f"not differentiable at x = {a}")
        wrongs = self._wrongs(level, p, expr)
        rule = outer_rule(level, p)
        rule_opts = [Option(RULES[rule], correct=True, value=rule)]
        for other in self._rule_distractors(rule):
            rule_opts.append(Option(RULES[other], misconception="wrong-rule", value=other,
                                    feedback=f"Not first. {RULE_FEEDBACK[rule]}"))
        deriv_opts = [Option(tex(d), correct=True, value=key(d))]
        for m, w in wrongs:
            deriv_opts.append(Option(tex(nice(w)), misconception=m, feedback=FEEDBACK[m], value=key(w)))
        steps = [
            Step(f"Which rule do you use first for ${sp.latex(expr)}$?", "choice", RULES[rule], options=rule_opts),
            Step("The derivative is:", "choice", tex(d), options=deriv_opts),
            Step(f"Evaluate the derivative at $x = {a}$.", "number", float(value), tolerance=0.01,
                 explain=f"$f'({a}) = {sp.latex(sp.nsimplify(value))}$"),
        ]
        v = sp.nsimplify(value)
        checks = [("clean", v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 500, f"f'({a}) = {v} isn't a clean number")]
        for m, w in wrongs:  # every wrong option must really be wrong
            if sp.simplify(w - d) == 0:
                checks.append(("distinct", False, f"'{m}' gives the right derivative"))
        tools = ["choose-rule", rule if level == 6 else self._tool(level), "evaluate"]
        scene = {"type": "integral", "tex": f"\\frac{{d}}{{dx}}\\left[{sp.latex(expr)}\\right]", "rule": f"\\text{{evaluate at }} x = {a}"}
        return Solution(steps, f"Differentiate $f(x) = {sp.latex(expr)}$, then evaluate at $x = {a}$.", scene, tools,
                        {"value": float(value), "_checks": checks})

    def _tool(self, level):
        return ["sum", "power", "product", "quotient", "chain"][level - 1]

    def _rule_distractors(self, rule):
        # Never offer a distractor that is also a valid first step (e.g. "product" for a quotient f·g⁻¹)
        # (power: not "quotient", since c·x⁻ⁿ displays as c/xⁿ, nor "product", since c·xⁿ is a constant times a function)
        return {"sum": ["product", "chain"], "power": ["chain", "sum"], "product": ["chain", "sum"],
                "quotient": ["chain", "sum"], "chain": ["power", "product"]}[rule]

    def _wrongs(self, level, p, expr):
        if level == 1:
            terms = sp.Add.make_args(expr)
            # constant → 1 instead of 0, and power-up on every term
            const = [t for t in terms if t.is_number]
            out = [("power-up", sum(power_up(*t.as_coeff_exponent(x)) for t in terms if not t.is_number))]
            if const:
                out.append(("constant-to-1", D(expr) + 1))
            else:
                out.append(("dropped-coefficient", sum(t.as_coeff_exponent(x)[1] * x ** (t.as_coeff_exponent(x)[1] - 1) for t in terms)))
            return out
        if level == 2:
            c, n = expr.as_coeff_exponent(x)
            return [("power-up", power_up(c, n)), ("exponent-unchanged", c * n * x**n)]
        if level == 3:
            f, g = E(p["f"]), E(p["g"])
            return [("product-of-derivatives", WRONG["product-of-derivatives"](f, g)), ("dropped-second-term", WRONG["dropped-second-term"](f, g))]
        if level == 4:
            f, g = E(p["f"]), E(p["g"])
            return [(m, WRONG[m](f, g)) for m in ("quotient-of-derivatives", "quotient-order", "forgot-square")]
        if level == 5:
            return [("dropped-inner", dropped_inner(expr)), ("power-up", sp.Integer(0) + expr.as_base_exp()[1] * expr.as_base_exp()[0] ** (expr.as_base_exp()[1] + 1) * D(expr.as_base_exp()[0]))]
        kind, f, g = p["kind"], E(p["f"]), E(p["g"])
        if kind == "product-chain":
            return [("product-of-derivatives", WRONG["product-of-derivatives"](f, g)), ("dropped-inner", D(f) * g + f * dropped_inner(g))]
        if kind == "quotient-chain":
            return [("quotient-order", WRONG["quotient-order"](g, f)), ("dropped-inner", (dropped_inner(g) * f - g * D(f)) / f**2)]
        inner = f * g
        return [("dropped-inner", 1 / (2 * sp.sqrt(inner))), ("product-of-derivatives", D(f) * D(g) / (2 * sp.sqrt(inner)))]


FRAMEWORK = DerivativeRules()
