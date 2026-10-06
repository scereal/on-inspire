# MATH 140 Unit 140.1 (Functions and Graphs) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build unit 140.1 like the other units: 6 subtopics across its 3 outcomes, each with a Learn walkthrough and a verified Practice level.

**Architecture:**
- One framework, `functions`, with 6 levels.
- Two widgets:
  - `transform` (sliders for a, h and k on a base graph);
  - `mirror` (f and its reflection across y = x).
- Five concepts and six walkthroughs.

**Spec:** `design/specs/2026-10-05-math-140-explorer-design.md`. §1 orders 140.1 after 140.5. Built autonomously at the user's request; the user chose to keep work local and continue.

## Global Constraints
- The same as the earlier unit plans.
- **Carried lessons**, each covered by a test:
  - **Correctness:** no correct option marked wrong, and every choice step has ≥ 2 distinct mistakes.
  - **Feedback:** it uses the problem's own numbers and describes what's shown.
  - **No giveaways:** none by form, none by an earlier step's prompt or explanation, and no verdict that can be pattern-matched.
  - **Text:** the scan covers story, prompts, options, feedback, explanations and scene, with balanced parentheses and braces.
  - **Uniqueness:** no two problems read the same.
  - **Shuffling:** options are shuffled by the players, so the data's order doesn't matter.

## Review Focus
1. **Domain:** strict vs non-strict inequalities follow the function (√ allows 0, ln and denominators don't). Dividing by a negative coefficient flips the inequality.
2. **Composition order:** (f∘g)(x) = f(g(x)). The swapped order is never correct unless f∘g = g∘f, which is rejected.
3. **Inverses:** the reciprocal 1/f is never offered as correct. The problem is rejected when f is its own inverse, since then "swapped" equals the answer.
4. **Transformations:** a horizontal shift right by h is (x − h). The sign-swapped option is always wrong. Stretch and shift order must match the formula.
5. **Log equations:** extraneous roots (making a log's argument ≤ 0) are offered only as wrong options, with feedback.

---

### Task 1: Widgets and five concepts
- `WidgetMath.transformed(base, a, h, k)` → x ↦ a·base(x − h) + k.
- `WidgetMath.mirrorPoint([x, y])` → [y, x].
- Widget `transform {base}`: sliders a, h and k, with a readout of the formula.
- Widget `mirror {f}`: draws f, y = x, and the reflected curve.
- Concepts:
  - `domain-and-range` (deeper: function);
  - `function-composition` (deeper: function);
  - `inverse-function` (deeper: function; related: inverse-function-derivative);
  - `graph-transformations` (deeper: function);
  - `logarithm` (deeper: function; related: derivative-of-ln).
- Steps: RED widget tests, then GREEN, then the concepts. Run `check_concepts`, `check_math` and `e2e_why`. Commit.

### Task 2: `functions` levels 1–3

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 1 | 140.1.1.domain | √(ax + b); ln(ax + b); 1/(x² − r²); √(ax + b)/(x − c) | choice: the condition (strict vs non-strict); choice: the domain (inequality-flip, strict/inclusive slip, forgot excluded point) |
| 2 | 140.1.1.composition | linear and quadratic f, g | number g(a); number f(g(a)); choice: the formula f(g(x)) (order-swapped, composition-is-product) |
| 3 | 140.1.1.inverse | ax + b; x³ + b; (ax + b)/(x + d) | choice f⁻¹(x) (reciprocal, solved-wrong); number f⁻¹(v) |

### Task 3: levels 4–6

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 4 | 140.1.2.transform | base x², √x, \|x\|, 1/x; one or two of a shift right/left, a shift up/down, a stretch, a reflection | choice: the formula for a description (shift-sign, horizontal-as-vertical, stretch-misplaced); number g(x₀) |
| 5 | 140.1.3.exp-log | b^{px+q} = b^n; log_b x + log_b(x − d) = n with an integer root | choice: the rewritten equation (log-of-product-as-product, exponent-misread); choice: the solution(s) (extraneous root); number x |
| 6 | 140.1.3.trig-values | sin, cos, tan at kπ/6, kπ/4, kπ/3 in [0, 2π), excluding undefined tan values | choice: the quadrant sign; choice: the exact value (cofunction-swap, quadrant-sign, reference-angle slip) |

### Task 4: Curriculum, six walkthroughs and the browser test

| Subtopic | Learn problem | Practice | Builds on |
|---|---|---|---|
| 140.1.1.domain | √(x − 2)/(x − 5): x ≥ 2, x ≠ 5 | L1 | foundation:function |
| 140.1.1.composition | f = 2x + 1, g = x²: (f∘g)(3) = 19, (g∘f)(3) = 49 | L2 | foundation:function |
| 140.1.1.inverse | °F = 9/5·°C + 32 inverted: 212 °F → 100 °C | L3 | 140.1.1.composition |
| 140.1.2.transform | 2(x − 3)² + 1 from x²: vertex (3, 1), twice as steep | L4 | foundation:function |
| 140.1.3.exp-log | 3·2^x = 48 → 2^x = 16 → x = 4; then log₂ 16 = 4 | L5 | 140.1.1.inverse |
| 140.1.3.trig-values | sin(5π/6): reference angle π/6, quadrant II, so 1/2 | L6 | foundation:unit-circle |

- [ ] Steps: RED curriculum entries; GREEN walkthroughs. Run `check_curriculum`, `check_concepts`, `e2e_calculus` and the full suite. Take screenshots. Commit.
