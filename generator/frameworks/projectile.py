"""Projectile aim (spec section 5.2). No air resistance; g comes from the theme (9.8, or 1.6 on the Moon).

Level 1: horizontal launch from height h, find vx.     Level 2: ground launch with fixed vy, find vx.
Level 3: fixed speed, find the lower of two angles.    Level 4: fixed vx, find vy to clear a wall.
"""
import math

from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step

HEIGHTS = [0.8, 1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20]
DISTANCES = [x / 2 for x in range(2, 241)]          # 1 m to 120 m in 0.5 m steps
VY = list(range(2, 21))
SPEEDS = list(range(4, 31))
VX4 = [x / 2 for x in range(4, 31)]                 # 2 to 15 m/s
W4 = [x / 2 for x in range(2, 41)]                  # 1 to 20 m
WALLS = [1, 1.5, 2, 2.5, 3, 3.5, 4]
SLIDER_STEP = 0.1


def round1(v):
    return round(v + 1e-12, 1)


def num(v):
    """Print 2.0 as 2 and 2.50 as 2.5."""
    return f"{v:g}"


def simulate(vx, vy, y0, g, dt=1e-4):
    """Independent check: step the flight forward until it reaches the ground; return landing x."""
    x, y, t = 0.0, y0, 0.0
    while True:
        nvy = vy - g * dt
        nx, ny = x + vx * dt, y + (vy + nvy) / 2 * dt
        if ny <= 0 and t > 0:
            frac = y / (y - ny) if y != ny else 0
            return x + (nx - x) * frac
        x, y, vy, t = nx, ny, nvy, t + dt
        if t > 120:
            return math.inf


def height_at(vx, vy, y0, g, x_target, dt=1e-4):
    x, y = 0.0, y0
    while x < x_target:
        nvy = vy - g * dt
        y += (vy + nvy) / 2 * dt
        vy = nvy
        x += vx * dt
    return y


def gravity(theme):
    return theme["physics"].get("g", [9.8])[0] if theme else 9.8


def target_radius(d):
    return max(0.25, 0.03 * d)


def g_of(p, theme=None):
    return p.get("g") or gravity(theme)


def derived(p, level, g):
    """The slider answers, computed the same way everywhere (solve, plausibility)."""
    if level == 1:
        return {"vx": round1(p["d"] / math.sqrt(2 * p["h"] / g))}
    if level == 2:
        return {"vx": round1(p["d"] / (2 * p["vy"] / g))}
    if level == 4:
        tw = p["w"] / p["vx"]
        return {"vy": round1((p["H"] + 0.5 * g * tw**2) / tw)}
    return {}


class Projectile(Framework):
    id = "projectile"
    title = "Projectile aim"
    outcome = "Horizontal and vertical motion are independent: the vertical motion sets the flight time, and distance = vₓ × time."
    levels = {
        1: Level("Off a ledge", {"fall-time": 1, "x=vt": 1}),
        2: Level("Up and over", {"rise-and-fall": 1, "x=vt": 1}),
        3: Level("Two angles", {"range-equation": 1, "complementary-angles": 1}),
        4: Level("Clear the wall", {"x=vt": 1, "height-at-time": 1}),
    }
    misconceptions = {
        "forgot-half": "Dropped the ½ in h = ½gt².",
        "no-square-root": "Forgot to take the square root when solving for t.",
        "speed-changes-fall-time": "Thought horizontal speed changes how long it takes to fall.",
        "heavier-falls-faster": "Thought heavier or faster objects fall faster.",
        "forgot-the-2": "Used only the time to the top: the trip down takes just as long.",
        "mixes-x-and-y": "Mixed horizontal and vertical quantities.",
        "one-right-answer": "Assumed only one angle can hit the target.",
        "adds-to-45": "Thought the two angles are symmetric about 45° by adding, not by summing to 90°.",
        "doubles": "Doubled the angle instead of using 90° − θ.",
        "supplement": "Used 180° − θ, which points backwards.",
        "doubled-time": "Doubled the time to the wall.",
        "fall-time-instead": "Used the time to fall from the wall's height instead of the horizontal trip.",
    }
    targets = {1: 90, 2: 80, 3: 70, 4: 80}
    STORY_FIELDS = {1: {"h", "d"}, 2: {"vy", "d"}, 3: {"v", "d"}, 4: {"vx", "w", "H"}}

    def sample(self, rng, level, theme):
        ph = theme["physics"]
        dists = [d for d in DISTANCES if ph["distance"][0] <= d <= ph["distance"][1]]
        g = gravity(theme)
        if level == 1:
            hs = [h for h in HEIGHTS if ph["height"][0] <= h <= ph["height"][1]]
            return {"h": rng.choice(hs), "d": rng.choice(dists), "g": g}
        if level == 2:
            return {"vy": rng.choice(VY), "d": rng.choice(dists), "g": g}
        if level == 3:
            v = rng.choice([s for s in SPEEDS if ph["speed"][0] <= s <= ph["speed"][1]])
            theta = rng.randint(10, 40)
            return {"v": v, "d": round1(v**2 * math.sin(math.radians(2 * theta)) / g), "g": g}
        hs = [h for h in WALLS if ph["height"][0] <= h <= ph["height"][1]]
        return {"vx": rng.choice(VX4), "w": rng.choice([w for w in W4 if w <= ph["distance"][1]]), "H": rng.choice(hs), "g": g}

    def canonical(self, p, level):
        return f"{level}:" + ",".join(f"{k}={p[k]}" for k in sorted(p))

    def count_solutions(self, p, level):
        if level != 3:
            return 1
        s = g_of(p) * p["d"] / p["v"] ** 2
        if s > 1:
            return 0
        lower = math.degrees(math.asin(s)) / 2
        return 1 if lower < 44.5 else 0  # at maximum range only 45° works, so there is no "lower arc"

    def plausibility(self, p, level, theme):
        dv = derived(p, level, g_of(p, theme))
        out = [("distance", p.get("d", p.get("w", 0)))]
        if level == 1:
            out += [("height", p["h"]), ("speed", dv["vx"])]
        elif level == 2:
            out += [("speed", math.hypot(dv["vx"], p["vy"]))]
        elif level == 3:
            out += [("speed", p["v"])]
        else:
            out += [("height", p["H"]), ("speed", math.hypot(p["vx"], dv["vy"]))]
        return out

    def checks(self, p, level, theme, solution):
        return solution.answers.get("_checks", [])

    def solve(self, p, level, theme):
        g = g_of(p, theme)
        label = theme["label"]
        fields = {k: num(v) for k, v in p.items() if k != "g"}
        story = theme["stories"][level][0].format(**fields)
        if level == 1:
            return self._level1(p, g, label, story)
        if level == 2:
            return self._level2(p, g, label, story)
        if level == 3:
            return self._level3(p, g, label, story)
        return self._level4(p, g, label, story)

    # Level helpers -------------------------------------------------------------------

    def _time_choice(self, prompt, right, wrongs):
        opts = [Option(f"{right:.2f} s", correct=True, value=round(right, 2))]
        for m, v, fb in wrongs:
            opts.append(Option(f"{v:.2f} s" if isinstance(v, float) else v, misconception=m, feedback=fb,
                               value=round(v, 2) if isinstance(v, float) else v))
        return Step(prompt, "choice", opts[0].label, options=opts)

    def _slider(self, prompt, answer, hi, unit, param, explain):
        return Step(prompt, "slider", answer, tolerance=SLIDER_STEP / 2, unit=unit, explain=explain,
                    slider={"param": param, "min": 0, "max": hi, "step": SLIDER_STEP})

    def _level1(self, p, g, label, story):
        h, d = p["h"], p["d"]
        t = math.sqrt(2 * h / g)
        vx = derived(p, 1, g)["vx"]
        land = simulate(vx, 0, h, g)
        steps = [
            self._time_choice(f"How long is {label} in the air?", t, [
                ("forgot-half", math.sqrt(h / g), "From h = ½gt², t = √(2h/g). Don't drop the ½."),
                ("no-square-root", 2 * h / g, "2h/g is t², not t."),
                ("speed-changes-fall-time", "It depends on how fast it's launched",
                 "Horizontal speed doesn't change how fast it falls: the fall time depends only on the height."),
            ]),
            self._slider(f"Set the horizontal speed so {label} lands on the target.", vx, 40 if vx < 35 else 110, "m/s", "vx",
                         f"vₓ = d / t = {num(d)} / {t:.2f} ≈ {vx} m/s."),
            Step(f"A second, heavier object is dropped straight down from the same height at the same moment. Which hits the ground first?",
                 "choice", "They land at the same time", options=[
                     Option("They land at the same time", correct=True, value="same"),
                     Option(f"The dropped one", misconception="speed-changes-fall-time",
                            feedback="Moving sideways doesn't slow the fall: both start with zero vertical speed.", value="dropped"),
                     Option("The heavier one", misconception="heavier-falls-faster",
                            feedback="Without air resistance, every object falls with the same acceleration g.", value="heavier"),
                 ]),
        ]
        checks = [("exists", abs(land - d) <= target_radius(d), f"simulated landing {land:.2f} m misses target {d} m")]
        scene = {"type": "projectile", "g": g, "y0": h, "target": d, "radius": target_radius(d), "slider": "vx", "fixed": {"vy": 0}}
        return Solution(steps, story, scene, ["fall-time", "x=vt"], {"vx": vx, "t": t, "_checks": checks})

    def _level2(self, p, g, label, story):
        vy, d = p["vy"], p["d"]
        t = 2 * vy / g
        vx = derived(p, 2, g)["vx"]
        land = simulate(vx, vy, 0, g)
        steps = [
            self._time_choice(f"How long is {label} in the air?", t, [
                ("forgot-the-2", vy / g, "vᵧ/g is only the time to reach the top. Coming down takes just as long."),
                ("mixes-x-and-y", d / vy, "The flight time comes from vertical motion only: d and vᵧ don't belong together."),
            ]),
            self._slider(f"Set the horizontal speed so {label} lands on the target.", vx, 40, "m/s", "vx",
                         f"vₓ = d / t = {num(d)} / {t:.2f} ≈ {vx} m/s."),
            Step("If you throw with twice the horizontal speed (same upward speed), what happens to the flight time?",
                 "choice", "It stays the same", options=[
                     Option("It stays the same", correct=True, value="same"),
                     Option("It doubles", misconception="speed-changes-fall-time",
                            feedback="Flight time depends only on the vertical motion. It lands twice as far, in the same time.", value="doubles"),
                     Option("It halves", misconception="speed-changes-fall-time",
                            feedback="Going faster sideways doesn't make it fall sooner.", value="halves"),
                 ]),
        ]
        checks = [("exists", abs(land - d) <= target_radius(d), f"simulated landing {land:.2f} m misses target {d} m")]
        scene = {"type": "projectile", "g": g, "y0": 0, "target": d, "radius": target_radius(d), "slider": "vx", "fixed": {"vy": vy}}
        return Solution(steps, story, scene, ["rise-and-fall", "x=vt"], {"vx": vx, "t": t, "_checks": checks})

    def _level3(self, p, g, label, story):
        v, d = p["v"], p["d"]
        s = g * d / v**2
        if s > 1:
            raise NoSolution(f"{d} m is beyond the maximum range at {v} m/s")
        theta = math.degrees(math.asin(min(s, 1))) / 2
        answer = round(theta)
        other = 90 - answer
        exact_land = simulate(v * math.cos(math.radians(theta)), v * math.sin(math.radians(theta)), 0, g)
        rounded_land = simulate(v * math.cos(math.radians(answer)), v * math.sin(math.radians(answer)), 0, g)
        steps = [
            Step("How many launch angles send it exactly onto the target?", "choice", "2", options=[
                Option("2", correct=True, value=2),
                Option("1", misconception="one-right-answer",
                       feedback="A low, fast-flying arc and a high, lofted arc can land in the same spot.", value=1),
                Option("Infinitely many", misconception="one-right-answer",
                       feedback="At a fixed speed, only specific angles reach that exact distance.", value="infinite"),
            ], explain="Range depends on sin(2θ), and sin(2θ) = sin(180° − 2θ), so two angles give the same range."),
            Step("Set the lower launch angle so it lands on the target.", "slider", answer, tolerance=0.5, unit="°",
                 slider={"param": "angle", "min": 0, "max": 90, "step": 1},
                 explain=f"sin(2θ) = gd/v² = {s:.3f}, so θ ≈ {answer}°."),
            Step("What's the other angle that lands in the same spot?", "choice", f"{other}°", options=[
                Option(f"{other}°", correct=True, value=other),
                Option(f"{45 + answer}°", misconception="adds-to-45", feedback="The two angles add up to 90°.", value=45 + answer),
                Option(f"{2 * answer}°", misconception="doubles", feedback="Doubling isn't the rule: the two angles add up to 90°.", value=2 * answer),
                Option(f"{180 - answer}°", misconception="supplement", feedback="An angle above 90° points backwards.", value=180 - answer),
            ], explain=f"{answer}° + {other}° = 90°."),
        ]
        checks = [
            ("clean", abs(theta - answer) <= 0.2, f"angle {theta:.2f}° isn't close to a whole degree"),
            ("exists", abs(exact_land - d) <= 0.05, f"simulation {exact_land:.3f} m disagrees with range formula"),
            ("findable", abs(rounded_land - d) <= target_radius(d), "rounded angle misses the target"),
        ]
        scene = {"type": "projectile", "g": g, "y0": 0, "target": d, "radius": target_radius(d), "slider": "angle", "fixed": {"speed": v}}
        return Solution(steps, story, scene, ["range-equation", "complementary-angles"], {"angle": answer, "_checks": checks})

    def _level4(self, p, g, label, story):
        vx, w, H = p["vx"], p["w"], p["H"]
        tw = w / vx
        vy = derived(p, 4, g)["vy"]
        t_top = vy / g
        if abs(tw - t_top) <= 0.03 * t_top:
            raise NoSolution("ball is at its peak at the wall: rising/falling is ambiguous")
        rising = tw < t_top
        y_at_wall = height_at(vx, vy, 0, g, w)
        steps = [
            self._time_choice(f"How long does {label} take to reach the wall?", tw, [
                ("doubled-time", 2 * tw, "Horizontal speed is constant: time = distance / speed."),
                ("fall-time-instead", math.sqrt(2 * H / g), "That's how long it takes to fall from the wall's height, not to travel there."),
            ]),
            self._slider("Set the upward speed so it just clears the top of the wall.", vy, 40, "m/s", "vy",
                         f"At t = {tw:.2f} s it must be {num(H)} m up: vᵧ = (H + ½gt²) / t ≈ {vy} m/s."),
            Step("When it passes the wall, is it still rising or already falling?", "choice",
                 "Still rising" if rising else "Already falling", options=[
                     Option("Still rising", correct=rising, value="rising",
                            misconception=None if rising else "fall-time-instead",
                            feedback="" if rising else f"It peaks at vᵧ/g ≈ {t_top:.2f} s, before it reaches the wall."),
                     Option("Already falling", correct=not rising, value="falling",
                            misconception=None if not rising else "fall-time-instead",
                            feedback="" if not rising else f"It peaks at vᵧ/g ≈ {t_top:.2f} s, after it passes the wall."),
                 ]),
        ]
        checks = [("exists", abs(y_at_wall - H) <= 0.05 * tw + 0.02, f"simulated height {y_at_wall:.2f} m at wall vs {H} m")]
        scene = {"type": "projectile", "g": g, "y0": 0, "wall": {"x": w, "h": H}, "target": None, "slider": "vy", "fixed": {"vx": vx}}
        return Solution(steps, story, scene, ["x=vt", "height-at-time"], {"vy": vy, "_checks": checks})


FRAMEWORK = Projectile()
