import math
import unittest

from generator.core import bank
from generator.core.themes import load_themes
from generator.core.validators import validate
from generator.frameworks import projectile

FW = projectile.FRAMEWORK
THEMES = {t["id"]: t for t in load_themes("projectile")}
BALL = THEMES["ball"]


class ProjectileTest(unittest.TestCase):
    def test_simulation_agrees_with_closed_form(self):
        # Level 1: horizontal launch from h with vx lands at vx·sqrt(2h/g)
        land = projectile.simulate(vx=6.0, vy=0.0, y0=2.0, g=9.8)
        self.assertAlmostEqual(land, 6.0 * math.sqrt(2 * 2.0 / 9.8), delta=0.01)
        # Ground launch lands at vx · 2vy/g
        self.assertAlmostEqual(projectile.simulate(vx=4.0, vy=7.0, y0=0.0, g=9.8), 4.0 * 2 * 7.0 / 9.8, delta=0.01)
        # Height when passing x = w
        self.assertAlmostEqual(projectile.height_at(4.0, 10.0, 0.0, 9.8, 6.0), 10 * 1.5 - 4.9 * 1.5**2, delta=0.01)

    def test_each_level_valid(self):
        cases = [(1, {"h": 10, "d": 10}, BALL), (2, {"vy": 7, "d": 8}, BALL),
                 (3, {"v": 15, "d": projectile.round1(15**2 * math.sin(math.radians(30)) / 9.8)}, BALL),
                 (4, {"vx": 6, "w": 6, "H": 3}, BALL)]
        for level, params, theme in cases:
            ok, why, sol, report = validate(FW, params, level, theme)
            self.assertTrue(ok, f"level {level}: {why}")
            self.assertTrue(any(s.format == "slider" for s in sol.steps))

    def test_two_angles_at_max_range_or_beyond_rejected(self):
        at_max = {"v": 14, "d": projectile.round1(14**2 / 9.8)}
        ok, why, _, _ = validate(FW, at_max, 3, BALL)
        self.assertFalse(ok)
        self.assertTrue(why.startswith("unique"), why)
        beyond = {"v": 10, "d": 30}
        ok, why, _, _ = validate(FW, beyond, 3, BALL)
        self.assertFalse(ok)
        self.assertTrue(why.startswith("exists"), why)

    def test_unrealistic_stomp_rocket_rejected(self):
        ok, why, _, _ = validate(FW, {"vy": 300, "d": 40}, 2, THEMES["stomp-rocket"])
        self.assertFalse(ok)
        self.assertTrue(why.startswith("plausible"), why)

    def test_forgot_the_2_is_exactly_half(self):
        ok, why, sol, _ = validate(FW, {"vy": 7, "d": 8}, 2, BALL)
        options = {o.misconception: o.value for o in sol.steps[0].options}
        right = next(o.value for o in sol.steps[0].options if o.correct)
        self.assertAlmostEqual(options["forgot-the-2"], right / 2, delta=0.006)

    def test_moon_uses_lunar_gravity(self):
        ok, why, sol, _ = validate(FW, {"h": 10, "d": 10}, 1, THEMES["moon-ball"])
        self.assertTrue(ok, why)
        self.assertEqual(sol.scene["g"], 1.6)

    def test_bank_has_300(self):
        problems, report = bank.build(FW, seed=1)
        self.assertGreaterEqual(sum(len(v) for v in problems.values()), 300, report)
        self.assertEqual(sorted(problems), [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
