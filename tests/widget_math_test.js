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
check("secant slope of the falling ball 4.9t² at 2 → 19.6", near(M.secantSlope(M.fn("fall"), 2, 1e-4), 19.6, 1e-3));
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
// Calculus core + integration by parts
const A = (x) => M.accumulate(M.fn("cos"), 0, x, 4000);
check("accumulated area's slope matches f (FTC)", near((A(1.2 + 1e-3) - A(1.2 - 1e-3)) / 2e-3, Math.cos(1.2), 1e-3));
let poly = [0, 0, 0, 1];  // x³ as coefficients of x⁰..x³
for (let i = 0; i < 4; i++) poly = M.diffPoly(poly);
check("differentiating x³ four times gives 0", poly.every((c) => c === 0));
check("x³ differentiated once is 3x²", M.diffPoly([0, 0, 0, 1]).join() === "0,0,3");
check("sin(2x) over [0, π/2] has area 1", near(M.stretchArea("sin", 2, 0, Math.PI / 2), 1, 1e-6));
const pc = M.productChange(3, 2, 0.5, 0.25);
check("product rule strips add up to the change in uv", near(pc.udv + pc.vdu + pc.corner, 3.5 * 2.25 - 6, 1e-12));
const sq = M.squeeze(0.5);
check("squeeze: inner triangle ≤ sector ≤ outer triangle", sq.inner < sq.sector && sq.sector < sq.outer);
check("squeeze: cos h ≤ sin h / h ≤ 1", Math.cos(0.5) <= Math.sin(0.5) / 0.5 && Math.sin(0.5) / 0.5 <= 1);
check("angle addition matches the unit circle", near(M.unitPoint(0.7 + 0.4).y, Math.sin(0.7) * Math.cos(0.4) + Math.cos(0.7) * Math.sin(0.4), 1e-12));
// Square wave
check("∫ sin 2t sin 3t over a period ≈ 0", near(M.productIntegral(2, 3), 0, 1e-6));
check("∫ sin² 3t over a period ≈ π", near(M.productIntegral(3, 3), Math.PI, 1e-6));
check("square-wave gap is smallest at 4/π", (() => {
  let best = 0, bestGap = Infinity;
  for (let a = 0; a <= 2; a += 0.001) { const g = M.rmsGap(a); if (g < bestGap) { bestGap = g; best = a; } }
  return near(best, 4 / Math.PI, 0.002);
})());
check("error parabola E(a) = a²/2 − 4a/π + 1", near(M.errorParabola(1), 0.5 - 4 / Math.PI + 1, 1e-12));
check("even harmonics: the two halves cancel", near(M.halfContributions(2).total, 0, 1e-6));
check("odd harmonics: the two halves add", near(M.halfContributions(3).total, 4 / 3, 1e-4));  // midpoint rule, 2000 strips
check("partial sum at π/2 approaches 1", near(M.partialSum(200, Math.PI / 2), 1, 0.005));
check("Gibbs peak stays near 1.179", near(M.peakOf(60), 1.179, 0.005));
// MATH 140
check("|x| right-hand slope at 0 is +1", near(M.secantSlope(M.fn("abs"), 0, 1e-4), 1, 1e-9));
check("|x| left-hand slope at 0 is −1", near(M.secantSlope(M.fn("abs"), 0, -1e-4), -1, 1e-9));
check("√x slope at 4 → 1/4", near(M.secantSlope(M.fn("sqrt"), 4, 1e-6), 0.25, 1e-5));
check("unknown function names are refused", (() => { try { M.fn("alert"); return false; } catch (e) { return true; } })());

// Unit 140.2: limits and continuity
{
  const far = M.farValues(M.fn("avgcost"), "infinity", 0, 1);
  check("far-out: average cost settles toward 3 as n grows", near(far[far.length - 1][1], 3, 0.01), JSON.stringify(far));
  const [[xl, yl], [xr, yr]] = M.farValues(M.fn("asym"), "asymptote", 2, 1);
  check("far-out: (x + 1)/(x − 2) blows up with opposite signs either side of 2", xl < 2 && xr > 2 && yl < -1000 && yr > 1000, `${yl}, ${yr}`);
  check("far-out: asymptote samples move toward the line as t grows",
    Math.abs(M.farValues(M.fn("asym"), "asymptote", 2, 0.8)[1][0] - 2) < Math.abs(M.farValues(M.fn("asym"), "asymptote", 2, 0.2)[1][0] - 2));
  let squeezed = true;
  for (let i = 1; i <= 200; i++) { const x = (i - 100.5) / 400; const y = M.fn("x2sin")(x); if (y > x * x + 1e-12 || y < -x * x - 1e-12) squeezed = false; }
  check("x² sin(1/x) stays between −x² and x²", squeezed);
  check("negsquare is −x²", M.fn("negsquare")(3) === -9);
  check("parking: 4 dollars per started hour (8 just before 2 h, 12 just after)", M.fn("parking")(1.999) === 8 && M.fn("parking")(2.001) === 12);
  check("jump: 1 on the left of 0, 3 on the right", M.fn("jump")(-0.001) === 1 && M.fn("jump")(0.001) === 3);
  check("line21(1) = 3", M.fn("line21")(1) === 3);
  check("ivtcubic changes sign on [0, 1]", M.fn("ivtcubic")(0) < 0 && M.fn("ivtcubic")(1) > 0);
}

print(failures ? `\n${failures} failed` : "\nall widget math checks passed");
if (failures) throw new Error(`${failures} failed`);
