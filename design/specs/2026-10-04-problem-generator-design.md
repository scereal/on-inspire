# Verified Math Problem Generator: Design

**Date:** 2026-10-04
**Status:** Draft for review

## 1. Purpose

Generate a practically endless supply of math problems from a small set of strong, hand-designed **frameworks**. Each framework encodes a problem type, a physical example or analogy, and a learning progression. Code validates every generated problem, and only problems that pass go into a **problem bank** that the site draws from at random.

**First goal:** a portfolio piece for the Brilliant Math Learning Designer application. It shows the problems and the system behind them: frameworks, validators and a reviewed bank.
**Later goal:** a practice section on On Inspire. Version 1 is structured so it can grow into that without a rewrite.

**Success criteria for version 1**
- Four frameworks (integration by parts, projectile aim, mixing, bouncing ball), each with at least 3 levels and several themes.
- At least 300 verified problems per framework, each passing every check in Section 4.
- A practice page that serves a random unseen problem per framework and level, at phone and desktop sizes.
- A review page for spot-checking generated problems and marking them reviewed or rejected.
- One command that re-validates the whole bank and runs every test.

## 2. Approach

Problems are **generated and validated ahead of time** in Python (with SymPy), written to a JSON bank under `docs/`, and served by the static GitHub Pages site. Alternatives that were considered and rejected:
- **Live generation in the browser:** no SymPy, weaker proofs, and no reviewable bank.
- **A hybrid:** the validation logic would exist in two languages and drift apart.

## 3. Structure

```
generator/
  core/
    framework.py     Framework base class (the contract in 3.1)
    validators.py    shared checks (Section 4)
    themes.py        theme loading and validation
    bank.py          canonical hashing, deduplication, writing bank files and report
  frameworks/
    ibp.py  projectile.py  mixing.py  bounce.py
  themes/            one YAML file per theme
  build_bank.py      CLI: python generator/build_bank.py <framework> --count N --seed S
  audit_bank.py      re-runs every validator on every banked problem
  tests/
docs/math/bank/      <framework>-<level>.json, report.json, review.json (verified problems only)
docs/math/practice/  practice page + shared player module + one scene renderer per framework
docs/math/review/    review page (not linked from the site)
```

### 3.1 Framework contract
Each framework defines:
1. **Teaching design:** learning outcome, allowed tools per level, levels, and named misconceptions (each with feedback text).
2. **`sample(rng, level, theme)`:** draws parameter values from allowed sets for that level and theme.
3. **`solve(params)`:** returns the full worked solution as an ordered list of **steps**. Each step has a prompt, a format (`choice`, `number`, `slider`), the correct answer (plus tolerance for numbers and sliders), and wrong options produced by misconception functions.
4. **`checks`:** framework-specific validators, run alongside the shared ones.
5. **Story templates:** several wordings per theme, so repeated problems don't read identically.

### 3.2 Themes
A theme is a YAML file that sets the story wording, the visuals and the realistic physical ranges:
```yaml
id: superball
framework: bounce
label: "a superball"
visuals: { color: "#c45c4a", shape: ball-small, scene: playground }
physics: { restitution: [0.85, 0.92] }
```
- **Mixing:** tea concentrate, orange juice concentrate (1:3 can recipe), fruit squash or cordial (about 1:4 to 1:10), cold-brew coffee concentrate (about 1:1 to 1:2).
- **Bounce:** superball (e ≈ 0.85–0.9), basketball (≈ 0.8), tennis ball (≈ 0.75), golf ball (≈ 0.8), clay (≈ 0.1, as a contrast).
- **Projectile:** ball, stomp rocket, water balloon, basketball over a wall, a BB fired level from a table (short range only), and a throw on the Moon (g = 1.6 m/s²).
- **Paper airplane:** not a projectile theme. Its flight is dominated by lift and drag, so it appears only in a deliberate "when does the model break?" step.
- **Visuals:** version 1 uses one simple SVG per object plus a palette per theme, in the site's existing style. A theme without a drawing falls back to text and a generic shape.

### 3.3 Problem record
```json
{ "id": "ibp-2-8f3a1c", "framework": "ibp", "level": 2, "theme": null, "seed": 4127,
  "params": {}, "story": "...",
  "steps": [{ "prompt": "...", "format": "choice", "answer": "...",
              "options": [{ "label": "...", "misconception": "u-gets-harder", "feedback": "..." }] }],
  "validation": { "exists": true, "unique": true, "clean": true, "taught_tools": ["parts", "parts"],
                  "distinct": true, "plausible": true, "findable": true },
  "generator_version": "1.0" }
```
The seed and generator version make every problem exactly reproducible.

## 4. Validation

Pipeline per candidate: **sample → solve → checks (cheapest first) → accept, or reject with a reason.** Rejection counts per reason go to `report.json`.

| Check | Rule |
|---|---|
| Exists | The solver finds a solution: a closed form (IBP), real positive roots (physics), a reachable target (mixing, via search over pour sequences). |
| Unique | The asked-for quantity has exactly one valid answer under the givens. The validator counts solutions; for choice steps it tries every option. |
| Clean numbers | Givens come from allowed sets per level. Answers are integers, fractions with small denominators, or round sensibly (angles to whole degrees, speeds to 0.1). |
| Taught tools | The solver uses only the operations allowed at that level, within a step limit. |
| Distinct answers | Every wrong option comes from a named misconception function. Options differ from the answer and from each other by a clear margin. If a misconception gives the correct answer for these values, the problem is rejected. |
| Physically valid | Values sit inside the theme's realistic ranges and the model's limits (e.g. no drag-dominated flights). |
| Findable (interactive) | Slider and drag targets fall on reachable positions inside the tolerance band, and no wrong setting also passes. |
| No duplicates | Problems are reduced to a canonical form and hashed; near-duplicates are capped. |

**Human review:** every validated problem is served. The review page shows a random sample per framework plus borderline cases. Marking one rejected removes it from the bank and adds it to the must-reject test fixtures (5.2). Serving only reviewed problems is a possible later setting.

## 5. Frameworks

### 5.1 Integration by parts
- **Outcome:** choose u so the problem simplifies; know when repeated parts ends; handle the sine/cosine loop.
- **Levels:**
  1. x·{eᵃˣ, sin bx, cos bx}, one round.
  2. A polynomial of degree 2–3 times the same. Includes "how many rounds?" (answer: the degree, because the polynomial must be u to reach zero).
  3. Loop: eᵃˣ·sin bx or eᵃˣ·cos bx. After two rounds the original integral reappears; solve for it.
  4. xⁿ·ln x, where ln x must be u.
- **Misconceptions:** choosing u so the problem gets harder; differentiating for v; dropping 1/a; expecting the loop to vanish or grow; not dividing out the reappearing integral.
- **Rule:** no "which u?" step on loop problems, since both choices work. The uniqueness check enforces this.

### 5.2 Projectile aim
- **Model:** no drag, g = 9.8 m/s² (1.6 on the Moon theme).
- **Outcome:** horizontal and vertical motion are independent; the vertical motion sets the flight time; distance = vₓ × time.
- **Levels:**
  1. A horizontal launch from a height: find vₓ for a target.
  2. A ground launch with fixed vᵧ: find vₓ.
  3. Fixed speed and distance: ask for the lower of the two angles, then reveal that the two angles sum to 90°.
  4. Clear a wall or hit a target at a given height.
- **Interactive step:** drag vₓ and vᵧ and watch the arc.
- **Misconceptions:** putting the full launch speed into the horizontal direction; dropping the 2 in flight time; dropping the ½ in ½gt²; "heavier falls faster" (a BB fired level and a dropped ball land together).

### 5.3 Mixing
- **Outcome:** strength is a fraction of the whole; a ratio is not a fraction; diluting multiplies strength; mixing averages it, weighted by amount.
- **Values sampled:** cup sizes (3–6 marks), the concentrate's recipe, and a target strength.
- **Steps:** ratio → fraction; build the drink with the cups (judged by the resulting strength, which is unique; the level caps the minimum number of moves); a weighted average with unequal amounts; optionally "fewest moves?", answered by the solver.

### 5.4 Bouncing ball
- **Outcome:** each bounce keeps a fixed fraction of the height, making a geometric sequence; infinitely many bounces still cover a finite distance.
- **Levels:**
  1. Height after n bounces, with the fraction given directly.
  2. Total distance: h + 2hr/(1−r).
  3. Start from the coefficient of restitution e, so the height fraction is r = e².
  4. Number of bounces until the ball stays below a given height (logarithms).
- **Misconceptions:** counting only the up or only the down part of each bounce; counting the first drop twice; using e instead of e²; "infinitely many bounces means infinite distance."
- **Rule:** in level 4, reject cases where a bounce height lands within rounding distance of the threshold.

## 6. Serving

- **Build:** `python generator/build_bank.py <framework> --count N --seed S`. Deterministic; results are committed. No CI build in version 1.
- **Bank files:** one per framework per level, about 100–200 KB each.
- **Practice page** (`docs/math/practice/?f=<framework>&level=<n>`):
  - draws a random problem this device hasn't seen (seen IDs in localStorage, wrapped in try/catch, nothing sent anywhere);
  - renders the story, the theme visuals and the steps, using a shared player module (step rail, choice, number and slider steps, per-misconception feedback) and one scene renderer per framework;
  - suggests the next level after 3 problems in a row solved on the first try, otherwise offers "Another one like this."
- **Existing hand-built pages** (square wave, two cups, integration by parts) stay as they are, plus a "Practice more like this" link.
- **Out of scope for version 1:** typed algebraic answers, adaptive steering toward a learner's misconceptions, accounts or server-side progress, and CI-built banks.

## 7. Testing

1. **Solvers checked by an independent method:**
   - IBP: SymPy differentiates each answer back to its integrand.
   - Projectile: a time-step simulation lands within a few centimeters of the closed-form answer.
   - Bounce: a 200-bounce simulation matches the series total.
   - Mixing: exact fraction arithmetic re-checks the search solver.
2. **Must-reject fixtures:** two-angle "find the angle"; a distractor equal to the answer; "which u?" on a loop problem; a 300 m/s stomp rocket; a bounce count on the threshold. Problems rejected in review are added here.
3. **Misconception functions:** each produces the intended wrong value on a hand-worked example.
4. **Bank audit:** every banked problem re-passes every validator, and the same seed rebuilds an identical bank. Hooked into `tests/check_math.py`.
5. **Themes:** required fields present, physical ranges inside realistic limits, and the fallback renders when there's no drawing.
6. **Practice page:** a headless browser plays one problem per framework and level at phone and desktop sizes, with one right and one wrong answer per step; feedback appears and there are no JavaScript errors.
7. **Acceptance rate:** the build fails if a framework accepts fewer than about 5% of its candidates.

## 8. Build order

1. Core (contract, shared validators, bank, audit) together with **integration by parts**, the easiest framework to verify symbolically.
2. Practice page and review page, using integration by parts.
3. Projectile (with the aiming interactive).
4. Mixing.
5. Bouncing ball.

Each step ends with its tests passing and its bank built.
