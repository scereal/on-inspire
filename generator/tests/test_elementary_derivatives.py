import re
import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import elementary_derivatives as ed

FW = ed.FRAMEWORK
x = ed.x


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


class ElementaryDerivativesTest(unittest.TestCase):
    def test_pick_drops_options_equal_to_the_answer(self):
        right = 3 * sp.cos(3 * x)
        kept = ed.pick(right, [("same", sp.cos(3 * x) * 3), ("wrong", sp.cos(3 * x)), ("also-wrong", -3 * sp.sin(3 * x))])
        self.assertEqual([m for m, _ in kept], ["wrong", "also-wrong"])

    # Level 1: trig ------------------------------------------------------------------
    def test_level1_sin_cos(self):
        ok, why, sol, _ = validate(FW, {"family": "sincos", "a": 2, "b": 1, "k": 3, "at": "0"}, 1, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 6)
        self.assertIsNotNone(by_misconception(sol.steps[0], "cos-sign"))

    def test_level1_quarter_turn_point(self):
        p = {"family": "sincos", "a": 1, "b": 2, "k": 2, "at": "quarter"}
        ok, why, sol, _ = validate(FW, p, 1, None)
        self.assertTrue(ok, why)
        f = ed.trig_function(p)
        self.assertAlmostEqual(sol.steps[1].answer, float(sp.diff(f, x).subs(x, sp.pi / 4)))

    # Level 2: exponentials and logs -------------------------------------------------
    def test_level2_log_derivative_ignores_the_inside_constant(self):
        ok, why, sol, _ = validate(FW, {"family": "log", "c": 3, "m": 4, "b": 1}, 2, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 3 + 2)
        kept_k = by_misconception(sol.steps[0], "ln-kept-k")
        self.assertIsNotNone(kept_k)
        self.assertFalse(kept_k.correct)

    def test_level2_exp_chain(self):
        ok, why, sol, _ = validate(FW, {"family": "exp", "a": 2, "k": 3, "b": -1}, 2, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 5)

    # Level 3: inverse functions -----------------------------------------------------
    def test_level3_reciprocal_at_the_matching_input(self):
        ok, why, sol, _ = validate(FW, {"p": 1, "q": 0, "a": 1}, 3, None)      # f = x³ + x, f(1) = 2
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 4)
        self.assertEqual(correct(sol.steps[2]).value, "1/4")
        self.assertFalse(by_misconception(sol.steps[2], "wrong-point").correct)

    def test_level3_rejects_a_equal_to_b(self):
        ok, _, _, _ = validate(FW, {"p": 1, "q": -2, "a": 1}, 3, None)          # f(1) = 0? no: 1 + 1 − 2 = 0 ≠ 1
        ok2, _, _, _ = validate(FW, {"p": 2, "q": -2, "a": 1}, 3, None)         # f(1) = 1 = a
        self.assertFalse(ok2)

    # Level 4: inverse trig ----------------------------------------------------------
    def test_level4_values_match_sympy(self):
        for p in [{"family": "atan", "k": 2, "m": 3, "at": "one"}, {"family": "atan", "k": 1, "m": 2, "at": "zero"},
                  {"family": "asin", "k": 3, "m": 2, "at": "zero"}]:
            ok, why, sol, _ = validate(FW, p, 4, None)
            self.assertTrue(ok, why)
            f, point = ed.inverse_trig(p)
            self.assertAlmostEqual(sol.steps[1].answer, float(sp.diff(f, x).subs(x, point)))

    def test_no_sign_glitches_in_text(self):
        problems, _ = bank.build(FW, seed=1)
        # also: write ln (not log), arctan (not atan), and tan's derivative as sec², matching its distractors
        bad = re.compile(r"- -|\+ -|x - 0\b|\$(negative|positive)\$|\+ 0\b|\\log|operatorname|tan\^\{2\}")
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
