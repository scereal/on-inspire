# Verified math problem generator

Generates practice problems from hand-designed frameworks, validates every one, and writes only the
problems that pass to `docs/math/bank/`, where the practice page (`docs/math/practice/`) serves them.
Design: `design/specs/2026-10-04-problem-generator-design.md`.

```
generator/
  core/          framework contract, shared validators, themes, bank writer
  frameworks/    ibp.py, projectile.py, mixing.py, bounce.py
  themes/        one YAML file per theme (story wording, visuals, realistic ranges)
  build_bank.py  python -m generator.build_bank <framework|all> [--count N] [--seed S]
  audit_bank.py  python -m generator.audit_bank
  tests/
```

Run everything with the project venv (`.venv/bin/pip install -r generator/requirements.txt`).

## What "verified" means

Every candidate is solved, then checked, cheapest first: **exists** (a solution), **unique** (the
asked-for quantity has exactly one answer), **taught tools** (solvable with the level's allowed
steps), **distinct** (every wrong option is a different, named misconception; a misconception that
happens to give the right answer rejects the problem), **plausible** (inside the theme's realistic
ranges), **findable** (slider answers sit on the slider grid), plus each framework's own checks
(e.g. SymPy re-differentiates every antiderivative; a time-step simulation re-flies every
projectile). Near-duplicates are dropped. `report.json` counts every rejection reason.

## Common tasks

- **Rebuild a bank:** `.venv/bin/python -m generator.build_bank ibp`. Same seed, same bytes.
- **Review problems:** open `docs/math/review/` (served locally), mark problems good or rejected,
  click *Copy decisions*, paste into `docs/math/bank/review.json`, and rebuild. Rejected IDs are
  skipped, and a rejection should become a new validator rule or must-reject test.
- **Add a theme:** add a YAML file to `themes/`; `tests/test_themes.py` checks it.
- **Check everything:** `.venv/bin/python tests/check_math.py` (unit tests + bank audit + site
  math). Browser test: `python tests/e2e_practice.py` (needs Playwright).
