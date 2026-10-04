"""The contract every problem framework implements (spec section 3.1)."""
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


class NoSolution(Exception):
    """Raised by solve() when the sampled values have no valid answer."""


@dataclass
class Level:
    name: str
    tools: dict  # allowed tool -> maximum number of uses


@dataclass
class Option:
    label: str
    correct: bool = False
    misconception: Optional[str] = None
    feedback: str = ""
    value: Any = None  # number or canonical string, used by the distinct-answers check


@dataclass
class Step:
    prompt: str
    format: str  # choice | number | slider | mix
    answer: Any
    options: list = field(default_factory=list)
    tolerance: float = 0.0
    unit: str = ""
    slider: Optional[dict] = None  # {"param", "min", "max", "step"}
    explain: str = ""  # shown after a correct answer

    def to_dict(self):
        d = asdict(self)
        return {k: v for k, v in d.items() if v not in (None, "", [], 0.0) or k in ("answer", "prompt", "format")}


@dataclass
class Solution:
    steps: list
    story: str
    scene: dict
    tools: list
    answers: dict = field(default_factory=dict)


class Framework:
    id = ""
    title = ""
    outcome = ""
    levels: dict = {}
    misconceptions: dict = {}
    targets: dict = {}  # level -> number of problems to bank
    version = "1.0"

    def themes_for(self, level):
        from .themes import load_themes

        return [t for t in load_themes(self.id) if level in t.get("levels", [])]

    def sample(self, rng, level, theme):
        raise NotImplementedError

    def solve(self, params, level, theme):
        raise NotImplementedError

    def count_solutions(self, params, level):
        """How many valid answers the asked-for quantity has. Must be 1 to bank."""
        return 1

    def plausibility(self, params, level, theme):
        """(name, value) pairs checked against the theme's physics ranges."""
        return []

    def checks(self, params, level, theme, solution):
        """Framework-specific (name, ok, reason) results, e.g. clean numbers."""
        return []

    def canonical(self, params, level):
        """The problem's math, ignoring story and theme, for duplicate detection."""
        return json.dumps(params, sort_keys=True)
