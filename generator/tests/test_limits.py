import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import limits as lim

FW = lim.FRAMEWORK
x = lim.x


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


class LimitsTest(unittest.TestCase):
    # Level 1: limits from a table ----------------------------------------------------
    def test_level1_answers_match_sympy(self):
        for p in [{"kind": "sin", "k": 3, "a": 0, "m": 1}, {"kind": "exp", "k": 2, "a": 1, "m": -1},
                  {"kind": "root", "k": 3, "a": -2, "m": 2}, {"kind": "pow", "k": 4, "a": 2, "m": 1}]:
            ok, why, sol, _ = validate(FW, p, 1, None)
            self.assertTrue(ok, why)
            f = lim.table_function(p)
            self.assertAlmostEqual(sol.steps[0].answer, float(sp.limit(f, x, p["a"])), places=9)

    def test_level1_undefined_value_never_stops_the_limit(self):
        ok, why, sol, _ = validate(FW, {"kind": "tan", "k": 2, "a": 0, "m": 1}, 1, None)
        self.assertTrue(ok, why)
        self.assertFalse(by_misconception(sol.steps[1], "limit-needs-value").correct)
        self.assertTrue(correct(sol.steps[1]).label.startswith("No"))

    def test_level1_table_shows_both_sides_and_the_gap(self):
        _, _, sol, _ = validate(FW, {"kind": "sin", "k": 2, "a": 1, "m": 1}, 1, None)
        tex = sol.scene["tex"]
        self.assertIn("0.999", tex)
        self.assertIn("1.001", tex)
        self.assertIn("undefined", tex)

    # Level 2: one-sided limits from a graph -------------------------------------------
    def test_level2_jump_has_no_limit(self):
        ok, why, sol, _ = validate(FW, {"family": "jump", "a": 1, "m1": 1, "b1": 0, "m2": -1, "b2": 4, "dot": "right"}, 2, None)
        self.assertTrue(ok, why)
        self.assertEqual(sol.scene["type"], "graph")
        self.assertIn("No", correct(sol.steps[1]).label)
        self.assertFalse(by_misconception(sol.steps[1], "limit-is-value").correct)

    def test_level2_removable_limit_is_never_the_value(self):
        # pieces meet at (1, 2), but f(1) = 5: the limit is 2
        ok, why, sol, _ = validate(FW, {"family": "removable", "a": 1, "m1": 1, "b1": 1, "m2": 2, "b2": 0, "c": 5}, 2, None)
        self.assertTrue(ok, why)
        self.assertIn("2", correct(sol.steps[1]).label)
        self.assertNotIn("5", correct(sol.steps[1]).label)
        self.assertFalse(by_misconception(sol.steps[1], "limit-is-value").correct)

    def test_level2_removable_without_a_value_still_has_a_limit(self):
        ok, why, sol, _ = validate(FW, {"family": "removable", "a": 0, "m1": -1, "b1": 3, "m2": 1, "b2": 3, "c": None}, 2, None)
        self.assertTrue(ok, why)
        self.assertIn("Yes", correct(sol.steps[1]).label)

    # Level 3: factor and cancel --------------------------------------------------------
    def test_level3_limit_and_cancelled_form(self):
        ok, why, sol, _ = validate(FW, {"family": "lin", "k": 1, "a": 3, "r": -3, "s": None}, 3, None)
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[0]).value, "0/0")
        self.assertAlmostEqual(sol.steps[2].answer, 6)

    def test_level3_quadratic_denominator(self):
        ok, why, sol, _ = validate(FW, {"family": "quad", "k": 2, "a": 1, "r": 4, "s": -2}, 3, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, float(sp.Rational(2 * (1 - 4), 1 + 2)))

    def test_level3_root_at_zero_rejected(self):
        # k(x + 0) and k(x − 0) are the same option: the sign-slip distractor would be correct
        ok, why, _, _ = validate(FW, {"family": "lin", "k": 2, "a": 1, "r": 0, "s": None}, 3, None)
        self.assertFalse(ok)
        self.assertIn("distinct", why)

    # Level 4: rationalize --------------------------------------------------------------
    def test_level4_limit_is_one_over_2d(self):
        ok, why, sol, _ = validate(FW, {"family": "top", "d": 2, "a": 0, "m": 1}, 4, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, 0.25)
        self.assertIn("+ 2", correct(sol.steps[0]).label)

    def test_level4_reciprocal_family(self):
        ok, why, sol, _ = validate(FW, {"family": "bottom", "d": 3, "a": 5, "m": 1}, 4, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, 6)

    def test_no_sign_glitches_in_text(self):
        # e.g. "(x - -4)", "+ -3", "(x - 0)", or an empty square root
        import re
        problems, _ = bank.build(FW, seed=1)
        bad = re.compile(r"- -|\+ -|x - 0\b|\\sqrt\{\\;\}")
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
