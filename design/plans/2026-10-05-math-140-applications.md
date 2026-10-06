# MATH 140 Unit 140.5 (Applications) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build unit 140.5 like the units before it. That means 7 subtopics across its 6 outcomes, each with a Learn walkthrough and a verified Practice level.

**Architecture:**
- One framework, `applications`, with 7 levels.
- Two widgets:
  - `tangent-point`, with modes `slide` (optional chord) and `approx`;
  - `ladder`.
- Six concepts and seven walkthroughs.

**Tech Stack:** As before.

**Spec:** `design/specs/2026-10-05-math-140-explorer-design.md`. §1 orders 140.5 after 140.4. Built autonomously at the user's request.

## Global Constraints
- The same as `design/plans/2026-10-05-math-140-elementary.md`.
- The carried lessons are tested:
  - no correct option marked wrong (`pick()`-style symbolic filtering);
  - no answer given away by its form;
  - feedback describes the expression on screen, with the problem's own numbers;
  - every choice step offers at least two distinct mistakes;
  - a bank-wide text-glitch scan.

## Review Focus
1. **Related rates:** the rate asked for has the correct sign, for example the ladder top sliding down has dy/dt < 0. The "forgot the chain rule in t" option is never correct.
2. **Linear approximation:** the over/under verdict follows concavity (f″ at a). The estimate is checked to genuinely differ from the true value beyond the tolerance, or the over/under question is meaningless.
3. **MVT:** c lies strictly inside (a, b), and "the midpoint" is never correct unless f is quadratic. If the midpoint coincides with c for a cubic, reject.
4. **Closed-interval extrema:** endpoints are always candidates. A critical point outside the interval is never correct. Problems with ties, where two candidates share the max or min value, are rejected.
5. **L'Hôpital:** never offered on a limit that isn't 0/0 or ∞/∞ without the correct answer being "don't use it". The quotient rule applied to top/bottom is always a wrong option.

---

### Task 1: Widgets and six concepts
- `WidgetMath.slopeAt(f, x)`: central difference.
- `WidgetMath.ladder(L, x, dxdt)` → `{y, dydt}`.
- Functions:
  - `crit3` = x³ − 3x;
  - `fencearea` = x(100 − 2x);
  - `ladderTop`;
  - `lhop` = (e^{2x} − 1)/x.
- Concepts:
  - `related-rates` (deeper: implicit-differentiation, chain-rule);
  - `linear-approximation` (deeper: derivative);
  - `mean-value-theorem` (deeper: derivative, continuity);
  - `critical-points` (deeper: derivative; related: second-derivative);
  - `optimization` (deeper: critical-points);
  - `lhopital` (deeper: derivative, indeterminate-form).
- RED widget tests first (ladder dydt at x = 6, L = 10, dxdt = 2 → −1.5; slopeAt(crit3, 1) = 0). Then GREEN; then the concepts. Run `check_concepts`, `check_math` and `e2e_why`. Commit.

### Task 2: `applications` levels 1–4

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 1 | 140.5.1.related-rates | ladder (Pythagorean triples), cube edge, rectangle with both sides changing | choice: the relation differentiated in t (forgot-chain-in-t, constant-not-zero); number: the rate; choice: what the sign means |
| 2 | 140.5.2.linear-approx | √x at a perfect square, ∛x at a perfect cube, 1/x, near a | number f′(a); choice L(x); number estimate; choice over/under by concavity |
| 3 | 140.5.3.mvt | quadratic on [a, b] (c = midpoint); x³ + px on [−b, 2b] (c = b) | number: average slope; choice: what the theorem promises (f′(c) = avg) vs misreadings; number c |
| 4 | 140.5.4.extrema | x³ − 3p²x + q on [lo, hi] | choice: candidates (critical points in the interval plus endpoints; forgot-endpoints; outside-point); number: absolute max; number: absolute min |

- [ ] **RED:** tests:
  - L1: the ladder sign is negative;
  - L2: the verdict matches f″, and the error exceeds the tolerance;
  - L3: c is inside the interval, and the midpoint is wrong for the cubic;
  - L4: endpoints are in the correct candidate set, ties are rejected, and the max/min match a brute-force scan;
  - the glitch scan;
  - no coin flips;
  - the bank has ≥ 100 per level.
- [ ] **GREEN:** implement and build. Run the suite and commit.

### Task 3: levels 5–7

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 5 | 140.5.4.sketch | cubic a(x − r)(x − s)(x − u)-style, with integer critical points | choice: where f is increasing; number: inflection x; choice: local max/min at a critical point by the second-derivative test |
| 6 | 140.5.5.optimization | river fence (L, three sides), open box from an s × s sheet (x = s/6), fixed product minimum sum | choice: the objective function; number: optimal x; number: optimal value |
| 7 | 140.5.6.lhopital | (e^{kx} − 1)/(mx), sin(kx)/(mx), (1 − cos kx)/x², ln x/(x − 1), xⁿ/e^{x} at ∞; plus not-indeterminate (cos x)/(x + 1) at 0 | choice: the form; choice: after differentiating (quotient-rule-instead); number: the limit |

- [ ] **RED:** tests:
  - L5: the increasing intervals match the sign of f′, and the second-derivative test is consistent;
  - L6: the optimum equals the SymPy maximiser, and it's an interior maximum;
  - L7: the not-indeterminate family's correct answer is "substitute", and the quotient-rule option is always wrong;
  - the glitch scan;
  - the bank has ≥ 100 per level.
- [ ] **GREEN:** implement and build. Run the suite and commit.

### Task 4: Curriculum, seven walkthroughs and the browser test

| Subtopic | Learn problem | Practice | Builds on |
|---|---|---|---|
| 140.5.1.related-rates | A 10 m ladder slides; its foot moves out at 2 m/s. When the foot is 6 m out, the top falls at 1.5 m/s | L1 | 140.4.3.implicit |
| 140.5.2.linear-approx | √16.5 ≈ 4 + 0.5/8 = 4.0625 (true 4.06202); an overestimate, because √ is concave down | L2 | 140.3.1.definition, 140.4.4.higher |
| 140.5.3.mvt | A car covers 120 km in 1.5 h, so at some instant its speed is exactly 80 km/h | L3 | 140.2.4.ivt, 140.3.1.definition |
| 140.5.4.extrema | f = x³ − 3x on [−2, 3]: candidates −2, −1, 1, 3; max 18 at 3, min −2 (tie at −2 and 1) | L4 | 140.2.4.ivt, 140.3.2.power |
| 140.5.4.sketch | f = x³ − 3x: increasing for \|x\| > 1, inflection at 0, local max at −1 | L5 | 140.4.4.higher |
| 140.5.5.optimization | 100 m of fence along a river: x = 25, area 1250 m² | L6 | 140.5.4.extrema |
| 140.5.6.lhopital | (e^{2x} − 1)/x at 0 → 2; plus why it fails on cos x/(x + 1) | L7 | 140.2.2.factor, 140.4.1.exp-log |

(The walkthrough is allowed a tie, f(−2) = f(1) = −2, to teach that the minimum value can occur twice. Practice rejects ties so that each answer is unique.)

- [ ] **RED:** add the curriculum entries. **GREEN:** write the walkthroughs. Run `check_curriculum`, `check_concepts`, `e2e_calculus` and the full suite. Take screenshots. Commit.
