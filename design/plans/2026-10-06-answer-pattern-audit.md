# Answer-Pattern Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** No multiple-choice step anywhere in the practice banks can be answered by the shape of its options. Today 18 step types give the answer away: the right answer is uniquely the longest or shortest option, or the middle value, in at least 60% of their problems.

**Architecture:**
- A pattern audit joins the checks in `tests/check_math.py`, so the problem can't come back.
- Each flagged step type is fixed in its own generator. The fixes:
  - balance fixed option texts;
  - add a wrong option of the same shape;
  - rotate which mistakes appear;
  - format numbers to the same width.

**Spec:** The practice spec (`design/specs/` for the generator) requires that every wrong option is a real misconception. The calculus spec, `design/specs/2026-10-05-math-140-explorer-design.md`, inherits that requirement. This plan follows from the 140.1 review's recommendation and the follow-up audit. The shuffle fix (96d3698) dealt with answers given away by position; this deals with answers given away by shape.

## Global Constraints
- Wrong options stay real misconceptions, with feedback that uses the problem's numbers.
- No option may become correct: the `pick`/`distinct` checks still apply.
- All banks are rebuilt, and the audit and every suite stay green.

## Review Focus
1. **New wrong options must be genuinely wrong** for every problem in their family, including edge parameters such as 0, ±1 and equal values.
2. **Rewritten fixed texts keep their meaning and feedback**, with no hint toward the answer.
3. **The audit's metric has to hold up:** it measures rendered length, so ties shouldn't hide giveaways and TeX length shouldn't create false ones.

---

### Task 1: The audit as a check (RED)
- Add `tests/check_patterns.py`, built from the audit script. For each (bank, step) with at least 20 problems, it measures how often the right answer is uniquely the shortest option, uniquely the longest, or the middle number. It fails at 60% or above.
- Hook it into `check_math.py`.
- Expected: it FAILS on the 18 step types.

### Task 2: Fixes, by framework (GREEN), each with its unit test where one exists

| Step type | Fix |
|---|---|
| bounce-3 s1 | format every option to 4 significant digits (0.09 → 0.0900) |
| bounce-4 s1 | rotate the offsets: (−1, +1), (+1, +2), (−2, −1) |
| mixing-2 s3 | balance the texts: "It is cut in half" / "It drops by a fixed amount" / "It stays the same" |
| projectile-1 s3 | "The dropped one lands first" / "The heavier one lands first" |
| projectile-2 s3 | "It doubles too" / "It is cut in half" / "It stays the same" |
| derivative-definition-2 s2 | bare labels: "$0$" / "Undefined" (the explanations move to feedback) |
| derivative-rules-1 s1 | "The sum rule, term by term" / "The product rule, for f·g" / "The chain rule, for f(g(x))" |
| limits-1 s2 | balance the three texts' lengths |
| limits-2 s2 | the wrong options name their reasoning: "Yes: it's 2, the value at x = 1" / "Yes: it's 1/2, the average" |
| limits-5 s1, s2 | longer wrong texts for s1. For s2, add a same-shape "bounds too tight" wrong option (c ± 1/x² or c ± \|x\|^{n+1}) and rotate it with the loose and lower-too-high options |
| continuity-1 s1 | longer wrong texts |
| applications-1 s1, s2 | s2 units: same-length wrong options (cm³ per second for an area). s1: rotate the forgot-chain / constant mistakes so neither is always the shortest |
| applications-2 s2 | always include a same-length "shift sign" wrong option, L = f(a) + f′(a)(x + a) |
| elementary-derivatives-3 s3 | rotate in a "−1/f′(a)" sign slip so the right answer isn't always the middle value |
| elementary-derivatives-5 s1 | always include "chain-dropped-outer", which has the same number of terms |
| elementary-derivatives-6 s2 | always include a same-shape sign slip: y·(p′ ln x − p/x) or its product-family analogue |

### Task 3: Rebuild every bank, run the full suite, and commit
