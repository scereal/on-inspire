# Verified Math Problem Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate, validate and serve banks of verified math problems from four frameworks (integration by parts, projectile, mixing, bouncing ball), with a practice page and a review page on the static site.

**Architecture:** Python frameworks (`generator/frameworks/*.py`) implement one contract: `sample → solve → checks`. A shared validator pipeline (`generator/core/validators.py`) accepts or rejects each candidate, and `build_bank.py` writes accepted problems as deterministic JSON to `docs/math/bank/`. A static practice page renders problems with a shared player and one scene renderer per framework.

**Tech Stack:** Python 3.12 (project `.venv`), SymPy, PyYAML, unittest. Vanilla JS/SVG, KaTeX from cdnjs for math labels. Playwright (scratch environment only) for the browser test.

**Spec:** `design/specs/2026-10-04-problem-generator-design.md`

## Global Constraints

- Run everything with `.venv/bin/python` (Python 3.12, sympy, pyyaml). No other dependencies.
- Bank output must be deterministic: same framework + seed → byte-identical JSON (sorted keys, no timestamps).
- Every banked problem passes: exists, unique, clean, taught_tools, distinct, plausible, findable, and no duplicate canonical form.
- At least 300 verified problems per framework, at least 3 levels each.
- Build fails if a framework accepts fewer than 5% of its candidates.
- Projectile model: no drag, g = 9.8 m/s² (1.6 on the Moon theme). The paper airplane is not a projectile theme.
- Bounce: height fraction r = e² when starting from the coefficient of restitution e.
- No "which u?" step on integration-by-parts loop problems.
- Browser storage access wrapped in try/catch; the page works without it.
- Practice/review pages must not require a build step and must work at 390 px width.

## Review Focus

1. **Distractor equal to the answer for special values** (a = 1 makes "dropped 1/a" correct; equal amounts make the unweighted average correct): the problem must be rejected. Tested in Tasks 2, 5 and 6.
2. **Projectile target exactly at maximum range** (one angle instead of two) or beyond it (none): rejected. Tested in Task 4.
3. **Bounce height landing on the threshold within rounding:** rejected. Tested in Task 6.
4. **A bank file missing or empty for a level** (fetch fails): the practice page shows a clear message instead of a blank page. Tested in Task 7's browser test.
5. **Slider answer at the edge of the slider range or off the grid:** rejected by the findable check. Tested in Task 1.

---

### Task 1: Core: contract, validators, bank writer, audit

**Files:**
- Create: `generator/__init__.py`, `generator/core/__init__.py`, `generator/core/framework.py`, `generator/core/validators.py`, `generator/core/themes.py`, `generator/core/bank.py`, `generator/build_bank.py`, `generator/audit_bank.py`, `generator/requirements.txt`
- Test: `generator/tests/test_core.py` (uses a tiny fake framework)

**Interfaces (produces):**
- `framework.Option(label: str, correct: bool = False, misconception: str | None = None, feedback: str = "", value: float | str | None = None)`
- `framework.Step(prompt: str, format: "choice" | "number" | "slider" | "mix", answer, options: list[Option] = [], tolerance: float = 0, unit: str = "", slider: dict | None = None, explain: str = "")`
- `framework.Solution(steps: list[Step], story: str, scene: dict, tools: list[str], answers: dict)`
- `framework.NoSolution(Exception)`
- `framework.Framework` with attributes `id, title, outcome, levels: dict[int, Level], misconceptions: dict[str, str], targets: dict[int, int]`, and methods `sample(rng, level, theme) -> dict`, `solve(params, level, theme) -> Solution`, `count_solutions(params, level) -> int`, `plausibility(params, level, theme) -> list[(name, value)]`, `checks(params, level, theme, solution) -> list[(name, ok, reason)]`, `canonical(params, level) -> str`.
- `framework.Level(name: str, tools: dict[str, int])`: allowed tool → max uses.
- `validators.validate(fw, params, level, theme, solution) -> (ok: bool, reason: str | None, report: dict)`
- `themes.load_themes(framework_id) -> list[dict]`, `themes.in_range(theme, name, value) -> bool`
- `bank.build(fw, count, seed) -> (problems_by_level: dict[int, list[dict]], report: dict)`, `bank.write(fw, problems_by_level, report)`, `bank.rebuild_problem(fw, record) -> dict`
- CLI: `python -m generator.build_bank <framework> --count N --seed S`, `python -m generator.audit_bank`

**Tests (test_core.py):**
- A valid fake problem passes and gets a full validation report.
- Rejections with the right reason: solve raises NoSolution → "exists"; count_solutions = 2 → "unique"; a choice step with two correct options → "distinct"; a distractor value equal to the answer → "distinct"; two numeric options within 10% → "distinct"; tools beyond the level → "taught_tools"; out-of-theme range → "plausible"; slider answer off grid or outside [min, max] → "findable".
- Duplicate canonical forms are kept once.
- The same seed builds byte-identical JSON; a different seed differs.
- `rebuild_problem` reproduces a stored record exactly.
- The build raises if acceptance < 5%.

---

### Task 2: Integration by parts framework

**Files:** Create `generator/frameworks/__init__.py` (registry `FRAMEWORKS: dict[str, Framework]`), `generator/frameworks/ibp.py`. Test: `generator/tests/test_ibp.py`. Bank: `docs/math/bank/ibp-{1..4}.json`.

**Levels:**
1. c·x·g(ax), g ∈ {exp, sin, cos}, a ∈ {1, 2, 3, 4, 1/2, 1/3}, c ∈ {1..6}. Steps: which u (choice) → find v (choice) → final answer (choice).
2. c·xⁿ·g(ax), n ∈ {2, 3}. Steps: how many rounds (choice) → which u (choice) → final answer (choice).
3. c·eᵃˣ·{sin, cos}(bx), a, b ∈ {1..4}. Steps: what reappears after two rounds (choice) → solve for I (choice). No which-u step.
4. c·xⁿ·ln(kx), n ∈ {1, 2, 3}, k ∈ {1, 2, 3}. Steps: which u (choice) → final answer (choice).

**Misconceptions:** u-gets-harder, whole-product-as-u, differentiated-for-v, dropped-1-over-a, trig-sign, tabular-sign, stopped-early, loop-vanishes, loop-grows, loop-sign, forgot-to-divide, polynomial-habit, forgot-square.

**Checks:** every answer differentiates back to the integrand (SymPy); every distractor answer does not; "which u" uniqueness by actually running one round of parts per option and testing whether the result is basic (polynomial-free trig/exp, or polynomial with no log); rationals in answers have numerator and denominator ≤ 60.

**Tests:** level 1 a = 1 rejects (dropped-1-over-a equals the answer); level 2 rounds answer equals n; loop coefficient is −b²/a²; level 4 rejects u = xⁿ by the uniqueness probe; loop problems have no which-u step; bank ≥ 300 with every level present.

---

### Task 3: Themes

**Files:** Create `generator/themes/*.yaml`. Test: `generator/tests/test_themes.py`.

Themes: projectile (ball, stomp-rocket, water-balloon, basketball, bb, moon-ball), bounce (superball, basketball, tennis-ball, golf-ball, clay), mixing (tea, orange-juice, squash, cold-brew). Each has `id, framework, label, visuals {color, shape, scene}`, `physics` ranges, `levels` it supports, and `stories` (templates with `{placeholders}`).

**Tests:** required fields; ranges are [low, high] with low < high and inside global limits (speed ≤ 120 m/s, height ≤ 50 m, restitution in (0, 1)); every framework except ibp has at least 3 themes; every story template's placeholders are filled by that framework's params.

---

### Task 4: Projectile framework

**Files:** `generator/frameworks/projectile.py`, test `generator/tests/test_projectile.py`, bank `docs/math/bank/projectile-{1..4}.json`.

**Levels:**
1. Horizontal launch from height h to distance d: flight time (choice) → vₓ (slider, step 0.1) → same-time-as-dropped (choice).
2. Ground launch, fixed vᵧ: flight time 2vᵧ/g (choice) → vₓ (slider) → doubling vₓ doesn't change time (choice).
3. Fixed speed v and distance d: how many angles (choice, answer 2) → lower angle (slider, step 1°) → other angle = 90° − θ (choice). Reject at or beyond maximum range, and when the computed angle isn't within 0.2° of a whole degree.
4. Fixed vₓ, wall at distance w with height H: time to wall (choice) → vᵧ to pass the wall top (slider) → rising or falling at the wall (choice; reject if within 3% of the peak).

**Checks:** independent time-step simulation (dt = 1e-4) lands within 0.05 m of the target (or passes within 0.05 m of the wall top); values inside theme ranges; slider answers on grid.

**Tests:** simulation agreement for each level; must-reject: d at max range, d beyond it, 300 m/s stomp rocket; distractor "forgot the 2" equals exactly half of the correct time; bank ≥ 300.

---

### Task 5: Mixing framework

**Files:** `generator/frameworks/mixing.py`, test `generator/tests/test_mixing.py`, bank `docs/math/bank/mixing-{1..3}.json`.

Cups A and B with 3–6 marks each; moves: add concentrate, add water, pour one mark across, empty (same as the two-cups page). A breadth-first search with exact `Fraction`s finds every reachable strength and its minimum moves per cup pair (cached).

**Levels:**
1. Ratio a:b from a recipe → fraction (choice) → build a/(a+b) (mix step, minimum moves ≤ 4).
2. Can you make s with these cups? (choice, yes) → build s requiring dilution (denominator > max marks; minimum moves ≤ 8) → what diluting does (choice).
3. Weighted average of m₁ marks at s₁ and m₂ at s₂ (choice) → build it (minimum moves ≤ 10).

**Tests:** BFS result re-checked by replaying the move path with Fraction arithmetic; equal amounts reject at level 3 (unweighted average equals the answer); a = b rejects at level 1 (water share equals the answer); bank ≥ 300.

---

### Task 6: Bouncing ball framework

**Files:** `generator/frameworks/bounce.py`, test `generator/tests/test_bounce.py`, bank `docs/math/bank/bounce-{1..4}.json`.

**Levels:**
1. Height after the first bounce (choice) → height after n bounces (number, tolerance 0.01 m) → does it ever stop in this model (choice).
2. Distance between first and second floor hit, 2hr (choice) → total distance h + 2hr/(1−r) (choice) → total distance (number).
3. Given e: height fraction e² (choice) → height after n bounces (number).
4. Bounces until below threshold T (choice of integers). Reject if any h·rⁿ is within 2% of T.

**Checks:** 200-bounce simulation sum matches the closed form within 0.1%; e inside the theme's range.

**Tests:** simulation agreement; threshold-edge rejection; e-not-squared distractor equals e·h; bank ≥ 300.

---

### Task 7: Practice page

**Files:** Create `docs/math/practice/index.html`, `docs/math/practice/player.js`, `docs/math/practice/scenes.js`. Modify `docs/math/index.html` (practice links), `docs/math/two-cups/index.html` and `docs/math/integration-by-parts/index.html` ("Practice more like this" link). Test: `tests/e2e_practice.py` (Playwright; skipped when not installed).

- No `?f=`: a picker listing the four frameworks and their levels.
- `?f=<id>&level=<n>`: fetch `../bank/<id>-<n>.json`, pick a random unseen problem (seen IDs in localStorage, try/catch), render the story and scene, then the steps: choice, number (tolerance), slider (live scene update), mix (two-cup bench using the problem's cup sizes and theme color). Per-misconception feedback; the next step unlocks after a correct answer.
- After 3 first-try solves in a row, suggest the next level; otherwise offer "Another one like this."
- KaTeX (cdnjs) renders `$...$` in labels.
- A missing bank file shows "This level isn't available yet" with a link back to the picker.

**Browser test:** for each framework and level: load, answer one step wrong then right, see feedback, finish the problem; no page errors; phone and desktop widths; a missing level shows the message.

---

### Task 8: Review page, test hook, docs, push

**Files:** Create `docs/math/review/index.html`, `docs/math/bank/review.json`. Modify `tests/check_math.py` (run generator unit tests + audit), `generator/README.md`.

- Review page: shows report.json acceptance stats and 10 random problems per framework, each with its steps, answers and distractors. "Looks good" / "Reject" buttons (with a reason) store decisions locally, and "Copy decisions" gives JSON to paste into `docs/math/bank/review.json`.
- `build_bank` skips IDs listed as rejected in review.json; the audit fails if one is present.
- Run the full suite, build all four banks, run the browser test, commit and push.
