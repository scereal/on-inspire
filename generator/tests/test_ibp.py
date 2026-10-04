import unittest

import sympy as sp

from generator.core import bank
from generator.core.validators import validate
from generator.frameworks import ibp

FW = ibp.FRAMEWORK
x = ibp.x


class IbpTest(unittest.TestCase):
    def run_one(self, level, **params):
        return validate(FW, params, level, None)

    def test_level1_valid_and_answer_differentiates_back(self):
        ok, why, sol, _ = self.run_one(1, g="sin", a="2", c=3)
        self.assertTrue(ok, why)
        F = sp.sympify(sol.answers["F"], locals={"x": x})
        self.assertEqual(sp.simplify(sp.diff(F, x) - 3 * x * sp.sin(2 * x)), 0)

    def test_level1_a_equal_1_rejected(self):
        ok, why, _, _ = self.run_one(1, g="cos", a="1", c=2)
        self.assertFalse(ok)
        self.assertIn("dropped-1-over-a", why)

    def test_level2_rounds_equal_degree(self):
        for n in (2, 3):
            ok, why, sol, _ = self.run_one(2, g="exp", a="2", c=1, n=n)
            self.assertTrue(ok, why)
            self.assertEqual(sol.answers["rounds"], n)
            self.assertEqual(ibp.rounds_needed(x**n * sp.exp(2 * x)), n)

    def test_level3_loop_coefficient(self):
        ok, why, sol, _ = self.run_one(3, t="sin", a=2, b=3, c=1)
        self.assertTrue(ok, why)
        self.assertEqual(sp.Rational(sol.answers["k"]), sp.Rational(-9, 4))
        self.assertFalse(any("Which choice of u" in s.prompt for s in sol.steps))

    def test_level4_polynomial_u_does_not_finish(self):
        self.assertFalse(ibp.finishes(x**2 * sp.log(x), x**2))
        self.assertTrue(ibp.finishes(x**2 * sp.log(x), sp.log(x)))
        ok, why, _, _ = self.run_one(4, n=2, k=1, c=1)
        self.assertTrue(ok, why)

    def test_every_distractor_is_wrong(self):
        for level, params in [(1, dict(g="exp", a="3", c=1)), (2, dict(g="sin", a="2", c=1, n=2)),
                              (3, dict(t="cos", a=1, b=2, c=1)), (4, dict(n=1, k=2, c=1))]:
            ok, why, sol, _ = self.run_one(level, **params)
            self.assertTrue(ok, f"level {level}: {why}")
            f = ibp.integrand(level, params)
            final = sol.steps[-1]
            for o in final.options:
                w = sp.sympify(o.value, locals={"x": x})
                is_right = sp.simplify(sp.diff(w, x) - f) == 0
                self.assertEqual(is_right, o.correct, f"level {level}: {o.label}")

    def test_bank_has_300_across_all_levels(self):
        problems, report = bank.build(FW, seed=1)
        self.assertGreaterEqual(sum(len(v) for v in problems.values()), 300, report)
        self.assertEqual(sorted(problems), [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
