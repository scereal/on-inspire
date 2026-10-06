# MATH 140 Unit 140.4 (Differentiating Elementary Functions) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build unit 140.4 like 140.2 and 140.3: 7 subtopics across its 4 outcomes, each with a Learn walkthrough and a verified Practice level.

**Architecture:**
- One new framework, `elementary-derivatives`, with 7 levels.
- New `secant` functions: ln, arctan, tan, xˣ.
- One new widget, `circle-tangent`.
- Six new "Why?" concepts and seven walkthroughs.
- Same data formats, checkers and browser tests as before.

**Tech Stack:** Static site under `docs/`, Python + SymPy generators and checkers, JavaScriptCore widget tests, Playwright.

**Spec:** `design/specs/2026-10-05-math-140-explorer-design.md`. §1 orders 140.4 after 140.2, built on the same pattern. The user asked for autonomous build-out ("automated mode"), so this plan goes straight to execution.

## Global Constraints
- The same constraints as `design/plans/2026-10-05-math-140-limits.md`:
  - McGill-based, with CLP as inspiration only;
  - every banked problem is validated and audited, 100 per level;
  - `window.X = <JSON>` data;
  - ask before explaining, exactly one correct option, feedback on every wrong one, SymPy-proven claims;
  - 390 px phone layout with no sideways scroll;
  - no private material.
- Lessons carried over from 140.2:
  - a bank-wide sign-glitch test;
  - a wrong option must never be symbolically equal to the right one;
  - feedback must describe the expression the learner actually sees;
  - exact answers must be typeable as fractions.

## Review Focus
1. **The derivative of ln(kx) is 1/x, not k/x:** k/x must never be the correct option.
2. **The inverse-function derivative is evaluated at the right point:** (f⁻¹)′(b) = 1/f′(a) where f(a) = b. The answer 1/f′(b) must never be correct, unless a = b makes them coincide; reject that case.
3. **Implicit differentiation:** forgetting the dy/dx on a y term is always a wrong option. The point must lie on the curve.
4. **Logarithmic differentiation:** y′ = y·(ln y)′. The option that forgets to multiply back by y must never be correct, including when y = 1 at the point; reject that case.
5. **Higher derivatives:** concave up/down follows the sign of f″. A point where f″ = 0 must never be asked about.

---

### Task 1: Widgets and six concepts
- Functions: `ln`, `atan`, `tan`, `xpowx` (xˣ).
- Widget `circle-tangent {r}`: drag a point around x² + y² = r²; it draws the tangent, with a readout of slope = −x/y.
- `WidgetMath.circleSlope(x, y)`: pure and tested.
- Concepts:
  - `derivative-of-ln` (deeper: derivative-of-exp, inverse-function-derivative);
  - `inverse-function-derivative` (deeper: derivative, chain-rule);
  - `derivative-of-arctan` (deeper: inverse-function-derivative, unit-circle);
  - `implicit-differentiation` (deeper: chain-rule);
  - `logarithmic-differentiation` (deeper: derivative-of-ln, chain-rule);
  - `second-derivative` (deeper: derivative).
- Each concept is linked as related from a natural neighbour until Task 4.

- [ ] **RED:** widget math tests (ln slope at 2 → 1/2; atan slope at 1 → 1/2; xˣ slope at 1 → 1; circleSlope(3, 4) = −3/4). Then GREEN; then the concepts with claims; then `check_concepts`, `check_math` and `e2e_why`; then commit.

### Task 2: `elementary-derivatives` levels 1–4

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 1 | 140.4.1.trig | a·sin(kx) + b·cos(kx); c·tan(kx) | choice f′ (cos-sign: (cos)′ = sin; dropped-inner k; tan′ = sec instead of sec²); number f′(0) |
| 2 | 140.4.1.exp-log | a·e^{kx} + c·ln(mx); a·2^{x} | choice f′ (exp-dropped-inner; power-rule-on-exp k·e^{kx−1}; ln-kept-k c·m/x; 2^x → x·2^{x−1}); number f′(1) when clean |
| 3 | 140.4.2.inverse | f = x³ + px + q (p ≥ 1, so increasing), b = f(a) | choice: a such that f(a) = b (used-b); number f′(a); choice (f⁻¹)′(b) = 1/f′(a) (forgot-to-flip f′(a); wrong-point 1/f′(b)) |
| 4 | 140.4.2.inverse-trig | k·arctan(mx) at x = 1/m (value k·m/2) or at 0; k·arcsin(mx) at 0 (value k·m) | choice f′ (arctan-no-chain k/(1+x²) when m ≠ 1; arcsin-like-arctan); number value |

- [ ] **RED:** tests:
  - L2: the ln(mx) answer is c/x, and k/x is a wrong option;
  - L3: rejects a = b; the 1/f′(b) option is wrong;
  - L4: the value equals SymPy;
  - a sign-glitch scan;
  - a check that no wrong option is symbolically equal to the right one (`sympify(label)`, where parseable);
  - the bank has ≥ 100 per level.
- [ ] **GREEN:** implement, register and build.
- [ ] Run the suite, then commit.

### Task 3: levels 5–7

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 5 | 140.4.3.implicit | x² + y² = r² at a lattice point; x·y = c; x² + xy + y² = c at a point on the curve | choice: d/dx of the y-terms (forgot-chain-on-y: 2y with no y′); choice dy/dx; number at the point |
| 6 | 140.4.3.log-diff | y = x^{p(x)} at x = 1 (y′ = p(1)); y = x^a(x + 1)^b/(x + 2)^c at x = 1 | choice ln y (exponent-not-down; ln-of-sum-split); choice y′/y; number y′(1) (rejects y(1) = 1 for the product family when the forgot-y option would match) |
| 7 | 140.4.4.higher | s(t) = a·t³ + b·t² + c·t + d | choice s′(t); choice s″(t); number a(t₀) = s″(t₀) (with s″(t₀) ≠ 0); choice concave up/down (concavity-from-f′) |

- [ ] **RED:** tests:
  - L5: the point is on the curve, the forgot-chain option is wrong, and the slope matches SymPy `idiff`;
  - L6: x^{p(x)} at 1 equals p(1), and the forgot-y option is never correct;
  - L7: concavity matches the sign of s″(t₀), and s″(t₀) = 0 is rejected.
- [ ] **GREEN:** implement and build.
- [ ] Run the suite, then commit.

### Task 4: Curriculum, seven walkthroughs and the browser test

| Subtopic | Learn problem | Practice | Builds on |
|---|---|---|---|
| 140.4.1.trig | sin′ = cos from the limit (link sin-h-over-h), then (sin 3x)′ = 3 cos 3x | L1 | 140.3.2.chain, foundation:unit-circle |
| 140.4.1.exp-log | A population P = 100e^{0.5t}: P′ = 0.5P; then ln x as the inverse, so (ln x)′ = 1/x | L2 | 140.3.2.chain, 140.4.2.inverse |
| 140.4.2.inverse | f(x) = x³ + x, f(1) = 2, so (f⁻¹)′(2) = 1/f′(1) = 1/4 | L3 | 140.3.2.chain, 140.1.1 |
| 140.4.2.inverse-trig | (arctan x)′ = 1/(1 + x²) from tan y = x; value 1/2 at x = 1 | L4 | 140.4.2.inverse, 140.4.1.trig |
| 140.4.3.implicit | Circle x² + y² = 25 at (3, 4): slope −3/4 | L5 | 140.3.2.chain |
| 140.4.3.log-diff | y = xˣ: ln y = x ln x, y′ = xˣ(ln x + 1); y′(1) = 1 | L6 | 140.4.1.exp-log, 140.4.3.implicit |
| 140.4.4.higher | A ball's height h(t) = 20t − 4.9t²: v(1) = 10.2, a = −9.8, concave down | L7 | 140.3.2.power |

- [ ] **RED:** add the curriculum subtopics. Run `check_curriculum`. Expected: unknown learn ids.
- [ ] **GREEN:** write the walkthroughs. Run `check_curriculum` and `check_concepts`. Expected: 0 problems.
- [ ] Run `e2e_calculus` (all walkthroughs) and the whole suite. Take phone screenshots of the new widget and a walkthrough. Commit.
