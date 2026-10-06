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

    # Pattern giveaways and repeats (unit 140.1 review) ---------------------------------
    def test_level5_power_answer_is_not_always_the_middle(self):
        problems, _ = built()
        exps = []
        for p in problems[5]:
            if p["params"]["family"] != "exp":
                continue
            opts = p["steps"][0]["options"]
            vals = sorted(int(re.search(r"\^\{(-?\d+)\}", o["label"]).group(1)) for o in opts)
            right = int(re.search(r"\^\{(-?\d+)\}", next(o for o in opts if o["correct"])["label"]).group(1))
            exps.append(right == vals[1])
        self.assertLess(sum(exps) / len(exps), 0.6, f"{sum(exps)}/{len(exps)} have the answer in the middle")

    def test_level6_correct_quadrant_is_not_the_repeated_one(self):
        problems, _ = built()
        for p in problems[6]:
            quads = [re.match(r"Quadrant (\w+)", o["label"]).group(1) for o in p["steps"][0]["options"]]
            self.assertEqual(len(set(quads)), 3, f"{p['id']}: {quads}")

    def test_level1_domain_answer_is_not_always_the_median(self):
        problems, _ = built()
        med = tot = 0
        for p in problems[1]:
            if p["params"]["family"] not in ("sqrt", "ln"):
                continue
            feats = []
            for o in p["steps"][1]["options"]:
                m = re.search(r"x (\\ge|\\le|>|<) (.+)\$", o["label"])
                feats.append(((m.group(1) in ("\\ge", ">")), (m.group(1) in ("\\ge", "\\le")), m.group(2), o["correct"]))
            right = next(f for f in feats if f[3]); wrong = [f for f in feats if not f[3]]
            share = lambda u, v: u[0] == v[0] or u[1] == v[1]       # direction or strictness (all share the boundary)
            tot += 1
            med += share(right, wrong[0]) and share(right, wrong[1]) and not share(wrong[0], wrong[1])
        self.assertLess(med / tot, 0.6, f"{med}/{tot} answers are the median option")

    def test_level2_answer_is_not_always_the_shortest(self):
        problems, _ = built()
        terms = lambda lbl: len(re.findall(r"(?<!^)(?<![\^{(])[+-]", lbl.strip("$").strip()))
        short = 0
        for p in problems[2]:
            opts = p["steps"][2]["options"]
            n = {o["label"]: terms(o["label"]) for o in opts}
            right = next(o["label"] for o in opts if o["correct"])
            short += all(n[right] < n[o["label"]] for o in opts if not o["correct"])
        self.assertLess(short / len(problems[2]), 0.6, f"{short} answers are uniquely the shortest")

    def test_no_repeated_stories_in_levels_2_to_4(self):
        problems, _ = built()
        for level in (2, 3, 4):
            stories = [p["story"] for p in problems[level]]
            self.assertEqual(len(stories), len(set(stories)), f"L{level} repeats a story")

    def test_bank(self):
        problems, report = built()
        for level in FW.levels:
            self.assertGreaterEqual(len(problems[level]), 100, report["levels"][str(level)])


if __name__ == "__main__":
    unittest.main()
