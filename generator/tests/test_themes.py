import string
import unittest

from generator.core.themes import GLOBAL_LIMITS, load_themes
from generator.frameworks import available

FRAMEWORKS = ["projectile", "bounce", "mixing"]


class ThemeTest(unittest.TestCase):
    def test_required_fields_and_ranges(self):
        for fid in FRAMEWORKS:
            themes = load_themes(fid)
            self.assertGreaterEqual(len(themes), 3, fid)
            for t in themes:
                for field in ("id", "label", "visuals", "physics", "levels", "stories"):
                    self.assertIn(field, t, f"{t.get('id')} missing {field}")
                self.assertTrue(t["visuals"].get("color", "").startswith("#"), t["id"])
                for name, (low, high) in t["physics"].items():
                    self.assertLessEqual(low, high, f"{t['id']}.{name}")
                    g_low, g_high = GLOBAL_LIMITS.get(name, (float("-inf"), float("inf")))
                    self.assertTrue(g_low <= low and high <= g_high, f"{t['id']}.{name} outside realistic limits")
                for level in t["levels"]:
                    self.assertIn(level, t["stories"], f"{t['id']} has no story for level {level}")

    def test_paper_airplane_is_not_a_projectile_theme(self):
        self.assertNotIn("paper-airplane", [t["id"] for t in load_themes("projectile")])

    def test_story_placeholders_are_filled_by_the_framework(self):
        for fid, fw in available().items():
            for t in load_themes(fid):
                for level, templates in t["stories"].items():
                    for template in templates:
                        used = {name for _, name, _, _ in string.Formatter().parse(template) if name}
                        self.assertLessEqual(used, fw.STORY_FIELDS[level], f"{t['id']} level {level}: {used}")


if __name__ == "__main__":
    unittest.main()
