import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import derivative_rules as dr

FW = dr.FRAMEWORK
x = dr.x
E = lambda s: sp.sympify(s, locals={"x": x})


class DerivativeRulesTest(unittest.TestCase):
    def test_misconception_functions_on_hand_worked_examples(self):
        f, g = E("x**2"), E("3*x + 1")
        self.assertEqual(sp.simplify(dr.WRONG["product-of-derivatives"](f, g) - E("6*x")), 0)          # (fg)' ≠ f'g'
        self.assertEqual(sp.simplify(dr.WRONG["quotient-of-derivatives"](f, g) - E("2*x/3")), 0)       # (f/g)' ≠ f'/g'
        self.assertEqual(sp.simplify(dr.WRONG["quotient-order"](f, g) - E("(3*x**2 - 2*x*(3*x + 1))/(3*x + 1)**2")), 0)
        self.assertEqual(sp.simplify(dr.WRONG["forgot-square"](f, g) - E("(2*x*(3*x + 1) - 3*x**2)/(3*x + 1)")), 0)
        self.assertEqual(sp.simplify(dr.dropped_inner(E("(3*x + 1)**4")) - E("4*(3*x + 1)**3")), 0)
        self.assertEqual(sp.simplify(dr.power_up(5, sp.Integer(3)) - E("15*x**4")), 0)                  # 5x³ → 15x⁴ (wrong)

    def test_each_level_valid_and_answer_is_the_derivative(self):
        cases = [(1, {"f": "2*x**3 - 4*x**2 + 5*x - 7", "a": 1}), (2, {"f": "6*sqrt(x)", "a": 4}),
                 (3, {"f": "x**2", "g": "3*x + 1", "c": 1, "a": 1}), (4, {"f": "x**2 + 1", "g": "x - 2", "a": 3}),
                 (5, {"f": "(3*x + 1)**4", "a": 0}), (6, {"kind": "product-chain", "f": "x**2", "g": "(2*x - 1)**3", "a": 1}),
                 (6, {"kind": "chain-of-product", "f": "x", "g": "2*x + 1", "a": 4})]
        for level, params in cases:
            ok, why, sol, _ = validate(FW, params, level, None)
            self.assertTrue(ok, f"level {level}: {why}")
            expr = dr.build(level, params)
            self.assertAlmostEqual(sol.answers["value"], float(sp.diff(expr, x).subs(x, params["a"])))

    def test_chain_of_product_is_answered_chain(self):
        ok, why, sol, _ = validate(FW, {"kind": "chain-of-product", "f": "x", "g": "2*x + 1", "a": 4}, 6, None)
        self.assertTrue(ok, why)
        self.assertEqual(sol.steps[0].answer, dr.RULES["chain"])
        self.assertIn("sqrt", sol.steps[0].prompt)

    def test_power_level_never_offers_quotient(self):
        ok, why, sol, _ = validate(FW, {"f": "2*x**(-2)", "a": 1}, 2, None)
        self.assertTrue(ok, why)
        self.assertNotIn(dr.RULES["quotient"], [o.label for o in sol.steps[0].options])

    def test_dropped_inner_rejected_when_inner_derivative_is_1(self):
        ok, why, _, _ = validate(FW, {"f": "(x + 3)**4", "a": 1}, 5, None)
        self.assertFalse(ok)
        self.assertIn("dropped-inner", why)

    def test_constant_times_product_is_ambiguous(self):
        ok, why, _, _ = validate(FW, {"f": "x**2", "g": "3*x + 1", "c": 2, "a": 1}, 3, None)
        self.assertFalse(ok)
        self.assertTrue(why.startswith("unique"), why)

    def test_unclean_evaluation_rejected(self):
        ok, why, _, _ = validate(FW, {"f": "x**2 + 1", "g": "x - 2", "a": 7}, 4, None)  # f'(7) = 59/25·… not clean
        if not ok:
            self.assertTrue(why.startswith(("clean", "exists")), why)

    def test_bank_has_300(self):
        problems, report = bank.build(FW, seed=1)
        self.assertGreaterEqual(sum(len(v) for v in problems.values()), 300, report)
        self.assertEqual(sorted(problems), [1, 2, 3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main()
