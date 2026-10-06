import re
import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import applications as ap

from functools import lru_cache

FW = ap.FRAMEWORK
x = ap.x


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


@lru_cache(maxsize=None)
def built():
    """Build the bank once per test run; several tests read it."""
    return bank.build(FW, seed=1)


class ApplicationsTest(unittest.TestCase):
    # Level 1: related rates ---------------------------------------------------------
    def test_level1_ladder_top_falls(self):
        ok, why, sol, _ = validate(FW, {"family": "ladder", "s": 2, "foot": 6, "rate": "2"}, 1, None)   # L = 10, x = 6, y = 8
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, -1.5)
        self.assertFalse(by_misconception(sol.steps[0], "forgot-chain-in-t").correct)
        self.assertIn("down", correct(sol.steps[2]).label)

    def test_level1_rectangle_product_rule(self):
        ok, why, sol, _ = validate(FW, {"family": "rectangle", "w": 4, "h": 3, "dw": "2", "dh": "1"}, 1, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, 2 * 3 + 4 * 1)

    # Level 2: linear approximation --------------------------------------------------
    def test_level2_sqrt_overestimates(self):
        ok, why, sol, _ = validate(FW, {"func": "sqrt", "a": 16, "d": "0.5"}, 2, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, 4.0625)
        self.assertEqual(correct(sol.steps[3]).value, "over")

    def test_level2_reciprocal_underestimates(self):
        ok, why, sol, _ = validate(FW, {"func": "recip", "a": 4, "d": "0.5"}, 2, None)
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[3]).value, "under")

    # Level 3: Mean Value Theorem ----------------------------------------------------
    def test_level3_cubic_c_is_not_the_midpoint(self):
        ok, why, sol, _ = validate(FW, {"family": "cubic", "p": 1, "b": 2}, 3, None)      # x³ + x on [−2, 4]: c = 2
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[2].answer, 2)
        self.assertNotAlmostEqual(sol.steps[2].answer, 1)

    def test_level3_c_inside_and_slope_matches(self):
        p = {"family": "quad", "p": 2, "q": -1, "r": 3, "a": -1, "w": 3}
        ok, why, sol, _ = validate(FW, p, 3, None)
        self.assertTrue(ok, why)
        f, a, b = ap.mvt_parts(p)
        c = sol.steps[2].answer
        self.assertTrue(a < c < b)
        self.assertAlmostEqual(float(sp.diff(f, x).subs(x, c)), float((f.subs(x, b) - f.subs(x, a)) / (b - a)))

    # Level 4: closed-interval extrema -----------------------------------------------
    def test_level4_endpoints_are_candidates_and_extremes_match_a_scan(self):
        p = {"p": 1, "q": 0, "lo": -2, "hi": 3}     # x³ − 3x on [−2, 3]: min −2 is a tie → rejected
        self.assertFalse(validate(FW, p, 4, None)[0])
        p = {"p": 1, "q": 1, "lo": -3, "hi": 3}     # x³ − 3x + 1 on [−3, 3]: values −17, 3, −1, 19
        ok, why, sol, _ = validate(FW, p, 4, None)
        self.assertTrue(ok, why)
        f = x**3 - 3 * x + 1
        grid = [f.subs(x, sp.Rational(k, 100)) for k in range(-300, 301)]
        self.assertAlmostEqual(sol.steps[1].answer, float(max(grid)))
        self.assertAlmostEqual(sol.steps[2].answer, float(min(grid)))
        self.assertIn("-3", correct(sol.steps[0]).label)

    # Level 5: curve sketching -------------------------------------------------------
    def test_level5_increasing_and_second_derivative_test(self):
        ok, why, sol, _ = validate(FW, {"a": 1, "r": -1, "s": 1, "d": 0}, 5, None)        # f' = 3(x + 1)(x − 1)
        self.assertTrue(ok, why)
        self.assertIn("x < -1", correct(sol.steps[0]).label)
        self.assertAlmostEqual(sol.steps[1].answer, 0)
        self.assertEqual(correct(sol.steps[2]).value, "max")
        ok, why, sol, _ = validate(FW, {"a": -1, "r": 0, "s": 2, "d": 1}, 5, None)
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[2]).value, "min")

    # Level 6: optimization ----------------------------------------------------------
    def test_level6_optimum_matches_sympy(self):
        for p, xs, best in [({"family": "river", "n": 100}, 25, 1250), ({"family": "box", "n": 12}, 2, 128),
                            ({"family": "sum", "n": 36}, 6, 12)]:
            ok, why, sol, _ = validate(FW, p, 6, None)
            self.assertTrue(ok, why)
            self.assertAlmostEqual(sol.steps[1].answer, xs)
            self.assertAlmostEqual(sol.steps[2].answer, best)

    # Level 7: L'Hôpital -------------------------------------------------------------
    def test_level7_not_indeterminate_means_substitute(self):
        ok, why, sol, _ = validate(FW, {"family": "plain", "k": 2, "m": 3, "n": 1}, 7, None)   # (cos x + 2)/(x + 3) → 1
        self.assertTrue(ok, why)
        self.assertEqual(correct(sol.steps[0]).value, "neither")
        self.assertFalse(by_misconception(sol.steps[1], "blind-lhopital").correct)

    def test_level7_quotient_rule_is_always_wrong(self):
        for p in [{"family": "exp", "k": 2, "m": 1, "n": 1}, {"family": "cos", "k": 3, "m": 1, "n": 1}, {"family": "ln", "k": 1, "m": 1, "n": 2},
                  {"family": "growth", "k": 1, "m": 1, "n": 3}]:
            ok, why, sol, _ = validate(FW, p, 7, None)
            self.assertTrue(ok, why)
            q = by_misconception(sol.steps[1], "quotient-rule-instead")
            self.assertIsNotNone(q, p)
            self.assertFalse(q.correct)
            f, point = ap.lhopital_parts(p)
            self.assertAlmostEqual(sol.steps[2].answer, float(sp.limit(f, x, point)))

    def test_no_text_glitches_and_no_coin_flips(self):
        problems, _ = built()
        bad = re.compile(r"(?<![\d.{])1 ?\\(sec|cos|sin|tan|sqrt)|\{1\\(cos|sin)|- -|\+ -|x - 0\b|\$(negative|positive)\$|\+ 0\b|\\log|operatorname")
        for level, items in problems.items():
            for p in items:
                for st in p["steps"]:
                    if st["format"] == "choice":
                        self.assertGreaterEqual(len(st["options"]), 3, f"L{level} {p['id']}: {st['prompt']}")
                texts = [p["story"]] + [t for st in p["steps"] for t in [st["prompt"], st.get("explain", "")] +
                                        [o.get("feedback", "") for o in st.get("options", [])] + [o["label"] for o in st.get("options", [])]]
                for t in texts:
                    self.assertIsNone(bad.search(t), f"L{level} {p['id']}: {t}")

    def test_scene_text_is_clean_and_balanced(self):
        problems, _ = built()
        for level, items in problems.items():
            for p in items:
                for t in [p["scene"].get("tex", ""), p["scene"].get("rule", ""), p["story"]] + [st["prompt"] for st in p["steps"]]:
                    stripped = t.replace("\\left(", "").replace("\\right)", "")
                    self.assertEqual(stripped.count("("), stripped.count(")"), f"L{level} {p['id']}: {t}")
                    self.assertEqual(t.count("{"), t.count("}"), f"L{level} {p['id']}: {t}")

    def test_no_two_problems_read_the_same(self):
        problems, _ = built()
        for level, items in problems.items():
            texts = [p["story"] + "|".join(st["prompt"] for st in p["steps"]) for p in items]
            self.assertEqual(len(texts), len(set(texts)), f"L{level} repeats a problem")

    def test_level7_growth_family_is_shown_as_a_fraction(self):
        ok, why, sol, _ = validate(FW, {"family": "growth", "k": 1, "m": 0, "n": 2}, 7, None)
        self.assertTrue(ok, why)
        self.assertIn("\\frac", sol.story)
        self.assertIn("2", sol.steps[2].explain)          # the rule is applied twice

    def test_level4_outside_point_distractor_appears(self):
        problems, _ = built()
        names = {o.get("misconception") for p in problems[4] for o in p["steps"][0]["options"]}
        self.assertIn("outside-point", names)

    def test_level4_max_explain_doesnt_give_away_the_min(self):
        ok, why, sol, _ = validate(FW, {"p": 1, "q": 1, "lo": -3, "hi": 3}, 4, None)
        self.assertTrue(ok, why)
        self.assertNotIn("-17", sol.steps[1].explain)

    def test_level1_units_come_before_the_number(self):
        ok, why, sol, _ = validate(FW, {"family": "cube", "edge": 3, "rate": "0.5"}, 1, None)
        self.assertTrue(ok, why)
        self.assertEqual(sol.steps[1].format, "choice")
        self.assertNotIn("cm³/s", sol.steps[2].prompt)

    def test_level2_true_value_held_back_and_decimals_stated(self):
        ok, why, sol, _ = validate(FW, {"func": "sqrt", "a": 16, "d": "0.5"}, 2, None)
        self.assertTrue(ok, why)
        self.assertNotIn("true value", sol.steps[2].explain)
        self.assertIn("4 decimal places", sol.steps[2].prompt)

    def test_level2_verdicts_are_mixed(self):
        from collections import Counter
        problems, _ = built()
        verdicts = Counter(next(o["value"] for o in p["steps"][3]["options"] if o["correct"]) for p in problems[2])
        self.assertGreaterEqual(min(verdicts["over"], verdicts["under"]), 35, verdicts)

    def test_level6_distractors_keep_their_shape(self):
        for p in [{"family": "split", "n": 10}, {"family": "sum", "n": 64}]:
            ok, why, sol, _ = validate(FW, p, 6, None)
            self.assertTrue(ok, why)
            for o in sol.steps[0].options:
                self.assertIsNone(re.search(r"= -?\d+\$$", o.label), o.label)
                self.assertIsNone(re.search(r"= \d+ x\$$", o.label), o.label)

    def test_bank(self):
        problems, report = built()
        for level in FW.levels:
            self.assertGreaterEqual(len(problems[level]), 100, report["levels"][str(level)])


if __name__ == "__main__":
    unittest.main()
