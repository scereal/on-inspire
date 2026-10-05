# MATH 140 Calculus Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `/calculus/math-140/`: an outcome map of all six MATH 140 units, with unit 140.3 (the derivative) fully built. That means 8 Learn walkthroughs, two verified Practice frameworks, "Builds on" tags, and entrances from the homepage and gallery.

**Architecture:** A JSON curriculum file drives a static map page. A Learn player renders JSON walkthroughs and reuses the "Why?" panel and widgets. Two new generator frameworks feed the existing practice page. Python checkers verify the data and the math; Playwright tests the pages.

**Tech Stack:** Vanilla JS/SVG, KaTeX 0.16.9 (cdnjs), Web Speech API (optional), Python 3.12 (`.venv`: SymPy, PyYAML), JavaScriptCore, Playwright (scratch environment).

**Spec:** `design/specs/2026-10-05-math-140-explorer-design.md`

## Global Constraints

- The `official` text must equal, verbatim: "Review of functions and graphs. Limits, continuity, derivative. Differentiation of elementary functions. Antidifferentiation. Applications."
- `curriculum.js` and `walkthroughs.js` are `window.X = ...` and valid JSON after the `=`.
- `builds_on` targets: existing outcome or subtopic IDs, or `foundation:<concept-id>`. No loops.
- Learn steps ask a question first; the narration appears only after a correct answer.
- Read aloud is hidden when `speechSynthesis` is unavailable.
- Each new framework banks at least 300 verified problems and passes the existing validator pipeline and audit.
- No CLP text or problems are copied.
- 390 px safe, keyboard-operable, browser storage in try/catch, existing suite stays green.

## Review Focus

1. **A tag pointing to an outcome in a unit that isn't built yet** (e.g. 140.2.1): the map opens that outcome and shows "coming soon", and nothing breaks. Tested in Task 1.
2. **A deep link to an unknown hash** (`#140.9.9`): the map loads normally, with nothing opened. Tested in Task 1.
3. **A Learn walkthrough ID that doesn't exist:** a clear message plus a link back to the map. Tested in Task 2.
4. **Speech synthesis absent or throwing:** Read aloud is hidden and the walkthrough still works. Tested in Task 2.
5. **Practice opened without a curriculum match** (e.g. an old ibp link): the practice page works unchanged, with no tags. Tested in Task 5.

---

### Task 1: Curriculum data, checker, map page, entrances

**Files:**
- Create: `docs/calculus/curriculum.js` (all six units' outcomes; unit 140.3 subtopics with `learn`/`practice` set to null for now), `docs/calculus/math-140/index.html`, `docs/calculus/calculus.css`, `tests/check_curriculum.py`, `tests/test_check_curriculum.py`, `tests/e2e_calculus.py`.
- Modify: `docs/index.html` (math hub leaf), `docs/math/index.html` (calculus + atlas sections), `tests/check_math.py`.

**Interfaces (produces):**
- `check_curriculum.load()`
- `check_curriculum.problems(curriculum, walkthrough_ids, bank_index, concept_ids) -> list[str]`
- Map page: `#<id>` deep links; chips are `<a data-target="<id>">`.

**Tests (fixtures):** a valid curriculum passes; each of these is reported: a duplicate ID; a subtopic ID not prefixed by its outcome ID; an unknown `learn` ID; an unknown practice framework or level; an unknown `builds_on` target; a `builds_on` loop; altered `official` text.

**Browser tests:** outcomes open and close; a chip to 140.2.1 opens it with "coming soon"; `#140.3.2` opens on load; `#140.9.9` opens nothing and raises no error; the homepage leaf and gallery links reach the map and the atlas; 390 px with no sideways scroll.

---

### Task 2: Learn player, walkthrough checks, new concepts

**Files:**
- Create: `docs/calculus/learn/index.html`, `docs/calculus/learn/player.js`, `docs/calculus/learn/walkthroughs.js` (empty list), `tests/check_walkthroughs.py` (merged into `check_curriculum` as a module).
- Modify: `docs/math/why/concepts.js` (5 concepts), `docs/math/why/widgets.js` (`abs`), `tests/check_concepts.py` (walkthroughs count as entry points), `tests/widget_math_test.js`.

**Tests:**
- Walkthrough fixtures: an unknown `[[term]]`; a choice step with zero or two correct options; a wrong option without feedback; a false claim; an unknown step `builds_on`. Each is reported.
- `abs` gives one-sided slopes of −1 and +1 at 0.
- Concept checker: a concept reachable only from a walkthrough isn't an orphan.
- Browser, using a fixture walkthrough served in place of `walkthroughs.js`: a wrong answer shows feedback; the right answer reveals the narration; a "Why?" term opens the panel; Next and Finish link to practice; an unknown ID shows a message; Read aloud is hidden when `speechSynthesis` is deleted.

---

### Task 3: `derivative-definition` framework + walkthroughs 140.3.1

**Files:**
- Create: `generator/frameworks/derivative_definition.py`, `generator/themes/rate-*.yaml` (position, temperature, population), `generator/tests/test_derivative_definition.py`, bank `docs/math/bank/derivative-definition-{1..3}.json`.
- Modify: `generator/frameworks/__init__.py` (register), `walkthroughs.js` (3), `curriculum.js` (fill in `learn`/`practice` for 140.3.1.*).

**Tests:**
- The SymPy limit of each difference quotient equals `diff`.
- Must-reject: early h = 0 substitution gives the right number; a corner misclassified.
- Level 3 classifications are checked against one-sided limits.
- At least 300 problems.
- Walkthrough claims, e.g. `expand(((3+h)**2 - 9)/h) = 6 + h`, and the ball's speed at t = 2.

---

### Task 4: `derivative-rules` framework + walkthroughs 140.3.2

**Files:** Create `generator/frameworks/derivative_rules.py`, `generator/tests/test_derivative_rules.py`, bank `derivative-rules-{1..6}.json`. Modify the registry, `walkthroughs.js` (5) and `curriculum.js` (140.3.2.*, plus outcome-level L6).

**Tests:**
- Each distractor function produces its named mistake on a hand-worked example.
- Must-reject: a dropped inner derivative when the inner derivative is 1; an ambiguous outermost rule (a constant times a product); an unclean evaluation value.
- "Which rule first" is unique.
- At least 300 problems.
- Walkthrough claims: the balloon's dV/dt = 72π, the quotient-rule derivation, the growing rectangle's area rate.

---

### Task 5: Practice integration, full browser test, proofread, push

**Files:** Modify `docs/math/practice/player.js` (outcome link + chips from a curriculum lookup by framework and level; per-subtopic streak key) and `tests/e2e_calculus.py` (full flow), plus `tests/e2e_practice.py` if needed.

**Tests:**
- Practice from the map shows the outcome link and tags.
- An ibp practice level still works, with no tags.
- All 8 walkthroughs played (wrong, then right, per step).
- Every walkthrough's widgets render.
- Phone and desktop.
- The full suite: `tests/check_math.py`, `tests/e2e_why.py`, `tests/e2e_practice.py`, `tests/e2e_calculus.py`.

Proofread every walkthrough and concept. Then commit, and offer integration through finishing-a-development-branch.
