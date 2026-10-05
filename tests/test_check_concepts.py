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
    node("start", deeper=["middle"], entry=True, body="Height is {{A1}} because of [[middle|the middle idea]], and $\\frac{d}{dx}$ is not a variable."),
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
        self.assertReports(self.broken(lambda c: None, attach={"start": set()}), "variable 'A1' is not supplied")

    def test_attach_to_unknown_entry(self):
        self.assertReports(self.broken(lambda c: None, attach={"start": {"A1"}, "nope": set()}), "page attaches unknown entry 'nope'")

    def test_attach_ids_from_sibling_json(self):
        import tempfile
        from pathlib import Path
        d = Path(tempfile.mkdtemp())
        (d / "index.html").write_text('<script src="items.js"></script> Why.attach(fb, item.why);')
        (d / "items.js").write_text('window.ITEMS = [{"title": "Pick u", "why": "ibp-pick-u"}];')
        self.assertEqual(cc.attach_calls([d / "index.html"]), {"ibp-pick-u": set()})

    def test_main_fails_when_a_page_loses_its_wiring(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        d = Path(tempfile.mkdtemp())
        pages = []
        for name in ("a", "b"):
            (d / name).mkdir()
            pages.append(d / name / "index.html")
        pages[0].write_text('Why.attach(fb, "start", { A1: 1 });')
        pages[1].write_text("<p>no wiring here</p>")
        concepts = VALID + [node("other-entry", deeper=["base"], entry=True)]
        with mock.patch.object(cc, "PAGES", pages), mock.patch.object(cc, "load", lambda: concepts):
            self.assertEqual(cc.main(), 1)

    def test_concept_reached_only_from_a_walkthrough_is_not_an_orphan(self):
        concepts = VALID + [node("walk-only", deeper=["base"])]
        self.assertReports(cc.problems(concepts, ATTACH), "orphan 'walk-only'")
        self.assertFalse(any("walk-only" in p for p in cc.problems(concepts, ATTACH, roots={"walk-only"})))

    def test_unattached_entry(self):
        self.assertReports(self.broken(lambda c: c.append(node("loose", deeper=["base"], entry=True))), "entry 'loose' isn't attached to any page")

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

    def test_attach_ids_from_step_data(self):
        import tempfile
        from pathlib import Path
        page = Path(tempfile.mkdtemp()) / "p.html"
        page.write_text('{ title: "One to three", why: "tc-one-to-three", target: 1 / 4 }\nWhy.attach(live, level.why);')
        self.assertEqual(cc.attach_calls([page]), {"tc-one-to-three": set()})


if __name__ == "__main__":
    unittest.main()
