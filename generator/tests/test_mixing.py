import unittest
from fractions import Fraction

from generator.core import bank
from generator.core.themes import load_themes
from generator.core.validators import validate
from generator.frameworks import mixing

FW = mixing.FRAMEWORK
TEA = next(t for t in load_themes("mixing") if t["id"] == "tea")


def replay(path, caps):
    """Independent re-implementation of the pour rules: (marks, concentrate) per cup."""
    cups = [[0, Fraction(0)], [0, Fraction(0)]]
    for action, i in path:
        cup, other = cups[i], cups[1 - i]
        if action == "concentrate":
            cup[0] += 1; cup[1] += 1
        elif action == "water":
            cup[0] += 1
        elif action == "pour":
            moved = cup[1] / cup[0]
            cup[0] -= 1; cup[1] -= moved
            other[0] += 1; other[1] += moved
        elif action == "empty":
            cup[0], cup[1] = 0, Fraction(0)
        assert 0 <= cup[0] <= caps[i] and 0 <= other[0] <= caps[1 - i], "move broke the cup limits"
    return [c[1] / c[0] if c[0] else None for c in cups]


class MixingTest(unittest.TestCase):
    def test_search_paths_replay_to_their_strength(self):
        table = mixing.reachable(4, 4)
        self.assertIn(Fraction(1, 8), table)
        for strength, (moves, path) in list(table.items())[:40]:
            self.assertEqual(len(path), moves)
            self.assertIn(strength, replay(path, (4, 4)))

    def test_level1_valid(self):
        ok, why, sol, _ = validate(FW, {"ma": 4, "mb": 4, "a": 1, "b": 3}, 1, TEA)
        self.assertTrue(ok, why)
        self.assertEqual(sol.steps[1].answer, "1/4")

    def test_equal_parts_rejected_at_level1(self):
        ok, why, _, _ = validate(FW, {"ma": 4, "mb": 4, "a": 1, "b": 1}, 1, TEA)
        self.assertFalse(ok)
        self.assertIn("water-share", why)

    def test_level2_needs_dilution(self):
        ok, why, sol, _ = validate(FW, {"ma": 4, "mb": 4, "s": "1/8"}, 2, TEA)
        self.assertTrue(ok, why)
        self.assertGreater(Fraction(sol.steps[1].answer).denominator, 4)

    def test_equal_amounts_rejected_at_level3(self):
        ok, why, _, _ = validate(FW, {"ma": 4, "mb": 4, "m1": 2, "s1": "1/2", "m2": 2, "s2": "1/4"}, 3, TEA)
        self.assertFalse(ok)
        self.assertIn("unweighted-average", why)

    def test_level3_weighted_average(self):
        ok, why, sol, _ = validate(FW, {"ma": 4, "mb": 4, "m1": 1, "s1": "1/2", "m2": 3, "s2": "1/4"}, 3, TEA)
        self.assertTrue(ok, why)
        self.assertEqual(Fraction(sol.steps[1].answer), Fraction(5, 16))

    def test_bank_has_300(self):
        problems, report = bank.build(FW, seed=1)
        self.assertGreaterEqual(sum(len(v) for v in problems.values()), 300, report)
        self.assertEqual(sorted(problems), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
