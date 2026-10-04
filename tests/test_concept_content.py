"""Content regressions: statements in concepts.js that a reviewer found false or misleading.

    .venv/bin/python -m unittest tests.test_concept_content
"""
import unittest

from tests import check_concepts as cc

BY_ID = {c["id"]: c for c in cc.load()}


class ConceptContentTest(unittest.TestCase):
    def test_dilution_example_is_not_self_contradicting(self):
        # 1/4 − 1/8 equals 1/8, so it can't be offered as the wrong subtraction
        self.assertNotIn("\\frac{1}{4} - \\frac{1}{8}", BY_ID["diluting-multiplies"]["body"])

    def test_gibbs_entry_says_the_overshoot_is_9_percent(self):
        body = BY_ID["sw-gibbs"]["body"]
        self.assertIn("overshooting by about 9% of the jump", body)
        self.assertNotIn("{{peak}}, about 9%", body)

    def test_angle_addition_justifies_the_rotation(self):
        body = BY_ID["angle-addition"]["body"]
        self.assertIn("(1, 0)", body)      # where the two unit arrows go under rotation
        self.assertIn("(0, 1)", body)

    def test_cos_at_angle_zero_is_the_right_hand_end(self):
        self.assertNotIn("top of the circle", BY_ID["cos-h-minus-1-over-h"]["body"])


if __name__ == "__main__":
    unittest.main()
