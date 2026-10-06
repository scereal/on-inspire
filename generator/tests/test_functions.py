import re
import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import functions as fn

from functools import lru_cache

FW = fn.FRAMEWORK
x = fn.x


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


@lru_cache(maxsize=None)
def built():
    """Build the bank once per test run; several tests read it."""
    return bank.build(FW, seed=1)


class FunctionsTest(unittest.TestCase):
    # Level 1: domain ----------------------------------------------------------------
    def test_level1_root_allows_zero_and_log_does_not(self):
        ok, why, sol, _ = validate(FW, {"family": "sqrt", "a": 1, "b": -2, "q": 0}, 1, None)
        self.assertTrue(ok, why)
        self.assertIn("\\ge 2", correct(sol.steps[1]).label)
        ok, why, sol, _ = validate(FW, {"family": "ln", "a": 1, "b": -2, "q": 0}, 1, None)
        self.assertTrue(ok, why)
        self.assertIn("> 2", correct(sol.steps[1]).label)

    def test_level1_negative_coefficient_flips(self):
        ok, why, sol, _ = validate(FW, {"family": "sqrt", "a": -2, "b": 6, "q": 0}, 1, None)     # √(6 − 2x): x ≤ 3
        self.assertTrue(ok, why)
        self.assertIn("\\le 3", correct(sol.steps[1]).label)
        self.assertIsNotNone(by_misconception(sol.steps[1], "forgot-to-flip"))

    def test_level1_combo_excludes_the_zero_of_the_bottom(self):
        ok, why, sol, _ = validate(FW, {"family": "combo", "a": 1, "b": -2, "q": 5}, 1, None)
        self.assertTrue(ok, why)
        self.assertIn("5", correct(sol.steps[1]).label)

    # Level 2: composition -----------------------------------------------------------
    def test_level2_values_and_order(self):
        ok, why, sol, _ = validate(FW, {"a": 2, "b": 1, "c": 1, "d": 0, "t": 3}, 2, None)          # f = 2x + 1, g = x²
        self.assertTrue(ok, why)
        self.assertEqual((sol.steps[0].answer, sol.steps[1].answer), (9, 19))
        self.assertFalse(by_misconception(sol.steps[2], "order-swapped").correct)

    # Level 3: inverses --------------------------------------------------------------
    def test_level3_inverse_round_trips_and_reciprocal_is_wrong(self):
        for p in [{"family": "linear", "a": 2, "b": 3, "d": 0, "u": 1}, {"family": "cube", "a": 1, "b": -2, "d": 0, "u": 2},
                  {"family": "mobius", "a": 2, "b": 1, "d": 3, "u": 1}]:
            ok, why, sol, _ = validate(FW, p, 3, None)
            self.assertTrue(ok, why)
            f = fn.inverse_function(p)
            inv = fn.inverse_formula(p)
            self.assertEqual(sp.simplify(f.subs(x, inv) - x), 0, p)
            self.assertFalse(by_misconception(sol.steps[0], "inverse-is-reciprocal").correct)
            self.assertAlmostEqual(sol.steps[1].answer, p["u"])

    def test_level3_rejects_self_inverse(self):
        self.assertFalse(validate(FW, {"family": "linear", "a": -1, "b": 4, "d": 0, "u": 1}, 3, None)[0])
        self.assertFalse(validate(FW, {"family": "mobius", "a": 2, "b": 1, "d": -2, "u": 1}, 3, None)[0])

    # Level 4: transformations ------------------------------------------------------
    def test_level4_shift_right_is_x_minus_h(self):
        ok, why, sol, _ = validate(FW, {"base": "square", "a": "1", "h": 3, "k": 2, "t": 1}, 4, None)
        self.assertTrue(ok, why)
        self.assertIn("(x - 3)^2", correct(sol.steps[0]).label)
        self.assertFalse(by_misconception(sol.steps[0], "shift-sign").correct)
        self.assertAlmostEqual(sol.steps[1].answer, 1 + 2)                 # g(h + t) = a·t² + k

    def test_level4_value_matches_the_formula(self):
        p = {"base": "sqrt", "a": "-2", "h": -1, "k": 3, "t": 4}
        ok, why, sol, _ = validate(FW, p, 4, None)
        self.assertTrue(ok, why)
        g = fn.transformed(p)
        self.assertAlmostEqual(sol.steps[1].answer, float(g.subs(x, p["h"] + p["t"])))

    # Level 5: exponential and log equations ------------------------------------------
    def test_level5_exponential_equation(self):
        ok, why, sol, _ = validate(FW, {"family": "exp", "b": 2, "p": 1, "q": 1, "x0": 4, "d": 0}, 5, None)   # 2^(x+1) = 32
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 4)

    def test_level5_extraneous_root_is_never_correct(self):
        ok, why, sol, _ = validate(FW, {"family": "log", "b": 2, "p": 0, "q": 0, "x0": 4, "d": 2}, 5, None)   # x(x − 2) = 8
        self.assertTrue(ok, why)
        self.assertIn("x = 4", correct(sol.steps[1]).label)
        self.assertNotIn("-2", correct(sol.steps[1]).label)
        self.assertFalse(by_misconception(sol.steps[1], "kept-extraneous").correct)

    # Level 6: exact trig values -------------------------------------------------------
    def test_level6_value_and_sign_match_sympy(self):
        for p in [{"func": "sin", "num": 5, "den": 6}, {"func": "cos", "num": 3, "den": 4}, {"func": "tan", "num": 4, "den": 3}]:
            ok, why, sol, _ = validate(FW, p, 6, None)
            self.assertTrue(ok, why)
            v = getattr(sp, p["func"])(sp.pi * p["num"] / p["den"])
            self.assertEqual(correct(sol.steps[1]).value, sp.sstr(sp.nsimplify(v)))
            self.assertIn("positive" if v > 0 else "negative", correct(sol.steps[0]).label)

    # Shared lessons -----------------------------------------------------------------
    def test_bank_text_is_clean(self):
        problems, _ = built()
        bad = re.compile(r"(?<![\d.{])1 ?\\(sec|cos|sin|tan|sqrt)|\{1\\(cos|sin)|- -|\+ -|x - 0\b|\$(negative|positive)\$|\+ 0\b|\\log(?!_)|operatorname")
        for level, items in problems.items():
            texts_seen = set()
            for p in items:
                key = p["story"] + "|".join(st["prompt"] for st in p["steps"])
                self.assertNotIn(key, texts_seen, f"L{level} repeats {p['id']}")
                texts_seen.add(key)
                for st in p["steps"]:
                    if st["format"] == "choice":
                        self.assertGreaterEqual(len(st["options"]), 3, f"L{level} {p['id']}: {st['prompt']}")
                texts = [p["story"], p["scene"].get("tex", ""), p["scene"].get("rule", "")] + [
                    t for st in p["steps"] for t in [st["prompt"], st.get("explain", "")] +
                    [o.get("feedback", "") for o in st.get("options", [])] + [o["label"] for o in st.get("options", [])]]
                for t in texts:
                    self.assertIsNone(bad.search(t), f"L{level} {p['id']}: {t}")
                    plain = t.replace("\\left(", "").replace("\\right)", "")
                    self.assertEqual(plain.count("("), plain.count(")"), f"L{level} {p['id']}: {t}")
                    self.assertEqual(t.count("{"), t.count("}"), f"L{level} {p['id']}: {t}")

    def test_bank(self):
        problems, report = built()
        for level in FW.levels:
            self.assertGreaterEqual(len(problems[level]), 100, report["levels"][str(level)])


if __name__ == "__main__":
    unittest.main()
