"""Continuity, the IVT and epsilon–delta (MATH 140, outcomes 140.2.4–140.2.5). Plan: design/plans/2026-10-05-math-140-limits.md.

Level 1: choose the constant that makes a function continuous.
Level 2: what the Intermediate Value Theorem does (and doesn't) tell you.
Level 3: the largest δ for a given ε, for a linear function.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x, C = sp.symbols("x c")
MAX_DEN = 20


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):g}")


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 200


def factor(v):
    return f"({sp.latex(x - v)})" if v else "x"


# Level 1 ----------------------------------------------------------------------------

def pieces(p, c=C):
    """(left piece for x < a, right piece for x ≥ a), with the unknown constant c."""
    d, e, g = p["d"], p["e"], p["g"]
    if p["family"] == "slope":
        return c * x + d, x**2 + e * x + g
    return x**2 + e * x + g, d * x + c


def cases_tex(p):
    left, right = pieces(p)
    a = p["a"]
    return f"f(x) = \\begin{{cases}} {sp.latex(left)} & x < {a} \\\\ {sp.latex(right)} & x \\ge {a} \\end{{cases}}"


# Level 2 ----------------------------------------------------------------------------

def ivt_function(p):
    if p["family"] == "cubic":
        return x**3 + p["p"] * x + p["q"]
    if p["family"] == "quad":
        return x**2 + p["p"] * x + p["q"]
    return sp.Integer(p["k"]) / (x - p["s"]) + p["m"]


class Continuity(Framework):
    id = "continuity"
    title = "Continuity"
    outcome = "Decide and enforce continuity, use the Intermediate Value Theorem, and work with the epsilon–delta definition."
    levels = {
        1: Level("Make it continuous", {"condition": 1, "limit": 1, "solve": 1}),
        2: Level("The Intermediate Value Theorem", {"evaluate-ends": 1, "ivt": 1}),
        3: Level("Epsilon and delta", {"limit": 1, "simplify-gap": 1, "delta": 1}),
    }
    misconceptions = {
        "slopes-must-match": "Required matching slopes. That's differentiability; continuity only needs the pieces to meet.",
        "defined-is-enough": "Thought being defined at the point is enough. The value has to match the limit.",
        "swapped-ends": "Swapped which endpoint gives which value.",
        "sign-error": "Mishandled a negative input (a negative number cubed stays negative).",
        "arithmetic-slip": "Made an arithmetic slip evaluating the endpoints.",
        "ivt-converse": "Read the IVT backwards: when it gives no guarantee, it doesn't say there's no solution.",
        "ivt-without-between": "Applied the IVT when the target isn't between the endpoint values.",
        "misread-between": "Missed that the target is between the endpoint values.",
        "ignores-continuity": "Applied the IVT to a function that isn't continuous on the interval.",
        "polynomial-discontinuous": "Doubted that a polynomial is continuous. Polynomials are continuous everywhere.",
        "forgot-slope": "Dropped the slope factor: |m(x − a)| = |m||x − a|.",
        "abs-of-negative": "Kept a negative sign outside an absolute value. Absolute values are never negative.",
        "forgot-to-subtract-L": "Measured |f(x)| instead of the gap |f(x) − L|.",
    }
    targets = {1: 100, 2: 100, 3: 100}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        if level == 1:
            family = rng.choice(["slope", "shift", "removable"])
            if family == "removable":
                return {"family": family, "a": rng.randint(-4, 4), "b": rng.randint(-5, 5), "k": rng.choice([1, 1, 2, 3, -1])}
            return {"family": family, "a": rng.choice([-3, -2, -1, 1, 2, 3]), "d": rng.randint(-5, 5),
                    "e": rng.randint(-3, 3), "g": rng.randint(-4, 4)}
        if level == 2:
            # Pick the verdict first so the three answers come up about equally often
            verdict = rng.choices(["guaranteed", "no-guarantee", "doesnt-apply"], weights=[4, 3, 3])[0]
            family = "break" if verdict == "doesnt-apply" else rng.choice(["cubic", "quad", "quad"])
            lo = rng.randint(-3, 1)
            hi = lo + rng.randint(2 if family == "break" else 1, 4)
            if family == "break":
                p = {"family": family, "k": rng.choice([1, 2, 3, -1, -2]), "s": rng.randint(lo + 1, hi - 1), "m": rng.randint(-2, 2), "lo": lo, "hi": hi}
            else:
                p = {"family": family, "p": rng.randint(-4, 4), "q": rng.randint(-5, 5), "lo": lo, "hi": hi}
            f = ivt_function(p)
            A, B = sorted([f.subs(x, lo), f.subs(x, hi)])
            inside = [n for n in range(int(sp.floor(A)) + 1, int(sp.ceiling(B))) if A < n < B]
            if verdict == "no-guarantee":
                outside = [n for n in range(int(sp.floor(A)) - 3, int(sp.ceiling(B)) + 4) if n < A or n > B]
                p["N"] = 0 if 0 in outside else rng.choice(outside)
            else:
                p["N"] = 0 if 0 in inside else (rng.choice(inside) if inside else 0)
            return p
        return {"m": rng.choice([2, 4, 5, 10, -2, -4, -5, -10]), "b": rng.randint(-5, 5), "a": rng.randint(-3, 3),
                "eps": rng.choice(["1", "0.5", "0.1", "0.05", "0.01"])}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._make_continuous, self._ivt, self._epsilon_delta][level](p)

    # Level 1 ----------------------------------------------------------------------------
    def _condition_step(self, a):
        return Step(f"What has to be true for $f$ to be continuous at $x = {a}$?", "choice", "limits", options=[
            Option(f"The limit as $x \\to {a}$ exists and equals $f({a})$", correct=True, value="limits"),
            Option("The slopes on each side match", misconception="slopes-must-match", value="slopes",
                   feedback="Matching slopes is the extra condition for a derivative. Continuity only needs the graph to meet itself with no gap."),
            Option(f"$f({a})$ just has to be defined", misconception="defined-is-enough", value="defined",
                   feedback=f"Being defined isn't enough: $f({a})$ must equal the value the graph is heading toward."),
        ])

    def _make_continuous(self, p):
        a = p["a"]
        if p["family"] == "removable":
            k, b = p["k"], p["b"]
            top = sp.expand(k * (x - a) * (x + b))
            c = sp.Integer(k * (a + b))
            steps = [
                self._condition_step(a),
                Step(f"What value of $c = f({a})$ makes $f$ continuous?", "number", float(c), tolerance=0.01,
                     explain=f"Cancel ${factor(a)}$: for $x \\ne {a}$, $f(x) = {sp.latex(sp.expand(k * (x + b)))}$, which approaches ${c}$. So $c = {c}$."),
            ]
            story = f"Let $f(x) = \\frac{{{sp.latex(top)}}}{{{sp.latex(x - a)}}}$ for $x \\ne {a}$, and $f({a}) = c$."
            scene = {"type": "integral", "tex": f"f(x) = \\begin{{cases}} \\frac{{{sp.latex(top)}}}{{{sp.latex(x - a)}}} & x \\ne {a} \\\\ c & x = {a} \\end{{cases}}", "rule": ""}
            checks = [("exists", sp.limit(top / (x - a), x, a) == c, "limit disagrees")]
            return Solution(steps, story, scene, ["condition", "solve"], {"c": float(c), "_checks": checks})
        if p["family"] == "slope" and a == 0:
            raise NoSolution("at a = 0 the unknown slope multiplies 0, so no value of c helps")
        left, right = pieces(p)
        known, unknown, side = (right, left, "right") if p["family"] == "slope" else (left, right, "left")
        target = known.subs(x, a)
        sol = sp.solve(sp.Eq(unknown.subs(x, a), target), C)
        if len(sol) != 1:
            raise NoSolution("no unique c")
        c = sol[0]
        steps = [
            self._condition_step(a),
            Step(f"The {side} piece has no $c$ in it. What value does it approach as $x \\to {a}$?", "number", float(target), tolerance=0.01,
                 explain=f"Substitute $x = {a}$ into ${sp.latex(known)}$: ${target}$."),
            Step(f"Make the other piece approach the same value. What is $c$?", "number", float(c), tolerance=0.01,
                 explain=f"${sp.latex(unknown.subs(x, a))} = {target}$, so $c = {sp.latex(c)}$."),
        ]
        story = "Find the value of $c$ that makes $f$ continuous everywhere."
        scene = {"type": "integral", "tex": cases_tex(p), "rule": ""}
        lft, rgt = pieces(p, c)
        checks = [("exists", sp.limit(lft, x, a, "-") == sp.limit(rgt, x, a, "+") == rgt.subs(x, a), "pieces don't meet"),
                  ("clean", clean(c), "c isn't clean")]
        return Solution(steps, story, scene, ["condition", "limit", "solve"], {"c": float(c), "_checks": checks})

    # Level 2 ----------------------------------------------------------------------------
    def _ivt(self, p):
        f, lo, hi, N = ivt_function(p), p["lo"], p["hi"], p["N"]
        A, B = f.subs(x, lo), f.subs(x, hi)
        if N in (A, B):
            raise NoSolution("an endpoint hits the target exactly")
        between = min(A, B) < N < max(A, B)
        broken = p["family"] == "break"
        if broken and not between:
            raise NoSolution("the discontinuous family needs the target between the end values, or the lesson is lost")
        hits = [r for r in sp.solve(sp.Eq(f, N), x) if r.is_real and lo <= r <= hi]
        if broken and hits:
            raise NoSolution("the broken function hits the target anyway, which blurs the lesson")
        verdict = "doesnt-apply" if broken else ("guaranteed" if between else "no-guarantee")
        pair = lambda u, v: f"$f({lo}) = {num(u)}$ and $f({hi}) = {num(v)}$"
        ends = [Option(pair(A, B), correct=True, value=f"{A},{B}")]
        if A != B:
            ends.append(Option(pair(B, A), misconception="swapped-ends", value=f"{B},{A}",
                               feedback="Match each value to its own endpoint."))
        if not broken and (lo < 0 or hi < 0):
            A2, B2 = f.subs(x, abs(lo)), f.subs(x, abs(hi))
            if (A2, B2) not in ((A, B), (B, A)):
                ends.append(Option(pair(A2, B2), misconception="sign-error", value=f"{A2},{B2}",
                                   feedback="Careful with negative inputs: $(-2)^3 = -8$ and $(-2)^2 = 4$."))
        if len(ends) < 3:
            ends.append(Option(pair(A + 1, B + 1), misconception="arithmetic-slip", value=f"{A + 1},{B + 1}",
                               feedback="Recompute both values carefully, one term at a time."))
        wrong = {
            "guaranteed": {
                "no-guarantee": ("ivt-without-between", f"${N}$ isn't between ${num(A)}$ and ${num(B)}$, so the IVT can't promise a solution."),
                "doesnt-apply": ("misread-between", f"$f$ isn't continuous on $[{lo}, {hi}]$: it breaks at $x = {p.get('s')}$, so the IVT says nothing."),
            },
            "no-root": ("ivt-converse", ("There happens to be none here, but the IVT can't tell you that: it never rules a solution out, it only promises one when its conditions hold."
                                         if not hits else "In fact there are solutions here. The IVT never rules a solution out; it only promises one when its conditions hold.")),
            "polynomial": ("polynomial-discontinuous", "Polynomials are continuous everywhere, so the IVT does apply here."),
        }
        opts = {
            "guaranteed": Option(f"$f(x) = {N}$ has at least one solution in $({lo}, {hi})$", value="guaranteed"),
            "no-root": Option(f"$f(x) = {N}$ has no solution in $[{lo}, {hi}]$", value="no-root", misconception="ivt-converse",
                              feedback=wrong["no-root"][1]),
            "no-guarantee": Option(f"Nothing: ${N}$ isn't between $f({lo})$ and $f({hi})$, so there's no guarantee either way", value="no-guarantee"),
            "doesnt-apply": Option(f"Nothing: $f$ isn't continuous on $[{lo}, {hi}]$, so the IVT doesn't apply", value="doesnt-apply"),
        }
        opts[verdict].correct = True
        if verdict == "guaranteed":
            opts["no-guarantee"].misconception, opts["no-guarantee"].feedback = "misread-between", f"${N}$ is between ${num(A)}$ and ${num(B)}$: check again."
            opts["doesnt-apply"].misconception, opts["doesnt-apply"].feedback = wrong["polynomial"]
        elif verdict == "no-guarantee":
            opts["guaranteed"].misconception, opts["guaranteed"].feedback = wrong["guaranteed"]["no-guarantee"]
            opts["doesnt-apply"].misconception, opts["doesnt-apply"].feedback = wrong["polynomial"]
        else:
            opts["guaranteed"].misconception = "ignores-continuity"
            opts["guaranteed"].feedback = f"$f$ jumps at $x = {p['s']}$ (the bottom is 0 there), so the IVT's promise doesn't hold. In fact $f(x) = {N}$ may have no solution."
            opts["no-guarantee"].misconception, opts["no-guarantee"].feedback = "misread-between", f"${N}$ is between ${num(A)}$ and ${num(B)}$. The problem is elsewhere."
        steps = [
            Step(f"Evaluate $f$ at both ends of $[{lo}, {hi}]$.", "choice", ends[0].label, options=ends),
            Step(f"What does the Intermediate Value Theorem tell you about $f(x) = {N}$ on $[{lo}, {hi}]$?", "choice",
                 opts[verdict].label, options=[opts[k] for k in ("guaranteed", "no-root", "no-guarantee", "doesnt-apply")]),
        ]
        story = f"Let $f(x) = {sp.latex(f)}$ on the interval $[{lo}, {hi}]$."
        scene = {"type": "integral", "tex": f"f(x) = {sp.latex(f)}, \\quad x \\in [{lo}, {hi}]", "rule": f"\\text{{target: }} f(x) = {N}"}
        checks = [("clean", clean(A) and clean(B), "endpoint values aren't clean")]
        return Solution(steps, story, scene, ["evaluate-ends", "ivt"], {"verdict": verdict, "_checks": checks})

    # Level 3 ----------------------------------------------------------------------------
    def _epsilon_delta(self, p):
        m, b, a = p["m"], p["b"], p["a"]
        eps = sp.Rational(p["eps"])
        f = m * x + b
        L = sp.Integer(m * a + b)
        delta = eps / abs(m)
        gap = f"|{sp.latex(x - a)}|"
        opts = [Option(f"${abs(m)}{gap}$", correct=True, value="right"),
                Option(f"${gap}$", misconception="forgot-slope", value="no-slope",
                       feedback=f"$f(x) - L = {sp.latex(sp.expand(f - L))}$, which is ${m}$ times ${factor(a)}$. Its size ${abs(m)}$ stays outside the absolute value."),
                Option(f"$|{sp.latex(f)}|$", misconception="forgot-to-subtract-L", value="no-L",
                       feedback=f"The gap is between $f(x)$ and the limit ${L}$: start from $|f(x) {'-' if L >= 0 else '+'} {abs(L)}|$.")]
        if m < 0:
            opts.append(Option(f"${m}{gap}$", misconception="abs-of-negative", value="neg",
                               feedback=f"$|{m}(\\ldots)| = {abs(m)}|\\ldots|$. An absolute value is never negative."))
        steps = [
            Step(f"What is $L = \\lim_{{x\\to {a}}} ({sp.latex(f)})$?", "number", float(L), tolerance=0.01,
                 explain=f"A line is continuous, so substitute: ${m}({a}) + {b} = {L}$.".replace("+ -", "- ")),
            Step(f"Simplify the gap $|f(x) - L|$.", "choice", opts[0].label, options=opts),
            Step(f"For $\\varepsilon = {p['eps']}$, what is the largest $\\delta$ that guarantees $|f(x) - L| < \\varepsilon$?", "number",
                 float(delta), tolerance=float(delta) * 0.01,
                 explain=f"${abs(m)}{gap} < {p['eps']}$ exactly when ${gap} < \\frac{{{p['eps']}}}{{{abs(m)}}} = {float(delta):g}$."),
        ]
        story = f"Show that $\\lim_{{x\\to {a}}} ({sp.latex(f)})$ exists using $\\varepsilon$ and $\\delta$."
        scene = {"type": "integral", "tex": f"|x - {a}| < \\delta \\implies |f(x) - L| < \\varepsilon".replace("- -", "+ ").replace("x - 0", "x"), "rule": ""}
        checks = [("exists", sp.limit(f, x, a) == L, "limit disagrees")]
        return Solution(steps, story, scene, ["limit", "simplify-gap", "delta"], {"delta": float(delta), "_checks": checks})


FRAMEWORK = Continuity()
