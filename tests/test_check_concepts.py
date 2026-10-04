"""Fixture tests for tests/check_concepts.py: one valid network, then one broken network per rule.

    .venv/bin/python -m unittest tests.test_check_concepts
"""
import copy
import unittest

from tests import check_concepts as cc


def node(id, deeper=(), related=(), foundation=False, body=None, entry=False, widget="secant", claims=None):
    n = {"id": id, "title": id.title(), "body": body if body is not None else f"About {id}.",
         "deeper": list(deeper), "related": list(related), "foundation": foundation,
         "widget": {"type": widget}}
    if entry:
        n["entry"] = True
    if claims:
        n["claims"] = claims
    return n


VALID = [
    node("start", deeper=["middle"], entry=True, body="Height is {A1} because of [[middle|the middle idea]]."),
    node("middle", deeper=["base"], related=["side"], body="Built on [[base]], compare [[side]]."),
    node("side", deeper=["base"]),
    node("base", foundation=True, claims=[{"sympy": "integrate(sin(x), (x, 0, pi))", "equals": "2"}]),
]
ATTACH = {"start": {"A1"}}


class CheckConceptsTest(unittest.TestCase):
    def broken(self, mutate, attach=None):
        concepts = copy.deepcopy(VALID)
        mutate(concepts)
        return cc.problems(concepts, ATTACH if attach is None else attach)

    def assertReports(self, found, fragment):
        self.assertTrue(any(fragment in p for p in found), f"expected '{fragment}' in {found}")

    def test_valid_network_passes(self):
        self.assertEqual(cc.problems(VALID, ATTACH), [])
        self.assertEqual(cc.verify_claims(VALID), [])

    def test_used_by_is_reverse_of_deeper(self):
        self.assertEqual(sorted(cc.used_by(VALID)["base"]), ["middle", "side"])

    def test_missing_link_target(self):
        self.assertReports(self.broken(lambda c: c[1]["related"].append("ghost")), "unknown concept 'ghost'")

    def test_term_not_in_link_lists(self):
        def mutate(c):
            c[2]["body"] = "Mentions [[middle]] without linking it."
        self.assertReports(self.broken(mutate), "[[middle]] is not in its deeper or related links")

    def test_deeper_loop(self):
        def mutate(c):  # middle -> side -> middle
            c[1]["deeper"].append("side")
            c[2]["deeper"].append("middle")
        self.assertReports(self.broken(mutate), "loop")

    def test_non_foundation_without_deeper(self):
        self.assertReports(self.broken(lambda c: c[2].update(deeper=[])), "has no deeper links")

    def test_foundation_with_deeper(self):
        self.assertReports(self.broken(lambda c: c[3].update(deeper=["side"])), "foundation 'base' links deeper")

    def test_orphan(self):
        self.assertReports(self.broken(lambda c: c.append(node("lonely", foundation=True))), "orphan 'lonely'")

    def test_duplicate_id(self):
        self.assertReports(self.broken(lambda c: c.append(node("side", deeper=["base"]))), "duplicate id 'side'")

    def test_unknown_widget(self):
        self.assertReports(self.broken(lambda c: c[1]["widget"].update(type="hologram")), "unknown widget 'hologram'")

    def test_missing_widget(self):
        self.assertReports(self.broken(lambda c: c[1].pop("widget")), "no widget")

    def test_entry_variable_not_supplied(self):
        self.assertReports(self.broken(lambda c: None, attach={"start": set()}), "{A1} is not supplied")

    def test_attach_to_unknown_entry(self):
        self.assertReports(self.broken(lambda c: None, attach={"start": {"A1"}, "nope": set()}), "page attaches unknown entry 'nope'")

    def test_false_claim(self):
        concepts = copy.deepcopy(VALID)
        concepts[3]["claims"] = [{"sympy": "integrate(sin(x), (x, 0, pi))", "equals": "3"}]
        self.assertReports(cc.verify_claims(concepts), "base")

    def test_approximate_claim(self):
        concepts = copy.deepcopy(VALID)
        concepts[3]["claims"] = [{"sympy": "2/pi*Si(pi)", "approx": 1.179, "tol": 0.001}]
        self.assertEqual(cc.verify_claims(concepts), [])

    def test_attach_calls_parsed_from_pages(self):
        import tempfile
        from pathlib import Path
        page = Path(tempfile.mkdtemp()) / "p.html"
        page.write_text('Why.attach(fb, "sw-best-height", { A1: fmt(A1), A3 : 2 });\nWhy.attach(box, "tc-half");')
        self.assertEqual(cc.attach_calls([page]), {"sw-best-height": {"A1", "A3"}, "tc-half": set()})


if __name__ == "__main__":
    unittest.main()
