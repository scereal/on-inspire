"""Can a multiple-choice step be answered from the shape of its options alone?

For every bank and step with at least MIN_PROBLEMS problems, measure how often the right answer is
uniquely the shortest option, uniquely the longest, or (for numeric options) the middle value. A
step type fails when any of those happens in LIMIT or more of its problems. The players shuffle
options, so position is not a giveaway; shape still can be.

Run from the repo root:  python3 tests/check_patterns.py
"""
import json
import re
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 0.6
MIN_PROBLEMS = 20


def size(label):
    """Roughly what a reader sees: a TeX command counts as one symbol; braces and spacing as nothing."""
    s = re.sub(r"\\(left|right|big|Big)\b", "", label)
    s = re.sub(r"\\frac", "", s)
    s = re.sub(r"\\[A-Za-z]+", "#", s)
    return len(re.sub(r"[{}$ ]|\\[,;!]", "", s))


def number(label):
    s = label.strip("$ ").replace("\\frac{", "").replace("}{", "/").replace("}", "").replace("−", "-")
    try:
        return float(Fraction(s))
    except (ValueError, ZeroDivisionError):
        return None


def tally(banks):
    """banks: {name: [problem, ...]} -> {(name, step): [n, shortest, longest, median]}"""
    stats = defaultdict(lambda: [0, 0, 0, 0])
    for name, problems in banks.items():
        for p in problems:
            for i, st in enumerate(p["steps"]):
                if st["format"] != "choice" or len(st["options"]) < 3:
                    continue
                opts = st["options"]
                right = next(o for o in opts if o["correct"])
                wrong_sizes = [size(o["label"]) for o in opts if not o["correct"]]
                s = stats[(name, i + 1)]
                s[0] += 1
                s[1] += all(size(right["label"]) < w for w in wrong_sizes)
                s[2] += all(size(right["label"]) > w for w in wrong_sizes)
                nums = [number(o["label"]) for o in opts]
                if None not in nums and len(set(nums)) == len(nums):
                    s[3] += sorted(nums)[len(nums) // 2] == number(right["label"]) and len(nums) % 2 == 1
    return stats


def problems_found(stats):
    found = []
    for (name, step), (n, short, long_, med) in sorted(stats.items()):
        if n < MIN_PROBLEMS:
            continue
        for count, what in ((short, "shortest"), (long_, "longest"), (med, "middle value")):
            if count / n >= LIMIT:
                found.append(f"{name} step {step}: the right answer is the {what} option in {count}/{n} problems")
    return found


def load_banks():
    banks = {}
    for f in sorted((ROOT / "docs/math/bank").glob("*-[0-9]*.json")):
        banks[f.stem] = json.loads(f.read_text())["problems"]
    return banks


def main():
    stats = tally(load_banks())
    found = problems_found(stats)
    for line in found:
        print("FAIL", line)
    print(f"answer patterns: {len(stats)} choice-step types, {len(found)} problem(s)")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
