// Tests for the math pages' JavaScript logic. Run through tests/check_math.py,
// which executes this file with macOS's built-in JavaScriptCore (jsc).
load("docs/math/square-wave/logic.js");
load("docs/math/two-cups/logic.js");

let failures = 0;
const check = (name, ok, detail = "") => {
  print(`${ok ? "pass" : "FAIL"}  ${name}${ok ? "" : `  ${detail}`}`);
  if (!ok) failures++;
};
const near = (a, b, tol) => Math.abs(a - b) <= tol;

// Square wave ---------------------------------------------------------------
const { gap, bestAmp, recipe, peak } = SquareWave;

// Numerically minimize the gap over one amplitude (golden-section search).
const argmin = (f, lo, hi) => {
  const g = (Math.sqrt(5) - 1) / 2;
  for (let i = 0; i < 80; i++) {
    const a = hi - g * (hi - lo), b = lo + g * (hi - lo);
    if (f(a) < f(b)) hi = b; else lo = a;
  }
  return (lo + hi) / 2;
};

check("best height of sin t is 4/π", near(bestAmp(1), 4 / Math.PI, 1e-12));
check("numeric best fit of sin t matches 4/π", near(argmin((a) => gap([{ n: 1, a }]), 0, 2), 4 / Math.PI, 0.002));
const A1 = bestAmp(1);
for (const n of [2, 3, 4, 5]) {
  const found = argmin((a) => gap([{ n: 1, a: A1 }, { n, a }]), -1, 1);
  check(`numeric best height of sin ${n}t is ${bestAmp(n).toFixed(3)}`, near(found, bestAmp(n), 0.002), `found ${found}`);
}
check("height 1 fits worse than 4/π (step 1 feedback)", gap([{ n: 1, a: 1 }]) > gap([{ n: 1, a: A1 }]));
check("sin 3t beats sin 5t as the second sine (step 2 feedback)",
  gap([{ n: 1, a: A1 }, { n: 3, a: bestAmp(3) }]) < gap([{ n: 1, a: A1 }, { n: 5, a: bestAmp(5) }]));
check("even sines can't lower the gap", near(gap([{ n: 1, a: A1 }, { n: 2, a: 0 }]), gap([{ n: 1, a: A1 }]), 1e-12));
// Claims made by the slider hints
const { sum } = SquareWave;
const mid = Math.PI / 2;
check("hint: height 1 touches the top only at the middle", near(sum([{ n: 1, a: 1 }], mid), 1, 1e-12) && sum([{ n: 1, a: 1 }], 0.5) < 1);
check("hint: too little sin 3t leaves a bulge in the middle", sum([{ n: 1, a: A1 }, { n: 3, a: 0.1 }], mid) > 1);
check("hint: too much sin 3t dips the middle below the top", sum([{ n: 1, a: A1 }, { n: 3, a: 0.75 }], mid) < 1);
check("hint: sin 3t points down in the middle and up near the corners", Math.sin(3 * mid) < 0 && Math.sin(3 * 0.3) > 0 && Math.sin(3 * (Math.PI - 0.3)) > 0);
check("step 3 shows 1.27, 0.42, 0.25", [1, 3, 5].map((n) => bestAmp(n).toFixed(2)).join() === "1.27,0.42,0.25");
check("step 3 distractor 1.27 ÷ 9 rounds to 0.14", (bestAmp(1) / 9).toFixed(2) === "0.14");
check("gap shrinks as sines are added", [1, 2, 3, 5, 10].every((k, i, ks) => i === 0 || gap(recipe(k)) < gap(recipe(ks[i - 1]))));
const gibbs = peak(recipe(400));
check("overshoot settles near 1.179 (Gibbs)", near(gibbs, 1.17898, 0.003), `got ${gibbs}`);
check("overshoot is about 9% of the jump", near((gibbs - 1) / 2, 0.09, 0.005));
check("overshoot stays put from 20 to 60 sines", near(peak(recipe(20)), peak(recipe(60)), 0.01));

// Two cups ------------------------------------------------------------------
const { start, move, strength, fraction, fewestMoves } = TwoCups;

for (const [target, label] of [[1 / 2, "1/2"], [1 / 4, "1/4"], [1 / 8, "1/8"], [3 / 8, "3/8"], [1 / 3, "1/3 (misstep)"], [1 / 16, "1/16 (named in feedback)"]]) {
  const m = fewestMoves(target);
  check(`${label} can be reached (fewest moves: ${m})`, m >= 0);
}
check("fractions display in lowest terms", fraction(0.375) === "3/8" && fraction(0.5) === "1/2" && fraction(1 / 16) === "1/16" && fraction(1 / 3) === "1/3" && fraction(2 / 3) === "2/3");
check("can't pour from an empty cup", move(start(), "pour", 0) === null);
let full = start();
for (let i = 0; i < 4; i++) full = move(full, "water", 0);
check("can't overfill a cup", move(full, "tea", 0) === null);
let c = move(move(start(), "tea", 0), "water", 0);       // A: 2 marks, 1/2 tea
c = move(c, "pour", 0);                                  // B: 1 mark, 1/2 tea
check("pouring keeps the strength", strength(c[0]) === 0.5 && strength(c[1]) === 0.5);
c = move(c, "water", 1);                                 // B: 2 marks, 1/4 tea
c = move(c, "pour", 1);                                  // A: 2 marks, 3/8 tea
check("equal parts of 1/2 and 1/4 make 3/8", fraction(strength(c[0])) === "3/8");

print(failures ? `\n${failures} failed` : "\nall JavaScript checks passed");
if (failures) throw new Error(`${failures} failed`);
