# MATH 140 Calculus Explorer: Design

**Date:** 2026-10-05
**Status:** Draft for review

## 1. Purpose

An interactive map of McGill's **MATH 140 (Calculus 1)**: each learning outcome is a button that opens its subtopics, and each subtopic offers **Learn** (one carefully narrated problem whose terms lead down to first principles) and **Practice** (endless, verified problems). **"Builds on"** tags show where an idea's foundations live, and a refresher is one tap away.

**Scope of this spec:**
- The shared structure: curriculum data, the outcome map, the Learn player, and the practice integration.
- **Unit 140.3, the derivative,** fully built.

The other five MATH 140 units follow the same pattern, each with its own plan, in this order: 140.2 limits and continuity, 140.4 differentiating elementary functions, 140.5 applications, 140.1 functions and graphs, 140.6 antidifferentiation.

**Out of scope:**
- MATH 141, 262 and 264 (outlined in §8 for later).
- Accounts, saved progress and the mastery mind-map (§9).
- Recorded voice-over.
- Using the CLP textbooks' text or problems. They're kept privately in the knowledge repo as inspiration only (CC BY-NC-SA 4.0).

**Success criteria**
- `/calculus/math-140/` shows all six units and every outcome and subtopic, with McGill's official description quoted and linked.
- All 8 subtopics of unit 140.3 have a working Learn walkthrough and a Practice level, and outcome 140.3.2 has a mixed Practice level.
- Every Learn and Practice item shows its "Builds on" tags, and each tag opens its target.
- Two new generator frameworks with at least 300 verified problems each.
- Five new concepts in the "Why?" network.
- Every check in §7 passes. The homepage and gallery link to the map and to the concept atlas.

## 2. Source of truth

McGill's official description (coursecatalogue.mcgill.ca/courses/math-140, retrieved 2026-10-05), quoted verbatim on the page:

> "Review of functions and graphs. Limits, continuity, derivative. Differentiation of elementary functions. Antidifferentiation. Applications."

The outcomes below are **our breakdown** of that description, and the page says so. Instructors' syllabi vary by term; a myCourses syllabus can refine the breakdown later.

### MATH 140 outcomes (shown on the map)

| Unit | Outcomes |
|---|---|
| 140.1 Functions and graphs | .1 Domain, range, composition, inverses · .2 Graph transformations · .3 Elementary functions (polynomial, rational, exponential, log, trig, inverse trig) |
| 140.2 Limits and continuity | .1 Limits from graphs and tables, one-sided limits · .2 Limit laws, algebraic techniques, squeeze theorem · .3 Limits at infinity, asymptotes · .4 Continuity and the Intermediate Value Theorem · .5 The ε–δ definition |
| 140.3 The derivative | .1 The derivative as an instantaneous rate, from the limit definition · .2 The sum, constant-multiple, power, product, quotient and chain rules |
| 140.4 Differentiating elementary functions | .1 Trig, exponential, log · .2 Inverse functions and inverse trig · .3 Implicit and logarithmic differentiation · .4 Higher derivatives |
| 140.5 Applications | .1 Related rates · .2 Linear approximation · .3 Mean Value Theorem · .4 Extrema and curve sketching · .5 Optimization · .6 L'Hôpital's rule |
| 140.6 Antidifferentiation | .1 Antiderivatives and +C · .2 Initial-value problems |

## 3. Curriculum data and the outcome map

### 3.1 Data
`docs/calculus/curriculum.js` is `window.CURRICULUM = {...}`, valid JSON after the `=`.

```js
{
  "course": "math-140", "title": "Calculus 1", "credits": 3,
  "official": "Review of functions and graphs. Limits, continuity, derivative. Differentiation of elementary functions. Antidifferentiation. Applications.",
  "source": "https://coursecatalogue.mcgill.ca/courses/math-140/",
  "units": [{
    "id": "140.3", "title": "The derivative",
    "outcomes": [{
      "id": "140.3.2", "title": "…", "summary": "…",
      "practice": {"framework": "derivative-rules", "level": 6},       // optional outcome-level (mixed) practice
      "subtopics": [{
        "id": "140.3.2.chain", "title": "The chain rule",
        "learn": "learn-chain-rule",                                   // or null ("coming soon")
        "practice": {"framework": "derivative-rules", "level": 5},     // or null
        "builds_on": ["140.3.2.power", "140.1.1"]                      // outcome/subtopic ids, or "foundation:<concept-id>"
      }]
    }]
  }]
}
```

Units not yet built list their outcomes. Their subtopics may be empty, or present with `learn`/`practice` set to null.

### 3.2 The page (`/calculus/math-140/`)
- **Header:** the official description, quoted and linked, plus a note that the breakdown is ours.
- **Units** appear as sections, and **each outcome is a button**. Opening one shows its subtopics in place, each with **Learn**, **Practice** and **Builds on** chips. Items that aren't built yet show "coming soon".
- **Chips:** an outcome or subtopic chip scrolls to its target and opens it. A `foundation:` chip opens that concept in the "Why?" panel.
- **Deep links:** `#<id>` opens that outcome on load, and every chip uses these.
- **Entrances:**
  - a homepage leaf "Calculus 1 (MATH 140)" on the Cool Math Problems node;
  - gallery sections for the calculus map and for the concept atlas (`/math/why/atlas.html`), which currently has no entrance.

## 4. Learn walkthroughs

### 4.1 Player (`/calculus/learn/?id=<walkthrough-id>`)
- **Pinned at the top:** the problem, with its subtopic and "Builds on" chips.
- **Steps, one at a time:** each starts with a question (choice, number or slider, with per-misconception feedback). After a correct answer the **narration** appears, then any math and an optional widget, then *Next step*.
- **Zooming in:** `[[concept]]` terms in the narration open the existing "Why?" panel, so the learner can follow them down to foundations.
- **Step tags:** a step may carry its own "Builds on" chips.
- **🔊 Read aloud** reads the current narration through the browser's speech feature. It's hidden when that feature is missing.
- **The finish screen** shows a summary, a **Practice this** link to the matching level, and a link back to the map.
- **Errors:** an unknown ID shows "This walkthrough isn't available yet" with a link back to the map.

### 4.2 Data
`docs/calculus/learn/walkthroughs.js` is `window.WALKTHROUGHS = [...]`, valid JSON after the `=`.

```js
{ "id": "learn-chain-rule", "subtopic": "140.3.2.chain", "title": "…", "problem": "…",
  "steps": [{ "ask": {"prompt": "…", "format": "choice", "answer": "…",
                      "options": [{"label": "…", "correct": true}, {"label": "…", "misconception": "…", "feedback": "…"}]},
              "narration": "… [[chain-rule]] …", "math": ["…"], "widget": {…}, "builds_on": ["140.3.2.power"] }],
  "summary": "…", "claims": [{"sympy": "…", "equals": "…"}] }
```
Step formats and widgets reuse the existing practice and "Why?" components.

## 5. Practice

### 5.1 `derivative-definition` (140.3.1)
| Level | Subtopic | Task | Misconceptions |
|---|---|---|---|
| 1 | Slope as a rate | Average rate of change from a story (position, temperature, population themes), then the secant slope as the interval shrinks | Change instead of rate; dividing the wrong way round |
| 2 | The limit definition | Choose the simplified difference quotient for a polynomial (degree ≤ 3), then take the limit | Cancelling h before expanding; substituting h = 0 early |
| 3 | Differentiable vs continuous | Piecewise and absolute-value functions: is it continuous at a? differentiable? | Continuous means differentiable; a corner counted as smooth |

### 5.2 `derivative-rules` (140.3.2)
| Level | Subtopic | Function families |
|---|---|---|
| 1 | Sum and constant multiple | Polynomials |
| 2 | Power rule | Negative and fractional powers, including roots and reciprocals |
| 3 | Product rule | Products of two polynomials, or polynomial × power |
| 4 | Quotient rule | Rational functions |
| 5 | Chain rule | (polynomial)ⁿ, √(polynomial) |
| 6 | Mixed | Any of the above, nested one level |

**Steps:**
1. "Which rule applies first?" (choice). The answer must be unique: the validator checks the outermost operation and rejects ambiguous forms.
2. "The derivative is…" (choice). Distractors come from named mistakes: (fg)′ = f′g′, (f/g)′ = f′/g′, a dropped inner derivative, g f′ − f g′ in the wrong order, a forgotten squared denominator, n xⁿ⁺¹, the constant differentiated to 1.
3. "Evaluate at x = a" (number, with tolerance). The value must be a clean integer or a simple fraction.

**Validation:** the standard checks (exists, unique, clean, taught tools, distinct, plausible, findable). SymPy confirms the answer and that every distractor is wrong for the sampled function. Both frameworks bank at least 300 problems.

### 5.3 Practice page changes
- Each problem shows its outcome (linked to `/calculus/math-140/#<id>`) and its "Builds on" chips.
- First-try streaks are also recorded per subtopic ID in browser storage (wrapped in try/catch), as a hook for the future mastery map.

## 6. Unit 140.3 content

| Subtopic | Learn problem | Practice | Builds on |
|---|---|---|---|
| 140.3.1.rate | A dropped ball: average speeds over shrinking intervals close in on its speed at t = 2 s | definition L1 | foundation:function, 140.2.1 |
| 140.3.1.definition | f(x) = x² at 3: (f(3+h) − f(3))/h = 6 + h → 6; then 2x in general | definition L2 | 140.3.1.rate, foundation:limit, 140.2.2 |
| 140.3.1.continuity | \|x\| at 0: continuous, one-sided slopes −1 and +1, no derivative; then why differentiable implies continuous | definition L3 | 140.3.1.definition, 140.2.4 |
| 140.3.2.sum | 3x² + 5x, and why derivatives split over sums and constants | rules L1 | 140.3.1.definition |
| 140.3.2.power | √x and 1/x, rewritten as x^½ and x⁻¹; whole-number powers proven by expanding (x+h)ⁿ, fractional ones deferred to 140.4 | rules L2 | 140.3.1.definition, 140.1.3 |
| 140.3.2.product | A rectangle whose sides grow over time: how fast does its area grow? | rules L3 | 140.3.1.definition, foundation:area-shapes |
| 140.3.2.quotient | Cost per item as a ratio; derive the rule from f · g⁻¹ | rules L4 | 140.3.2.product, 140.3.2.chain, 140.3.2.power |
| 140.3.2.chain | An inflating balloon: dr/dt = 2 cm/s, so dV/dt at r = 3 is 72π cm³/s | rules L5 | 140.3.2.power, 140.1.1 |

Outcome 140.3.2 also offers the mixed practice (rules L6).

**New "Why?" concepts:**

| id | Deeper | Related | Widget |
|---|---|---|---|
| `average-vs-instantaneous-rate` | function, limit | derivative | secant (position curve) |
| `differentiable-implies-continuous` | derivative, limit | | secant (new `abs` function: one-sided slopes) |
| `sum-and-constant-rules` | derivative, limit | | secant |
| `negative-and-fractional-powers` | power-rule | | secant |
| `quotient-rule` | product-rule, chain-rule, power-rule | | product-rectangle |

Existing concepts (derivative, limit, power, product and chain rules) are linked, not duplicated.

## 7. Validation and testing

1. **Curriculum checker** (`tests/check_curriculum.py`, part of `tests/check_math.py`):
   - unique, correctly nested IDs;
   - `learn` IDs exist, and `practice` framework and level exist in `docs/math/bank/index.json`;
   - `builds_on` targets exist (outcome, subtopic or `foundation:` concept), and the prerequisites have no loops;
   - the `official` text matches §2 verbatim.
2. **Walkthrough checks:**
   - `[[terms]]` resolve in the concept network;
   - choice steps have exactly one correct option and feedback on each wrong one;
   - every claim is proven by SymPy;
   - step `builds_on` targets exist.
   - The concept checker counts walkthroughs as entry points, so all five new concepts must be reachable.
3. **Generator tests** for both frameworks:
   - SymPy checks on every answer and every distractor;
   - at least 300 problems each, and the bank audit;
   - must-reject cases: dropped inner derivative when the inner derivative is 1; ambiguous rule choice (e.g. a constant times a product); a definition problem where early h = 0 substitution gives the right number; a corner misclassified.
4. **Widget math:** `abs` gives one-sided slopes −1 and +1 at 0.
5. **Browser tests** (phone and desktop):
   - **Map:** outcomes open; chips jump and open their target; `#140.3.2` opens on load; units not yet built show "coming soon".
   - **Learn:** each of the 8 walkthroughs gets one wrong, then one right answer per step; a "Why?" term opens and closes; finishing links to the right practice level.
   - **Read aloud** is hidden when speech isn't available.
   - **Practice:** problems show their outcome link and tags.
   - **Entrances:** the homepage leaf and gallery links reach the map and the atlas.
   - **Everywhere:** no JavaScript errors and no sideways scroll at 390 px.
6. **The existing suite stays green.**

## 8. Later courses (for reference)

The same structure extends to the rest of the sequence. Official descriptions (retrieved 2026-10-05):
- **MATH 141, Calculus 2 (4 cr):** "The definite integral. Techniques of integration. Applications. Introduction to sequences and series."
- **MATH 262, Intermediate Calculus (3 cr, Engineering):** "Series and power series, including Taylor's theorem. Brief review of vector geometry. Vector functions and curves. Partial differentiation and differential calculus for vector valued functions. Unconstrained and constrained extremal problems. Multiple integrals including surface area and change of variables."
- **MATH 264, Advanced Calculus for Engineers (3 cr, Engineering; corequisite MATH 263):** "Review of multiple integrals. Differential and integral calculus of vector fields including the theorems of Gauss, Green, and Stokes. Introduction to partial differential equations, separation of variables, Sturm-Liouville problems, and Fourier series."

The existing integration-by-parts page maps to 141.2.2, and the square-wave page to 264.6. Cross-course tags (e.g. 262.4.4, the multivariable chain rule, building on 140.3.2.chain) use the same `builds_on` field.

## 9. Future: accounts and mastery (not in this spec)

A saved-progress mind-map, colored by mastery, needs a small backend for accounts and storage. **Mastery as automaticity:** correct, fast and consistent across spaced sessions, not just once. The per-subtopic streaks recorded in §5.3 are the starting data.

## 10. Build order

1. Curriculum data, checker and map page, with entrances (homepage, gallery, atlas link).
2. Learn player, walkthrough checks, the five new concepts and `abs`.
3. `derivative-definition` framework, plus walkthroughs 140.3.1 (×3).
4. `derivative-rules` framework, plus walkthroughs 140.3.2 (×5).
5. Practice page tags and links, the full browser test, proofreading.
