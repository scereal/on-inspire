import re
import unittest
from functools import lru_cache

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import antiderivatives as ad

FW = ad.FRAMEWORK
x, t = ad.x, ad.t


@lru_cache(maxsize=None)
def built():
    """Build the bank once per test run; several tests read it."""
    return bank.build(FW, seed=1)


def correct(step):
    return next(o for o in step.options if o.correct)


def by_misconception(step, name):
    return next((o for o in step.options if o.misconception == name), None)


class AntiderivativesTest(unittest.TestCase):
    def test_level1_power_rule_backwards(self):
        ok, why, sol, _ = validate(FW, {"terms": [[3, "2"], [4, "1"], [-5, "0"]], "a": 1, "b": 2}, 1, None)
        self.assertTrue(ok, why)
        self.assertIn("+ C", correct(sol.steps[0]).label)
        self.assertAlmostEqual(sol.steps[1].answer, 8)                    # (8 + 8 − 10) − (1 + 2 − 5)
        for o in sol.steps[0].options:
            self.assertIn("+ C", o.label)                                 # + C never gives the answer away

    def test_level1_never_offers_x_to_the_minus_one(self):
        self.assertFalse(validate(FW, {"terms": [[2, "-1"], [1, "1"]], "a": 1, "b": 2}, 1, None)[0])

    def test_level2_chain_in_reverse_divides_by_k(self):
        ok, why, sol, _ = validate(FW, {"family": "trig", "a": 2, "b": 0, "k": 3, "c": 0}, 2, None)
        self.assertTrue(ok, why)
        self.assertIn("\\frac{2 \\sin{\\left(3 x \\right)}}{3}", correct(sol.steps[0]).label)
        self.assertFalse(by_misconception(sol.steps[0], "multiplied-by-k").correct)
        self.assertAlmostEqual(sol.steps[1].answer, 2 / 3)

    def test_level2_values_match_sympy(self):
        for p in [{"family": "trig", "a": 1, "b": 2, "k": 2, "c": 0}, {"family": "exp", "a": 3, "b": 0, "k": 2, "c": 0},
                  {"family": "sec", "a": 0, "b": 0, "k": 1, "c": 4}]:
            ok, why, sol, _ = validate(FW, p, 2, None)
            self.assertTrue(ok, why)
            f, x1 = ad.basic_parts(p)
            F = sp.integrate(f, x)
            self.assertAlmostEqual(sol.steps[1].answer, float(F.subs(x, x1) - F.subs(x, 0)))

    def test_level2_sec_squared_answer_written_as_tan(self):
        ok, why, sol, _ = validate(FW, {"family": "sec", "a": 0, "b": 0, "k": 1, "c": -5}, 2, None)
        self.assertTrue(ok, why)
        self.assertIn("\\tan", correct(sol.steps[0]).label)

    def test_level3_ivp_uses_the_point(self):
        ok, why, sol, _ = validate(FW, {"a": 6, "b": 0, "c": -2, "x0": 1, "y0": 5, "x1": 2}, 3, None)   # f = 2x³ − 2x + 5
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 5)
        self.assertAlmostEqual(sol.steps[2].answer, 17)

    def test_level3_rejects_c_zero(self):
        self.assertFalse(validate(FW, {"a": 6, "b": 0, "c": -2, "x0": 1, "y0": 0, "x1": 2}, 3, None)[0])

    def test_level4_motion(self):
        ok, why, sol, _ = validate(FW, {"a0": -10, "j": 0, "v0": 15, "s0": 2, "T": 1}, 4, None)
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.steps[1].answer, 5)
        self.assertAlmostEqual(sol.steps[2].answer, 2 + 15 - 5)
        self.assertFalse(by_misconception(sol.steps[0], "forgot-v0").correct)

    def test_answers_are_not_findable_by_shape(self):
        problems, _ = built()
        terms = lambda lbl: len(re.findall(r"(?<![\^{(])\s[+-]\s", lbl))
        for level, items in problems.items():
            short = 0
            for p in items:
                opts = p["steps"][0]["options"]
                n = {o["label"]: terms(o["label"]) for o in opts}
                right = next(o["label"] for o in opts if o["correct"])
                short += all(n[right] < n[o["label"]] for o in opts if not o["correct"])
            self.assertLess(short / len(items), 0.6, f"L{level}: {short} answers are uniquely the shortest")

    def test_bank_text_is_clean(self):
        problems, _ = built()
        bad = re.compile(r"(?<![\d.{])1 ?\\(sec|cos|sin|tan|sqrt)|\{1\\(cos|sin)|- -|\+ -|x - 0\b|\$(negative|positive)\$|\+ 0\b|\\log(?!_)|operatorname")
        for level, items in problems.items():
            stories = [p["story"] for p in items]
            self.assertEqual(len(stories), len(set(stories)), f"L{level} repeats a story")
            for p in items:
                for st in p["steps"]:
                    if st["format"] == "choice":
                        self.assertGreaterEqual(len(st["options"]), 3, f"L{level} {p['id']}")
                texts = [p["story"], p["scene"].get("tex", ""), p["scene"].get("rule", "")] + [
                    tx for st in p["steps"] for tx in [st["prompt"], st.get("explain", "")] +
                    [o.get("feedback", "") for o in st.get("options", [])] + [o["label"] for o in st.get("options", [])]]
                for tx in texts:
                    self.assertIsNone(bad.search(tx), f"L{level} {p['id']}: {tx}")
                    plain = tx.replace("\\left(", "").replace("\\right)", "")
                    self.assertEqual(plain.count("("), plain.count(")"), f"L{level} {p['id']}: {tx}")
                    self.assertEqual(tx.count("{"), tx.count("}"), f"L{level} {p['id']}: {tx}")

    def test_bank(self):
        problems, report = built()
        for level in FW.levels:
            self.assertGreaterEqual(len(problems[level]), 100, report["levels"][str(level)])


if __name__ == "__main__":
    unittest.main()
