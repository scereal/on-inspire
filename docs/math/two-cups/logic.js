// Pure logic for the two-cups mixing problem. No DOM, so tests can run it directly.
// Each cup holds 1000 mL with a mark every 250 mL, and every move shifts one mark's worth.
(function (root) {
  const CAP = 1000;
  const STEP = 250;
  const EPS = 1e-9;

  const start = () => [{ vol: 0, tea: 0 }, { vol: 0, tea: 0 }];
  const copy = (cups) => cups.map((c) => ({ ...c }));
  const strength = (cup) => (cup.vol ? cup.tea / cup.vol : 0);

  // Returns the new cups, or null if the move is impossible.
  const move = (cups, action, i) => {
    const next = copy(cups);
    const cup = next[i];
    const other = next[1 - i];
    switch (action) {
      case "tea":
        if (cup.vol + STEP > CAP) return null;
        cup.vol += STEP; cup.tea += STEP;
        return next;
      case "water":
        if (cup.vol + STEP > CAP) return null;
        cup.vol += STEP;
        return next;
      case "pour": {
        if (cup.vol < STEP || other.vol + STEP > CAP) return null;
        const moved = STEP * strength(cup);
        cup.vol -= STEP; cup.tea -= moved;
        other.vol += STEP; other.tea += moved;
        if (cup.vol === 0) cup.tea = 0;
        return next;
      }
      case "empty":
        if (!cup.vol) return null;
        next[i] = { vol: 0, tea: 0 };
        return next;
      default:
        return null;
    }
  };

  const ACTIONS = ["tea", "water", "pour", "empty"];

  // Does any cup hold at least one mark of a drink at exactly this strength?
  const hits = (cups, target) => cups.some((c) => c.vol >= STEP && Math.abs(strength(c) - target) < EPS);

  // Strength as a fraction in lowest terms, e.g. 0.375 -> "3/8", 1/3 -> "1/3".
  const fraction = (x) => {
    if (x < EPS) return "0";
    if (x > 1 - EPS) return "1";
    for (let d = 2; d <= 1024; d++) {
      const n = Math.round(x * d);
      if (Math.abs(n / d - x) < EPS) return `${n}/${d}`;
    }
    return x.toFixed(3);
  };

  // Fewest moves to reach a target strength (breadth-first search), or -1 if unreachable.
  const fewestMoves = (target, limit = 14) => {
    const key = (cups) => cups.map((c) => `${c.vol}:${c.tea.toFixed(6)}`).join("|");
    let frontier = [start()];
    const seen = new Set([key(frontier[0])]);
    for (let depth = 0; depth <= limit; depth++) {
      const nextFrontier = [];
      for (const cups of frontier) {
        if (hits(cups, target)) return depth;
        for (const a of ACTIONS) for (const i of [0, 1]) {
          const n = move(cups, a, i);
          if (!n) continue;
          const k = key(n);
          if (!seen.has(k)) { seen.add(k); nextFrontier.push(n); }
        }
      }
      frontier = nextFrontier;
    }
    return -1;
  };

  const api = { CAP, STEP, start, strength, move, hits, fraction, fewestMoves };
  root.TwoCups = api;
  if (typeof module !== "undefined") module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
