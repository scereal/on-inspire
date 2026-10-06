"""Antidifferentiation (MATH 140, outcomes 140.6.1–140.6.2). Plan: design/plans/2026-10-05-math-140-antiderivatives.md.

Level 1: the power rule backwards (sums of powers), with + C.
Level 2: antiderivatives of cos, sin, e^(kx) and sec², undoing the chain rule.
Level 3: initial-value problems.
Level 4: motion: acceleration to velocity to position.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x, t = sp.symbols("x t")
MAX_DEN = 20


def L(e):
    return sp.latex(e, ln_notation=True, inv_trig_style="full")


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):g}")


def key(e):
    return sp.sstr(sp.simplify(e))


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 100000


def same(a, b):
    return sp.simplify(a - b) == 0


def plus(v):
    return "" if v == 0 else (f" + {v}" if v > 0 else f" - {-v}")


def withc(e):
    return f"${L(e)} + C$"


def pick(right, candidates, n=2):
    kept = []
    for c in candidates:
        if same(c[1], right) or any(same(c[1], k[1]) for k in kept):
            continue
        kept.append(c)
        if len(kept) == n:
            break
    return kept


def rotate(items, k):
    k %= len(items)
    return items[k:] + items[:k]


def basic_parts(p):
    k = p["k"]
    if p["family"] == "trig":
        return p["a"] * sp.cos(k * x) + p["b"] * sp.sin(k * x), sp.pi / (2 * k)
    if p["family"] == "exp":
        return p["a"] * sp.exp(k * x), sp.log(2) / k
    if p["family"] == "log":
        return sp.Integer(p["c"]) / x, sp.E
    return p["c"] * sp.sec(k * x) ** 2, sp.pi / (4 * k)


FEEDBACK = {
    "differentiated-instead": "That's the derivative. An antiderivative goes the other way: its derivative should give back the original.",
    "forgot-to-divide": "Raising the power isn't enough: divide by the new exponent, so differentiating brings the coefficient back.",
    "multiplied-by-n": "Multiplying by the new exponent is what differentiating does. To undo it, divide.",
    "multiplied-by-k": "Differentiating sin(kx) brings out a factor k, so the antiderivative of cos(kx) must divide by k, not multiply.",
    "sin-sign": "(cos x)′ = −sin x, so the antiderivative of sin x is −cos x: the minus sign comes along.",
    "power-rule-on-trig": "sec² isn't a power of a variable. Read the derivative table backwards: (tan x)′ = sec² x.",
    "integrated-twice": "That antidifferentiates twice. One antiderivative raises each exponent by one, not two.",
    "position-not-velocity": "That's the shape of the position formula. Velocity needs only one integration of the acceleration.",
    "divided-by-old-exponent": "Divide by the new exponent, n + 1, not the old one: then differentiating gives back the original coefficient.",
    "divided-not-raised": "Raise the exponent by one as well as dividing: the antiderivative of xⁿ is xⁿ⁺¹/(n + 1).",
    "constant-inside-log": "The constant multiplies the log; it doesn't go inside it. (ln|cx|)′ = 1/x, not c/x.",
    "power-rule-on-exp": "e^{kx} isn't x to a power, so the power rule doesn't apply. Undo the chain rule: divide by k.",
    "forgot-v0": "Integrating gives a constant too: here it's the starting velocity v(0).",
    "integrated-twice": "That integrates the acceleration twice. Velocity needs one integration; position needs two.",
    "differentiated-a": "Velocity is the antiderivative of acceleration, not its derivative.",
}


class Antiderivatives(Framework):
    id = "antiderivatives"
    title = "Antiderivatives"
    outcome = "Find antiderivatives with their + C, and use a known value to solve initial-value problems."
    levels = {
        1: Level("The power rule backwards", {"antidifferentiate": 1, "difference": 1}),
        2: Level("Trig and exponential antiderivatives", {"antidifferentiate": 1, "difference": 1}),
        3: Level("Initial-value problems", {"antidifferentiate": 1, "solve-c": 1, "evaluate": 1}),
        4: Level("Motion: acceleration to position", {"velocity": 1, "evaluate-v": 1, "evaluate-s": 1}),
    }
    misconceptions = {k: v for k, v in FEEDBACK.items()}
    targets = {1: 100, 2: 100, 3: 100, 4: 100}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        nz = lambda lo, hi: rng.choice([v for v in range(lo, hi + 1) if v])
        if level == 1:
            pool = ["0", "1", "2", "3", "4", "-2", "-3", "1/2", "3/2"]
            exps = rng.sample(pool, rng.choice([2, 2, 3]))
            terms = [[nz(-6, 8), e] for e in exps]
            neg = any(sp.Rational(e) < 0 or not sp.Rational(e).is_integer for e in exps)
            a = rng.randint(1, 2) if neg else rng.randint(0, 2)
            return {"terms": terms, "a": a, "b": a + rng.randint(1, 2)}
        if level == 2:
            family = rng.choice(["trig", "trig", "exp", "sec", "log"])
            if family == "log":
                return {"family": family, "a": 0, "b": 0, "k": 1, "c": rng.choice([v for v in range(-6, 9) if v not in (0, 1, -1)])}
            if family == "trig":
                return {"family": family, "a": rng.randint(-4, 5), "b": rng.randint(-4, 5), "k": rng.randint(1, 4), "c": 0}
            if family == "exp":
                return {"family": family, "a": nz(-5, 6), "b": 0, "k": rng.randint(1, 4), "c": 0}
            return {"family": family, "a": 0, "b": 0, "k": rng.randint(1, 4), "c": nz(-5, 6)}
        if level == 3:
            return {"a": rng.choice([3, 6, -3, 6, 12, 0]), "b": rng.choice([2, 4, -2, 0, 6]), "c": rng.randint(-5, 5),
                    "x0": rng.choice([0, 1, -1, 2]), "y0": rng.randint(-6, 9), "x1": rng.choice([1, 2, 3, -1, -2])}
        return {"a0": nz(-10, 8), "j": rng.choice([0, 0, 6, -6, 12]), "v0": rng.randint(-5, 20), "s0": rng.randint(0, 20), "T": rng.randint(1, 4)}

    def canonical(self, p, level):
        # evaluation points don't make a new problem (lesson from the 140.1 review)
        skip = {1: ("a", "b"), 2: (), 3: ("x1",), 4: ("T",)}[level]
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p) if k not in skip)

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._power, self._basic, self._ivp, self._motion][level](p)

    def _choice(self, prompt, right_label, right_value, wrongs):
        if len(wrongs) < 2:
            raise NoSolution("fewer than two distinct mistakes: a coin flip")
        labels = [right_label] + [w[1] for w in wrongs]
        if len(set(labels)) != len(labels):
            raise NoSolution("two options read the same")
        return Step(prompt, "choice", right_label, options=[Option(right_label, correct=True, value=right_value)] +
                    [Option(lbl, misconception=m, value=v, feedback=fb) for m, lbl, v, fb in wrongs])

    def _anti_step(self, prompt, F, cands, seed, feedback=None, pairs=None):
        if pairs:                                   # a chosen pair first, the rest as fallbacks if one collapses
            names = pairs[seed % len(pairs)]
            cands = [c for c in cands if c[0] in names] + [c for c in cands if c[0] not in names]
        else:
            cands = rotate(cands, seed)
        wrongs = pick(F, cands)
        fb = {**FEEDBACK, **(feedback or {})}
        return self._choice(prompt, withc(F), key(F), [(m, withc(e), key(e), fb[m]) for m, e in wrongs])

    # Three of five pairs include a mistake with the same coefficients as the answer, so "the smallest
    # numbers" doesn't single out the answer, and no single mistake is always on screen.
    POWER_PAIRS = [("divided-not-raised", "forgot-to-divide"), ("divided-not-raised", "multiplied-by-n"),
                   ("divided-not-raised", "differentiated-instead"), ("integrated-twice", "forgot-to-divide"),
                   ("divided-by-old-exponent", "multiplied-by-n")]

    def _power_mistakes(self, terms):
        """Named mistakes for a sum of c·x^e terms; two of them also shrink the coefficients, like the answer."""
        up = lambda f: sum(f(c, e) for c, e in terms)
        # ordered so most neighbouring pairs include a mistake with the same or smaller numbers than the answer
        return [("forgot-to-divide", up(lambda c, e: c * x ** (e + 1))),
                ("divided-not-raised", up(lambda c, e: sp.Rational(c) / (e + 1) * x**e)),
                ("multiplied-by-n", up(lambda c, e: c * (e + 1) * x ** (e + 1))),
                ("integrated-twice", up(lambda c, e: sp.Rational(c) / ((e + 1) * (e + 2)) * x ** (e + 2) if e != -2 else 0)),
                ("divided-by-old-exponent", up(lambda c, e: (sp.Rational(c) / e if e != 0 else c) * x ** (e + 1))),
                ("differentiated-instead", up(lambda c, e: c * e * x ** (e - 1) if e != 0 else 0))]

    # Level 1 ----------------------------------------------------------------------------
    def _power(self, p):
        terms = [(c, sp.Rational(e)) for c, e in p["terms"]]
        if any(e == -1 for _, e in terms):
            raise NoSolution("x^-1 belongs to ln, not the power rule")
        f = sum(c * x**e for c, e in terms)
        F = sum(sp.Rational(c) / (e + 1) * x ** (e + 1) for c, e in terms)
        cands = self._power_mistakes(terms)
        a, b = p["a"], p["b"]
        diff = F.subs(x, b) - F.subs(x, a)
        steps = [self._anti_step("Find the general antiderivative $F(x)$.", F, cands, sum(c for c, _ in terms), pairs=self.POWER_PAIRS),
                 Step(f"What is $F({b}) - F({a})$? (The $C$ cancels.)", "number", float(diff), tolerance=0.01,
                      explain=f"$F({b}) - F({a}) = {L(F.subs(x, b))} - ({L(F.subs(x, a))}) = {L(diff)}$")]
        checks = [("exists", same(sp.diff(F, x), f), "F doesn't differentiate to f"), ("clean", clean(diff), "difference isn't clean")]
        story = f"Find the antiderivatives of $f(x) = {L(f)}$."
        scene = {"type": "integral", "tex": f"\\int \\left({L(f)}\\right)dx", "rule": "\\int x^n\\,dx = \\frac{x^{n+1}}{n + 1} + C"}
        return Solution(steps, story, scene, ["antidifferentiate", "difference"], {"_checks": checks})

    # Level 2 ----------------------------------------------------------------------------
    def _basic(self, p):
        f, x1 = basic_parts(p)
        if f == 0:
            raise NoSolution("nothing to integrate")
        k = p["k"]
        fam = p["family"]
        F = (p["c"] * sp.tan(k * x) / k if fam == "sec" else              # SymPy writes sin/cos; the course writes tan
             p["c"] * sp.log(sp.Abs(x)) if fam == "log" else sp.integrate(f, x))
        kk = "" if k == 1 else str(k)
        feedback = {}
        if fam == "trig":
            a, b = p["a"], p["b"]
            feedback = {"multiplied-by-k": f"Differentiating $\\sin({kk}x)$ brings out a factor {k}, so the antiderivative divides by {k} instead of multiplying.",
                        "sin-sign": "$(\\cos u)' = -\\sin u$, so the antiderivative of sine carries a minus sign: $\\int\\sin(" + kk + "x)\\,dx = -\\frac{\\cos(" + kk + "x)}{" + str(k) + "}$."}
            cands = [("multiplied-by-k", k * (a * sp.sin(k * x) - b * sp.cos(k * x))),
                     ("sin-sign", (a * sp.sin(k * x) + b * sp.cos(k * x)) / k),
                     ("differentiated-instead", sp.diff(f, x))]
        elif fam == "exp":
            a = p["a"]
            feedback = {"multiplied-by-k": f"$(e^{{{kk}x}})' = {k}e^{{{kk}x}}$, so to undo it divide by {k}, don't multiply.",
                        "forgot-to-divide": f"Differentiate it: $(e^{{{kk}x}})' = {k}e^{{{kk}x}}$, which is {k} times too big. Divide by {k}."}
            cands = [("multiplied-by-k", a * k * sp.exp(k * x)),
                     ("power-rule-on-exp", a * sp.exp(k * x + 1) / (k * x + 1)),
                     ("forgot-to-divide", a * sp.exp(k * x))]
        elif fam == "log":
            c = p["c"]
            cands = [("constant-inside-log", sp.log(sp.Abs(c * x))), ("differentiated-instead", sp.diff(f, x)),
                     ("divided-by-old-exponent", c * sp.log(sp.Abs(x)) / x)]
            feedback = {"divided-by-old-exponent": "$\\frac{1}{x}$ is the one power the power rule can't handle (it would divide by 0). Its antiderivative is $\\ln|x|$."}
        else:
            c = p["c"]
            feedback = {"multiplied-by-k": f"$(\\tan({kk}x))' = {k}\\sec^2({kk}x)$, so divide by {k}, don't multiply."}
            cands = [("multiplied-by-k", c * k * sp.tan(k * x)),
                     ("power-rule-on-trig", c * sp.sec(k * x) ** 3 / 3),
                     ("differentiated-instead", sp.diff(f, x))]
        x0 = sp.Integer(1) if fam == "log" else sp.Integer(0)
        diff = sp.nsimplify(F.subs(x, x1) - F.subs(x, x0))
        steps = [self._anti_step("Find the general antiderivative $F(x)$.", F, cands, k + p["a"] + p["b"] + p["c"], feedback),
                 Step(f"What is $F\\left({L(x1)}\\right) - F({x0})$?", "number", float(diff), tolerance=0.01,
                      explain=f"$F\\left({L(x1)}\\right) - F({x0}) = {L(diff)}$")]
        checks = [("exists", same(sp.diff(F.subs(sp.Abs(x), x), x), f), "F doesn't differentiate to f"), ("clean", clean(diff), "difference isn't clean")]
        story = f"Find the antiderivatives of $f(x) = {L(f)}$."
        scene = {"type": "integral", "tex": f"\\int \\left({L(f)}\\right)dx", "rule": "\\text{read the derivative table backwards; divide by the inside's } k"}
        return Solution(steps, story, scene, ["antidifferentiate", "difference"], {"_checks": checks})

    # Level 3 ----------------------------------------------------------------------------
    def _ivp(self, p):
        a, b, c, x0, y0, x1 = p["a"], p["b"], p["c"], p["x0"], p["y0"], p["x1"]
        if x1 == x0 or x1 == 0:
            raise NoSolution("evaluate somewhere new (at 0 the answer would just be C)")
        fp = a * x**2 + b * x + c
        if sp.degree(fp, x) < 1:
            raise NoSolution("needs a non-constant derivative")
        F = sp.integrate(fp, x)
        C = y0 - F.subs(x, x0)
        if C == 0:
            raise NoSolution("C = 0 would make forgetting C give the right value")
        val = F.subs(x, x1) + C
        if val in (C, y0):
            raise NoSolution("the last answer would repeat C or the given value")
        cands = self._power_mistakes([(cf, sp.Integer(e)) for (e,), cf in sp.Poly(fp, x).terms()])
        steps = [self._anti_step("Find the general antiderivative of $f'(x)$.", F, cands, a + b + c + y0, pairs=self.POWER_PAIRS),
                 Step(f"Use $f({x0}) = {y0}$. What is $C$?", "number", float(C), tolerance=0.01,
                      explain=f"$f({x0}) = {L(F.subs(x, x0))} + C = {y0}$, so $C = {L(C)}$."),
                 Step(f"So what is $f({x1})$?", "number", float(val), tolerance=0.01,
                      explain=f"$f(x) = {L(F)}{plus(C)}$, so $f({x1}) = {L(val)}$.")]
        story = f"Find $f$ if $f'(x) = {L(fp)}$ and $f({x0}) = {y0}$."
        scene = {"type": "integral", "tex": f"f'(x) = {L(fp)}, \\quad f({x0}) = {y0}", "rule": "\\text{integrate, then use the point to find } C"}
        checks = [("clean", clean(C) and clean(val), "values aren't clean")]
        return Solution(steps, story, scene, ["antidifferentiate", "solve-c", "evaluate"], {"_checks": checks})

    # Level 4 ----------------------------------------------------------------------------
    def _motion(self, p):
        a0, j, v0, s0, T = p["a0"], p["j"], p["v0"], p["s0"], p["T"]
        acc = a0 + j * t
        v = v0 + sp.integrate(acc, t)
        s = s0 + sp.integrate(v, t)
        others = [("integrated-twice", v0 + sp.integrate(sp.integrate(acc, t), t)),
                  ("position-not-velocity", v0 * t + sp.integrate(sp.integrate(acc, t), t)),
                  ("differentiated-a", v0 + sp.diff(acc, t) * t), ("forgot-to-divide", v0 + a0 * t + j * t**2)]
        # forgot-v0 rotates with the rest: always offering it made "the option with the constant" a giveaway
        wrongs = pick(v, rotate([("forgot-v0", v - v0)] + others, a0 + j + v0))
        v_step = self._choice("What is the velocity $v(t)$?", f"$v(t) = {L(v)}$", key(v),
                              [(m, f"$v(t) = {L(e)}$", key(e), FEEDBACK[m]) for m, e in wrongs])
        vT, sT = v.subs(t, T), s.subs(t, T)
        steps = [v_step,
                 Step(f"What is the velocity at $t = {T}$ s, in m/s?", "number", float(vT), tolerance=0.01, explain=f"$v({T}) = {L(vT)}$ m/s"),
                 Step(f"Integrate again, using $s(0) = {s0}$. Where is the cart at $t = {T}$ s, in metres?", "number", float(sT), tolerance=0.01,
                      explain=f"$s(t) = {L(s)}$, so $s({T}) = {L(sT)}$ m.")]
        story = f"A cart starts at position $s(0) = {s0}$ m with velocity $v(0) = {v0}$ m/s. Its acceleration is $a(t) = {L(acc)}$ m/s²."
        scene = {"type": "integral", "tex": f"a(t) = {L(acc)}, \\quad v(0) = {v0}, \\quad s(0) = {s0}", "rule": "v = \\int a\\,dt, \\quad s = \\int v\\,dt"}
        checks = [("clean", clean(vT) and clean(sT), "values aren't clean")]
        return Solution(steps, story, scene, ["velocity", "evaluate-v", "evaluate-s"], {"_checks": checks})


FRAMEWORK = Antiderivatives()
