import unittest

from generator.core import bank
from generator.core.themes import load_themes
from generator.core.validators import validate
from generator.frameworks import bounce

FW = bounce.FRAMEWORK
THEMES = {t["id"]: t for t in load_themes("bounce")}


class BounceTest(unittest.TestCase):
    def test_total_distance_matches_simulation(self):
        for h, r in [(2, 0.64), (1.5, 0.81), (3, 0.25)]:
            self.assertAlmostEqual(bounce.total_distance(h, r), bounce.simulate_distance(h, r), delta=0.001 * bounce.total_distance(h, r))

    def test_levels_valid(self):
        cases = [(1, {"h": 2, "pct": 60, "n": 3}, "basketball"), (2, {"h": 2, "pct": 75, "n": 3}, "superball"),
                 (3, {"h": 2, "e": 0.8, "n": 2}, "golf-ball"), (4, {"h": 2, "pct": 64, "T": 0.25}, "basketball")]
        for level, params, theme in cases:
            ok, why, sol, _ = validate(FW, params, level, THEMES[theme])
            self.assertTrue(ok, f"level {level}: {why}")

    def test_threshold_edge_rejected(self):
        # 2 m × 0.5³ = 0.25 m exactly: "below 0.25 m" is ambiguous after rounding
        ok, why, _, _ = validate(FW, {"h": 2, "pct": 50, "T": 0.25}, 4, THEMES["tennis-ball"])
        self.assertFalse(ok)
        self.assertTrue(why.startswith("clean"), why)

    def test_e_not_squared_distractor(self):
        ok, why, sol, _ = validate(FW, {"h": 2, "e": 0.8, "n": 2}, 3, THEMES["golf-ball"])
        values = {o.misconception: o.value for o in sol.steps[0].options}
        self.assertAlmostEqual(values["e-not-squared"], 0.8)
        right = next(o.value for o in sol.steps[0].options if o.correct)
        self.assertAlmostEqual(right, 0.64)

    def test_unrealistic_restitution_rejected(self):
        ok, why, _, _ = validate(FW, {"h": 2, "pct": 30, "n": 2}, 1, THEMES["tennis-ball"])
        self.assertFalse(ok)
        self.assertTrue(why.startswith("plausible"), why)

    def test_bank_has_300(self):
        problems, report = bank.build(FW, seed=1)
        self.assertGreaterEqual(sum(len(v) for v in problems.values()), 300, report)
        self.assertEqual(sorted(problems), [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
