// Live models for the atlas. Each widget draws on a canvas, reads its colours from the page theme,
// and stops animating when the reader navigates away (Widgets.stopAll).
window.Widgets = (function () {
  const loops = new Set();
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  let C = null;
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  function colors() {
    C = { ink: css("--ink"), muted: css("--muted"), rule: css("--rule"), pen: css("--pen"), box: css("--box"), ok: css("--ok"), gold: css("--gold"),
      card: css("--card"), paper: css("--paper"), penSoft: css("--pen-soft"), boxSoft: css("--box-soft"), sans: css("--sans") };
    return C;
  }
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", colors);

  // ---------- scaffolding ----------
  function frame(host, title, note) {
    const w = document.createElement("div");
    w.className = "widget";
    w.innerHTML = `<div class="w-title">${title}</div>`;
    host.appendChild(w);
    if (note) { const n = document.createElement("p"); n.className = "w-note"; n.innerHTML = note; w._note = n; }
    return w;
  }
  function surface(w, aspect, draw) {
    const cv = document.createElement("canvas");
    w.appendChild(cv);
    const g = cv.getContext("2d");
    const s = { cv, g, W: 600, H: 600 * aspect };
    const fit = () => {
      const cw = Math.max(260, cv.clientWidth || w.clientWidth - 20 || 600);
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      s.W = cw; s.H = Math.round(cw * aspect);
      cv.width = Math.round(cw * dpr); cv.height = Math.round(s.H * dpr); cv.style.height = s.H + "px";
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    fit();
    if (window.ResizeObserver) {
      const ro = new ResizeObserver(() => { if (!cv.isConnected) { ro.disconnect(); return; } const old = s.W, oldH = s.H; if (cv.clientWidth && Math.abs(cv.clientWidth - old) < 1 && cv.height) return; fit(); if (draw && (old !== s.W || oldH !== s.H || true)) draw(); });
      ro.observe(cv);
    }
    return s;
  }
  function controls(w, html) { const d = document.createElement("div"); d.className = "w-controls"; d.innerHTML = html; w.appendChild(d); return d; }
  function readout(w) { const d = document.createElement("div"); d.className = "w-read"; d.setAttribute("aria-live", "polite"); w.appendChild(d); if (w._note) w.appendChild(w._note); return d; }
  const slider = (id, label, min, max, step, val) => `<label for="${id}">${label} <span data-out="${id}"></span><input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${val}"></label>`;
  const check = (id, label, on) => `<label class="check"><input type="checkbox" id="${id}" ${on ? "checked" : ""}> ${label}</label>`;
  const uid = () => "w" + Math.random().toString(36).slice(2, 8);
  function loop(fn) {
    const L = { alive: true };
    loops.add(L);
    let last = performance.now();
    const tick = (now) => {
      if (!L.alive) return;
      const dt = Math.min(0.05, (now - last) / 1000); last = now;
      try { fn(dt); } catch (e) { L.alive = false; loops.delete(L); return; }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    return L;
  }
  function arrow(g, x1, y1, x2, y2, color, wdt = 2) {
    const a = Math.atan2(y2 - y1, x2 - x1), h = 8, len = Math.hypot(x2 - x1, y2 - y1);
    g.strokeStyle = color; g.fillStyle = color; g.lineWidth = wdt;
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke();
    if (len < 3) return;
    g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - h * Math.cos(a - 0.4), y2 - h * Math.sin(a - 0.4)); g.lineTo(x2 - h * Math.cos(a + 0.4), y2 - h * Math.sin(a + 0.4)); g.closePath(); g.fill();
  }
  function label(g, s, x, y, color, align = "left", size = 13) { g.fillStyle = color || C.ink; g.font = `${size}px ${C.sans}`; g.textAlign = align; g.fillText(s, x, y); g.textAlign = "left"; }
  function disc(g, x, y, r, fill, stroke) { g.beginPath(); g.arc(x, y, r, 0, 2 * Math.PI); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = 1.5; g.stroke(); } }
  function springPath(g, x1, y1, x2, y2, n, color) {
    const L = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / L, uy = (y2 - y1) / L, px = -uy, py = ux;
    g.strokeStyle = color; g.lineWidth = 1.6; g.beginPath(); g.moveTo(x1, y1);
    for (let i = 0; i <= n; i++) { const t = 6 + ((L - 12) * i) / n, s = i === 0 || i === n ? 0 : i % 2 ? 6 : -6; g.lineTo(x1 + ux * t + px * s, y1 + uy * t + py * s); }
    g.lineTo(x2, y2); g.stroke();
  }
  function axes(g, x0, y0, w, h, xl, yl) {
    g.strokeStyle = C.rule; g.lineWidth = 1; g.strokeRect(x0, y0, w, h);
    if (xl) label(g, xl, x0 + w - 4, y0 + h - 5, C.muted, "right", 11);
    if (yl) label(g, yl, x0 + 4, y0 + 12, C.muted, "left", 11);
  }
  function plot(g, xs, ys, X, Y, color, wdt = 2, dash) {
    g.strokeStyle = color; g.lineWidth = wdt; g.setLineDash(dash || []); g.beginPath();
    let pen = false;
    for (let i = 0; i < xs.length; i++) {
      if (!isFinite(ys[i])) { pen = false; continue; }
      const px = X(xs[i]), py = Y(ys[i]);
      if (!pen) { g.moveTo(px, py); pen = true; } else g.lineTo(px, py);
    }
    g.stroke(); g.setLineDash([]);
  }
  const lin = (a, b, n) => Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1));
  function rk4(f, y, h) {
    const k1 = f(y), k2 = f(y.map((v, i) => v + (h / 2) * k1[i])), k3 = f(y.map((v, i) => v + (h / 2) * k2[i])), k4 = f(y.map((v, i) => v + h * k3[i]));
    return y.map((v, i) => v + (h / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  }
  function bindOut(w, fmt) { w.querySelectorAll("input[type=range]").forEach((el) => { const o = w.querySelector(`[data-out="${el.id}"]`); const up = () => { if (o) o.textContent = fmt[el.id] ? fmt[el.id](+el.value) : el.value; }; el.addEventListener("input", up); up(); }); }
  function pointer(cv, onDown, onMove) {
    let drag = false;
    const pos = (e) => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    cv.addEventListener("pointerdown", (e) => { if (onDown(...pos(e))) { drag = true; cv.setPointerCapture(e.pointerId); e.preventDefault(); } });
    cv.addEventListener("pointermove", (e) => { if (drag) onMove(...pos(e)); });
    cv.addEventListener("pointerup", () => { drag = false; });
    cv.addEventListener("pointercancel", () => { drag = false; });
  }

  const W = {};

  // ---------- 2-D plotting helpers ----------
  // A view maps world coordinates to canvas pixels; equal scales in x and y unless asked otherwise.
  function view(s, xr, yr, pad = 10) {
    const sx = (s.W - 2 * pad) / (xr[1] - xr[0]), sy = (s.H - 2 * pad) / (yr[1] - yr[0]);
    return {
      X: (x) => pad + (x - xr[0]) * sx, Y: (y) => s.H - pad - (y - yr[0]) * sy,
      iX: (px) => xr[0] + (px - pad) / sx, iY: (py) => yr[0] + (s.H - pad - py) / sy, xr, yr, sx, sy,
    };
  }
  const box = (cx, cy, halfW, aspect) => [[cx - halfW, cx + halfW], [cy - halfW * aspect, cy + halfW * aspect]];
  function grid(f, xr, yr, n) {
    const ny = Math.max(8, Math.round((n * (yr[1] - yr[0])) / (xr[1] - xr[0])));
    const xs = lin(xr[0], xr[1], n + 1), ys = lin(yr[0], yr[1], ny + 1);
    return { xs, ys, F: ys.map((y) => xs.map((x) => f(x, y))) };
  }
  function levelsOf(F, k) {
    const v = F.flat().filter(isFinite).sort((a, b) => a - b);
    return Array.from({ length: k }, (_, i) => v[Math.min(v.length - 1, Math.floor(v.length * ((i + 0.6) / k) ** 2.2))]);
  }
  // Marching squares: draws the level sets of f.
  function contour(g, V, G, levels, color, wdt = 1) {
    const { xs, ys, F } = G;
    g.strokeStyle = color; g.lineWidth = wdt;
    levels.forEach((L) => {
      g.beginPath();
      for (let j = 0; j < ys.length - 1; j++) for (let i = 0; i < xs.length - 1; i++) {
        const c = [[xs[i], ys[j], F[j][i]], [xs[i + 1], ys[j], F[j][i + 1]], [xs[i + 1], ys[j + 1], F[j + 1][i + 1]], [xs[i], ys[j + 1], F[j + 1][i]]];
        const pts = [];
        for (let e = 0; e < 4; e++) {
          const [x1, y1, v1] = c[e], [x2, y2, v2] = c[(e + 1) % 4];
          if ((v1 - L) * (v2 - L) < 0) { const t = (L - v1) / (v2 - v1); pts.push([x1 + t * (x2 - x1), y1 + t * (y2 - y1)]); }
        }
        for (let k = 0; k + 1 < pts.length; k += 2) { g.moveTo(V.X(pts[k][0]), V.Y(pts[k][1])); g.lineTo(V.X(pts[k + 1][0]), V.Y(pts[k + 1][1])); }
      }
      g.stroke();
    });
  }
  // Shade the cells where bad(x, y) is true.
  function shade(g, V, s, bad, color, step = 5) {
    g.fillStyle = color;
    for (let py = 0; py < s.H; py += step) for (let px = 0; px < s.W; px += step) if (bad(V.iX(px + step / 2), V.iY(py + step / 2))) g.fillRect(px, py, step, step);
  }
  function solve(A, b) {
    const n = b.length, M = A.map((r, i) => r.concat([b[i]]));
    for (let k = 0; k < n; k++) {
      let p = k;
      for (let i = k + 1; i < n; i++) if (Math.abs(M[i][k]) > Math.abs(M[p][k])) p = i;
      [M[k], M[p]] = [M[p], M[k]];
      if (Math.abs(M[k][k]) < 1e-300) return null;
      for (let i = k + 1; i < n; i++) { const f = M[i][k] / M[k][k]; for (let j = k; j <= n; j++) M[i][j] -= f * M[k][j]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let t = M[i][n]; for (let j = i + 1; j < n; j++) t -= M[i][j] * x[j]; x[i] = t / M[i][i]; }
    return x;
  }
  // Eigenvalues of a small symmetric matrix (cyclic Jacobi).
  function eigSym(A0) {
    const n = A0.length, A = A0.map((r) => r.slice());
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0;
      for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += A[p][q] ** 2;
      if (off < 1e-22) break;
      for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
        if (Math.abs(A[p][q]) < 1e-300) continue;
        const th = (A[q][q] - A[p][p]) / (2 * A[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), sn = t * c;
        for (let k = 0; k < n; k++) { const akp = A[k][p], akq = A[k][q]; A[k][p] = c * akp - sn * akq; A[k][q] = sn * akp + c * akq; }
        for (let k = 0; k < n; k++) { const apk = A[p][k], aqk = A[q][k]; A[p][k] = c * apk - sn * aqk; A[q][k] = sn * apk + c * aqk; }
      }
    }
    return A.map((r, i) => r[i]).sort((a, b) => a - b);
  }
  function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  const gauss = (r) => { const u = Math.max(1e-12, r()), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const f3 = (x) => (Math.abs(x) >= 1e4 || (Math.abs(x) < 1e-3 && x !== 0) ? x.toExponential(2) : (+x.toFixed(3)).toString());
  const val = (id) => +document.getElementById(id).value;
  const rerun = (w, draw) => w.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", draw));

  // 1. Definiteness of a 2x2 Hessian ------------------------------------------------------
  W.definiteness = (host) => {
    const w = frame(host, "Set the entries of a symmetric matrix H. The contours are q(x) = ½ xᵀHx.", "Positive definite: a bowl (closed ellipses, a minimum). Indefinite: a saddle (hyperbolas). Semidefinite: a trough with a flat direction. The determinant and the trace tell you which, without computing eigenvalues.");
    const a = uid(), b = uid(), c = uid();
    const s = surface(w, 0.6, () => draw());
    controls(w, slider(a, "H₁₁:", -3, 3, 0.1, 2) + slider(b, "H₁₂ = H₂₁:", -3, 3, 0.1, 0.8) + slider(c, "H₂₂:", -3, 3, 0.1, 1));
    const out = readout(w);
    bindOut(w, {});
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const h11 = val(a), h12 = val(b), h22 = val(c);
      const [xr, yr] = box(0, 0, 2.2, s.H / s.W), V = view(s, xr, yr);
      const q = (x, y) => 0.5 * (h11 * x * x + 2 * h12 * x * y + h22 * y * y);
      const G = grid(q, xr, yr, 70);
      const lv = [-4, -2, -1, -0.4, -0.1, 0.1, 0.4, 1, 2, 4];
      contour(g, V, G, lv.filter((l) => l > 0), C.pen, 1.4);
      contour(g, V, G, lv.filter((l) => l < 0), C.box, 1.4);
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(V.X(xr[0]), V.Y(0)); g.lineTo(V.X(xr[1]), V.Y(0)); g.moveTo(V.X(0), V.Y(yr[0])); g.lineTo(V.X(0), V.Y(yr[1])); g.stroke();
      const tr = h11 + h22, det = h11 * h22 - h12 * h12, disc2 = Math.sqrt(Math.max(0, (tr / 2) ** 2 - det));
      const l1 = tr / 2 - disc2, l2 = tr / 2 + disc2;
      const eps = 1e-9;
      const kind = l1 > eps ? "positive definite: a bowl, the origin is a strict minimum" : l2 < -eps ? "negative definite: a dome, the origin is a strict maximum"
        : l1 < -eps && l2 > eps ? "indefinite: a saddle" : l2 > eps ? "positive semidefinite: a trough, flat along one direction" : l1 < -eps ? "negative semidefinite: a ridge" : "zero";
      label(g, "teal: q > 0   orange: q < 0", 14, s.H - 12, C.muted, "left", 12);
      out.innerHTML = `det H = <b>${f3(det)}</b>, trace = <b>${f3(tr)}</b>, eigenvalues ≈ <b>${f3(l1)}</b>, <b>${f3(l2)}</b> → <b>${kind}</b>.`;
    }
    rerun(w, draw); draw();
  };

  // 2. Pareto front and the weighted sum ---------------------------------------------------
  W.pareto = (host) => {
    const w = frame(host, "300 candidate beams. Each dot is one design: its mass against its deflection. Slide the weight to trade one objective for the other.", "Green dots are non-dominated: no other design is lighter and stiffer at once. Minimizing w·mass + (1 − w)·deflection always lands on the front, and changing w walks along it. No single dot is 'the optimum' until you decide how much stiffness a kilogram is worth.");
    const k = uid();
    const r = rng(559);
    const pts = Array.from({ length: 300 }, () => { const b = 0.5 + r(), h = 0.5 + 1.5 * r(); return { m: b * h, d: 1 / (b * h ** 3) }; });
    const mMax = Math.max(...pts.map((p) => p.m)), dMax = Math.max(...pts.map((p) => p.d));
    pts.forEach((p) => { p.x = p.m / mMax; p.y = Math.log10(p.d / dMax * 100 + 1) / Math.log10(101); });
    pts.forEach((p) => { p.front = !pts.some((q) => q !== p && q.x <= p.x && q.y <= p.y && (q.x < p.x || q.y < p.y)); });
    const s = surface(w, 0.6, () => draw());
    controls(w, slider(k, "weight on mass, w:", 0, 1, 0.01, 0.5));
    const out = readout(w);
    bindOut(w, { [k]: (v) => v.toFixed(2) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const wt = val(k), V = view(s, [-0.02, 1.05], [-0.05, 1.05], 30);
      axes(g, 30, 10, s.W - 40, s.H - 40, "mass →", "deflection ↑");
      const score = (p) => wt * p.x + (1 - wt) * p.y;
      const best = pts.reduce((b, p) => (score(p) < score(b) ? p : b));
      const front = pts.filter((p) => p.front).sort((p, q) => p.x - q.x);
      pts.forEach((p) => disc(g, V.X(p.x), V.Y(p.y), p.front ? 3.4 : 2.2, p.front ? C.ok : C.rule));
      g.strokeStyle = C.ok; g.lineWidth = 1.2; g.beginPath(); front.forEach((p, i) => (i ? g.lineTo(V.X(p.x), V.Y(p.y)) : g.moveTo(V.X(p.x), V.Y(p.y)))); g.stroke();
      // iso-line of the weighted score through the chosen design
      const S = score(best);
      g.setLineDash([5, 4]); g.strokeStyle = C.box; g.beginPath();
      if (wt < 1) { g.moveTo(V.X(-0.02), V.Y((S - wt * -0.02) / (1 - wt))); g.lineTo(V.X(1.05), V.Y((S - wt * 1.05) / (1 - wt))); }
      else { g.moveTo(V.X(S), V.Y(-0.05)); g.lineTo(V.X(S), V.Y(1.05)); }
      g.stroke(); g.setLineDash([]);
      disc(g, V.X(best.x), V.Y(best.y), 6, C.box, C.card);
      out.innerHTML = `Chosen design: mass <b>${(best.x * 100).toFixed(0)}%</b> of the heaviest, deflection score <b>${best.y.toFixed(2)}</b>. ${front.length} of 300 designs are on the front.`;
    }
    rerun(w, draw); draw();
  };

  // 3. Feasible region ------------------------------------------------------------------------
  W.feasible = (host) => {
    const w = frame(host, "Two constraints: stay inside the circle x₁² + x₂² ≤ R², and above the line x₁ + x₂ ≥ s. Minimize f = x₁ + 2x₂.", "Shrink R or raise s until the shaded region disappears: the problem becomes infeasible, and no optimizer can fix that. When the region exists, the optimum (orange dot) sits on its boundary, and the constraints it touches are the active ones.");
    const a = uid(), b = uid();
    const s = surface(w, 0.6, () => draw());
    controls(w, slider(a, "R:", 0.3, 2.5, 0.01, 1.6) + slider(b, "s:", -2, 3, 0.01, 0.5));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(2) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const R = val(a), sl = val(b), [xr, yr] = box(0, 0, 3, s.H / s.W), V = view(s, xr, yr);
      const g1 = (x, y) => x * x + y * y - R * R, g2 = (x, y) => sl - x - y, f = (x, y) => x + 2 * y;
      shade(g, V, s, (x, y) => g1(x, y) > 0 || g2(x, y) > 0, C.boxSoft);
      contour(g, V, grid(f, xr, yr, 40), lin(-6, 6, 13), C.rule);
      contour(g, V, grid(g1, xr, yr, 120), [0], C.pen, 2);
      contour(g, V, grid(g2, xr, yr, 20), [0], C.gold, 2);
      // the optimum: the candidates are the circle's own minimizer, and the two circle-line intersections
      const cands = [];
      const t = R / Math.sqrt(5); cands.push([-t, -2 * t]);
      const d = 2 * R * R - sl * sl;
      if (d >= 0) { const r0 = Math.sqrt(d); cands.push([(sl + r0) / 2, (sl - r0) / 2], [(sl - r0) / 2, (sl + r0) / 2]); }
      const feas = cands.filter(([x, y]) => g1(x, y) <= 1e-9 && g2(x, y) <= 1e-9);
      if (!feas.length) { out.innerHTML = `<b>Infeasible.</b> The line x₁ + x₂ = ${sl.toFixed(2)} misses the circle: no point satisfies both constraints.`; return; }
      const best = feas.reduce((p, q) => (f(...q) < f(...p) ? q : p));
      disc(g, V.X(best[0]), V.Y(best[1]), 6, C.box, C.card);
      const act = [Math.abs(g1(...best)) < 1e-6 ? "the circle" : null, Math.abs(g2(...best)) < 1e-6 ? "the line" : null].filter(Boolean);
      out.innerHTML = `Optimum x* ≈ (<b>${best[0].toFixed(3)}</b>, <b>${best[1].toFixed(3)}</b>), f* = <b>${f(...best).toFixed(3)}</b>. Active: <b>${act.join(" and ")}</b>${act.length === 1 ? "; the other constraint is inactive and could be deleted without changing the answer" : ""}.`;
    }
    rerun(w, draw); draw();
  };

  // 4. Design of experiments ------------------------------------------------------------------
  W.doe = (host) => {
    const w = frame(host, "Place n samples in a 2-D design space. Compare the plans.", "The ticks along each edge are the samples projected onto one variable. A full factorial grid repeats the same few values in each variable; a Latin hypercube uses n distinct values per variable. But an LHS can still be bad: 'unlucky' puts every point on the diagonal, which is why optimized LHS maximizes the minimum distance.");
    const m = uid(), n = uid(), sd = uid();
    const s = surface(w, 0.62, () => draw());
    controls(w, `<label for="${m}">plan<select id="${m}"><option value="lhs">Latin hypercube</option><option value="full">full factorial</option><option value="rand">random</option><option value="bad">LHS, unlucky</option></select></label>` + slider(n, "n:", 4, 36, 1, 9) + `<button type="button" class="btn quiet" id="${sd}">New random draw</button>`);
    const out = readout(w);
    bindOut(w, {});
    let seed = 7;
    document.getElementById(sd).addEventListener("click", () => { seed++; draw(); });
    function plan(kind, N) {
      const r = rng(seed * 31 + N);
      if (kind === "full") { const k = Math.max(2, Math.round(Math.sqrt(N))); const P = []; for (let i = 0; i < k; i++) for (let j = 0; j < k; j++) P.push([(i + 0.5) / k, (j + 0.5) / k]); return P; }
      if (kind === "rand") return Array.from({ length: N }, () => [r(), r()]);
      const perm = Array.from({ length: N }, (_, i) => i);
      if (kind === "lhs") for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
      return perm.map((p, i) => [(i + (kind === "bad" ? 0.5 : r())) / N, (p + (kind === "bad" ? 0.5 : r())) / N]);
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const kind = document.getElementById(m).value, P = plan(kind, val(n));
      const side = Math.min(s.W - 60, s.H - 40), x0 = (s.W - side) / 2, y0 = 10;
      const X = (u) => x0 + u * side, Y = (v) => y0 + side - v * side;
      g.strokeStyle = C.rule; g.lineWidth = 1; g.strokeRect(x0, y0, side, side);
      if (kind !== "full" && kind !== "rand") { g.globalAlpha = 0.5; for (let i = 1; i < P.length; i++) { g.beginPath(); g.moveTo(X(i / P.length), y0); g.lineTo(X(i / P.length), y0 + side); g.moveTo(x0, Y(i / P.length)); g.lineTo(x0 + side, Y(i / P.length)); g.stroke(); } g.globalAlpha = 1; }
      P.forEach(([u, v]) => { disc(g, X(u), Y(v), 4.5, C.pen); g.strokeStyle = C.box; g.lineWidth = 1.5; g.beginPath(); g.moveTo(X(u), y0 + side); g.lineTo(X(u), y0 + side + 8); g.moveTo(x0, Y(v)); g.lineTo(x0 - 8, Y(v)); g.stroke(); });
      let dmin = Infinity;
      for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) dmin = Math.min(dmin, Math.hypot(P[i][0] - P[j][0], P[i][1] - P[j][1]));
      const ux = new Set(P.map((p) => p[0].toFixed(4))).size;
      out.innerHTML = `${P.length} samples, <b>${ux}</b> distinct values of x₁, minimum spacing <b>${dmin.toFixed(3)}</b> (bigger is better spread).`;
    }
    rerun(w, draw); draw();
  };

  // 5. Model assessment: underfit, overfit, test error ----------------------------------------
  W.fit = (host) => {
    const w = frame(host, "Fit a polynomial of degree p to 12 noisy samples. The right panel tracks training and test error as p grows.", "Training error (teal) only ever falls. Test error (orange) falls, bottoms out, then climbs: past that point the model is fitting the noise. A small ridge penalty tames the high-degree wiggles without lowering the degree.");
    const k = uid(), l = uid();
    const r = rng(2024), truth = (x) => Math.sin(2 * Math.PI * x) + 0.4 * x;
    const xtr = lin(0.02, 0.98, 12).map((x) => x + 0.02 * gauss(r)), ytr = xtr.map((x) => truth(x) + 0.18 * gauss(r));
    const xte = lin(0.01, 0.99, 60), yte = xte.map((x) => truth(x) + 0.18 * gauss(r));
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(k, "degree p:", 0, 11, 1, 3) + slider(l, "ridge log₁₀ λ:", -12, 0, 0.5, -12));
    const out = readout(w);
    bindOut(w, { [l]: (v) => (v <= -12 ? "off" : v.toFixed(1)) });
    const feat = (x, p) => Array.from({ length: p + 1 }, (_, j) => (2 * x - 1) ** j);
    function fitPoly(p, lam) {
      const Phi = xtr.map((x) => feat(x, p));
      const A = Array.from({ length: p + 1 }, (_, i) => Array.from({ length: p + 1 }, (_, j) => Phi.reduce((t, row) => t + row[i] * row[j], 0) + (i === j ? lam : 0)));
      const bb = Array.from({ length: p + 1 }, (_, i) => Phi.reduce((t, row, n) => t + row[i] * ytr[n], 0));
      const c = solve(A, bb) || new Array(p + 1).fill(0);
      return (x) => feat(x, p).reduce((t, v, j) => t + v * c[j], 0);
    }
    const rmse = (m, xs, ys) => Math.sqrt(xs.reduce((t, x, i) => t + (m(x) - ys[i]) ** 2, 0) / xs.length);
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const p = val(k), lam = val(l) <= -12 ? 1e-12 : 10 ** val(l), m = fitPoly(p, lam);
      const wL = s.W * 0.6;
      const X = (x) => 10 + x * (wL - 20), Y = (y) => s.H / 2 - y * (s.H / 4.6);
      axes(g, 8, 8, wL - 16, s.H - 16, "x", "y");
      const xs = lin(0, 1, 300);
      plot(g, xs, xs.map(truth), X, Y, C.muted, 1.2, [4, 4]);
      plot(g, xs, xs.map((x) => Math.max(-3, Math.min(3, m(x)))), X, Y, C.pen, 2.2);
      xte.forEach((x, i) => disc(g, X(x), Y(yte[i]), 2, C.boxSoft, C.box));
      xtr.forEach((x, i) => disc(g, X(x), Y(ytr[i]), 4, C.pen));
      // error vs degree
      const errs = Array.from({ length: 12 }, (_, q) => { const mq = fitPoly(q, lam); return [rmse(mq, xtr, ytr), rmse(mq, xte, yte)]; });
      const x0 = wL + 14, w2 = s.W - x0 - 10, top = 14, h2 = s.H - 40, eMax = 1.0;
      axes(g, x0, top, w2, h2, "degree", "RMSE");
      const EX = (q) => x0 + 6 + (q / 11) * (w2 - 12), EY = (e) => top + h2 - (Math.min(e, eMax) / eMax) * (h2 - 16);
      plot(g, errs.map((_, q) => q), errs.map((e) => e[0]), EX, EY, C.pen, 2);
      plot(g, errs.map((_, q) => q), errs.map((e) => e[1]), EX, EY, C.box, 2);
      g.strokeStyle = C.gold; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(EX(p), top); g.lineTo(EX(p), top + h2); g.stroke(); g.setLineDash([]);
      label(g, "train", EX(11) - 2, EY(errs[11][0]) - 6, C.pen, "right", 11); label(g, "test", EX(11) - 2, EY(errs[11][1]) + 14, C.box, "right", 11);
      const bestQ = errs.reduce((b, e, q) => (e[1] < errs[b][1] ? q : b), 0);
      out.innerHTML = `Degree ${p}: training RMSE <b>${errs[p][0].toFixed(3)}</b>, test RMSE <b>${errs[p][1].toFixed(3)}</b>. Lowest test error at degree <b>${bestQ}</b>. (Noise level: 0.18.)`;
    }
    rerun(w, draw); draw();
  };

  // 6. RBF interpolation and the shape parameter ---------------------------------------------
  W.rbf = (host) => {
    const w = frame(host, "Gaussian RBF interpolation through 7 samples, φ(r) = exp(−(εr)²). Change the shape parameter ε.", "Large ε: narrow spikes that drop to zero between samples. Small ε: wide, smooth bumps, but the interpolation matrix becomes nearly singular (watch the condition number) and the weights blow up. The best ε is in between, and cross-validation is how you find it.");
    const e = uid();
    const truth = (x) => Math.sin(5 * x) + 0.5 * x, xs0 = [0.05, 0.2, 0.33, 0.5, 0.62, 0.8, 0.95], ys0 = xs0.map(truth);
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(e, "log₁₀ ε:", -0.5, 2, 0.02, 0.6));
    const out = readout(w);
    bindOut(w, { [e]: (v) => "ε = " + f3(10 ** v) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const eps = 10 ** val(e), phi = (r) => Math.exp(-((eps * r) ** 2));
      const A = xs0.map((a) => xs0.map((b) => phi(Math.abs(a - b))));
      const wts = solve(A, ys0) || xs0.map(() => 0);
      const ev = eigSym(A), cond = ev[ev.length - 1] / Math.max(Math.abs(ev[0]), 1e-300);
      const m = (x) => xs0.reduce((t, xi, i) => t + wts[i] * phi(Math.abs(x - xi)), 0);
      const X = (x) => 10 + x * (s.W - 20), Y = (y) => s.H * 0.55 - y * (s.H / 4.2);
      axes(g, 8, 8, s.W - 16, s.H - 16, "x", "y");
      const xs = lin(0, 1, 400);
      plot(g, xs, xs.map(truth), X, Y, C.muted, 1.2, [4, 4]);
      plot(g, xs, xs.map((x) => Math.max(-2.5, Math.min(2.5, m(x)))), X, Y, C.pen, 2.2);
      xs0.forEach((x, i) => disc(g, X(x), Y(ys0[i]), 4.5, C.box));
      const err = Math.sqrt(xs.reduce((t, x) => t + (m(x) - truth(x)) ** 2, 0) / xs.length);
      out.innerHTML = `ε = <b>${f3(eps)}</b>: error against the truth (dashed) <b>${f3(err)}</b>, largest |weight| <b>${f3(Math.max(...wts.map(Math.abs)))}</b>, condition number of Φ <b>${cond > 1e15 ? "> 10¹⁵ (numerically singular)" : f3(cond)}</b>.`;
    }
    rerun(w, draw); draw();
  };

  // 7. Kriging / Gaussian process -------------------------------------------------------------
  W.kriging = (host) => {
    const w = frame(host, "A Gaussian process through a few samples. Click the plot to add a sample. The band is the mean ± 2σ.", "The band pinches to zero at each sample and widens between them: that's the model telling you where it's unsure, which is what makes GP surrogates useful for deciding where to sample next. Turn off 'normalize y' and watch the mean sink toward 0 away from the data, because the prior mean is 0.");
    const l = uid(), nz = uid(), nm = uid(), rs = uid();
    const truth = (x) => 3 + Math.sin(6 * x) + 0.5 * Math.cos(15 * x);
    let X0 = [0.1, 0.35, 0.55, 0.9];
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(l, "length scale ℓ:", 0.02, 0.5, 0.005, 0.12) + slider(nz, "noise σₙ:", 0, 0.3, 0.01, 0) + check(nm, "normalize y", true) + `<button type="button" class="btn quiet" id="${rs}">Reset samples</button>`);
    const out = readout(w);
    bindOut(w, {});
    document.getElementById(rs).addEventListener("click", () => { X0 = [0.1, 0.35, 0.55, 0.9]; draw(); });
    const Xp = (x) => 10 + x * (s.W - 20), Yp = (y) => s.H - 14 - (y + 0.5) * ((s.H - 28) / 5.5);
    pointer(s.cv, (px) => { const x = (px - 10) / (s.W - 20); if (x > 0 && x < 1 && X0.length < 25) { X0.push(x); draw(); } return false; }, () => {});
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const ell = val(l), sn = val(nz), norm = document.getElementById(nm).checked;
      const Y0 = X0.map(truth), mu0 = norm ? Y0.reduce((a, b) => a + b, 0) / Y0.length : 0;
      const sf2 = norm ? Math.max(0.3, Y0.reduce((t, y) => t + (y - mu0) ** 2, 0) / Y0.length) : 1;
      const k = (a, b) => sf2 * Math.exp(-((a - b) ** 2) / (2 * ell * ell));
      const K = X0.map((a, i) => X0.map((b, j) => k(a, b) + (i === j ? sn * sn + 1e-8 : 0)));
      const alpha = solve(K, Y0.map((y) => y - mu0)) || X0.map(() => 0);
      const xs = lin(0, 1, 240), mean = [], sd = [];
      xs.forEach((x) => {
        const ks = X0.map((a) => k(x, a)), v = solve(K, ks) || ks.map(() => 0);
        mean.push(mu0 + ks.reduce((t, kv, i) => t + kv * alpha[i], 0));
        sd.push(Math.sqrt(Math.max(0, sf2 - ks.reduce((t, kv, i) => t + kv * v[i], 0))));
      });
      axes(g, 8, 8, s.W - 16, s.H - 16, "x", "y");
      g.fillStyle = C.penSoft; g.beginPath();
      xs.forEach((x, i) => (i ? g.lineTo(Xp(x), Yp(mean[i] + 2 * sd[i])) : g.moveTo(Xp(x), Yp(mean[i] + 2 * sd[i]))));
      for (let i = xs.length - 1; i >= 0; i--) g.lineTo(Xp(xs[i]), Yp(mean[i] - 2 * sd[i]));
      g.closePath(); g.fill();
      plot(g, xs, xs.map(truth), Xp, Yp, C.muted, 1.2, [4, 4]);
      plot(g, xs, mean, Xp, Yp, C.pen, 2.2);
      X0.forEach((x, i) => disc(g, Xp(x), Yp(Y0[i]), 4.5, C.box));
      const iMax = sd.indexOf(Math.max(...sd));
      g.strokeStyle = C.gold; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(Xp(xs[iMax]), 10); g.lineTo(Xp(xs[iMax]), s.H - 10); g.stroke(); g.setLineDash([]);
      out.innerHTML = `${X0.length} samples. Most uncertain at x ≈ <b>${xs[iMax].toFixed(2)}</b> (gold line, σ = ${sd[iMax].toFixed(2)}): the natural place for the next sample. Prior mean: <b>${mu0.toFixed(2)}</b>.`;
    }
    rerun(w, draw); draw();
  };

  // 8. Descent methods on a contour map (also the scaling preset) ---------------------------
  const FUNCS = {
    bowl: { name: "tilted bowl", f: (x, y) => 2 * x * x + 2 * x * y + 3 * y * y + 2 * x, g: (x, y) => [4 * x + 2 * y + 2, 2 * x + 6 * y], H: () => [[4, 2], [2, 6]], c: [-0.5, 0], hw: 2.6, x0: [1.8, 1.2] },
    valley: { name: "narrow valley", f: (x, y) => 0.5 * (x * x + 25 * y * y), g: (x, y) => [x, 25 * y], H: () => [[1, 0], [0, 25]], c: [0, 0], hw: 3, x0: [-2.6, 0.8] },
    rosen: { name: "Rosenbrock (b = 10)", f: (x, y) => (1 - x) ** 2 + 10 * (y - x * x) ** 2, g: (x, y) => [-2 * (1 - x) - 40 * x * (y - x * x), 20 * (y - x * x)], H: (x, y) => [[2 - 40 * (y - x * x) + 80 * x * x, -40 * x], [-40 * x, 20]], c: [0, 1], hw: 2.2, x0: [-1.5, 2.2] },
  };
  function runMethod(P, method, x0, alpha, maxIt = 300) {
    const path = [x0.slice()];
    let x = x0.slice(), Hinv = [[1, 0], [0, 1]], g = P.g(...x), it = 0;
    const armijo = (d) => { let a = 1; const f0 = P.f(...x), slope = g[0] * d[0] + g[1] * d[1]; for (let k = 0; k < 40 && P.f(x[0] + a * d[0], x[1] + a * d[1]) > f0 + 1e-4 * a * slope; k++) a *= 0.5; return a; };
    for (; it < maxIt; it++) {
      if (Math.hypot(...g) < 1e-6) break;
      let d, a;
      if (method === "gd") { d = [-g[0], -g[1]]; a = alpha; }
      else if (method === "gdls") { d = [-g[0], -g[1]]; a = armijo(d); }
      else if (method === "newton") { const H = P.H(...x); d = solve(H, [-g[0], -g[1]]) || [-g[0], -g[1]]; a = 1; }
      else { d = [-(Hinv[0][0] * g[0] + Hinv[0][1] * g[1]), -(Hinv[1][0] * g[0] + Hinv[1][1] * g[1])]; if (d[0] * g[0] + d[1] * g[1] >= 0) { Hinv = [[1, 0], [0, 1]]; d = [-g[0], -g[1]]; } a = armijo(d); }
      const xn = [x[0] + a * d[0], x[1] + a * d[1]];
      if (!isFinite(xn[0]) || Math.hypot(...xn) > 1e6) { path.push(xn); return { path, it: it + 1, diverged: true }; }
      const gn = P.g(...xn);
      if (method === "bfgs") {
        const sv = [xn[0] - x[0], xn[1] - x[1]], yv = [gn[0] - g[0], gn[1] - g[1]], sy = sv[0] * yv[0] + sv[1] * yv[1];
        if (sy > 1e-12) {
          const r = 1 / sy, I = [[1, 0], [0, 1]];
          const Lm = I.map((row, i) => row.map((v, j) => v - r * sv[i] * yv[j])), Rm = I.map((row, i) => row.map((v, j) => v - r * yv[i] * sv[j]));
          const T = Lm.map((row) => [0, 1].map((j) => row[0] * Hinv[0][j] + row[1] * Hinv[1][j]));
          Hinv = T.map((row, i) => [0, 1].map((j) => row[0] * Rm[0][j] + row[1] * Rm[1][j] + r * sv[i] * sv[j]));
        }
      }
      x = xn; g = gn; path.push(x.slice());
    }
    return { path, it, diverged: false };
  }
  W.descent = (host, spec) => {
    const scaling = spec.preset === "scaling";
    const w = frame(host, scaling ? "Gradient descent with a line search on f = ½(κx₁² + x₂²). Stretch the bowl with κ, then rescale the variables." : "Pick a function and a method. Click the map to move the start point.",
      scaling ? "As κ grows, the contours become thin ellipses and the steepest direction points across the valley, not along it: the iteration count explodes. Rescaling x̂₁ = √κ·x₁ makes the bowl round again, and one line-search step lands on the minimum."
        : "Fixed-step gradient descent overshoots if α is too big and crawls if it's too small. A line search (Armijo backtracking) picks α for you. Newton's method uses curvature and jumps straight to the minimum of a quadratic; BFGS learns that curvature from gradients alone.");
    const fn = uid(), md = uid(), al = uid(), kp = uid(), sc = uid();
    const s = surface(w, 0.62, () => draw());
    controls(w, scaling ? slider(kp, "κ:", 0, 3, 0.05, 1.3) + check(sc, "rescale x̂₁ = √κ x₁", false)
      : `<label for="${fn}">function<select id="${fn}">${Object.entries(FUNCS).map(([k2, P]) => `<option value="${k2}">${P.name}</option>`).join("")}</select></label>`
      + `<label for="${md}">method<select id="${md}"><option value="gd">gradient, fixed step α</option><option value="gdls">gradient + Armijo line search</option><option value="newton">Newton</option><option value="bfgs">BFGS + line search</option></select></label>` + slider(al, "α:", 0.01, 0.6, 0.01, 0.12));
    const out = readout(w);
    bindOut(w, { [kp]: (v) => "κ = " + f3(10 ** v) });
    let start = null;
    function problem() {
      if (!scaling) return FUNCS[document.getElementById(fn).value];
      const kap = 10 ** val(kp), on = document.getElementById(sc).checked;
      if (on) return { f: (x, y) => 0.5 * (x * x + y * y), g: (x, y) => [x, y], H: () => [[1, 0], [0, 1]], c: [0, 0], hw: 3.2, x0: [-1.0 * Math.sqrt(kap), 1.6], scaled: true, kap };
      return { f: (x, y) => 0.5 * (kap * x * x + y * y), g: (x, y) => [kap * x, y], H: () => [[kap, 0], [0, 1]], c: [0, 0], hw: 3.2, x0: [-1.0, 1.6], kap };
    }
    let V = null;
    pointer(s.cv, (px, py) => { if (V) { start = [V.iX(px), V.iY(py)]; draw(); } return false; }, () => {});
    rerun(w, () => { start = null; draw(); });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const P = problem(), method = scaling ? "gdls" : document.getElementById(md).value;
      const hw = P.scaled ? Math.max(P.hw, Math.abs(P.x0[0]) * 1.2) : P.hw;
      const [xr, yr] = box(P.c[0], P.c[1] + (P === FUNCS.rosen ? 0.2 : 0), hw, s.H / s.W);
      V = view(s, xr, yr);
      const G = grid(P.f, xr, yr, 90);
      contour(g, V, G, levelsOf(G.F, 14), C.rule, 1.2);
      const x0 = start || P.x0;
      const res = runMethod(P, method, x0, scaling ? 1 : val(al));
      g.strokeStyle = C.box; g.lineWidth = 1.8; g.beginPath();
      res.path.forEach((p, i) => { const px = Math.max(-50, Math.min(s.W + 50, V.X(p[0]))), py = Math.max(-50, Math.min(s.H + 50, V.Y(p[1]))); i ? g.lineTo(px, py) : g.moveTo(px, py); });
      g.stroke();
      res.path.slice(0, 80).forEach((p) => disc(g, V.X(p[0]), V.Y(p[1]), 2.6, C.box));
      disc(g, V.X(x0[0]), V.Y(x0[1]), 5, C.gold, C.card);
      const last = res.path[res.path.length - 1];
      const tail = res.diverged ? "<b>diverged</b>: the step is too long for this curvature." : res.it >= 300 ? "<b>not converged</b> after 300 iterations." : `converged in <b>${res.it}</b> iteration${res.it === 1 ? "" : "s"} to (${last[0].toFixed(3)}, ${last[1].toFixed(3)}).`;
      out.innerHTML = scaling ? `κ = ${f3(P.kap)}${P.scaled ? " (rescaled: the bowl is round)" : ""}: ${tail}` : `${tail}`;
    }
    draw();
  };

  // 9. Armijo backtracking on a line ----------------------------------------------------------
  W.armijo = (host) => {
    const w = frame(host, "The slice φ(α) = f(x + αd) along a descent direction. Armijo accepts α when φ(α) lies under the line φ(0) + c₁αφ′(0).", "Green stretches of the α axis are acceptable. Backtracking starts at α₀ and halves until it lands in green: it never needs the exact minimizer. A larger c₁ demands more decrease and shrinks the green zone; the curvature (Wolfe) condition also rules out steps that are too short.");
    const c = uid(), a0 = uid(), wf = uid();
    const phi = (a) => 1 - 2 * a + 1.1 * a * a + 0.35 * a ** 4, dphi = (a) => -2 + 2.2 * a + 1.4 * a ** 3;
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(c, "c₁:", 0.01, 0.9, 0.01, 0.3) + slider(a0, "start α₀:", 0.2, 2, 0.05, 1.6) + check(wf, "also require curvature, c₂ = 0.9", false));
    const out = readout(w);
    bindOut(w, {});
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const c1 = val(c), wolfe = document.getElementById(wf).checked;
      const X = (a) => 30 + (a / 2) * (s.W - 44), Y = (v) => 16 + ((1.3 - v) / 1.9) * (s.H - 46);
      axes(g, 28, 8, s.W - 36, s.H - 30, "α", "φ");
      const ok = (a) => phi(a) <= phi(0) + c1 * a * dphi(0) && (!wolfe || dphi(a) >= 0.9 * dphi(0));
      const as = lin(0, 2, 600);
      g.fillStyle = C.ok; as.forEach((a) => { if (a > 0 && ok(a)) g.fillRect(X(a) - 1, s.H - 24, 2.4, 6); });
      plot(g, [0, 2], [phi(0), phi(0) + c1 * 2 * dphi(0)], X, Y, C.ok, 1.5, [5, 4]);
      plot(g, [0, 0.7], [phi(0), phi(0) + 0.7 * dphi(0)], X, Y, C.muted, 1, [2, 3]);
      plot(g, as, as.map(phi), X, Y, C.pen, 2.2);
      let a = val(a0), k = 0;
      const trials = [];
      for (; k < 20; k++) { trials.push(a); if (ok(a)) break; a /= 2; }
      trials.forEach((t, i) => { disc(g, X(t), Y(phi(t)), 5, i === trials.length - 1 ? C.box : C.card, C.box); label(g, String(i + 1), X(t), Y(phi(t)) - 9, C.box, "center", 11); });
      let lo = null, hi = null;
      as.forEach((t) => { if (t > 0 && ok(t)) { if (lo === null) lo = t; hi = t; } });
      out.innerHTML = `Acceptable roughly for α in [<b>${lo === null ? "–" : lo.toFixed(2)}</b>, <b>${hi === null ? "–" : hi.toFixed(2)}</b>]. Backtracking from α₀ = ${val(a0).toFixed(2)} accepts <b>α = ${f3(trials[trials.length - 1])}</b> after ${trials.length} trial${trials.length > 1 ? "s" : ""}. (Exact minimizer ≈ 0.76.)`;
    }
    rerun(w, draw); draw();
  };

  // 10. Trust region ---------------------------------------------------------------------------
  W.trust = (host) => {
    const w = frame(host, "A quadratic model m(p) = gᵀp + ½pᵀBp around the current point, trusted only inside a circle of radius Δ.", "Grow Δ until the circle contains the model's own minimum (for a convex model) and the step stops changing. Make the model indefinite and the step always runs to the boundary, which is exactly what makes trust regions safe where Newton's step isn't. ρ compares the true decrease with the predicted one and decides the next radius.");
    const d = uid(), bt = uid();
    const s = surface(w, 0.62, () => draw());
    controls(w, slider(d, "radius Δ:", 0.1, 3, 0.02, 0.8) + `<label for="${bt}">model curvature B<select id="${bt}"><option value="pd">positive definite</option><option value="ind">indefinite</option></select></label>`);
    const out = readout(w);
    bindOut(w, { [d]: (v) => v.toFixed(2) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const D = val(d), gv = [-1.2, -0.6], B = document.getElementById(bt).value === "pd" ? [[1, 0.3], [0.3, 0.6]] : [[1, 0.3], [0.3, -0.4]];
      const m = (x, y) => gv[0] * x + gv[1] * y + 0.5 * (B[0][0] * x * x + 2 * B[0][1] * x * y + B[1][1] * y * y);
      const fTrue = (x, y) => m(x, y) + 0.06 * x ** 4 + 0.08 * y ** 4;
      const [xr, yr] = box(0.6, 0.4, 3.4, s.H / s.W), V = view(s, xr, yr);
      const G = grid(m, xr, yr, 80);
      contour(g, V, G, levelsOf(G.F, 14), C.rule, 1.2);
      const lmin = eigSym(B)[0];
      const pOf = (lam) => solve([[B[0][0] + lam, B[0][1]], [B[1][0], B[1][1] + lam]], [-gv[0], -gv[1]]);
      let p, interior = false;
      if (lmin > 0) { const pn = pOf(0); if (Math.hypot(...pn) <= D) { p = pn; interior = true; } }
      if (!p) { let lo = Math.max(0, -lmin) + 1e-9, hi = lo + 100; for (let k = 0; k < 100; k++) { const mid = (lo + hi) / 2; if (Math.hypot(...pOf(mid)) > D) lo = mid; else hi = mid; } p = pOf(hi); }
      const gn = Math.hypot(...gv), gBg = gv[0] * (B[0][0] * gv[0] + B[0][1] * gv[1]) + gv[1] * (B[1][0] * gv[0] + B[1][1] * gv[1]);
      const tau = gBg <= 0 ? 1 : Math.min(1, gn ** 3 / (D * gBg)), pc = [-tau * D * gv[0] / gn, -tau * D * gv[1] / gn];
      g.strokeStyle = C.pen; g.lineWidth = 2; g.beginPath(); g.arc(V.X(0), V.Y(0), D * V.sx, 0, 2 * Math.PI); g.stroke();
      g.fillStyle = C.penSoft; g.fill();
      arrow(g, V.X(0), V.Y(0), V.X(p[0]), V.Y(p[1]), C.box, 2.2);
      disc(g, V.X(pc[0]), V.Y(pc[1]), 4.5, C.gold, C.card);
      disc(g, V.X(0), V.Y(0), 4, C.ink);
      label(g, "Cauchy point", V.X(pc[0]) + 7, V.Y(pc[1]) + 14, C.gold, "left", 11);
      const pred = -m(...p), act = -fTrue(...p), rho = act / pred;
      const verdict = rho < 0.25 ? "ρ < 0.25: poor agreement, shrink Δ" : rho > 0.75 && !interior ? "ρ > 0.75 and the step hit the boundary: expand Δ" : "keep Δ";
      out.innerHTML = `Step ‖p‖ = <b>${Math.hypot(...p).toFixed(2)}</b> ${interior ? "(the model's own minimum, inside the circle)" : "(on the boundary)"}. Predicted decrease <b>${pred.toFixed(3)}</b>, actual <b>${act.toFixed(3)}</b>, ρ = <b>${rho.toFixed(2)}</b> → ${verdict}.`;
    }
    rerun(w, draw); draw();
  };

  // 11. Linear programming geometry -------------------------------------------------------------
  W.lp = (host) => {
    const w = frame(host, "Maximize c₁x₁ + c₂x₂ over the shaded polygon. Turn the objective direction c.", "The optimum always sits at a vertex (a basic feasible solution); the simplex method walks from vertex to vertex along improving edges. When c is perpendicular to an edge, the whole edge ties: infinitely many optima, but still a vertex among them.");
    const t = uid();
    const cons = [[1, 1, 4], [1, 3, 6], [2, -1, 5]]; // a x1 + b x2 <= rhs, plus x >= 0
    const all = cons.concat([[-1, 0, 0], [0, -1, 0]]);
    const feas = (x, y) => all.every(([a, b, r]) => a * x + b * y <= r + 1e-9);
    const verts = [];
    for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) { const p = solve([[all[i][0], all[i][1]], [all[j][0], all[j][1]]], [all[i][2], all[j][2]]); if (p && feas(...p) && !verts.some((v) => Math.hypot(v[0] - p[0], v[1] - p[1]) < 1e-9)) verts.push(p); }
    const cx = verts.reduce((a, v) => a + v[0], 0) / verts.length, cy = verts.reduce((a, v) => a + v[1], 0) / verts.length;
    verts.sort((p, q) => Math.atan2(p[1] - cy, p[0] - cx) - Math.atan2(q[1] - cy, q[0] - cx));
    const s = surface(w, 0.62, () => draw());
    controls(w, slider(t, "direction of c:", 0, 180, 1, 35));
    const out = readout(w);
    bindOut(w, { [t]: (v) => v + "°" });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const th = (val(t) * Math.PI) / 180, c = [Math.cos(th), Math.sin(th)];
      const [xr, yr] = box(2, 1.4, 2.8, s.H / s.W), V = view(s, xr, yr);
      g.fillStyle = C.penSoft; g.strokeStyle = C.pen; g.lineWidth = 2; g.beginPath(); verts.forEach((v, i) => (i ? g.lineTo(V.X(v[0]), V.Y(v[1])) : g.moveTo(V.X(v[0]), V.Y(v[1])))); g.closePath(); g.fill(); g.stroke();
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(V.X(xr[0]), V.Y(0)); g.lineTo(V.X(xr[1]), V.Y(0)); g.moveTo(V.X(0), V.Y(yr[0])); g.lineTo(V.X(0), V.Y(yr[1])); g.stroke();
      const vals = verts.map((v) => c[0] * v[0] + c[1] * v[1]), best = Math.max(...vals);
      const winners = verts.filter((_, i) => vals[i] > best - 1e-6);
      // objective level line through the optimum
      g.setLineDash([6, 4]); g.strokeStyle = C.box; g.beginPath();
      const px = -c[1], py = c[0], o = winners[0];
      g.moveTo(V.X(o[0] - 8 * px), V.Y(o[1] - 8 * py)); g.lineTo(V.X(o[0] + 8 * px), V.Y(o[1] + 8 * py)); g.stroke(); g.setLineDash([]);
      verts.forEach((v) => disc(g, V.X(v[0]), V.Y(v[1]), 4, C.card, C.pen));
      winners.forEach((v) => disc(g, V.X(v[0]), V.Y(v[1]), 6.5, C.box, C.card));
      arrow(g, V.X(cx), V.Y(cy), V.X(cx + 0.9 * c[0]), V.Y(cy + 0.9 * c[1]), C.gold, 2.4);
      label(g, "c", V.X(cx + 0.95 * c[0]) + 6, V.Y(cy + 0.95 * c[1]), C.gold);
      out.innerHTML = winners.length > 1 ? `A <b>whole edge</b> is optimal, from (${winners.map((v) => v.map((z) => z.toFixed(2)).join(", ")).join(") to (")}): c is perpendicular to it.`
        : `Optimal vertex x* = (<b>${winners[0][0].toFixed(2)}</b>, <b>${winners[0][1].toFixed(2)}</b>), objective <b>${best.toFixed(3)}</b>. ${verts.length} vertices in all.`;
    }
    rerun(w, draw); draw();
  };

  // 12. KKT conditions by dragging a point ------------------------------------------------------
  W.kkt = (host) => {
    const w = frame(host, "Minimize f = (x₁ − 2)² + (x₂ − 1.5)² inside the circle g₁ = x₁² + x₂² − 2 ≤ 0. Drag the point; it snaps to boundaries.", "At a KKT point, −∇f (orange) is a non-negative combination of the active constraint gradients (teal): the constraints push back exactly as hard as f pulls. If −∇f has a component along the boundary, slide that way. If a multiplier would be negative, the constraint is pulling the wrong way: release it and move inside.");
    const t2 = uid(), go = uid();
    const s = surface(w, 0.62, () => draw());
    controls(w, check(t2, "add g₂ = x₁ − 1 ≤ 0", false) + `<button type="button" class="btn quiet" id="${go}">Jump to the optimum</button>`);
    const out = readout(w);
    let P = [-0.6, 0.4], V = null;
    const f = (x, y) => (x - 2) ** 2 + (y - 1.5) ** 2, gf = (x, y) => [2 * (x - 2), 2 * (y - 1.5)];
    const cons = () => [{ n: "g₁", g: (x, y) => x * x + y * y - 2, d: (x, y) => [2 * x, 2 * y] }].concat(document.getElementById(t2).checked ? [{ n: "g₂", g: (x) => x - 1, d: () => [1, 0] }] : []);
    function snap(p) {
      const two = document.getElementById(t2).checked, tol = 10 / V.sx;
      let [x, y] = p;
      if (two && Math.hypot(x - 1, y - 1) < tol * 1.4) return [1, 1];
      const r = Math.hypot(x, y);
      if (Math.abs(r - Math.SQRT2) < tol) { x *= Math.SQRT2 / r; y *= Math.SQRT2 / r; }
      if (two && Math.abs(x - 1) < tol) x = 1;
      return [x, y];
    }
    document.getElementById(go).addEventListener("click", () => { P = document.getElementById(t2).checked ? [1, 1] : [2 * Math.SQRT2 / 2.5, 1.5 * Math.SQRT2 / 2.5]; draw(); });
    pointer(s.cv, (px, py) => { if (!V) return false; const hit = Math.hypot(px - V.X(P[0]), py - V.Y(P[1])) < 22; if (hit) return true; P = snap([V.iX(px), V.iY(py)]); draw(); return true; },
      (px, py) => { P = snap([V.iX(px), V.iY(py)]); draw(); });
    rerun(w, draw);
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const [xr, yr] = box(0.4, 0.5, 2.6, s.H / s.W); V = view(s, xr, yr);
      const C2 = cons();
      shade(g, V, s, (x, y) => C2.some((c) => c.g(x, y) > 0), C.boxSoft);
      const G = grid(f, xr, yr, 70); contour(g, V, G, [0.25, 0.75, 1.5, 2.5, 4, 6, 9, 13], C.rule, 1.2);
      C2.forEach((c) => contour(g, V, grid(c.g, xr, yr, 120), [0], C.pen, 2));
      disc(g, V.X(2), V.Y(1.5), 3, C.muted); label(g, "unconstrained min", V.X(2) - 6, V.Y(1.5) - 8, C.muted, "right", 11);
      const [x, y] = P, gr = gf(x, y), sc = 0.35;
      const viol = C2.filter((c) => c.g(x, y) > 1e-6), act = C2.filter((c) => Math.abs(c.g(x, y)) <= 1e-6);
      arrow(g, V.X(x), V.Y(y), V.X(x - sc * gr[0]), V.Y(y - sc * gr[1]), C.box, 2.4);
      act.forEach((c) => { const d = c.d(x, y), n = Math.hypot(...d); arrow(g, V.X(x), V.Y(y), V.X(x + (0.9 * d[0]) / n), V.Y(y + (0.9 * d[1]) / n), C.pen, 2); });
      disc(g, V.X(x), V.Y(y), 7, C.gold, C.card);
      let msg;
      if (viol.length) msg = `<b>Infeasible</b>: ${viol.map((c) => c.n).join(" and ")} violated. KKT points must be feasible first.`;
      else if (!act.length) msg = Math.hypot(...gr) < 1e-3 ? "Interior and ∇f = 0: a KKT point with every μ = 0." : `Interior point, no active constraints, but ∇f ≠ 0 (‖∇f‖ = ${Math.hypot(...gr).toFixed(2)}): <b>not KKT</b>. Follow the orange arrow.`;
      else {
        // least squares for -grad f = sum mu_j grad g_j
        const D = act.map((c) => c.d(x, y));
        const A = D.map((a) => D.map((b) => a[0] * b[0] + a[1] * b[1])), b = D.map((a) => -(a[0] * gr[0] + a[1] * gr[1]));
        const mu = solve(A, b) || D.map(() => 0);
        const res = [-gr[0] - mu.reduce((t, m, j) => t + m * D[j][0], 0), -gr[1] - mu.reduce((t, m, j) => t + m * D[j][1], 0)];
        const rel = Math.hypot(...res) / Math.max(1e-9, Math.hypot(...gr));
        const muTxt = act.map((c, j) => `μ(${c.n}) = <b>${mu[j].toFixed(2)}</b>`).join(", ");
        if (rel > 0.04) msg = `Active: ${act.map((c) => c.n).join(", ")}. −∇f still has a component along the boundary (${(rel * 100).toFixed(0)}% of it): <b>not KKT</b>. Slide along the boundary in the direction of the orange arrow.`;
        else if (mu.some((m) => m < -1e-3)) msg = `${muTxt}. Stationary, but a multiplier is <b>negative</b>: that constraint wants to be released. <b>Not KKT.</b>`;
        else msg = `${muTxt}, all ≥ 0, and −∇f lines up with the active gradients: <b>a KKT point</b>. f = ${f(x, y).toFixed(3)}.`;
      }
      out.innerHTML = `x = (${x.toFixed(2)}, ${y.toFixed(2)}). ${msg}`;
    }
    draw();
  };

  // 13. Penalty versus barrier ---------------------------------------------------------------------
  W.penalty = (host) => {
    const w = frame(host, "Minimize f = x² subject to x ≥ 1 (the answer is x* = 1). Compare an exterior penalty with an interior log barrier as r grows.", "The penalty minimizer (teal) approaches 1 from the infeasible side: x = r/(1 + r). The barrier minimizer (green) approaches from inside the feasible region. Both need r → ∞ for the exact answer, and the curves grow steep and ill-conditioned as they get there; that's the motivation for the augmented Lagrangian.");
    const r = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(r, "log₁₀ r:", -1, 3, 0.05, 0));
    const out = readout(w);
    bindOut(w, { [r]: (v) => "r = " + f3(10 ** v) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const R = 10 ** val(r);
      const X = (x) => 20 + ((x + 0.5) / 3) * (s.W - 30), Y = (v) => s.H - 20 - (v / 6) * (s.H - 34);
      axes(g, 18, 8, s.W - 26, s.H - 26, "x", "");
      g.fillStyle = C.boxSoft; g.fillRect(X(-0.5), 9, X(1) - X(-0.5), s.H - 28);
      g.strokeStyle = C.box; g.beginPath(); g.moveTo(X(1), 9); g.lineTo(X(1), s.H - 19); g.stroke();
      label(g, "infeasible", X(0.25), 24, C.box, "center", 11);
      const xs = lin(-0.5, 2.5, 500);
      plot(g, xs, xs.map((x) => x * x), X, Y, C.muted, 1.4, [4, 4]);
      plot(g, xs, xs.map((x) => { const v = x * x + R * Math.max(0, 1 - x) ** 2; return v > 7 ? NaN : v; }), X, Y, C.pen, 2.2);
      plot(g, xs, xs.map((x) => { if (x <= 1) return NaN; const v = x * x - Math.log(x - 1) / R; return v > 7 || v < -1 ? NaN : v; }), X, Y, C.ok, 2.2);
      const xp = R / (1 + R), xb = (1 + Math.sqrt(1 + 2 / R)) / 2;
      disc(g, X(xp), Y(xp * xp + R * (1 - xp) ** 2), 5.5, C.pen, C.card);
      if (xb * xb - Math.log(xb - 1) / R < 7) disc(g, X(xb), Y(xb * xb - Math.log(xb - 1) / R), 5.5, C.ok, C.card);
      out.innerHTML = `r = ${f3(R)}: penalty minimizer <b>${xp.toFixed(4)}</b> (violates x ≥ 1 by ${(1 - xp).toFixed(4)}); barrier minimizer <b>${xb.toFixed(4)}</b> (feasible, ${(xb - 1).toFixed(4)} inside).`;
    }
    rerun(w, draw); draw();
  };

  return {
    render(host, spec) {
      colors();
      const f = W[spec.type];
      if (!f) return;
      try { f(host, spec); } catch (e) { console.error("widget", spec.type, e); }
    },
    stopAll() { loops.forEach((L) => { L.alive = false; }); loops.clear(); },
  };
})();
