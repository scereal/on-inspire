# "Why?" Concept Network Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add "Why is this the case?" to all 15 steps of the square-wave, two-cups and integration-by-parts pages, opening a network of 45 first-principles concepts (plus 15 entries), each with an interactive widget.

**Architecture:** Concepts are JSON data (`docs/math/why/concepts.js`) rendered by one panel (`why.js`) and 11 reusable widgets (`widgets.js`, math in pure `WidgetMath` functions). A Python checker proves the network's structure and every math claim; JavaScriptCore tests the widget math; Playwright tests the pages.

**Tech Stack:** Vanilla JS and SVG, KaTeX 0.16.9 from cdnjs, Python 3.12 (`.venv`, SymPy), JavaScriptCore (`jsc`), Playwright (scratch environment).

**Spec:** `design/specs/2026-10-04-why-network-design.md`

## Global Constraints

- Scope: the three hand-built pages only. The practice page is untouched.
- Node format exactly as spec §3.1. `concepts.js` is `window.CONCEPTS = [...]`, valid JSON after the `=`.
- Deeper links: no loops, and every node reaches a foundation. Related links resolve. Used-by is computed, never stored.
- Every `[[id]]` in a body appears in that node's `deeper` or `related` list.
- Widget functions are named from a fixed list. No `eval` or `Function`.
- "Why?" appears only after a correct answer.
- Keyboard, touch and screen-reader support; 390 px safe; no motion on its own; localStorage wrapped in try/catch.
- Existing page behavior and tests keep passing (`tests/check_math.py`, `tests/logic_test.js`).

## Review Focus

1. **Opening "Why?" on a new step while the panel is open for an earlier step:** the panel switches to the new entry with fresh history. Tested in Task 2.
2. **KaTeX fails to load** (offline, CDN blocked): explanations still show readable raw math and nothing throws. Tested in Task 2.
3. **localStorage unavailable:** the panel works; visited marks just don't persist. Tested in Task 2.
4. **A concept with more than 8 neighbors:** the map shows 8 plus a "+N more" list. Tested in Task 2.
5. **Pressing Back at the first concept:** Back is disabled; it never errors or closes unexpectedly. Tested in Task 2.

---

### Task 1: Network checker and foundations

**Files:** Create `docs/math/why/concepts.js` (the 6 foundations), `tests/check_concepts.py`. Modify `tests/check_math.py` (call the checker). Test: `tests/test_check_concepts.py` (fixture graphs).

**Interfaces (produces):**
- `check_concepts.load(path) -> list[dict]`
- `check_concepts.problems(concepts, attach_calls) -> list[str]` (empty = valid)
- `check_concepts.attach_calls(page_paths) -> dict[entry_id, set[var]]`, parsed from `Why.attach(..., "id", {k: …})`
- `check_concepts.verify_claims(concepts) -> list[str]` (SymPy)

**Tests (fixtures):** a valid tiny graph passes; each of these is reported: a missing link target; a `[[term]]` not in the link lists; a deeper loop; a non-foundation with no deeper links; a foundation with deeper links; an orphan; a duplicate id; an unknown widget type; an entry variable not supplied; a false claim (`integrate(sin(x),(x,0,pi)) = 3`).

---

### Task 2: The panel

**Files:** Create `docs/math/why/why.js`, `docs/math/why/why.css`, `docs/math/why/atlas.html` (a list of concepts with "open" buttons; the full map comes in Task 7). Test: `tests/e2e_why.py` (Playwright; panel navigation on the atlas page).

**Interfaces:**
- `Why.attach(container, entryId, vars)`: appends a "Why is this the case?" button.
- `Why.open(entryId, vars, opener)`, `Why.close()`
- `Why.usedBy(id) -> string[]`
- Widgets are rendered through `window.Widgets?.render(type, el, config)` when present, otherwise a placeholder.

**Behavior:** trail, Back (disabled at the first concept), crumbs, three button groups, map (centre, used-by above, deeper below, related at the sides, 8 shown + "+N more", list below 480 px), Escape / Back to the problem returns focus to the opener, focus on the title after each change, visited marks stored in localStorage (try/catch), KaTeX via `renderMathInElement` when available.

**Browser tests:** open an entry; follow a term, a deeper link, a related link and a map node; Back ×2; crumb jump; Back disabled at the start; Escape returns focus; opening a second entry resets history; works with localStorage blocked (`page.add_init_script` that makes it throw) and with KaTeX blocked (route abort); no errors; 390 px with no sideways scroll.

---

### Task 3: Widgets, batch 1 (secant, limit-zoom, unit-circle, riemann, fraction-bar)

**Files:** Create `docs/math/why/widgets.js`. Test: `tests/widget_math_test.js` (jsc), hooked into `tests/check_math.py`.

**Interfaces:** `Widgets.render(type, container, config) -> {reset()}`; `WidgetMath.fn(name)` (named functions: square, cube, sin, cos, exp, sin2, cos2, sinh_over_h, cosh_minus_1_over_h, exph_minus_1_over_h); `WidgetMath.secantSlope(f, x0, h)`, `riemann(f, a, b, n, rule)`, `unitPoint(theta)`, `pour(cup, marks)`, `strength(cup)`.

**Math tests:** secant slope of x² at 1 with h = 1e-4 ≈ 2; riemann(sin, 0, π, 1000) ≈ 2; riemann(square, 0, 1, 2000) ≈ 1/3; sin h / h at 1e-4 ≈ 1; unitPoint(π/2) = (0, 1); pouring a mark keeps strength; combining (1 mark at 1/2) + (1 mark at 1/4) gives 3/8.

---

### Task 4: Two cups

**Files:** Modify `docs/math/why/concepts.js` (8 two-cups concepts + 4 entries `tc-*`), `docs/math/two-cups/index.html` (KaTeX + why files + `Why.attach` per level), `widgets.js` (fraction-bar modes: ratio, cup, pour, grid, dilute, serial, combine).

**Checks:** the network checker passes; claims such as `Rational(1,2)*Rational(1,4) = 1/8` and `(1*Rational(1,2) + 1*Rational(1,4))/2 = 3/8`; the browser test completes all 4 levels and opens Why on each.

---

### Task 5: Calculus core + integration by parts

**Files:** Modify `concepts.js` (13 core + 6 IBP concepts + 7 entries `ibp-*`), `docs/math/integration-by-parts/index.html` (`Why.attach` per item, KaTeX), `widgets.js` (accumulator, product-rectangle, chain-stretch, derivative-ladder; unit-circle squeeze and two-angle modes). Extend `widget_math_test.js`.

**Claims:** `diff(sin(x),x) = cos(x)`, `diff(exp(x),x) = exp(x)`, `limit(sin(h)/h,h,0) = 1`, `limit((cos(h)-1)/h,h,0) = 0`, `diff(x**3,x) = 3*x**2`, `integrate(sin(x),x) = -cos(x)`, `diff(x*sin(x)+cos(x),x) = x*cos(x)`, the product rule on `x*exp(x)`.

**Widget math:** the accumulator's slope at x matches f(x) (within 1e-3); four derivative-ladder steps on x³ give 0; chain-stretch area of sin(2x) on [0, π/2] = 1 (half of 2).

---

### Task 6: Square wave

**Files:** Modify `concepts.js` (12 square-wave concepts + 4 entries `sw-*`), `docs/math/square-wave/index.html` (`Why.attach` with `{A1}`, `{A3}`, `{peak}`), `widgets.js` (wave-mixer: single, gap, product, shift, partials, zoom; parabola-min: base, projection).

**Claims:** `integrate(sin(t),(t,0,pi)) = 2`, `integrate(sin(t)**2,(t,0,2*pi))/(2*pi) = 1/2`, `integrate(sin(2*t)*sin(3*t),(t,0,2*pi)) = 0`, `(integrate(sin(n*t),(t,0,pi)) - integrate(sin(n*t),(t,pi,2*pi)))/pi = 4/(n*pi)` for n = 1, 3, 5 and 0 for n = 2, the Gibbs limit `2/pi*Si(pi) ≈ 1.179`.

**Widget math:** the wave-mixer product area for m ≠ n is ≈ 0; the parabola-min minimum at 4/π for the square wave.

---

### Task 7: Atlas map, full browser test, proofread, push

**Files:** Modify `atlas.html` (whole-network map, foundations at the bottom, layered by depth), extend `tests/e2e_why.py` (every page and step; every atlas widget renders and responds). Proofread all 60 nodes on the atlas (wording, the "deeper = more basic" direction). Run `tests/check_math.py`, `tests/e2e_why.py` and `tests/e2e_practice.py`, then commit and push.
