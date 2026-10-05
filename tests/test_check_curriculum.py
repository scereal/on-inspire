"""Fixture tests for tests/check_curriculum.py.

    .venv/bin/python -m unittest tests.test_check_curriculum
"""
import copy
import unittest

from tests import check_curriculum as cc

VALID = {
    "course": "math-140", "title": "Calculus 1", "credits": 3, "official": cc.OFFICIAL, "source": "https://x",
    "units": [
        {"id": "140.2", "title": "Limits", "outcomes": [{"id": "140.2.1", "title": "Limits from graphs", "summary": "s", "subtopics": []}]},
        {"id": "140.3", "title": "The derivative", "outcomes": [{
            "id": "140.3.1", "title": "Rates", "summary": "s",
            "practice": {"framework": "ibp", "level": 1},
            "subtopics": [
                {"id": "140.3.1.rate", "title": "Slope as a rate", "learn": "learn-rate",
                 "practice": {"framework": "ibp", "level": 2}, "builds_on": ["foundation:function", "140.2.1"]},
                {"id": "140.3.1.definition", "title": "Definition", "learn": None, "practice": None,
                 "builds_on": ["140.3.1.rate"]},
            ]}]},
    ],
}
WALKS = {"learn-rate"}
BANK = {"ibp": {"levels": {"1": {}, "2": {}}}}
CONCEPTS = {"function", "limit"}


class CheckCurriculumTest(unittest.TestCase):
    def broken(self, mutate):
        cur = copy.deepcopy(VALID)
        mutate(cur)
        return cc.problems(cur, WALKS, BANK, CONCEPTS)

    def assertReports(self, found, fragment):
        self.assertTrue(any(fragment in p for p in found), f"expected '{fragment}' in {found}")

    def sub(self, cur, i=0):
        return cur["units"][1]["outcomes"][0]["subtopics"][i]

    def test_valid_passes(self):
        self.assertEqual(cc.problems(VALID, WALKS, BANK, CONCEPTS), [])

    def test_duplicate_id(self):
        self.assertReports(self.broken(lambda c: self.sub(c, 1).update(id="140.3.1.rate")), "duplicate id '140.3.1.rate'")

    def test_subtopic_not_nested(self):
        self.assertReports(self.broken(lambda c: self.sub(c, 1).update(id="140.4.1.definition")), "isn't inside outcome 140.3.1")

    def test_unknown_learn(self):
        self.assertReports(self.broken(lambda c: self.sub(c).update(learn="learn-ghost")), "unknown walkthrough 'learn-ghost'")

    def test_unknown_practice(self):
        self.assertReports(self.broken(lambda c: self.sub(c).update(practice={"framework": "ibp", "level": 9})), "no practice bank ibp level 9")
        self.assertReports(self.broken(lambda c: self.sub(c).update(practice={"framework": "nope", "level": 1})), "no practice bank nope level 1")

    def test_unknown_builds_on(self):
        self.assertReports(self.broken(lambda c: self.sub(c).update(builds_on=["140.9.9"])), "unknown target '140.9.9'")
        self.assertReports(self.broken(lambda c: self.sub(c).update(builds_on=["foundation:ghost"])), "unknown target 'foundation:ghost'")

    def test_builds_on_loop(self):
        self.assertReports(self.broken(lambda c: self.sub(c).update(builds_on=["140.3.1.definition"])), "loop")

    def test_official_text_altered(self):
        self.assertReports(self.broken(lambda c: c.update(official="Limits and stuff.")), "official description")


WALK = {
    "id": "learn-rate", "subtopic": "140.3.1.rate", "title": "t", "problem": "p",
    "steps": [{"ask": {"prompt": "q", "format": "choice", "answer": "A",
                       "options": [{"label": "A", "correct": True}, {"label": "B", "misconception": "m", "feedback": "f"}]},
               "narration": "See [[limit]].", "builds_on": ["140.2.1"]}],
    "summary": "s", "claims": [{"sympy": "diff(x**2, x)", "equals": "2*x"}],
}
KNOWN = {"140.2.1", "140.3.1.rate"}


class CheckWalkthroughsTest(unittest.TestCase):
    def broken(self, mutate):
        w = copy.deepcopy(WALK)
        mutate(w)
        return cc.walkthrough_problems([w], CONCEPTS, KNOWN)

    def assertReports(self, found, fragment):
        self.assertTrue(any(fragment in p for p in found), f"expected '{fragment}' in {found}")

    def ask(self, w):
        return w["steps"][0]["ask"]

    def test_valid_passes(self):
        self.assertEqual(cc.walkthrough_problems([WALK], CONCEPTS, KNOWN), [])
        self.assertEqual(cc.verify_walkthrough_claims([WALK]), [])

    def test_unknown_term(self):
        self.assertReports(self.broken(lambda w: w["steps"][0].update(narration="See [[ghost]].")), "unknown concept 'ghost'")

    def test_choice_needs_exactly_one_correct(self):
        self.assertReports(self.broken(lambda w: self.ask(w)["options"][1].update(correct=True)), "2 correct options")
        self.assertReports(self.broken(lambda w: self.ask(w)["options"][0].update(correct=False)), "0 correct options")

    def test_wrong_option_needs_feedback(self):
        self.assertReports(self.broken(lambda w: self.ask(w)["options"][1].pop("feedback")), "no feedback")

    def test_unknown_step_builds_on(self):
        self.assertReports(self.broken(lambda w: w["steps"][0].update(builds_on=["140.9.9"])), "unknown target '140.9.9'")

    def test_unknown_subtopic(self):
        self.assertReports(self.broken(lambda w: w.update(subtopic="140.9.9.x")), "unknown subtopic '140.9.9.x'")

    def test_false_claim(self):
        w = copy.deepcopy(WALK)
        w["claims"] = [{"sympy": "diff(x**2, x)", "equals": "3*x"}]
        self.assertTrue(cc.verify_walkthrough_claims([w]))


if __name__ == "__main__":
    unittest.main()
