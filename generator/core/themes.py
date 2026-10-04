"""Theme files (generator/themes/*.yaml): story wording, visuals and realistic ranges."""
from functools import lru_cache
from pathlib import Path

import yaml

THEME_DIR = Path(__file__).resolve().parent.parent / "themes"

# Hard limits no theme may exceed (spec section 3.2)
GLOBAL_LIMITS = {
    "speed": (0, 120),        # m/s
    "height": (0, 50),        # m
    "distance": (0, 200),     # m
    "restitution": (0, 1),
    "strength": (0, 1),
}


@lru_cache(maxsize=None)
def _all_themes():
    themes = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(THEME_DIR.glob("*.yaml"))]
    return tuple(sorted(themes, key=lambda t: t["id"]))


def load_themes(framework_id):
    return [t for t in _all_themes() if t["framework"] == framework_id]


def in_range(theme, name, value):
    low, high = theme["physics"][name]
    return low <= value <= high


def summary(theme):
    """What the browser needs about a theme."""
    if not theme:
        return None
    return {"id": theme["id"], "label": theme["label"], "visuals": theme.get("visuals", {})}
