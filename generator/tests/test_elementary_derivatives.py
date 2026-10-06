import re
import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import elementary_derivatives as ed

from functools import lru_cache

FW = ed.FRAMEWORK
x = ed.x


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


@lru_cache(maxsize=None)
def built():
    """Build the bank once per test run; several tests read it."""
    return bank.build(FW, seed=1)


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
        opt = by_misconception(sol.steps[2], "wrong-point")
        self.assertTrue(opt is None or not opt.correct)

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

    # Level 5: implicit differentiation -------------------------------------------------
    def test_level5_point_on_curve_and_slope_matches_idiff(self):
        y = sp.Symbol("y")
        for p in [{"family": "circle", "r": 5, "px": 3, "py": 4}, {"family": "hyperbola", "c": 6, "px": 2, "py": 3},
                  {"family": "mixed", "px": 1, "py": 2}]:
            ok, why, sol, _ = validate(FW, p, 5, None)
            self.assertTrue(ok, why)
            curve = ed.implicit_curve(p)
            self.assertEqual(curve.subs({x: p["px"], y: p["py"]}), 0)
            slope = sp.idiff(curve, y, x).subs({x: p["px"], y: p["py"]})
            self.assertAlmostEqual(sol.steps[2].answer, float(slope))
            for name in ("forgot-chain-on-y", "treated-y-as-x", "chain-dropped-outer", "dropped-x-factor", "extra-chain-on-x"):
                slip = by_misconception(sol.steps[0], name)
                self.assertTrue(slip is None or not slip.correct, name)

    def test_level5_rejects_points_off_the_curve(self):
        ok, _, _, _ = validate(FW, {"family": "circle", "r": 5, "px": 3, "py": 3}, 5, None)
        self.assertFalse(ok)

    # Level 6: logarithmic differentiation ----------------------------------------------
    def test_level6_power_family_value(self):
        ok, why, sol, _ = validate(FW, {"family": "power", "a": 1, "b": 2, "c": 0}, 6, None)   # y = x^(x² + 2x)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, 3)
        opt = by_misconception(sol.steps[1], "forgot-y")
        self.assertTrue(opt is None or not opt.correct)

    def test_level6_product_family_matches_sympy(self):
        p = {"family": "quotient", "a": 2, "b": 1, "c": 1}
        ok, why, sol, _ = validate(FW, p, 6, None)
        self.assertTrue(ok, why)
        f = ed.log_diff_function(p)
        self.assertAlmostEqual(sol.steps[2].answer, float(sp.diff(f, x).subs(x, 1)))

    # Level 7: higher derivatives -------------------------------------------------------
    def test_level7_concavity_follows_the_second_derivative(self):
        ok, why, sol, _ = validate(FW, {"a": 1, "b": -6, "c": 2, "d": 1, "t0": 1}, 7, None)   # s'' = 6t − 12 → −6 at t = 1
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, -6)
        self.assertIn("down", correct(sol.steps[3]).label)

    def test_level7_rejects_an_inflection_point(self):
        ok, _, _, _ = validate(FW, {"a": 1, "b": -6, "c": 2, "d": 1, "t0": 2}, 7, None)        # s''(2) = 0
        self.assertFalse(ok)

    def test_level7_acceleration_written_like_its_distractors(self):
        ok, why, sol, _ = validate(FW, {"a": 1, "b": -1, "c": 5, "d": 0, "t0": 4}, 7, None)
        self.assertTrue(ok, why)
        self.assertNotIn("left(", correct(sol.steps[1]).label)

    def test_level5_circle_offers_two_wrong_options(self):
        ok, why, sol, _ = validate(FW, {"family": "circle", "r": 5, "px": 3, "py": 4}, 5, None)
        self.assertTrue(ok, why)
        self.assertEqual(len(sol.steps[0].options), 3)

    def test_level6_take_logs_offers_two_wrong_options(self):
        for p in [{"family": "product", "a": 2, "b": 1, "c": 1}, {"family": "power", "a": 1, "b": 2, "c": 0}]:
            ok, why, sol, _ = validate(FW, p, 6, None)
            self.assertTrue(ok, why)
            self.assertEqual(len(sol.steps[0].options), 3, p)

    def test_level5_hyperbola_feedback_talks_about_xy(self):
        ok, why, sol, _ = validate(FW, {"family": "hyperbola", "c": 6, "px": 2, "py": 3}, 5, None)
        self.assertTrue(ok, why)
        for o in sol.steps[0].options:
            if not o.correct:
                self.assertNotIn("y^2", o.feedback, o.label)
                self.assertIn("xy", o.feedback.replace(" ", ""), o.label)

    def test_level1_tan_sign_feedback_matches_a_negative_coefficient(self):
        ok, why, sol, _ = validate(FW, {"family": "tan", "c": -2, "k": 1, "at": "0"}, 1, None)
        self.assertTrue(ok, why)
        fb = by_misconception(sol.steps[0], "tan-sign").feedback
        self.assertIn("-2", fb)

    def test_level1_no_unit_coefficient_in_labels(self):
        ok, why, sol, _ = validate(FW, {"family": "tan", "c": 1, "k": 1, "at": "0"}, 1, None)
        self.assertTrue(ok, why)
        self.assertIsNone(re.search(r"(?<![\d.])1 \\sec", correct(sol.steps[0]).label), correct(sol.steps[0]).label)

    def test_steps_never_fall_to_a_coin_flip(self):
        self.assertFalse(validate(FW, {"family": "product", "a": 1, "b": 1, "c": 1}, 6, None)[0])
        self.assertFalse(validate(FW, {"a": 1, "b": 0, "c": 2, "d": 1, "t0": 1}, 7, None)[0])

    def test_rotated_mistakes_still_appear_in_the_bank(self):
        problems, _ = built()
        names = lambda level, step: {o.get("misconception") for p in problems[level] for o in p["steps"][step]["options"]}
        self.assertIn("wrong-point", names(3, 2))
        self.assertIn("forgot-y", names(6, 1))
        self.assertIn("forgot-chain-on-y", names(5, 0))

    def test_no_sign_glitches_in_text(self):
        problems, _ = built()
        # also: write ln (not log), arctan (not atan), and tan's derivative as sec², matching its distractors
        bad = re.compile(r"(?<![\d.])1 \\(sec|cos|sin|tan)|- -|\+ -|x - 0\b|\$(negative|positive)\$|\+ 0\b|\\log|operatorname|tan\^\{2\}")
        for level, items in problems.items():
            for p in items:
                texts = [p["story"]] + [t for st in p["steps"] for t in [st["prompt"], st.get("explain", "")] +
                                        [o.get("feedback", "") for o in st.get("options", [])] + [o["label"] for o in st.get("options", [])]]
                for t in texts:
                    self.assertIsNone(bad.search(t), f"L{level} {p['id']}: {t}")

    def test_bank(self):
        problems, report = built()
        for level in FW.levels:
            self.assertGreaterEqual(len(problems[level]), 100, report["levels"][str(level)])


if __name__ == "__main__":
    unittest.main()
