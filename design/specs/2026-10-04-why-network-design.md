# "Why?" Concept Network: Design

**Date:** 2026-10-04
**Status:** Draft for review

## 1. Purpose

On the three hand-built math pages (square wave, two cups, integration by parts), let a learner who has just answered a step ask **"Why is this the case?"** and explore a **network of first-principles explanations**, each with its own small interactive. Every chain of "why" ends at a genuine foundation: a definition or basic law.

**Who it's for:** learners on the portfolio pages, and Brilliant reviewers judging how the ideas are taught.

**Success criteria**
- All 15 steps on the three pages offer "Why is this the case?" after a correct answer.
- About 45 shared concepts plus 15 step-specific entry explanations, each with an interactive widget.
- The network has three kinds of link (deeper, related, used-by), a concept map, a browser-style Back, a trail, and "Back to the problem".
- The validator proves: links resolve, deeper links have no loops and always reach a foundation, no orphans, page variables are supplied, and every stated math claim is true (SymPy).
- It works with keyboard, touch and screen readers, at 390 px wide, with reduced motion respected.

**Out of scope:** the practice page and generated problems; typed answers; accounts or analytics.

## 2. Approach

The concepts are **data**, rendered by a **small library of reusable widgets** (11 types) and one **panel**. Two alternatives were rejected: a custom interactive per concept (about 50 mini-apps: slow, inconsistent, hard to test), and text-first with visuals added later (doesn't meet the "interactive for each concept" requirement).

## 3. The network

### 3.1 Node format
```js
{
  "id": "integral-as-area",
  "title": "The integral is area, built from rectangles",
  "body": "… [[limit]] … [[area-shapes]] …",          // [[id]] renders as a button
  "math": ["\\int_a^b f(x)\\,dx = \\lim_{n\\to\\infty} \\sum_{i=1}^{n} f(x_i)\\,\\Delta x"],
  "widget": { "type": "riemann", "f": "square", "a": 0, "b": 1 },
  "deeper": ["limit", "area-shapes"],                // "true because of…"
  "related": ["derivative", "average-of-function"],  // sideways
  "foundation": false,
  "claims": [{ "sympy": "integrate(x**2, (x, 0, 1))", "equals": "1/3" }]
}
```
- **Entry nodes** (`"entry": true`) are written for one step and may contain `{variables}` filled in by the page (e.g. `{A1}` = 1.27).
- **Used-by** links are computed as the reverse of deeper links, never stored.
- Every `[[id]]` in a body must also appear in that node's `deeper` or `related` list.

### 3.2 Foundations (6)
| id | Idea | Widget |
|---|---|---|
| `function` | A rule that turns each input into one output | secant (trace mode: move x, read f(x)) |
| `limit` | The value a quantity settles toward, including the ε–δ idea | limit-zoom (shrinkable ε band) |
| `unit-circle` | sin θ and cos θ are the coordinates of a point on the unit circle | unit-circle |
| `area-shapes` | Area of rectangles and triangles | riemann (shapes mode) |
| `fraction-as-parts` | a/b means a of b equal parts | fraction-bar |
| `conservation` | Pouring moves concentrate around; it never creates or destroys it | fraction-bar (pour mode) |

### 3.3 Shared calculus core (13)
| id | Deeper | Related | Widget |
|---|---|---|---|
| `derivative` | limit, function | integral-as-area | secant (x², x₀ = 1) |
| `integral-as-area` | limit, area-shapes | derivative, average-of-function | riemann (x² on [0, 1]) |
| `ftc` (fundamental theorem) | derivative, integral-as-area | antiderivative-plus-c | accumulator (cos) |
| `antiderivative-plus-c` | derivative, ftc | check-by-differentiating | accumulator (shift mode) |
| `sin-h-over-h` | limit, unit-circle, area-shapes | cos-h-minus-1-over-h | unit-circle (squeeze mode) |
| `cos-h-minus-1-over-h` | sin-h-over-h, limit | | limit-zoom |
| `angle-addition` | unit-circle | product-to-sum | unit-circle (two-angle mode) |
| `derivative-of-sin-cos` | derivative, angle-addition, sin-h-over-h, cos-h-minus-1-over-h | sine-waves | secant (sin) |
| `product-rule` | derivative, limit | chain-rule | product-rectangle |
| `chain-rule` | derivative | product-rule | chain-stretch |
| `power-rule` | derivative | polynomial-as-u | secant (x³) |
| `derivative-of-exp` | derivative, limit | | limit-zoom ((eʰ − 1)/h) |
| `product-to-sum` | angle-addition | orthogonality | wave-mixer (product mode) |

### 3.4 Square wave (12)
| id | Deeper | Related | Widget |
|---|---|---|---|
| `sine-waves` | unit-circle, function | | wave-mixer (single) |
| `average-of-function` | integral-as-area | why-square-the-gap, weighted-average | riemann (average mode) |
| `why-square-the-gap` | average-of-function | best-fit-parabola | wave-mixer (gap mode) |
| `best-fit-parabola` | derivative, why-square-the-gap | projection | parabola-min |
| `projection` | best-fit-parabola, integral-as-area | orthogonality | parabola-min (projection mode) |
| `integral-sin-half-period` (= 2) | ftc, derivative-of-sin-cos | average-of-sin-squared | riemann (sin on [0, π]) |
| `average-of-sin-squared` (= ½) | average-of-function, unit-circle | integral-sin-half-period | riemann (sin² vs cos²) |
| `orthogonality` | product-to-sum, integral-as-area | projection, half-wave-symmetry | wave-mixer (product mode, m = 2, n = 3) |
| `half-wave-symmetry` | integral-as-area, sine-waves | orthogonality | wave-mixer (shift-by-π mode) |
| `coefficients-4-over-n-pi` | projection, integral-sin-half-period, chain-rule, average-of-sin-squared | partial-sums | wave-mixer |
| `partial-sums` | limit, sine-waves | gibbs | wave-mixer (N slider) |
| `gibbs` | partial-sums, integral-as-area | why-square-the-gap | wave-mixer (zoom at jump) |

### 3.5 Integration by parts (6)
| id | Deeper | Related | Widget |
|---|---|---|---|
| `parts-is-product-rule-backwards` | product-rule, ftc | minus-sign-in-parts | product-rectangle |
| `minus-sign-in-parts` | parts-is-product-rule-backwards | | product-rectangle (strip mode) |
| `polynomial-as-u` | power-rule, parts-is-product-rule-backwards | | derivative-ladder |
| `one-over-a` | chain-rule, antiderivative-plus-c | integral-of-sin | chain-stretch (area mode) |
| `integral-of-sin` (= −cos) | derivative-of-sin-cos, antiderivative-plus-c | one-over-a | accumulator (sin) |
| `check-by-differentiating` | ftc, antiderivative-plus-c | integral-of-sin | accumulator |

### 3.6 Two cups (8)
| id | Deeper | Related | Widget |
|---|---|---|---|
| `ratio-vs-fraction` | fraction-as-parts | strength | fraction-bar (ratio mode) |
| `strength` | fraction-as-parts, conservation | ratio-vs-fraction | fraction-bar (cup mode) |
| `pouring-keeps-strength` | strength, conservation | diluting-multiplies | fraction-bar (pour mode) |
| `fraction-of-a-fraction` | fraction-as-parts | equivalent-fractions | fraction-bar (grid mode) |
| `diluting-multiplies` | strength, fraction-of-a-fraction | weighted-average | fraction-bar (dilute mode) |
| `serial-dilution` | diluting-multiplies, pouring-keeps-strength | equivalent-fractions | fraction-bar (serial mode) |
| `weighted-average` | strength, conservation | average-of-function | fraction-bar (combine mode) |
| `equivalent-fractions` | fraction-as-parts | fraction-of-a-fraction | fraction-bar (grid mode) |

### 3.7 Entry explanations (15)
| Page and step | Entry id | Deeper |
|---|---|---|
| Square wave 1: fit one sine | `sw-best-height` ({A1}) | projection, best-fit-parabola, integral-sin-half-period, average-of-sin-squared |
| Square wave 2: second sine | `sw-why-sin3t` ({A3}) | half-wave-symmetry, orthogonality |
| Square wave 3: the pattern | `sw-pattern` | coefficients-4-over-n-pi |
| Square wave 4: overshoot | `sw-gibbs` ({peak}) | gibbs, partial-sums |
| Two cups 1: half and half | `tc-half` | strength, equivalent-fractions |
| Two cups 2: one to three | `tc-one-to-three` | ratio-vs-fraction, strength |
| Two cups 3: 1/8 | `tc-one-eighth` | serial-dilution, diluting-multiplies |
| Two cups 4: 3/8 | `tc-three-eighths` | weighted-average, pouring-keeps-strength |
| IBP 1: pick u | `ibp-pick-u` | polynomial-as-u, parts-is-product-rule-backwards |
| IBP 2: sign error (∫ sin) | `ibp-sign` | integral-of-sin, check-by-differentiating |
| IBP 3: v = 3e³ˣ error | `ibp-v` | one-over-a, derivative-of-exp |
| IBP 4: fill the blank | `ibp-blank` | parts-is-product-rule-backwards, polynomial-as-u |
| IBP 5: chain-rule factor | `ibp-chain` | one-over-a, chain-rule |
| IBP 6: flipped minus | `ibp-minus` | minus-sign-in-parts |
| IBP 7: check by differentiating | `ibp-check` | check-by-differentiating, product-rule |

## 4. Widgets (11)

Shared `docs/math/why/widgets.js`. Each widget is `render(container, config)`, with its math in pure functions (`WidgetMath`) so it can be tested. Functions are chosen by name from a fixed list (`square`, `cube`, `sin`, `cos`, `exp`, `sin2`, …). Concept data never runs code.

| Widget | Interaction | Modes |
|---|---|---|
| `secant` | Drag h toward 0; the secant becomes the tangent; slope readout | trace |
| `limit-zoom` | Zoom toward h = 0; value readout; shrinkable ε band | |
| `riemann` | Rectangle-count slider; sum vs exact area | shapes, average |
| `accumulator` | Sweep x; accumulated area graphed; slope matches f | shift (+C) |
| `unit-circle` | Drag the angle; sin and cos as coordinates | squeeze, two-angle, trace |
| `wave-mixer` | Sine sliders over a target; gap shading | single, gap, product, shift, partials, zoom |
| `parabola-min` | Drag a; the error parabola and its minimum | projection |
| `product-rectangle` | A u × v rectangle grows by du, dv; strips labelled | strip |
| `chain-stretch` | Slide a: g(x) → g(ax); slopes × a, areas ÷ a | area |
| `derivative-ladder` | Tap "differentiate": a polynomial reaches 0; sin and eˣ cycle | |
| `fraction-bar` | Split, pour, combine bars of parts | ratio, cup, pour, grid, dilute, serial, combine |

Every widget: a "Try this" prompt, a live readout (`aria-live`), Reset, keyboard and touch control, no motion on its own, 390 px safe.

## 5. The panel

- **Trigger:** after a correct answer, the step's feedback box gains **"Why is this the case?"**. Pages call `Why.attach(feedbackBox, entryId, variables)`.
- **Inline panel** below the step:
  - trail and **Back**
  - title, explanation with term buttons, math (KaTeX), widget
  - three button groups: **Why? Go deeper**, **Related ideas**, **Where else this is used**
  - concept map
  - **Back to the problem**
- **Concept map:** current concept in the centre, used-by above, deeper below, related to the sides. Visited concepts are marked; up to about 8 neighbors are shown, then a "+N more" list. Below 480 px the map becomes a compact list.
- **Navigation:** every jump pushes onto a history list. **Back** pops it. Trail crumbs jump back several steps. **Escape** or **Back to the problem** closes the panel and returns focus to the trigger button. Focus moves to the title on every change.
- **Visited** concepts persist in localStorage (wrapped in try/catch; the page works without it).
- **Files:** `docs/math/why/concepts.js` (`window.CONCEPTS = [...]`, valid JSON after `=`), `widgets.js`, `why.js`, `why.css`. The three pages load these plus KaTeX from cdnjs.

## 6. Validation and testing

1. **Network checks** (Python, part of `tests/check_math.py`):
   - unique IDs, required fields, valid widget types and settings;
   - every link and `[[term]]` resolves, and every term is in that node's link lists;
   - deeper links have no loops, every non-foundation has at least one deeper link, foundations have none, and every node reaches a foundation;
   - every concept is reachable from an entry, and all 15 entries exist;
   - every `{variable}` in an entry is supplied by its page's `Why.attach` call.
2. **Math claims:** every `claims` item is proven with SymPy.
3. **Widget math:** `WidgetMath` functions are tested via JavaScriptCore. For example: the Riemann sum for sin on [0, π] → 2; the secant slope of x² at 1 → 2; ∫ sin 2t sin 3t over a period → 0; pouring keeps strength; differentiating x³ four times gives 0.
4. **Concept atlas** (`docs/math/why/atlas.html`): every concept with its widget and links, plus the whole network map. Used for proofreading and as a portfolio exhibit.
5. **Browser test** (phone and desktop):
   - on each page, complete each step, open Why?, then follow a term, a deeper link, a related link and a map node;
   - use Back, a trail crumb and Back to the problem, and check focus returns;
   - on the atlas page, every widget renders and responds to one interaction;
   - no JavaScript errors and no sideways scrolling anywhere.

## 7. Build order

1. Panel, network checks, and the foundations with their widgets (secant, limit-zoom, unit-circle, riemann, fraction-bar).
2. Two cups: its concepts and entries, with the fraction-bar modes.
3. Integration by parts: accumulator, product-rectangle, chain-stretch, derivative-ladder, plus the calculus core.
4. Square wave: wave-mixer, parabola-min, plus its concepts and entries.
5. Atlas page, browser test, final proofread.
