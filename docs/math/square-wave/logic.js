// Pure math for the square-wave builder. No DOM, so tests can run it directly.
(function (root) {
  const TAU = Math.PI * 2;

  // The target: +1 on (0, π), -1 on (π, 2π), repeating.
  const square = (t) => {
    const s = Math.sin(t);
    return Math.abs(s) < 1e-12 ? 0 : Math.sign(s);
  };

  // terms: [{ n, a }] meaning a·sin(n·t)
  const sum = (terms, t) => terms.reduce((acc, { n, a }) => acc + a * Math.sin(n * t), 0);

  // Root-mean-square distance between the sum and the square wave over one period.
  const gap = (terms, samples = 1440) => {
    let total = 0;
    for (let i = 0; i < samples; i++) {
      const t = ((i + 0.5) / samples) * TAU;
      const d = sum(terms, t) - square(t);
      total += d * d;
    }
    return Math.sqrt(total / samples);
  };

  // Least-squares amplitude for sin(n·t): 4/(nπ) for odd n, 0 for even n.
  const bestAmp = (n) => (n % 2 === 1 ? 4 / (n * Math.PI) : 0);

  // The first k odd harmonics at their best amplitudes.
  const recipe = (k) => Array.from({ length: k }, (_, i) => ({ n: 2 * i + 1, a: bestAmp(2 * i + 1) }));

  // Height of the overshoot just after the jump at t = 0.
  const peak = (terms) => {
    const top = Math.max(...terms.map((term) => term.n));
    const end = Math.min(Math.PI / 2, (4 * Math.PI) / top);
    let best = -Infinity;
    for (let i = 1; i <= 4000; i++) best = Math.max(best, sum(terms, (i / 4000) * end));
    return best;
  };

  const api = { TAU, square, sum, gap, bestAmp, recipe, peak };
  root.SquareWave = api;
  if (typeof module !== "undefined") module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
