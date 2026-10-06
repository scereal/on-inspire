"""Applications of the derivative (MATH 140, outcomes 140.5.1–140.5.6). Plan: design/plans/2026-10-05-math-140-applications.md.

Level 1: related rates.
Level 2: linear approximation.
Level 3: the Mean Value Theorem.
Level 4: absolute extrema on a closed interval.
"""
import sympy as sp

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

x = sp.Symbol("x")
MAX_DEN = 20


def L(e):
    return sp.latex(e, ln_notation=True, inv_trig_style="full")


def tex(e):
    return f"${L(e)}$"


def num(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):g}")


def dec(v):
    """A short decimal for text: 1.5, -0.25, 4.0625."""
    return f"{float(v):.6g}"


def key(e):
    return sp.sstr(sp.simplify(e))


def clean(v):
    v = sp.nsimplify(v)
    return v.is_Rational and v.q <= MAX_DEN and abs(v.p) <= 2000


def same(a, b):
    return sp.simplify(a - b) == 0


def pick(right, candidates, n=2):
    kept = []
    for name, e in candidates:
        if same(e, right) or any(same(e, k) for _, k in kept):
            continue
        kept.append((name, e))
        if len(kept) == n:
            break
    return kept


# Level 2 ----------------------------------------------------------------------------

def approx_parts(p):
    a, d = sp.Integer(p["a"]), sp.Rational(p["d"])
    f = {"sqrt": sp.sqrt(x), "cbrt": sp.cbrt(x), "recip": 1 / x}[p["func"]]
    return f, a, d


# Level 3 ----------------------------------------------------------------------------

def mvt_parts(p):
    if p["family"] == "quad":
        f = p["p"] * x**2 + p["q"] * x + p["r"]
        return f, sp.Integer(p["a"]), sp.Integer(p["a"] + p["w"])
    b = sp.Integer(p["b"])
    return x**3 + p["p"] * x, -b, 2 * b


class Applications(Framework):
    id = "applications"
    title = "Applications of the derivative"
    outcome = "Use derivatives for related rates, approximation, the Mean Value Theorem, extrema, optimization and L'Hôpital's rule."
    levels = {
        1: Level("Related rates", {"differentiate-in-t": 1, "solve-rate": 1, "interpret": 1}),
        2: Level("Linear approximation", {"slope": 1, "tangent-line": 1, "estimate": 1, "concavity": 1}),
        3: Level("The Mean Value Theorem", {"average-slope": 1, "mvt": 1, "solve": 1}),
        4: Level("Absolute extrema", {"candidates": 1, "max": 1, "min": 1}),
    }
    misconceptions = {
        "forgot-chain-in-t": "Differentiated with respect to x instead of t: every changing quantity picks up its own rate.",
        "constant-not-zero": "Differentiated a constant as if it changed. A fixed length has rate 0.",
        "sign-ignored": "Ignored the sign of the rate, which says which way the quantity is moving.",
        "equal-rates": "Assumed linked quantities change at the same speed.",
        "product-of-rates": "Multiplied the rates. The product rule gives w′h + wh′.",
        "sum-of-rates": "Added the rates. The product rule gives w′h + wh′.",
        "power-rule-skipped": "Kept s³ instead of differentiating it to 3s².",
        "units-wrong": "Gave the wrong units for the rate.",
        "forgot-shift": "Used x instead of x − a in the tangent line.",
        "forgot-base": "Dropped the starting value f(a) from the tangent line.",
        "tangent-is-exact": "Treated the tangent line as exact. It's only an approximation away from a.",
        "concavity-backwards": "Mixed up which way the curve bends relative to its tangent.",
        "value-not-slope": "Read the theorem as matching values. It matches slopes: f′(c) equals the average rate.",
        "rolle-confusion": "Confused it with Rolle's theorem (f′(c) = 0), which needs f(a) = f(b).",
        "forgot-endpoints": "Left out the endpoints. On a closed interval the extremes can sit at the ends.",
        "outside-point": "Included a critical point outside the interval.",
        "forgot-critical": "Checked only the endpoints and missed the critical points inside.",
    }
    targets = {1: 100, 2: 100, 3: 100, 4: 100}

    def themes_for(self, level):
        return []

    def sample(self, rng, level, theme):
        nz = lambda lo, hi: rng.choice([v for v in range(lo, hi + 1) if v])
        if level == 1:
            family = rng.choice(["ladder", "ladder", "cube", "rectangle"])
            if family == "ladder":
                s = rng.randint(1, 4)
                return {"family": family, "s": s, "foot": rng.choice([3, 4]) * s, "rate": rng.choice(["0.5", "1", "2", "3", "1.5"])}
            if family == "cube":
                return {"family": family, "edge": rng.randint(1, 10), "rate": rng.choice(["0.1", "0.5", "1", "2", "3"])}
            return {"family": family, "w": rng.randint(2, 12), "h": rng.randint(2, 12), "dw": rng.choice(["1", "2", "3", "0.5"]),
                    "dh": rng.choice(["1", "2", "-1", "0.5", "-2"])}
        if level == 2:
            func = rng.choice(["sqrt", "sqrt", "cbrt", "recip"])
            a = {"sqrt": [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144], "cbrt": [1, 8, 27, 64, 125, 216], "recip": [1, 2, 4, 5, 10]}[func]
            deltas = ["0.5", "-0.5", "1", "-1", "0.2", "-0.2", "0.4", "-0.4", "0.3", "-0.3", "0.6", "-0.6", "1.5", "2", "-2", "3"]
            return {"func": func, "a": rng.choice(a), "d": rng.choice(deltas)}
        if level == 3:
            if rng.random() < 0.35:
                return {"family": "cubic", "p": rng.randint(-3, 5), "b": rng.randint(1, 3)}
            return {"family": "quad", "p": nz(-3, 3), "q": rng.randint(-5, 5), "r": rng.randint(-4, 4), "a": rng.randint(-3, 2), "w": rng.randint(1, 4)}
        p = rng.choice([1, 2])
        lo = rng.randint(-4, 1)
        return {"p": p, "q": rng.randint(-5, 5), "lo": lo, "hi": rng.randint(lo + 2, 4)}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        return [None, self._related, self._approx, self._mvt, self._extrema][level](p)

    def _choice(self, prompt, right_label, right_value, wrongs):
        """wrongs: (misconception, label, value, feedback); needs two of them."""
        if len(wrongs) < 2:
            raise NoSolution("fewer than two distinct mistakes: a coin flip")
        return Step(prompt, "choice", right_label, options=[Option(right_label, correct=True, value=right_value)] +
                    [Option(lbl, misconception=m, value=v, feedback=fb) for m, lbl, v, fb in wrongs])

    # Level 1 ----------------------------------------------------------------------------
    def _related(self, p):
        fam = p["family"]
        if fam == "ladder":
            s, foot, rate = p["s"], p["foot"], sp.Rational(p["rate"])
            Lad = 5 * s
            top = sp.sqrt(Lad**2 - foot**2)
            dy = -foot * rate / top
            relation = "2x\\frac{dx}{dt} + 2y\\frac{dy}{dt} = 0"
            d_step = self._choice(f"Differentiate $x^2 + y^2 = {Lad**2}$ with respect to time $t$:", f"${relation}$", "right", [
                ("forgot-chain-in-t", "$2x + 2y = 0$", "no-chain", "$x$ and $y$ both change with time, so each term picks up its own rate: $(x^2)' = 2x\\frac{dx}{dt}$."),
                ("constant-not-zero", f"$2x\\frac{{dx}}{{dt}} + 2y\\frac{{dy}}{{dt}} = {2 * Lad}$", "const", f"The ladder's length doesn't change, so ${Lad**2}$ has rate 0."),
            ])
            mean = self._choice("What does the sign of $\\frac{dy}{dt}$ tell you?", f"The top slides down at {dec(-dy)} m/s", "down", [
                ("sign-ignored", f"The top slides up at {dec(-dy)} m/s", "up", "A negative rate means $y$ is decreasing: the top is moving down the wall."),
                ("equal-rates", f"The top slides down at {dec(rate)} m/s, like the foot", "same", f"The rates are linked by $x\\frac{{dx}}{{dt}} = -y\\frac{{dy}}{{dt}}$, not equal. With $x = {foot}$ and $y = {top}$ they differ."),
            ])
            steps = [d_step,
                     Step(f"When the foot is ${foot}$ m from the wall, what is $\\frac{{dy}}{{dt}}$, in m/s?", "number", float(dy), tolerance=0.005,
                          explain=f"$y = \\sqrt{{{Lad**2} - {foot**2}}} = {top}$, so $2({foot})({dec(rate)}) + 2({top})\\frac{{dy}}{{dt}} = 0$ and $\\frac{{dy}}{{dt}} = {dec(dy)}$."),
                     mean]
            story = f"A {Lad} m ladder leans against a wall. Its foot slides away from the wall at {dec(rate)} m/s. Let $x$ be the foot's distance from the wall and $y$ the height of the top."
            answer = dy
        elif fam == "cube":
            e, rate = p["edge"], sp.Rational(p["rate"])
            dV = 3 * e**2 * rate
            d_step = self._choice("Differentiate $V = s^3$ with respect to $t$:", "$\\frac{dV}{dt} = 3s^2\\frac{ds}{dt}$", "right", [
                ("forgot-chain-in-t", "$\\frac{dV}{dt} = 3s^2$", "no-chain", "$s$ changes with time, so the chain rule multiplies by $\\frac{ds}{dt}$."),
                ("power-rule-skipped", "$\\frac{dV}{dt} = s^3\\frac{ds}{dt}$", "no-power", "Differentiate $s^3$ first: $3s^2$, then multiply by $\\frac{ds}{dt}$."),
            ])
            mean = self._choice("What are the units of $\\frac{dV}{dt}$?", "cm³ per second", "cm3/s", [
                ("units-wrong", "cm per second", "cm/s", "Volume is in cm³, so its rate is cm³ per second."),
                ("units-wrong", "cm² per second", "cm2/s", "Volume is in cm³, so its rate is cm³ per second."),
            ])
            steps = [d_step,
                     Step(f"How fast is the volume growing when the edge is {e} cm, in cm³/s?", "number", float(dV), tolerance=0.01,
                          explain=f"$3({e})^2({dec(rate)}) = {dec(dV)}$ cm³/s."),
                     mean]
            story = f"The edges of a cube grow at {dec(rate)} cm/s."
            answer = dV
        else:
            w, h, dw, dh = p["w"], p["h"], sp.Rational(p["dw"]), sp.Rational(p["dh"])
            dA = dw * h + w * dh
            d_step = self._choice("Differentiate $A = wh$ with respect to $t$:", "$\\frac{dA}{dt} = \\frac{dw}{dt}h + w\\frac{dh}{dt}$", "right", [
                ("product-of-rates", "$\\frac{dA}{dt} = \\frac{dw}{dt}\\cdot\\frac{dh}{dt}$", "product", "The product rule has two terms: each side's rate times the other side."),
                ("sum-of-rates", "$\\frac{dA}{dt} = \\frac{dw}{dt} + \\frac{dh}{dt}$", "sum", "Rates of a product don't add. The product rule gives $w'h + wh'$."),
            ])
            mean = self._choice("What are the units of $\\frac{dA}{dt}$?", "cm² per second", "cm2/s", [
                ("units-wrong", "cm per second", "cm/s", "Area is in cm², so its rate is cm² per second."),
                ("units-wrong", "cm²", "cm2", "A rate needs \"per second\": cm² per second."),
            ])
            steps = [d_step,
                     Step(f"How fast is the area changing when $w = {w}$ cm and $h = {h}$ cm, in cm²/s?", "number", float(dA), tolerance=0.01,
                          explain=f"$({dec(dw)})({h}) + ({w})({dec(dh)}) = {dec(dA)}$ cm²/s."),
                     mean]
            move = lambda r: f"{'grows' if r > 0 else 'shrinks'} at {dec(abs(r))} cm/s"
            story = f"A rectangle's width $w$ {move(dw)} and its height $h$ {move(dh)}."
            answer = dA
        checks = [("clean", clean(answer), "rate isn't clean")]
        scene = {"type": "integral", "tex": {"ladder": "x^2 + y^2 = L^2", "cube": "V = s^3", "rectangle": "A = wh"}[fam], "rule": "\\text{differentiate with respect to } t"}
        return Solution(steps, story, scene, ["differentiate-in-t", "solve-rate", "interpret"], {"rate": float(answer), "_checks": checks})

    # Level 2 ----------------------------------------------------------------------------
    def _approx(self, p):
        f, a, d = approx_parts(p)
        if a + d <= 0 or abs(d) >= a:
            raise NoSolution("the estimate point must stay well inside the domain")
        fa, fpa, fppa = f.subs(x, a), sp.diff(f, x).subs(x, a), sp.diff(f, x, 2).subs(x, a)
        tangent = fa + fpa * (x - a)
        est = tangent.subs(x, a + d)
        true = f.subs(x, a + d)
        if abs(float(est - true)) < 0.0002:
            raise NoSolution("the estimate is indistinguishable from the true value at this tolerance")
        over = fppa < 0
        name = {"sqrt": "\\sqrt{x}", "cbrt": "\\sqrt[3]{x}", "recip": "\\frac{1}{x}"}[p["func"]]
        xv = a + d
        line = self._choice(f"What is the tangent line $L(x)$ at $x = {a}$?", f"$L(x) = {L(fa)} + {L(fpa)}(x - {a})$".replace("+ -", "- "), "right", [
            ("forgot-shift", f"$L(x) = {L(fa)} + {L(fpa)}x$".replace("+ -", "- "), "no-shift", f"The slope multiplies the distance from the tangent point, $x - {a}$, not $x$ itself."),
            ("forgot-base", f"$L(x) = {L(fpa)}(x - {a})$", "no-base", f"Start from the known value $f({a}) = {L(fa)}$, then add the change."),
        ])
        bend = self._choice(f"Is ${dec(est)}$ an overestimate or an underestimate of the true value?",
                            "An overestimate" if over else "An underestimate", "over" if over else "under", [
            ("concavity-backwards", "An underestimate" if over else "An overestimate", "under" if over else "over",
             f"$f''({a})$ is {'negative' if over else 'positive'}, so the curve bends {'down' if over else 'up'}, away from the tangent line, which sits {'above' if over else 'below'} it."),
            ("tangent-is-exact", "Exact: the tangent line matches the curve", "exact",
             "The tangent line only touches the curve at $x = " + str(a) + "$. Elsewhere it's an approximation."),
        ])
        steps = [
            Step(f"What is $f'({a})$ for $f(x) = {name}$?", "number", float(fpa), tolerance=0.0005, explain=f"$f'({a}) = {L(fpa)}$"),
            line,
            Step(f"Use $L(x)$ to estimate $f({dec(xv)})$.", "number", float(est), tolerance=0.0001,
                 explain=f"$L({dec(xv)}) = {L(fa)} + \\left({L(fpa)}\\right)({dec(d)}) = {dec(est)}$ (the true value is ${dec(true)}$)."),
            bend,
        ]
        story = f"Estimate ${name.replace('x', dec(xv))}$ using the tangent line to $f(x) = {name}$ at $x = {a}$."
        scene = {"type": "integral", "tex": f"f(x) \\approx f({a}) + f'({a})(x - {a})", "rule": ""}
        return Solution(steps, story, scene, ["slope", "tangent-line", "estimate", "concavity"], {"estimate": float(est), "_checks": []})

    # Level 3 ----------------------------------------------------------------------------
    def _mvt(self, p):
        f, a, b = mvt_parts(p)
        avg = (f.subs(x, b) - f.subs(x, a)) / (b - a)
        cs = [r for r in sp.solve(sp.Eq(sp.diff(f, x), avg), x) if r.is_real and a < r < b]
        if len(cs) != 1:
            raise NoSolution("needs exactly one c strictly inside")
        c = cs[0]
        if p["family"] == "cubic" and c == (a + b) / 2:
            raise NoSolution("a cubic whose c is the midpoint teaches the wrong lesson")
        promise = self._choice(f"What does the Mean Value Theorem promise for some $c$ in $({a}, {b})$?", f"$f'(c) = {L(avg)}$", "slope", [
            ("value-not-slope", f"$f(c) = {L(avg)}$", "value", "The theorem matches slopes, not values: the tangent at $c$ is parallel to the chord."),
            ("rolle-confusion", "$f'(c) = 0$", "zero", f"$f'(c) = 0$ is Rolle's theorem, which needs $f({a}) = f({b})$. Here the average slope is ${L(avg)}$."),
        ])
        steps = [
            Step(f"What is the average rate of change of $f$ on $[{a}, {b}]$?", "number", float(avg), tolerance=0.01,
                 explain=f"$\\frac{{f({b}) - f({a})}}{{{b} - ({a})}} = \\frac{{{f.subs(x, b)} - ({f.subs(x, a)})}}{{{b - a}}} = {L(avg)}$"),
            promise,
            Step("Find that $c$.", "number", float(c), tolerance=0.01, explain=f"$f'(x) = {L(sp.diff(f, x))} = {L(avg)}$ inside the interval at $c = {L(c)}$."),
        ]
        story = f"Let $f(x) = {L(f)}$ on $[{a}, {b}]$."
        scene = {"type": "integral", "tex": f"f'(c) = \\frac{{f({b}) - f({a})}}{{{b} - ({a})}}".replace("- (-", "+ (").replace("+ (", "+ ").replace(")}", "}") if a < 0 else f"f'(c) = \\frac{{f({b}) - f({a})}}{{{b} - {a}}}", "rule": ""}
        checks = [("clean", clean(c) and clean(avg), "c or the average isn't clean")]
        return Solution(steps, story, scene, ["average-slope", "mvt", "solve"], {"c": float(c), "_checks": checks})

    # Level 4 ----------------------------------------------------------------------------
    def _extrema(self, p):
        pp, q, lo, hi = p["p"], p["q"], p["lo"], p["hi"]
        f = x**3 - 3 * pp**2 * x + q
        crit = [-pp, pp]
        inside = [c for c in crit if lo < c < hi]
        outside = [c for c in crit if not lo <= c <= hi]
        cands = sorted(set(inside + [lo, hi]))
        values = {c: f.subs(x, c) for c in cands}
        hi_v, lo_v = max(values.values()), min(values.values())
        if list(values.values()).count(hi_v) > 1 or list(values.values()).count(lo_v) > 1:
            raise NoSolution("a tie: the max or min happens twice")
        show = lambda cs: "$" + ", ".join(str(c) for c in cs) + "$" if cs else "none"
        wrongs = []
        if inside:
            wrongs.append(("forgot-endpoints", show(sorted(inside)), "inside", f"On a closed interval the endpoints ${lo}$ and ${hi}$ are candidates too."))
            wrongs.append(("forgot-critical", show([lo, hi]), "ends", f"Check where $f'(x) = 0$ inside the interval as well: $x = {', '.join(map(str, inside))}$."))
        if outside:
            wrongs.append(("outside-point", show(sorted(set(cands + outside))), "outside", f"$x = {', '.join(map(str, outside))}$ is outside $[{lo}, {hi}]$, so it doesn't count."))
        cand_step = self._choice(f"Which $x$-values are the candidates for the absolute max and min on $[{lo}, {hi}]$?", show(cands), "right", wrongs[:2])
        steps = [
            cand_step,
            Step(f"What is the absolute maximum value of $f$ on $[{lo}, {hi}]$?", "number", float(hi_v), tolerance=0.01,
                 explain="Compare: " + ", ".join(f"$f({c}) = {values[c]}$" for c in cands) + "."),
            Step(f"And the absolute minimum value?", "number", float(lo_v), tolerance=0.01),
        ]
        story = f"Find the absolute maximum and minimum of $f(x) = {L(f)}$ on $[{lo}, {hi}]$."
        scene = {"type": "integral", "tex": f"f(x) = {L(f)}, \\quad x \\in [{lo}, {hi}]", "rule": f"f'(x) = {L(sp.diff(f, x))}"}
        return Solution(steps, story, scene, ["candidates", "max", "min"], {"max": float(hi_v), "min": float(lo_v), "_checks": []})


FRAMEWORK = Applications()
