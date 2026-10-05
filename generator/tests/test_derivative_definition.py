import unittest

import sympy as sp

from generator.core import bank
from generator.core.themes import load_themes
from generator.core.validators import validate
from generator.frameworks import derivative_definition as dd

FW = dd.FRAMEWORK
THEMES = {t["id"]: t for t in load_themes("derivative-definition")}
x, h = dd.x, dd.h


class DerivativeDefinitionTest(unittest.TestCase):
    def test_level1_rate_story(self):
        ok, why, sol, _ = validate(FW, {"a": "49/10", "b": 0, "c": 0, "t1": 2, "t2": 4}, 1, THEMES["falling-ball"])
        self.assertTrue(ok, why)
        self.assertAlmostEqual(sol.answers["instant"], 19.6)
        self.assertAlmostEqual(sol.answers["average"], 29.4)

    def test_level1_scene_carries_a_drawable_curve(self):
        # the page can't evaluate SymPy strings, so the scene ships the formula as TeX and sampled points
        _, _, sol, _ = validate(FW, {"a": "49/10", "b": 0, "c": 0, "t1": 2, "t2": 4}, 1, THEMES["falling-ball"])
        scene = sol.scene
        self.assertEqual(scene["type"], "rate")
        self.assertIn("tex", scene)
        ts = [pt[0] for pt in scene["curve"]]
        self.assertLessEqual(min(ts), 0)
        self.assertGreaterEqual(max(ts), 4)
        for t_val, y in scene["curve"]:
            self.assertAlmostEqual(y, 4.9 * t_val ** 2, places=6)
        self.assertAlmostEqual(scene["y1"], 19.6)
        self.assertAlmostEqual(scene["y2"], 78.4)

    def test_level1_quantity_never_turns_around_on_the_graph(self):
        # T = t²/2 − 4t + 85 bottoms out at t = 4: over [4, 6] the coffee would warm up by itself
        ok, why, _, _ = validate(FW, {"a": "1/2", "b": -4, "c": 85, "t1": 4, "t2": 6}, 1, THEMES["cooling-coffee"])
        self.assertFalse(ok)
        self.assertIn("rate", why)

    def test_level1_one_unit_interval_rejected(self):
        # over [2, 3] the change (24.5 m) equals the rate (24.5 m/s): the change-not-rate mistake is invisible
        ok, why, _, _ = validate(FW, {"a": "49/10", "b": 0, "c": 0, "t1": 2, "t2": 3}, 1, THEMES["falling-ball"])
        self.assertFalse(ok)
        self.assertIn("change-not-rate", why)

    def test_level2_difference_quotient_limit_is_the_derivative(self):
        for params in [{"kind": "quad", "a": 2, "b": -3, "c": 1, "p": 2}, {"kind": "cubic", "a": 1, "b": 2, "c": 0, "p": -1}]:
            f = dd.poly(params)
            q = sp.simplify((f.subs(x, params["p"] + h) - f.subs(x, params["p"])) / h)
            self.assertEqual(sp.limit(q, h, 0), sp.diff(f, x).subs(x, params["p"]))
            ok, why, sol, _ = validate(FW, params, 2, None)
            self.assertTrue(ok, why)

    def test_level2_rejects_when_early_substitution_looks_right(self):
        # f'(p) = 0 at the vertex: the "plug in h = 0 first, get 0" mistake would give the right number
        ok, why, _, _ = validate(FW, {"kind": "quad", "a": 1, "b": -4, "c": 0, "p": 2}, 2, None)
        self.assertFalse(ok)
        self.assertIn("early-substitution", why)

    def test_level3_classifications_match_one_sided_limits(self):
        expected = {"abs": (True, False), "kink": (True, False), "jump": (False, False), "smooth": (True, True)}
        for kind, (cont, diff) in expected.items():
            params = {"kind": kind, "a": 1, "k": 2, "m1": -1, "m2": 2}
            got = dd.classify(params)
            self.assertEqual((got["continuous"], got["differentiable"]), (cont, diff), kind)
            ok, why, sol, _ = validate(FW, params, 3, None)
            self.assertTrue(ok, f"{kind}: {why}")

    def test_corner_is_never_called_differentiable(self):
        for a in range(-2, 3):
            got = dd.classify({"kind": "abs", "a": a, "k": 0, "m1": 0, "m2": 0})
            self.assertEqual(got["left_slope"], -1)
            self.assertEqual(got["right_slope"], 1)
            self.assertFalse(got["differentiable"])

    def test_bank_has_300(self):
        problems, report = bank.build(FW, seed=1)
        self.assertGreaterEqual(sum(len(v) for v in problems.values()), 300, report)
        self.assertEqual(sorted(problems), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
