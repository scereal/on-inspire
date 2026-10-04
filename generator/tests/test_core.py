"""Core pipeline tests, using a tiny fake framework whose params trigger each rejection."""
import json
import unittest
from unittest import mock

from generator.core import bank
from generator.core.framework import Framework, Level, NoSolution, Option, Solution, Step
from generator.core.validators import validate


class Fake(Framework):
    id = "fake"
    title = "Fake"
    outcome = "Testing"
    levels = {1: Level("only", {"add": 1})}
    misconceptions = {"off-by-one": "Added one too many."}
    targets = {1: 20}

    def themes_for(self, level):
        return [{"id": "t", "label": "a thing", "visuals": {}, "physics": {"speed": [1, 10]}, "levels": [1]}]

    def sample(self, rng, level, theme):
        return {"a": rng.randrange(1, 40), "flags": []}

    def solve(self, p, level, theme):
        flags = p.get("flags", [])
        if "none" in flags:
            raise NoSolution("no answer")
        a = p["a"]
        wrong = a if "same" in flags else (a * 1.05 if "close" in flags else a + 10)
        options = [Option(str(a), correct=True, value=a), Option(str(wrong), misconception="off-by-one", value=wrong)]
        if "two-correct" in flags:
            options[1] = Option(str(a + 10), correct=True, value=a + 10)
        slider_answer = 5.05 if "off-grid" in flags else (10.0 if "edge" in flags else 5.0)
        steps = [
            Step("What is a?", "choice", str(a), options=options),
            Step("Set it", "slider", slider_answer, tolerance=0.05, slider={"param": "v", "min": 0, "max": 10, "step": 0.1}),
        ]
        tools = ["add", "add"] if "extra-tool" in flags else ["add"]
        return Solution(steps=steps, story=f"A is {a}.", scene={"type": "fake"}, tools=tools, answers={"a": a})

    def count_solutions(self, p, level):
        return 2 if "two-answers" in p.get("flags", []) else 1

    def plausibility(self, p, level, theme):
        return [("speed", 50 if "too-fast" in p.get("flags", []) else 5)]

    def canonical(self, p, level):
        return str(p["a"])


THEME = {"id": "t", "label": "a thing", "visuals": {}, "physics": {"speed": [1, 10]}, "levels": [1]}


class ValidatorTest(unittest.TestCase):
    def check(self, flags, reason=None):
        ok, why, _, report = validate(Fake(), {"a": 7, "flags": flags}, 1, THEME)
        if reason is None:
            self.assertTrue(ok, why)
            self.assertTrue(all(report.values()), report)
        else:
            self.assertFalse(ok)
            self.assertTrue(why.startswith(reason), f"expected {reason}, got {why}")

    def test_valid_problem_passes(self):
        self.check([])

    def test_rejections(self):
        self.check(["none"], "exists")
        self.check(["two-answers"], "unique")
        self.check(["two-correct"], "distinct")
        self.check(["same"], "distinct")
        self.check(["close"], "distinct")
        self.check(["extra-tool"], "taught_tools")
        self.check(["too-fast"], "plausible")
        self.check(["off-grid"], "findable")
        self.check(["edge"], "findable")


class IntegerOptionsTest(unittest.TestCase):
    def test_adjacent_whole_numbers_are_distinct(self):
        from generator.core.validators import distinct_problem
        step = Step("How many?", "choice", "10", options=[Option("10", correct=True, value=10), Option("11", value=11, misconception="m")])
        self.assertIsNone(distinct_problem([step]))
        step.options[1] = Option("10.0", value=10, misconception="m")
        self.assertIsNotNone(distinct_problem([step]))


class BankTest(unittest.TestCase):
    def test_duplicates_kept_once_and_deterministic(self):
        with mock.patch.object(Fake, "sample", lambda self, rng, level, theme: {"a": rng.randrange(1, 6), "flags": []}):
            problems, report = bank.build(Fake(), 20, seed=1, min_accept=0)
        ids = [p["id"] for p in problems[1]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertLessEqual(len(ids), 5)
        self.assertGreater(report["levels"]["1"]["rejected"].get("duplicate", 0), 0)

    def test_same_seed_same_bytes(self):
        a = json.dumps(bank.build(Fake(), 20, seed=3)[0], sort_keys=True)
        b = json.dumps(bank.build(Fake(), 20, seed=3)[0], sort_keys=True)
        c = json.dumps(bank.build(Fake(), 20, seed=4)[0], sort_keys=True)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_rebuild_reproduces_record(self):
        problems, _ = bank.build(Fake(), 5, seed=2)
        for record in problems[1]:
            self.assertEqual(bank.rebuild_problem(Fake(), record), record)

    def test_low_acceptance_fails(self):
        with mock.patch.object(Fake, "sample", lambda self, rng, level, theme: {"a": 1, "flags": ["none"]}):
            with self.assertRaises(bank.BuildError):
                bank.build(Fake(), 20, seed=1)

    def test_rejected_in_review_skipped(self):
        problems, _ = bank.build(Fake(), 5, seed=2)
        banned = problems[1][0]["id"]
        again, report = bank.build(Fake(), 5, seed=2, rejected_ids={banned})
        self.assertNotIn(banned, [p["id"] for p in again[1]])


if __name__ == "__main__":
    unittest.main()
