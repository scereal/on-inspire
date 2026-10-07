// Static problem figures: small SVG sketches in the style of the lecture notes.
window.Figures = (function () {
  const W = 220, H = 160;
  const deg = Math.PI / 180;
  const line = (x1, y1, x2, y2, cls = "f-line") => `<line class="${cls}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
  const circ = (x, y, r, cls = "f-mass") => `<circle class="${cls}" cx="${x}" cy="${y}" r="${r}"/>`;
  const text = (x, y, s, cls = "f-label", anchor = "middle") => `<text class="${cls}" x="${x}" y="${y}" text-anchor="${anchor}">${s}</text>`;
  function arrow(x1, y1, x2, y2, cls = "f-force") {
    const a = Math.atan2(y2 - y1, x2 - x1), h = 7;
    const p1 = [x2 - h * Math.cos(a - 0.4), y2 - h * Math.sin(a - 0.4)], p2 = [x2 - h * Math.cos(a + 0.4), y2 - h * Math.sin(a + 0.4)];
    return `<g class="${cls}"><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/><polygon points="${x2},${y2} ${p1[0]},${p1[1]} ${p2[0]},${p2[1]}"/></g>`;
  }
  function ground(x1, x2, y) {
    let s = line(x1, y, x2, y, "f-ground");
    for (let x = x1 + 4; x < x2; x += 8) s += line(x, y, x - 5, y + 6, "f-ground");
    return s;
  }
  function wall(x, y1, y2) {
    let s = line(x, y1, x, y2, "f-ground");
    for (let y = y1 + 4; y < y2; y += 8) s += line(x, y, x - 6, y + 5, "f-ground");
    return s;
  }
  function spring(x1, y1, x2, y2, n = 7) {
    const L = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / L, uy = (y2 - y1) / L, px = -uy, py = ux;
    let d = `M${x1},${y1} L${x1 + ux * 6},${y1 + uy * 6}`;
    for (let i = 0; i < n; i++) {
      const t = 6 + ((L - 12) * (i + 0.5)) / n, s = i % 2 ? -5 : 5;
      d += ` L${x1 + ux * t + px * s},${y1 + uy * t + py * s}`;
    }
    d += ` L${x2 - ux * 6},${y2 - uy * 6} L${x2},${y2}`;
    return `<path class="f-line" d="${d}"/>`;
  }
  function damper(x1, y, x2) {
    const m = (x1 + x2) / 2;
    return line(x1, y, m - 4, y) + `<path class="f-line" d="M${m - 10},${y - 6} L${m + 4},${y - 6} M${m - 10},${y + 6} L${m + 4},${y + 6} M${m - 10},${y - 6} L${m - 10},${y + 6}"/>` + line(m - 4, y - 4, m - 4, y + 4) + line(m - 4, y, x2, y);
  }
  function angleArc(cx, cy, r, a0, a1, label) {
    const p0 = [cx + r * Math.cos(a0), cy + r * Math.sin(a0)], p1 = [cx + r * Math.cos(a1), cy + r * Math.sin(a1)];
    const mid = (a0 + a1) / 2;
    return `<path class="f-arc" d="M${p0[0]},${p0[1]} A${r},${r} 0 0 ${a1 > a0 ? 1 : 0} ${p1[0]},${p1[1]}"/>` + text(cx + (r + 9) * Math.cos(mid), cy + (r + 9) * Math.sin(mid) + 4, label);
  }
  const pend = (px, py, L, th) => [px + L * Math.sin(th), py + L * Math.cos(th)];

  const F = {
    vectors() {
      const o = [70, 120];
      return arrow(o[0], o[1], o[0] + 60, o[1] - 80, "f-force") + text(o[0] + 70, o[1] - 82, "F") +
        arrow(o[0], o[1], o[0] + 90, o[1], "f-vec") + text(o[0] + 98, o[1] + 4, "u") +
        line(o[0] + 60, o[1] - 80, o[0] + 60, o[1], "f-dash") + `<line class="f-proj" x1="${o[0]}" y1="${o[1] + 6}" x2="${o[0] + 60}" y2="${o[1] + 6}"/>` + text(o[0] + 30, o[1] + 20, "F·u");
    },
    pendulum(o = {}) {
      const P = [110, 25], th = 30 * deg, L = 90, B = pend(P[0], P[1], L, th);
      let s = ground(80, 140, P[1]) + line(P[0], P[1], P[0], P[1] + L + 12, "f-dash") + line(P[0], P[1], B[0], B[1]) + circ(P[0], P[1], 3, "f-pin") + circ(B[0], B[1], 8) +
        angleArc(P[0], P[1], 26, Math.PI / 2 - th, Math.PI / 2, "θ") + text(P[0] + 30, P[1] + 50, "ℓ");
      if (o.show && o.show.includes("T")) s += arrow(B[0], B[1], B[0] - 28 * Math.sin(th), B[1] - 28 * Math.cos(th)) + text(B[0] - 26, B[1] - 26, "T");
      if (o.show && o.show.includes("v")) s += arrow(B[0], B[1], B[0] + 32 * Math.cos(th), B[1] - 32 * Math.sin(th), "f-vec") + text(B[0] + 38, B[1] - 16, "v");
      if (o.force) s += arrow(B[0], B[1], B[0] + 40, B[1]) + text(B[0] + 46, B[1] + 4, "F", "f-label", "start");
      return s + arrow(B[0], B[1], B[0], B[1] + 30, "f-grav") + text(B[0] + 10, B[1] + 34, "mg", "f-label", "start");
    },
    "pendulum-xy"() {
      const P = [90, 25], th = 35 * deg, L = 95, B = pend(P[0], P[1], L, th);
      return ground(60, 120, P[1]) + arrow(P[0], P[1], P[0] + 100, P[1], "f-axis") + text(P[0] + 106, P[1] + 4, "x", "f-label", "start") +
        arrow(P[0], P[1], P[0], P[1] + 125, "f-axis") + text(P[0] - 8, P[1] + 128, "y") +
        line(P[0], P[1], B[0], B[1]) + circ(B[0], B[1], 8) + line(B[0], P[1], B[0], B[1], "f-dash") + line(P[0], B[1], B[0], B[1], "f-dash") +
        text(B[0] + 12, B[1] + 4, "(x, y)", "f-label", "start") + text(P[0] + 18, P[1] + 46, "ℓ");
    },
    "cart-pendulum"(o = {}) {
      const cx = 115, cy = 52, th = 28 * deg, L = 80, B = pend(cx, cy + 12, L, th);
      let s = ground(10, 210, cy + 26) + `<rect class="f-body" x="${cx - 26}" y="${cy - 10}" width="52" height="28" rx="3"/>` + circ(cx - 15, cy + 22, 4, "f-wheel") + circ(cx + 15, cy + 22, 4, "f-wheel");
      if (o.spring) s += wall(14, cy - 14, cy + 26) + spring(14, cy + 4, cx - 26, cy + 4) + text(52, cy - 6, "k");
      s += line(cx, cy + 12, cx, cy + 12 + L + 6, "f-dash") + line(cx, cy + 12, B[0], B[1]) + circ(B[0], B[1], 7) + circ(cx, cy + 12, 2.5, "f-pin") +
        angleArc(cx, cy + 12, 24, Math.PI / 2 - th, Math.PI / 2, "θ") + text(cx, cy + 4, "M", "f-label-inv") + text(B[0] + 12, B[1] + 4, "m", "f-label", "start") +
        arrow(cx, cy - 20, cx + 30, cy - 20, "f-axis") + text(cx + 36, cy - 16, "x", "f-label", "start");
      if (o.force) s += arrow(B[0], B[1], B[0] + 38, B[1]) + text(B[0] + 44, B[1] + 4, "F", "f-label", "start");
      return s;
    },
    "rolling-disk"(o = {}) {
      const cx = 125, cy = 95, r = 35;
      let s = ground(10, 210, cy + r) + circ(cx, cy, r, "f-disk") + circ(cx, cy, 2.5, "f-pin") + line(cx, cy, cx + r * Math.cos(-40 * deg), cy + r * Math.sin(-40 * deg)) +
        text(cx + 14, cy - 12, "r") + text(cx - 8, cy + 4, "C") + circ(cx, cy + r, 2.5, "f-pin") + text(cx + 8, cy + r - 4, "P", "f-label", "start") +
        `<path class="f-arc" d="M${cx + 18},${cy - 42} A45,45 0 0 1 ${cx + 44},${cy - 18}"/>` + text(cx + 46, cy - 36, "θ");
      if (o.spring) s += wall(14, cy - 20, cy + r) + spring(14, cy, cx - r, cy) + text(50, cy - 10, "k");
      return s + arrow(cx, cy - r - 12, cx + 32, cy - r - 12, "f-axis") + text(cx + 38, cy - r - 8, "x", "f-label", "start");
    },
    "spring-pendulum"() {
      const P = [110, 22], th = 30 * deg, L = 100, B = pend(P[0], P[1], L, th);
      return ground(80, 140, P[1]) + line(P[0], P[1], P[0], P[1] + L + 10, "f-dash") + spring(P[0], P[1], B[0], B[1], 9) + circ(B[0], B[1], 8) + circ(P[0], P[1], 3, "f-pin") +
        angleArc(P[0], P[1], 28, Math.PI / 2 - th, Math.PI / 2, "θ") + text(P[0] + 40, P[1] + 52, "r, k") + text(B[0] + 12, B[1] + 4, "m", "f-label", "start");
    },
    dumbbell() {
      const a = [55, 115], b = [165, 55];
      return line(a[0], a[1], b[0], b[1]) + circ(a[0], a[1], 7) + circ(b[0], b[1], 7) + line(a[0], a[1], a[0] + 70, a[1], "f-dash") +
        angleArc(a[0], a[1], 30, -Math.atan2(a[1] - b[1], b[0] - a[0]), 0, "θ") + text(a[0] - 4, a[1] + 22, "(x₁, y₁)") + text(b[0] + 4, b[1] - 14, "(x₂, y₂)") + text(110, 76, "ℓ");
    },
    "two-link"() {
      const O = [45, 125], A = [O[0] + 80 * Math.cos(-50 * deg), O[1] + 80 * Math.sin(-50 * deg)], B = [A[0] + 80, A[1] + 10];
      return ground(20, 80, O[1] + 6) + line(O[0], O[1], A[0], A[1], "f-thick") + line(A[0], A[1], B[0], B[1], "f-thick") + circ(O[0], O[1], 4, "f-pin") + circ(A[0], A[1], 4, "f-pin") +
        angleArc(O[0], O[1], 26, -50 * deg, 0, "θ₁") + line(A[0], A[1], A[0] + 50 * Math.cos(-50 * deg), A[1] + 50 * Math.sin(-50 * deg), "f-dash") +
        angleArc(A[0], A[1], 30, -50 * deg, Math.atan2(10, 80), "θ₂") + `<path class="f-force-arc" d="M${A[0] - 12},${A[1] + 12} A17,17 0 1 1 ${A[0] + 12},${A[1] + 12}"/>` + text(A[0], A[1] + 30, "τ");
    },
    "slot-disk"() {
      const c = [100, 82], R = 62, a = -25 * deg, ux = Math.cos(a), uy = Math.sin(a);
      return circ(c[0], c[1], R, "f-disk") + line(c[0] - R * ux, c[1] - R * uy, c[0] + R * ux, c[1] + R * uy, "f-slot") +
        spring(c[0] - R * ux, c[1] - R * uy, c[0] + 22 * ux, c[1] + 22 * uy, 7) + `<rect class="f-body" x="${c[0] + 22 * ux - 8}" y="${c[1] + 22 * uy - 7}" width="16" height="14" transform="rotate(${-25} ${c[0] + 22 * ux} ${c[1] + 22 * uy})"/>` +
        spring(c[0] + 30 * ux, c[1] + 30 * uy, c[0] + R * ux, c[1] + R * uy, 5) + circ(c[0], c[1], 2.5, "f-pin") +
        `<path class="f-force-arc" d="M${c[0] + R + 10},${c[1] - 25} A70,70 0 0 0 ${c[0] + 30},${c[1] - R - 12}"/>` + text(c[0] + R + 16, c[1] - 30, "Ω", "f-label", "start") + text(c[0] + 22 * ux, c[1] + 22 * uy + 22, "x, m");
    },
    satellite() {
      const E = [70, 95], S = [175, 45];
      return `<ellipse class="f-orbit" cx="105" cy="80" rx="95" ry="58"/>` + circ(E[0], E[1], 11, "f-earth") + circ(S[0], S[1], 5) + line(E[0], E[1], S[0], S[1]) +
        line(E[0], E[1], E[0] + 120, E[1], "f-dash") + angleArc(E[0], E[1], 32, -Math.atan2(E[1] - S[1], S[0] - E[0]), 0, "θ") + text(125, 62, "r") + text(E[0], E[1] + 26, "Earth") + text(S[0] + 8, S[1] - 8, "m", "f-label", "start");
    },
    paraboloid() {
      let d = "M30,30";
      for (let i = 0; i <= 40; i++) { const x = -1 + i / 20; d += ` L${110 + 80 * x},${135 - 105 * x * x}`; }
      return `<path class="f-line" d="${d}"/>` + `<ellipse class="f-orbit" cx="110" cy="30" rx="80" ry="10"/>` + arrow(110, 135, 110, 10, "f-axis") + text(118, 14, "z", "f-label", "start") +
        circ(160, 135 - 105 * 0.39, 6) + arrow(160, 135 - 105 * 0.39, 160 - 24, 135 - 105 * 0.39 + 14, "f-force") + text(132, 100, "R = λ∇f");
    },
    boat() {
      const c = [110, 85], a = -32 * deg;
      const pts = [[40, 0], [18, 14], [-32, 14], [-32, -14], [18, -14]].map(([x, y]) => [c[0] + x * Math.cos(a) - y * Math.sin(a), c[1] + x * Math.sin(a) + y * Math.cos(a)]);
      return `<polygon class="f-body" points="${pts.map((p) => p.join(",")).join(" ")}"/>` + arrow(c[0], c[1], c[0] + 70 * Math.cos(a), c[1] + 70 * Math.sin(a), "f-vec") +
        text(c[0] + 80 * Math.cos(a), c[1] + 80 * Math.sin(a), "v") + arrow(c[0], c[1], c[0] - 40 * Math.sin(a) * -1, c[1] + 40 * Math.cos(a), "f-ban") + text(c[0] + 26, c[1] + 44, "no sideways v") +
        line(c[0], c[1], c[0] + 60, c[1], "f-dash") + angleArc(c[0], c[1], 28, a, 0, "θ");
    },
    "spin-pendulum"() {
      const top = [110, 20], th = 38 * deg, L = 95, B = pend(top[0], top[1], L, th);
      return line(top[0], 8, top[0], 150, "f-shaft") + `<path class="f-force-arc" d="M${top[0] - 22},${14} A24,8 0 1 0 ${top[0] + 22},${14}"/>` + text(top[0] + 30, 12, "Ω", "f-label", "start") +
        line(top[0], top[1], B[0], B[1]) + circ(B[0], B[1], 8) + circ(top[0], top[1], 3, "f-pin") + angleArc(top[0], top[1], 30, Math.PI / 2 - th, Math.PI / 2, "θ") +
        line(top[0], B[1], B[0], B[1], "f-dash") + text((top[0] + B[0]) / 2, B[1] + 14, "ℓ sin θ");
    },
    "spin-rod"() {
      const top = [110, 20], th = 45 * deg, L = 110, B = pend(top[0], top[1], L, th);
      return line(top[0], 8, top[0], 150, "f-shaft") + `<path class="f-force-arc" d="M${top[0] - 22},${14} A24,8 0 1 0 ${top[0] + 22},${14}"/>` + text(top[0] + 30, 12, "Ω", "f-label", "start") +
        line(top[0], top[1], B[0], B[1], "f-rod") + circ(top[0], top[1], 3, "f-pin") + circ((top[0] + B[0]) / 2, (top[1] + B[1]) / 2, 3, "f-pin") + text((top[0] + B[0]) / 2 + 12, (top[1] + B[1]) / 2, "G", "f-label", "start") +
        angleArc(top[0], top[1], 30, Math.PI / 2 - th, Math.PI / 2, "θ");
    },
    smd(o = {}) {
      const y = 85;
      let s = wall(20, 45, 125) + ground(20, 210, 112) + `<rect class="f-body" x="120" y="${y - 22}" width="44" height="44" rx="3"/>` + text(142, y + 5, "m", "f-label-inv") +
        spring(20, y - 12, 120, y - 12) + text(70, y - 22, "k");
      if (o.damper !== false) s += damper(20, y + 12, 120) + text(70, y + 30, "c");
      if (o.force) s += arrow(164, y, 205, y) + text(200, y - 8, "F(t)");
      return s + arrow(142, y - 34, 172, y - 34, "f-axis") + text(178, y - 30, "x", "f-label", "start");
    },
    brachistochrone() {
      let cyc = "M20,25";
      for (let i = 1; i <= 40; i++) { const u = (Math.PI * i) / 40; cyc += ` L${20 + 50 * (u - Math.sin(u))},${25 + 50 * (1 - Math.cos(u))}`; }
      return arrow(20, 25, 205, 25, "f-axis") + text(205, 18, "x") + arrow(20, 25, 20, 150, "f-axis") + text(12, 148, "y") +
        line(20, 25, 20 + 50 * Math.PI, 125, "f-dash") + `<path class="f-curve" d="${cyc}"/>` + circ(20, 25, 4) + circ(20 + 50 * Math.PI, 125, 4, "f-pin") + text(120, 112, "cycloid") + text(110, 60, "line");
    },
  };
  return {
    svg(spec) {
      const f = F[spec.type];
      if (!f) return "";
      return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${spec.type.replace(/-/g, " ")} sketch">${f(spec)}</svg>`;
    },
  };
})();
