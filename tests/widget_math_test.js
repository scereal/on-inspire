// Tests for WidgetMath in docs/math/why/widgets.js. Run through tests/check_math.py (macOS JavaScriptCore).
load("docs/math/why/widgets.js");

let failures = 0;
const check = (name, ok, detail = "") => {
  print(`${ok ? "pass" : "FAIL"}  ${name}${ok ? "" : `  ${detail}`}`);
  if (!ok) failures++;
};
const near = (a, b, tol) => Math.abs(a - b) <= tol;
const M = WidgetMath;

// Batch 1: secant, limit-zoom, unit-circle, riemann, fraction-bar
check("secant slope of x² at 1 → 2", near(M.secantSlope(M.fn("square"), 1, 1e-4), 2, 1e-3));
check("secant slope of sin at 0 → 1", near(M.secantSlope(M.fn("sin"), 0, 1e-4), 1, 1e-3));
check("riemann(sin, 0, π, 1000) → 2", near(M.riemann(M.fn("sin"), 0, Math.PI, 1000), 2, 1e-4));
check("riemann(x², 0, 1, 2000) → 1/3", near(M.riemann(M.fn("square"), 0, 1, 2000), 1 / 3, 1e-6));
check("left-rule riemann of x² underestimates", M.riemann(M.fn("square"), 0, 1, 10, "left") < 1 / 3);
check("sin h / h at 1e-4 → 1", near(M.fn("sinh_over_h")(1e-4), 1, 1e-6));
check("(cos h − 1)/h at 1e-4 → 0", near(M.fn("cosh_minus_1_over_h")(1e-4), 0, 1e-3));
check("(eʰ − 1)/h at 1e-4 → 1", near(M.fn("exph_minus_1_over_h")(1e-4), 1, 1e-3));
check("(x² − 1)/(x − 1) near 1 → 2", near(M.fn("hole")(1.0001), 2, 1e-3));
const top = M.unitPoint(Math.PI / 2);
check("unitPoint(π/2) = (0, 1)", near(top.x, 0, 1e-12) && near(top.y, 1, 1e-12));
check("unit point stays on the circle", near(Math.hypot(M.unitPoint(2.3).x, M.unitPoint(2.3).y), 1, 1e-12));
const [a, b] = M.pour({ marks: 2, conc: 1 }, { marks: 0, conc: 0 }, 1);
check("pouring a mark keeps strength", near(M.strength(a), 0.5, 1e-12) && near(M.strength(b), 0.5, 1e-12));
check("pouring conserves concentrate", near(a.conc + b.conc, 1, 1e-12));
check("1 mark at 1/2 + 1 mark at 1/4 = 3/8", near(M.combine([{ marks: 1, conc: 0.5 }, { marks: 1, conc: 0.25 }]), 0.375, 1e-12));
// Two cups modes
check("diluting with equal water halves strength", near(M.strength(M.dilute({ marks: 2, conc: 1 }, 2)), 0.25, 1e-12));
check("a fraction of a fraction multiplies", near(M.fractionOf(1 / 2, 1 / 4), 1 / 8, 1e-12));
check("serial dilution halves each round", M.serial(1, 3).map((x) => M.toFraction(x)).join() === "1/2,1/4,1/8");
check("unknown function names are refused", (() => { try { M.fn("alert"); return false; } catch (e) { return true; } })());

print(failures ? `\n${failures} failed` : "\nall widget math checks passed");
if (failures) throw new Error(`${failures} failed`);
