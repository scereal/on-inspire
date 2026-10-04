"""Check the math behind docs/math/.

Run from the repo root:  .venv/bin/python tests/check_math.py

- Integration by parts: every correct answer differentiates back to its integrand,
  every planted error does not, and every blank fits the rule.
- Square wave: the Fourier coefficients and Gibbs overshoot quoted on the page.
- Page logic: runs tests/logic_test.js with macOS's built-in JavaScriptCore.
- Problem generator: unit tests plus a full audit of every banked problem.
"""
import json
import pathlib
import re
import subprocess
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
x, n = sp.symbols("x n")
failures = 0


def check(name, ok, detail=""):
    global failures
    print(f"{'pass' if ok else 'FAIL'}  {name}" + ("" if ok else f"  {detail}"))
    failures += not ok


def same(a, b):
    return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0


def derivative_matches(antiderivative, integrand):
    return same(sp.diff(sp.sympify(antiderivative), x), integrand)


# Integration by parts --------------------------------------------------------
text = (ROOT / "docs/math/integration-by-parts/items.js").read_text()
items = json.loads(re.search(r"=\s*(\[.*\]);\s*$", text, re.S).group(1))
print(f"Integration by parts: {len(items)} items")
for i, item in enumerate(items, 1):
    v = item["verify"]
    f = v["integrand"]
    check(f"#{i} answer differentiates to {f}", derivative_matches(v["answer"], f))
    if "shown" in v:
        check(f"#{i} planted error really is wrong", not derivative_matches(v["shown"], f))
        check(f"#{i} has a valid wrong-line index", 0 <= item["wrong"] < len(item["lines"]))
    if "blank" in v:
        check(f"#{i} blank satisfies uv - integral of blank", same(sp.diff(sp.sympify(v["uv"]), x) - sp.sympify(v["blank"]), f))
    for w in v.get("wrongs", []):
        check(f"#{i} distractor {w} is wrong", not derivative_matches(w, f))
    if item["type"] == "choose":
        check(f"#{i} has exactly one right option", sum(bool(o.get("right")) for o in item["options"]) == 1)

# Square wave -----------------------------------------------------------------
print("Square wave")
for k in range(1, 8):
    # Square wave is +1 on (0, π) and -1 on (π, 2π)
    b = (sp.integrate(sp.sin(k * x), (x, 0, sp.pi)) - sp.integrate(sp.sin(k * x), (x, sp.pi, 2 * sp.pi))) / sp.pi
    expected = sp.Rational(4, k) / sp.pi if k % 2 else 0
    check(f"coefficient of sin {k}t is {expected}", sp.simplify(b - expected) == 0)
gibbs = float(2 / sp.pi * sp.Si(sp.pi))
check(f"Gibbs limit (2/π)·Si(π) = {gibbs:.5f} rounds to 1.18", f"{gibbs:.2f}" == "1.18")

# Page logic ------------------------------------------------------------------
print("Page logic (JavaScriptCore)")
result = subprocess.run([JSC, "tests/logic_test.js"], cwd=ROOT, capture_output=True, text=True)
print(result.stdout.rstrip())
if result.returncode:
    print(result.stderr.rstrip())
check("JavaScript logic tests", result.returncode == 0)

# "Why?" concept network ----------------------------------------------------------
print("Concept network")
result = subprocess.run([sys.executable, "tests/check_concepts.py"], cwd=ROOT, capture_output=True, text=True)
print("  " + (result.stdout.strip().splitlines() or [""])[-1])
if result.returncode:
    print(result.stdout + result.stderr)
check("concept network and claims", result.returncode == 0)
result = subprocess.run([sys.executable, "-m", "unittest", "tests.test_check_concepts"], cwd=ROOT, capture_output=True, text=True)
check("concept checker tests", result.returncode == 0)

# Problem generator --------------------------------------------------------------
print("Problem generator")
try:
    import yaml  # noqa: F401  (the generator's other dependency besides sympy)
    for name, cmd in [("generator unit tests", ["-m", "unittest", "discover", "-s", "generator/tests", "-t", "."]),
                      ("bank audit", ["-m", "generator.audit_bank"])]:
        result = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
        tail = (result.stdout + result.stderr).strip().splitlines()[-1:] or [""]
        print(f"  {tail[0]}")
        check(name, result.returncode == 0)
except ImportError:
    print("  skipped: run with the project venv (.venv/bin/python tests/check_math.py) to include the generator")

print(f"\n{failures} failed" if failures else "\nall checks passed")
sys.exit(1 if failures else 0)
