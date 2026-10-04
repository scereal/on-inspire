"""Mixing concentrate and water with two marked cups (spec section 5.3).

Moves (one mark each): add concentrate, add water, pour one mark into the other cup, empty a cup.
Level 1: ratio → fraction, then build it.   Level 2: a strength that needs dilution.   Level 3: weighted average.
"""
from collections import deque
from fractions import Fraction
from functools import lru_cache

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

CUP_SIZES = [3, 4, 5, 6]
MOVE_CAP = {1: 4, 2: 8, 3: 10}
MAX_DENOMINATOR = 16
SIMPLE = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(2, 3), Fraction(3, 4), Fraction(1, 1)]
NAMES = ["A", "B"]


def frac(s):
    return Fraction(s)


def show(f):
    f = Fraction(f)
    return "1 (pure)" if f == 1 else str(f)


def strength_of(f, conc):
    """'pure strong tea' or '1/3 strong tea', for sentences."""
    return f"pure {conc}" if Fraction(f) == 1 else f"{Fraction(f)} {conc}"


def move(state, action, i, caps):
    (va, ca), (vb, cb) = state
    cups = [[va, ca], [vb, cb]]
    cup, other = cups[i], cups[1 - i]
    if action in ("concentrate", "water"):
        if cup[0] >= caps[i]:
            return None
        cup[0] += 1
        if action == "concentrate":
            cup[1] += 1
    elif action == "pour":
        if cup[0] < 1 or other[0] >= caps[1 - i]:
            return None
        moved = cup[1] / cup[0]
        cup[0] -= 1
        cup[1] -= moved
        other[0] += 1
        other[1] += moved
    elif action == "empty":
        if cup[0] == 0:
            return None
        cup[0], cup[1] = 0, Fraction(0)
    return (cups[0][0], cups[0][1]), (cups[1][0], cups[1][1])


@lru_cache(maxsize=None)
def reachable(ma, mb, limit=12):
    """Every strength some cup can hold (with at least one mark), with the fewest moves and one path."""
    caps = (ma, mb)
    start = ((0, Fraction(0)), (0, Fraction(0)))
    seen, best = {start: []}, {}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        path = seen[state]
        for vol, conc in state:
            if vol:
                s = conc / vol
                if s not in best:
                    best[s] = (len(path), path)
        if len(path) >= limit:
            continue
        for action in ("concentrate", "water", "pour", "empty"):
            for i in (0, 1):
                nxt = move(state, action, i, caps)
                if nxt is not None and nxt not in seen:
                    seen[nxt] = path + [(action, i)]
                    queue.append(nxt)
    return best


def describe(path):
    words = {"concentrate": "add concentrate to {}", "water": "add water to {}", "pour": "pour one mark from {} into the other cup",
             "empty": "empty {}"}
    return "; ".join(words[a].format(f"cup {NAMES[i]}") for a, i in path)


class Mixing(Framework):
    id = "mixing"
    title = "Mixing drinks"
    outcome = "Strength is a fraction of the whole: a ratio isn't a fraction, diluting multiplies strength, and mixing averages it."
    levels = {
        1: Level("Ratios and parts", {"ratio-to-fraction": 1, "build": 1}),
        2: Level("Diluting a dilution", {"build": 1, "dilute": 1}),
        3: Level("Mixing two drinks", {"weighted-average": 1, "build": 1}),
    }
    misconceptions = {
        "ratio-as-fraction": "Read a:b as a/b. A ratio compares parts with each other, not with the whole.",
        "water-share": "Gave the water's share instead of the concentrate's.",
        "cup-size-limit": "Thought a cup's marks limit how precise a strength can be.",
        "dilution-subtracts": "Thought diluting takes off a fixed amount of strength.",
        "dilution-no-change": "Thought adding water leaves the strength unchanged.",
        "unweighted-average": "Averaged the strengths without weighting by amount.",
        "add-strengths": "Added the strengths, as if the water vanished.",
        "multiply-strengths": "Multiplied the strengths, which is what diluting does, not mixing.",
    }
    targets = {1: 50, 2: 140, 3: 120}  # level 1 has only ~65 distinct problems (cup sizes × recipes)
    STORY_FIELDS = {1: {"ma", "mb"}, 2: {"ma", "mb"}, 3: {"ma", "mb"}}

    def sample(self, rng, level, theme):
        ma, mb = rng.choice(CUP_SIZES), rng.choice(CUP_SIZES)
        if level == 1:
            a, b = rng.choice(theme["ratios"])
            return {"ma": ma, "mb": mb, "a": a, "b": b}
        if level == 2:
            options = sorted(s for s, (m, _) in reachable(ma, mb).items()
                             if max(ma, mb) < s.denominator <= MAX_DENOMINATOR and m <= MOVE_CAP[2])
            if not options:
                return {"ma": ma, "mb": mb, "s": "1/1000"}
            return {"ma": ma, "mb": mb, "s": str(rng.choice(options))}
        m1, m2 = rng.randint(1, 3), rng.randint(1, 3)
        s1, s2 = rng.sample(SIMPLE, 2)
        return {"ma": ma, "mb": mb, "m1": m1, "s1": str(s1), "m2": m2, "s2": str(s2)}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def plausibility(self, p, level, theme):
        return [("strength", float(self._target(p, level)))]

    def _target(self, p, level):
        if level == 1:
            return Fraction(p["a"], p["a"] + p["b"])
        if level == 2:
            return frac(p["s"])
        return (p["m1"] * frac(p["s1"]) + p["m2"] * frac(p["s2"])) / (p["m1"] + p["m2"])

    def checks(self, p, level, theme, solution):
        moves = solution.answers["moves"]
        target = self._target(p, level)
        return [("clean", target.denominator <= MAX_DENOMINATOR, f"strength {target} has an awkward denominator"),
                ("findable", moves <= MOVE_CAP[level], f"needs {moves} moves, level allows {MOVE_CAP[level]}")]

    def _build_step(self, target, ma, mb, concentrate):
        table = reachable(ma, mb)
        if target not in table:
            raise NoSolution(f"{target} can't be made with {ma}- and {mb}-mark cups")
        moves, path = table[target]
        step = Step(f"Make a drink that is exactly {show(target)} {concentrate}, in either cup.", "mix", str(target),
                    explain=f"One way in {moves} moves: {describe(path)}.")
        return step, moves, path

    def solve(self, p, level, theme):
        ma, mb = p["ma"], p["mb"]
        conc = theme.get("concentrate", "concentrate")
        intro = theme["stories"][level][0].format(ma=ma, mb=mb)
        target = self._target(p, level)
        scene = {"type": "mixing", "cups": [ma, mb], "target": str(target), "color": theme["visuals"]["color"], "concentrate": conc}

        if level == 1:
            a, b = p["a"], p["b"]
            story = f"{intro} The recipe is {a} part{'s' if a > 1 else ''} {conc} to {b} part{'s' if b > 1 else ''} water."
            build, moves, path = self._build_step(target, ma, mb, conc)
            steps = [Step(f"What fraction of the finished drink is {conc}?", "choice", show(target), options=[
                Option(show(target), correct=True, value=float(target)),
                Option(show(Fraction(a, b)), misconception="ratio-as-fraction",
                       feedback=f"{a}:{b} compares {conc} with water. Count every part: {a} + {b} = {a + b}.", value=float(Fraction(a, b))),
                Option(show(Fraction(b, a + b)), misconception="water-share",
                       feedback="That's the water's share. Which part is the concentrate?", value=float(Fraction(b, a + b))),
            ]), build]
            tools = ["ratio-to-fraction", "build"]
        elif level == 2:
            story = f"{intro} Each move fills, pours or empties one mark."
            build, moves, path = self._build_step(target, ma, mb, conc)
            steps = [
                Step(f"Can you make a drink that is exactly {show(target)} {conc}, using only these cups?", "choice", "Yes", options=[
                    Option("Yes", correct=True, value="yes"),
                    Option(f"No: the cups only have {max(ma, mb)} marks", misconception="cup-size-limit",
                           feedback="True if you only start from pure concentrate. But you can dilute a drink that's already diluted.", value="no"),
                ], explain="Dilute, then dilute part of the result again: each round multiplies the strength."),
                build,
                Step("When you mix a drink with an equal amount of water, its strength:", "choice", "Halves", options=[
                    Option("Halves", correct=True, value="halves"),
                    Option("Drops by a fixed amount", misconception="dilution-subtracts",
                           feedback="Diluting scales the strength: equal water doubles the volume, so strength is cut in half.", value="minus"),
                    Option("Stays the same", misconception="dilution-no-change",
                           feedback="The same amount of concentrate is now spread through twice the liquid.", value="same"),
                ]),
            ]
            tools = ["build", "dilute"]
        else:
            m1, m2, s1, s2 = p["m1"], p["m2"], frac(p["s1"]), frac(p["s2"])
            story = (f"{intro} You pour {m1} mark{'s' if m1 > 1 else ''} of a drink that's {strength_of(s1, conc)} "
                     f"together with {m2} mark{'s' if m2 > 1 else ''} of one that's {strength_of(s2, conc)}.")
            build, moves, path = self._build_step(target, ma, mb, conc)
            avg, add, mul = (s1 + s2) / 2, s1 + s2, s1 * s2
            steps = [Step(f"How strong is the mixture?", "choice", show(target), options=[
                Option(show(target), correct=True, value=float(target)),
                Option(show(avg), misconception="unweighted-average",
                       feedback=f"There's more of one drink than the other. Weight each strength by its marks: ({m1}·{show(s1)} + {m2}·{show(s2)}) / {m1 + m2}.",
                       value=float(avg)),
                Option(show(add), misconception="add-strengths", feedback="Adding strengths ignores the water in each drink.", value=float(add)),
                Option(show(mul), misconception="multiply-strengths",
                       feedback="Multiplying is what diluting does. Mixing two drinks lands between their strengths.", value=float(mul)),
            ], explain="Total concentrate ÷ total marks."), build]
            tools = ["weighted-average", "build"]
        return Solution(steps, story, scene, tools, {"moves": moves, "path": [list(m) for m in path]})


FRAMEWORK = Mixing()
