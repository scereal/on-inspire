# MATH 140 Unit 140.6 (Antidifferentiation) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the last MATH 140 unit: 4 subtopics across its 2 outcomes, each with a Learn walkthrough and a verified Practice level.

**Architecture:** One framework, `antiderivatives`, with 4 levels. Three concepts and four walkthroughs. The existing `accumulator` widget is reused: its `shift` mode shows the + C family.

**Spec:** `design/specs/2026-10-05-math-140-explorer-design.md`. §1 orders 140.6 last. Built autonomously; the user chose to keep work local.

## Global Constraints
- The same as the earlier unit plans, including every carried lesson.
- New from the 140.1 review: no answer findable by pattern. Tests check that the correct option isn't the median, the sole shortest, or the one sharing a feature with every wrong option. Evaluation points stay out of `canonical`.

## Review Focus
1. **+ C:** every general antiderivative option includes + C, so "forgot + C" can't be the giveaway or a correct-looking option. The + C step is taught in the walkthrough and concept.
2. **Reverse power rule:** dividing by n + 1 is never confused with multiplying by n. x⁻¹ is excluded from the power level (it belongs to ln).
3. **Chain in reverse:** ∫cos(kx) = sin(kx)/k. Multiplying by k is always a wrong option, and the sign of ∫sin is right.
4. **IVPs:** C is solved from the given point. The answer to f(x₁) uses that C; a distractor value made without C must differ.
5. **Motion:** v uses v₀ and s uses s₀. The signs follow the story, for example gravity is negative when up is positive.

---

### Task 1: Three concepts
- `reverse-power-rule` (deeper: power-rule, antiderivative-plus-c)
- `basic-antiderivatives` (deeper: derivative-of-sin-cos, derivative-of-exp, antiderivative-plus-c)
- `initial-value-problem` (deeper: antiderivative-plus-c)

Widgets: `accumulator` (f: square, cos), with the shift mode used for + C. Run `check_concepts`, then commit.

### Task 2: `antiderivatives` levels 1–4

| Level | Subtopic | Family | Steps |
|---|---|---|---|
| 1 | 140.6.1.power | sums of a·xⁿ (n ≠ −1, including ½ and negative powers) | choice: F(x) + C (differentiated-instead, forgot-to-divide, multiplied-by-n); number F(b) − F(a), where C cancels |
| 2 | 140.6.1.basic | a·cos kx + b·sin kx; a·e^{kx}; c/x; c·sec² kx | choice: F(x) + C (sin-sign, multiplied-by-k, differentiated-instead); number F(x₁) − F(0) (or from 1 to e) |
| 3 | 140.6.2.ivp | f′ polynomial or basic, with f(x₀) = y₀ | choice: the general antiderivative; number C; number f(x₁) |
| 4 | 140.6.2.motion | a constant or a + bt; v(0), s(0) | choice: v(t) (forgot-v0, differentiated-a); number v(T); number s(T) |

- Steps: RED tests (each Review Focus item; the pattern tests; glitch and balance scans; unique stories; ≥ 100 problems per level). Then GREEN. Run the suite, then commit.

### Task 3: Curriculum, four walkthroughs and the browser test

| Subtopic | Learn problem | Practice | Builds on |
|---|---|---|---|
| 140.6.1.power | ∫(3x² + 4x − 5) dx = x³ + 2x² − 5x + C; F(2) − F(1) = 8 | L1 | 140.3.2.power |
| 140.6.1.basic | ∫(cos x + e^{2x}) dx = sin x + ½e^{2x} + C | L2 | 140.4.1.trig, 140.4.1.exp-log |
| 140.6.2.ivp | f′ = 6x² − 2, f(1) = 5: f = 2x³ − 2x + 5, f(2) = 17 | L3 | 140.6.1.power |
| 140.6.2.motion | Ball thrown up at 15 m/s from 2 m: v = 15 − 9.8t, s = 2 + 15t − 4.9t², s(1) = 12.1 m | L4 | 140.6.2.ivp, 140.4.4.higher |

- Steps: RED curriculum entries; GREEN walkthroughs. Once every outcome is built, the map's "coming soon" path has nothing left to show, so its browser check becomes a check that no outcome says "coming soon". Run the full suite and commit.
