"""Shared checks every candidate problem must pass (spec section 4)."""
import math
from collections import Counter

from .framework import NoSolution
from .themes import GLOBAL_LIMITS, in_range

DISTINCT_MARGIN = 0.10  # numeric options must differ by at least 10%


def validate(fw, params, level, theme):
    """Solve and check one candidate. Returns (ok, reason, solution, report)."""
    report = {}

    def fail(name, why):
        report[name] = False
        return False, f"{name}: {why}", solution, report

    solution = None
    try:
        solution = fw.solve(params, level, theme)
    except NoSolution as e:
        return fail("exists", str(e))
    report["exists"] = True

    n = fw.count_solutions(params, level)
    if n != 1:
        return fail("unique", f"{n} valid answers")
    report["unique"] = True

    allowed = fw.levels[level].tools
    for tool, uses in Counter(solution.tools).items():
        if uses > allowed.get(tool, 0):
            return fail("taught_tools", f"{tool} used {uses}x, level allows {allowed.get(tool, 0)}")
    report["taught_tools"] = True

    why = distinct_problem(solution.steps)
    if why:
        return fail("distinct", why)
    report["distinct"] = True

    for name, value in fw.plausibility(params, level, theme):
        low, high = GLOBAL_LIMITS.get(name, (-math.inf, math.inf))
        if not low <= value <= high:
            return fail("plausible", f"{name}={value:g} outside realistic limits")
        if theme and name in theme.get("physics", {}) and not in_range(theme, name, value):
            return fail("plausible", f"{name}={value:g} unrealistic for {theme['id']}")
    report["plausible"] = True

    why = findable_problem(solution.steps)
    if why:
        return fail("findable", why)
    report["findable"] = True

    for name, ok, why in fw.checks(params, level, theme, solution):
        if not ok:
            return fail(name, why)
        report[name] = True
    report.setdefault("clean", True)
    return True, None, solution, report


def distinct_problem(steps):
    for i, step in enumerate(steps, 1):
        if step.format != "choice":
            continue
        correct = [o for o in step.options if o.correct]
        if len(correct) != 1:
            return f"step {i} has {len(correct)} correct options"
        right = correct[0].value
        for o in step.options:
            if o.correct or o.value is None or right is None:
                continue
            if same_value(o.value, right):
                return f"step {i}: '{o.misconception}' gives the right answer"
        labels = [o.label.strip().lower() for o in step.options]
        if len(set(labels)) != len(labels):
            return f"step {i} repeats an option label"
        numbers = [o.value for o in step.options if isinstance(o.value, (int, float))]
        for a_i, a in enumerate(numbers):
            for b in numbers[a_i + 1:]:
                scale = max(abs(a), abs(b), 1e-9)
                if abs(a - b) < DISTINCT_MARGIN * scale:
                    return f"step {i}: options {a:g} and {b:g} are too close"
    return None


def same_value(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    return str(a) == str(b)


def findable_problem(steps):
    for i, step in enumerate(steps, 1):
        if step.format == "number" and step.tolerance <= 0:
            return f"step {i}: number step needs a tolerance"
        if step.format != "slider":
            continue
        s = step.slider
        lo, hi, grid, ans = s["min"], s["max"], s["step"], step.answer
        if not lo < ans < hi:
            return f"step {i}: answer {ans:g} not inside the slider range"
        k = (ans - lo) / grid
        if abs(k - round(k)) > 1e-6:
            return f"step {i}: answer {ans:g} not on the slider grid"
        hits = sum(1 for j in range(int(round((hi - lo) / grid)) + 1) if abs(lo + j * grid - ans) <= step.tolerance + 1e-9)
        if hits != 1:
            return f"step {i}: {hits} slider positions pass"
    return None
