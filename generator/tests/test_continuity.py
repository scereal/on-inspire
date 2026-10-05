import re
import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import continuity as co

FW = co.FRAMEWORK
x = co.x


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


class ContinuityTest(unittest.TestCase):
    # Level 1: make it continuous ------------------------------------------------------
    def test_level1_slope_family_makes_the_limits_meet(self):
        p = {"family": "slope", "a": 2, "d": 1, "e": 0, "g": 0}      # c·x + 1 below 2, x² from 2 on → c = 3/2
        ok, why, sol, _ = validate(FW, p, 1, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[-1].answer, 1.5)
        left, right = co.pieces(p, sp.Rational(3, 2))
        self.assertEqual(sp.limit(left, x, 2, "-"), sp.limit(right, x, 2, "+"))

    def test_level1_rejects_a_zero_for_slope_family(self):
        ok, why, _, _ = validate(FW, {"family": "slope", "a": 0, "d": 1, "e": 0, "g": 0}, 1, None)
        self.assertFalse(ok)

    def test_level1_removable_value_is_the_limit(self):
        ok, why, sol, _ = validate(FW, {"family": "removable", "a": 3, "b": 3, "k": 1}, 1, None)   # (x² − 9)/(x − 3), so f(3) = 6
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[-1].answer, 6)
        self.assertFalse(by_misconception(sol.steps[0], "slopes-must-match").correct)

    # Level 2: the Intermediate Value Theorem ------------------------------------------
    def test_level2_guaranteed_root(self):
        ok, why, sol, _ = validate(FW, {"family": "cubic", "p": 1, "q": -1, "lo": 0, "hi": 1, "N": 0}, 2, None)
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[1]).value, "guaranteed")

    def test_level2_same_signs_mean_no_guarantee_never_no_root(self):
        # x² − x − 2 is positive at −3 and 3 but has roots at −1 and 2
        ok, why, sol, _ = validate(FW, {"family": "quad", "p": -1, "q": -2, "lo": -3, "hi": 3, "N": 0}, 2, None)
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[1]).value, "no-guarantee")
        self.assertFalse(by_misconception(sol.steps[1], "ivt-converse").correct)

    def test_level2_discontinuous_function_doesnt_qualify(self):
        ok, why, sol, _ = validate(FW, {"family": "break", "k": 1, "s": 0, "m": 0, "lo": -1, "hi": 2, "N": 0}, 2, None)
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[1]).value, "doesnt-apply")

    def test_level2_converse_is_never_correct(self):
        problems, _ = bank.build(FW, seed=1)
        for p in problems[2]:
            step = p["steps"][1]
            self.assertFalse(any(o["correct"] and o.get("misconception") == "ivt-converse" for o in step["options"]), p["id"])

    def test_level2_verdicts_are_balanced(self):
        from collections import Counter
        problems, _ = bank.build(FW, seed=1)
        verdicts = Counter(next(o["value"] for o in p["steps"][1]["options"] if o["correct"]) for p in problems[2])
        for v in ("guaranteed", "no-guarantee", "doesnt-apply"):
            self.assertGreaterEqual(verdicts[v], 20, verdicts)

    def test_level2_broken_functions_really_miss_the_target(self):
        # the lesson: the end values straddle N, yet f(x) = N has no solution, because f breaks
        problems, _ = bank.build(FW, seed=1)
        for p in problems[2]:
            if p["params"]["family"] == "break":
                q = p["params"]
                f = co.ivt_function(q)
                sols = [r for r in sp.solve(sp.Eq(f, q["N"]), x) if r.is_real and q["lo"] <= r <= q["hi"]]
                self.assertEqual(sols, [], p["id"])

    # Level 3: epsilon–delta ------------------------------------------------------------
    def test_level3_delta_is_epsilon_over_slope(self):
        ok, why, sol, _ = validate(FW, {"m": -4, "b": 3, "a": 2, "eps": "0.1"}, 3, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[0].answer, -5)
        self.assertAlmostEqual(sol.steps[2].answer, 0.025)
        self.assertIn("4", correct(sol.steps[1]).label)

    def test_no_sign_glitches_in_text(self):
        problems, _ = bank.build(FW, seed=1)
        bad = re.compile(r"- -|\+ -|x - 0\b|\$(negative|positive)\$")
        for level, items in problems.items():
            for p in items:
                texts = [p["story"]] + [t for st in p["steps"] for t in [st["prompt"], st.get("explain", "")] +
                                        [o.get("feedback", "") for o in st.get("options", [])] + [o["label"] for o in st.get("options", [])]]
                for t in texts:
                    self.assertIsNone(bad.search(t), f"L{level} {p['id']}: {t}")

    def test_bank(self):
        problems, report = bank.build(FW, seed=1)
        for level in FW.levels:
            self.assertGreaterEqual(len(problems[level]), 100, report["levels"][str(level)])


if __name__ == "__main__":
    unittest.main()
