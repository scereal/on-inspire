"""Bouncing ball (spec section 5.4). Each bounce keeps a fraction r of the height: a geometric sequence.

Level 1: height after n bounces.   Level 2: total distance (a finite infinite sum).
Level 3: start from the coefficient of restitution e, so r = e².   Level 4: bounces until below a height.
"""
import math

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

HEIGHTS = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
THRESHOLDS = [0.05, 0.1, 0.2, 0.25, 0.3, 0.5]
EDGE = 0.02  # level 4: reject if any bounce lands within 2% of the threshold


def total_distance(h, r):
    return h + 2 * h * r / (1 - r)


def simulate_distance(h, r, bounces=200):
    """Independent check: add up each fall and rise."""
    dist, height = h, h
    for _ in range(bounces):
        height *= r
        dist += 2 * height
    return dist


def m(v):
    return f"{v:.2f} m" if v >= 0.1 else f"{v:.3f} m"


def r_of(p):
    return p["e"] ** 2 if "e" in p else p["pct"] / 100


class Bounce(Framework):
    id = "bounce"
    title = "Bouncing ball"
    outcome = "Each bounce keeps the same fraction of the height, a geometric sequence, and infinitely many bounces cover a finite distance."
    levels = {
        1: Level("Shrinking bounces", {"multiply": 1, "power": 1}),
        2: Level("Total distance", {"multiply": 1, "partial-sum": 1, "geometric-series": 1}),
        3: Level("Coefficient of restitution", {"square-e": 1, "power": 1}),
        4: Level("When does it drop below?", {"power": 1, "logarithm": 1}),
    }
    misconceptions = {
        "kept-vs-lost": "Used the fraction lost instead of the fraction kept.",
        "skipped-a-bounce": "Applied the fraction twice for one bounce.",
        "finite-bounces": "Thought the model ball stops after a few bounces.",
        "one-way-only": "Counted only the fall (or only the rise) of each bounce.",
        "ignores-shrink": "Forgot that each bounce is lower than the last.",
        "first-drop-twice": "Counted the first drop as if it went up and down.",
        "infinite-sum-infinite": "Thought infinitely many bounces must add up to an infinite distance.",
        "e-not-squared": "Used e for the height ratio. e is a speed ratio; height goes with speed squared.",
        "root-not-square": "Used √e: height depends on speed squared, so the fraction is e².",
        "loss-fraction": "Used 1 − e, the fraction of speed lost.",
        "off-by-one": "Counted one bounce too few or too many.",
    }
    targets = {1: 80, 2: 80, 3: 70, 4: 80}
    STORY_FIELDS = {1: {"h", "pct"}, 2: {"h", "pct"}, 3: {"h", "e"}, 4: {"h", "pct"}}

    def sample(self, rng, level, theme):
        ph = theme["physics"]
        h = rng.choice([x for x in HEIGHTS if ph["height"][0] <= x <= ph["height"][1]])
        lo, hi = ph["restitution"]
        if level == 3:
            return {"h": h, "e": round(rng.uniform(lo, hi), 2), "n": rng.randint(1, 3)}
        pcts = [p for p in range(5, 100, 5) if lo <= math.sqrt(p / 100) <= hi] or [round(lo**2 * 100)]
        p = {"h": h, "pct": rng.choice(pcts)}
        if level == 4:
            p["T"] = rng.choice([t for t in THRESHOLDS if t < h * p["pct"] / 100])
        else:
            p["n"] = rng.randint(2, 4)
        return p

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def plausibility(self, p, level, theme):
        return [("height", p["h"]), ("restitution", math.sqrt(r_of(p)))]

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        h, r = p["h"], r_of(p)
        label = theme["label"]
        story = theme["stories"][level][0].format(**{k: f"{v:g}" for k, v in p.items()})
        scene = {"type": "bounce", "h": h, "r": r, "color": theme["visuals"]["color"], "shape": theme["visuals"]["shape"]}
        if level == 1:
            n = p["n"]
            ans = round(h * r**n, 3)
            steps = [
                Step("How high does it rise after the first bounce?", "choice", m(h * r), options=[
                    Option(m(h * r), correct=True, value=round(h * r, 3)),
                    Option(m(h * (1 - r)), misconception="kept-vs-lost",
                           feedback=f"It keeps {p['pct']}% of the height, so multiply by {r:g}, not by {1 - r:g}.", value=round(h * (1 - r), 3)),
                    Option(m(h * r * r), misconception="skipped-a-bounce",
                           feedback="One bounce means one multiplication by the fraction.", value=round(h * r * r, 3)),
                ]),
                Step(f"How high does it rise after bounce number {n}? (in metres)", "number", ans,
                     tolerance=max(0.005, 0.01 * ans), unit="m", explain=f"{h:g} × {r:g}^{n} ≈ {ans:g} m."),
                Step("In this model, does the ball ever stop bouncing?", "choice", "No: every bounce is smaller, but never zero", options=[
                    Option("No: every bounce is smaller, but never zero", correct=True, value="never"),
                    Option("Yes, after about 10 bounces", misconception="finite-bounces",
                           feedback="Multiplying by a fraction shrinks the height but never reaches zero. Real balls stop because of effects this model leaves out.", value="ten"),
                ]),
            ]
            return Solution(steps, story, scene, ["multiply", "power"], {"height": ans})
        if level == 2:
            third_hit = round(h + 2 * h * r + 2 * h * r**2, 3)
            total = total_distance(h, r)
            one_way, double = h / (1 - r), 2 * h / (1 - r)
            sim = simulate_distance(h, r)
            steps = [
                Step("How far does it travel between hitting the floor the first and second time?", "choice", m(2 * h * r), options=[
                    Option(m(2 * h * r), correct=True, value=round(2 * h * r, 3)),
                    Option(m(h * r), misconception="one-way-only", feedback="It goes up and then comes back down: count both.", value=round(h * r, 3)),
                    Option(m(2 * h), misconception="ignores-shrink", feedback="It doesn't rise all the way back to the starting height.", value=round(2 * h, 3)),
                ]),
                Step("How far has it traveled in total when it hits the floor for the third time? (in metres)", "number", third_hit,
                     tolerance=max(0.005, 0.01 * third_hit), unit="m",
                     explain=f"{h:g} (first drop) + 2·{h * r:g} + 2·{h * r * r:g} ≈ {third_hit:g} m."),
                Step("If it bounced forever, how far would it travel in total?", "choice", m(total), options=[
                    Option(m(total), correct=True, value=round(total, 3)),
                    Option(m(one_way), misconception="one-way-only", feedback="That counts each bounce once. Every bounce goes up and down.", value=round(one_way, 3)),
                    Option(m(double), misconception="first-drop-twice", feedback="The first drop only goes down: it isn't doubled.", value=round(double, 3)),
                    Option("Infinitely far", misconception="infinite-sum-infinite",
                           feedback="The bounces shrink geometrically, so their sum converges: h + 2hr/(1 − r).", value="infinite"),
                ], explain=f"h + 2hr/(1 − r) = {h:g} + 2·{h:g}·{r:g}/{1 - r:g} ≈ {total:.2f} m."),
            ]
            checks = [("exists", abs(sim - total) <= 0.001 * total, f"series {total:.4f} vs simulation {sim:.4f}")]
            return Solution(steps, story, scene, ["multiply", "partial-sum", "geometric-series"], {"total": total, "_checks": checks})
        if level == 3:
            e, n = p["e"], p["n"]
            ans = round(h * r**n, 3)
            steps = [
                # every option to 4 decimal places, so the right one isn't the only long number
                Step("What fraction of its height does it keep on each bounce?", "choice", f"{r:.4f}", options=[
                    Option(f"{r:.4f}", correct=True, value=round(r, 4)),
                    Option(f"{e:.4f}", misconception="e-not-squared",
                           feedback="e compares speeds. Height depends on speed squared, so the height fraction is e².", value=e),
                    # half the problems swap in √e, so the right value isn't reliably the middle one
                    (Option(f"{1 - e:.4f}", misconception="loss-fraction", feedback="1 − e is the fraction of speed lost, not height kept.", value=round(1 - e, 4))
                     if int(round(e * 100)) % 2 == 0 else
                     Option(f"{math.sqrt(e):.4f}", misconception="root-not-square",
                            feedback="Height grows with the square of the speed, not its square root: the fraction is e², not √e.", value=round(math.sqrt(e), 4))),
                ], explain=f"Rise height ∝ (launch speed)², so each bounce keeps e² = {r:.4g} of the height."),
                Step(f"How high does it rise after bounce number {n}? (in metres)", "number", ans,
                     tolerance=max(0.001, 0.01 * ans), unit="m", explain=f"{h:g} × ({e:g}²)^{n} ≈ {ans:g} m."),
            ]
            return Solution(steps, story, scene, ["square-e", "power"], {"height": ans})

        T = p["T"]
        n = math.ceil(math.log(T / h) / math.log(r))
        heights = [h * r**k for k in range(1, n + 2)]
        edge = min(abs(x - T) / T for x in heights)
        if n < 2:
            raise NoSolution("drops below on the first bounce")
        story += f" How many bounces until it no longer rises to {T:g} m?"
        # vary which side the wrong counts sit on, so the answer isn't always the middle number
        offsets = [(-1, 1), (1, 2), (-2, -1)][n % 3] if n > 2 else (1, 2)
        wrong_count = lambda k: (Option(str(k), misconception="off-by-one", feedback=f"After {k} bounces it still reaches {m(h * r**k)}.", value=k)
                                 if k < n else Option(str(k), misconception="off-by-one",
                                                      feedback=f"It already falls short after {n} bounces ({m(h * r**n)}).", value=k))
        steps = [Step(f"After how many bounces does it first fail to reach {T:g} m?", "choice", str(n), options=[
            Option(str(n), correct=True, value=n)] + [wrong_count(n + o) for o in offsets], explain=f"Solve {h:g}·{r:g}ⁿ < {T:g}: n > ln({T:g}/{h:g}) / ln({r:g}) ≈ {math.log(T / h) / math.log(r):.2f}, so n = {n}.")]
        checks = [("clean", edge > EDGE, f"a bounce lands within {edge:.1%} of {T:g} m")]
        return Solution(steps, story, scene, ["power", "logarithm"], {"n": n, "_checks": checks})


FRAMEWORK = Bounce()
