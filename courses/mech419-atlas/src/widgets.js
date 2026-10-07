// Live models for the atlas. Each widget draws on a canvas, reads its colours from the page theme,
// and stops animating when the reader navigates away (Widgets.stopAll).
window.Widgets = (function () {
  const loops = new Set();
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const G = 9.81;
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

  // 1. Dot product as projection ---------------------------------------------------------
  W.dot = (host) => {
    const w = frame(host, "Drag the tip of F. Turn the direction u. The green bar is F·u.");
    let F = [2.4, 1.8];
    const id = uid();
    const s = surface(w, 0.55, () => draw());
    const ctl = controls(w, slider(id, "Direction of u:", 0, 180, 1, 20));
    const out = readout(w);
    bindOut(w, { [id]: (v) => v + "°" });
    const map = () => { const sc = s.H / 4.2; return { sc, ox: s.W * 0.42, oy: s.H * 0.62 }; };
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const { sc, ox, oy } = map();
      const a = (+ctl.querySelector("input").value * Math.PI) / 180, u = [Math.cos(a), Math.sin(a)];
      const dot = F[0] * u[0] + F[1] * u[1];
      g.strokeStyle = C.rule; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(ox - u[0] * sc * 3, oy + u[1] * sc * 3); g.lineTo(ox + u[0] * sc * 3, oy - u[1] * sc * 3); g.stroke(); g.setLineDash([]);
      const foot = [dot * u[0], dot * u[1]];
      g.strokeStyle = C.muted; g.setLineDash([3, 3]); g.lineWidth = 1; g.beginPath(); g.moveTo(ox + F[0] * sc, oy - F[1] * sc); g.lineTo(ox + foot[0] * sc, oy - foot[1] * sc); g.stroke(); g.setLineDash([]);
      g.strokeStyle = C.ok; g.lineWidth = 7; g.lineCap = "round"; g.beginPath(); g.moveTo(ox, oy); g.lineTo(ox + foot[0] * sc, oy - foot[1] * sc); g.stroke(); g.lineCap = "butt";
      arrow(g, ox, oy, ox + u[0] * sc, oy - u[1] * sc, C.pen, 2.5); label(g, "u", ox + u[0] * sc * 1.15, oy - u[1] * sc * 1.15, C.pen);
      arrow(g, ox, oy, ox + F[0] * sc, oy - F[1] * sc, C.box, 2.5); disc(g, ox + F[0] * sc, oy - F[1] * sc, 7, C.box);
      label(g, "F", ox + F[0] * sc + 10, oy - F[1] * sc - 6, C.box);
      const mag = Math.hypot(...F), phi = Math.acos(Math.max(-1, Math.min(1, dot / mag))) * 180 / Math.PI;
      out.innerHTML = `|F| = ${mag.toFixed(2)}, angle between them φ = ${phi.toFixed(0)}°, so <b>F·u = |F| cos φ = ${dot.toFixed(2)}</b>` + (Math.abs(dot) < 0.08 * mag ? " — perpendicular: a point moving along u gets no work from F." : dot < 0 ? " — negative: F opposes motion along u." : "");
    }
    pointer(s.cv, (x, y) => { const { sc, ox, oy } = map(); return Math.hypot(x - (ox + F[0] * sc), y - (oy - F[1] * sc)) < 24; },
      (x, y) => { const { sc, ox, oy } = map(); F = [Math.max(-3.5, Math.min(3.5, (x - ox) / sc)), Math.max(-1.4, Math.min(2.6, (oy - y) / sc))]; draw(); });
    ctl.querySelector("input").addEventListener("input", draw);
    draw();
  };

  // 2. Choosing coordinates for a pendulum ------------------------------------------------
  W.dof = (host) => {
    const w = frame(host, "Same pendulum, three descriptions. Which ones pin the bob down?");
    const id = uid(), sel = uid();
    const s = surface(w, 0.55, () => draw());
    const ctl = controls(w, slider(id, "θ:", -170, 170, 1, 35) + `<label for="${sel}">Describe it with<select id="${sel}"><option value="th">θ alone (1 coordinate)</option><option value="xy">x and y (2 coordinates)</option><option value="x">x alone</option></select></label>`);
    const out = readout(w);
    bindOut(w, { [id]: (v) => v + "°" });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const th = (+document.getElementById(id).value * Math.PI) / 180, mode = document.getElementById(sel).value;
      const P = [s.W * 0.4, s.H * 0.48], L = s.H * 0.38;
      const B = [P[0] + L * Math.sin(th), P[1] + L * Math.cos(th)];
      g.strokeStyle = C.rule; g.setLineDash([5, 5]); g.beginPath(); g.arc(P[0], P[1], L, 0, 2 * Math.PI); g.stroke(); g.setLineDash([]);
      g.strokeStyle = C.muted; g.lineWidth = 1; g.beginPath(); g.moveTo(P[0] - L * 1.2, P[1]); g.lineTo(P[0] + L * 1.2, P[1]); g.moveTo(P[0], P[1] - L * 1.15); g.lineTo(P[0], P[1] + L * 1.15); g.stroke();
      label(g, "x", P[0] + L * 1.2 + 4, P[1] + 4, C.muted); label(g, "y", P[0] + 4, P[1] - L * 1.15 + 10, C.muted);
      if (mode === "x") {
        const B2 = [B[0], P[1] - (B[1] - P[1])];
        g.globalAlpha = 0.45; g.strokeStyle = C.ink; g.lineWidth = 2; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(P[0], P[1]); g.lineTo(B2[0], B2[1]); g.stroke(); g.setLineDash([]); disc(g, B2[0], B2[1], 10, C.box); g.globalAlpha = 1;
        g.strokeStyle = C.box; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(B[0], P[1] - L * 1.15); g.lineTo(B[0], P[1] + L * 1.15); g.stroke(); g.setLineDash([]);
      }
      g.strokeStyle = C.ink; g.lineWidth = 2.5; g.beginPath(); g.moveTo(P[0], P[1]); g.lineTo(B[0], B[1]); g.stroke();
      disc(g, P[0], P[1], 4, C.card, C.ink); disc(g, B[0], B[1], 11, C.pen);
      if (mode === "xy") {
        g.strokeStyle = C.ok; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(B[0], P[1]); g.lineTo(B[0], B[1]); g.lineTo(P[0], B[1]); g.stroke(); g.setLineDash([]);
      }
      if (mode === "th") { g.strokeStyle = C.gold; g.lineWidth = 2; g.beginPath(); g.arc(P[0], P[1], L * 0.3, Math.PI / 2 - th, Math.PI / 2, th < 0 ? false : true); g.stroke(); }
      const xm = Math.sin(th), ym = -Math.cos(th);
      const txt = {
        th: `θ = ${(th * 180 / Math.PI).toFixed(0)}° fixes the bob uniquely, all the way round. <b>1 coordinate, 1 DOF</b>: independent.`,
        xy: `x = ${xm.toFixed(2)}ℓ, y = ${ym.toFixed(2)}ℓ. But x² + y² − ℓ² = ${(xm * xm + ym * ym - 1).toFixed(3)}ℓ² always: <b>2 coordinates, 1 constraint, still 1 DOF</b>. They're dependent.`,
        x: `x = ${xm.toFixed(2)}ℓ. The faded bob has the same x: <b>y = ±${Math.abs(ym).toFixed(2)}ℓ</b>. x alone works only if the bob never rises above the pivot.`,
      };
      out.innerHTML = txt[mode];
    }
    w.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", draw));
    draw();
  };

  // 3. Virtual work on the cart-pendulum ---------------------------------------------------
  W.virtual = (host) => {
    const w = frame(host, "Imagine a nudge (δx, δθ) with time frozen. Each force's work on the nudge builds the generalized forces.", "Values: k = 40 N/m, cart at x = 0.15 m, F = 10 N at the bob, m₂ = 1 kg, ℓ = 1 m. The rod's pull acts equally and oppositely on cart and bob and the rod can't stretch, so its net virtual work is zero.");
    const a = uid(), b = uid(), c = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "θ:", -60, 60, 1, 25) + slider(b, "virtual δx:", -0.3, 0.3, 0.01, 0) + slider(c, "virtual δθ:", -25, 25, 1, 18));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v + "°", [b]: (v) => v.toFixed(2) + " m", [c]: (v) => v + "°" });
    const k = 40, x0 = 0.15, F = 10, m2 = 1, l = 1;
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const th = (+document.getElementById(a).value * Math.PI) / 180, dx = +document.getElementById(b).value, dth = (+document.getElementById(c).value * Math.PI) / 180;
      const sc = s.H * 0.5, gy = s.H * 0.24, X = (x) => s.W * 0.28 + x * sc;
      g.strokeStyle = C.muted; g.lineWidth = 1; g.beginPath(); g.moveTo(10, gy + 18); g.lineTo(s.W - 10, gy + 18); g.stroke();
      springPath(g, 14, gy, X(x0) - 30, gy, 10, C.ink);
      const drawSys = (x, t, alpha, dash) => {
        g.globalAlpha = alpha; g.setLineDash(dash ? [5, 4] : []);
        g.strokeStyle = C.pen; g.lineWidth = 2; g.strokeRect(X(x) - 30, gy - 14, 60, 30);
        const bx = X(x) + l * sc * Math.sin(t) * 0.75, by = gy + l * sc * Math.cos(t) * 0.75;
        g.strokeStyle = C.ink; g.beginPath(); g.moveTo(X(x), gy); g.lineTo(bx, by); g.stroke();
        disc(g, bx, by, 10, dash ? null : C.pen, dash ? C.pen : null);
        g.globalAlpha = 1; g.setLineDash([]);
        return [bx, by];
      };
      const B0 = drawSys(x0, th, 1, false);
      const B1 = drawSys(x0 + dx, th + dth, 0.7, true);
      arrow(g, B0[0], B0[1], B1[0], B1[1], C.ok, 2.5);
      label(g, "δr", B1[0] + 10, B1[1] - 10, C.ok);
      arrow(g, B0[0], B0[1], B0[0] + 50, B0[1], C.box, 2); label(g, "F", B0[0] + 56, B0[1] + 4, C.box);
      arrow(g, B0[0], B0[1], B0[0], B0[1] + 40, C.muted, 2); label(g, "m₂g", B0[0] + 6, B0[1] + 52, C.muted);
      arrow(g, X(x0) - 30, gy + 28, X(x0) - 70, gy + 28, C.box, 2); label(g, "−kx", X(x0) - 70, gy + 44, C.box);
      const Qx = -k * x0 + F, Qt = -m2 * G * l * Math.sin(th) + F * l * Math.cos(th);
      out.innerHTML = `Q<sub>x</sub> = −kx + F = <b>${Qx.toFixed(2)} N</b> &nbsp; Q<sub>θ</sub> = −m₂gℓ sin θ + Fℓ cos θ = <b>${Qt.toFixed(2)} N·m</b><br>δW = Q<sub>x</sub>δx + Q<sub>θ</sub>δθ = ${Qx.toFixed(2)}(${dx.toFixed(2)}) + ${Qt.toFixed(2)}(${dth.toFixed(3)}) = <b>${(Qx * dx + Qt * dth).toFixed(3)} J</b>`;
    }
    w.querySelectorAll("input").forEach((el) => el.addEventListener("input", draw));
    draw();
  };

  // 4. Cart-pendulum: nonlinear vs linear --------------------------------------------------
  W.cartpend = (host, opt) => {
    const w = frame(host, "The cart-pendulum from Lagrange's equations, integrated live. Compare it with the linearized model.", "M = 2 kg, m = 1 kg, ℓ = 0.5 m, k = 50 N/m: the same numbers as the pipeline question. Small swings: the dashed linear model tracks the real one. Large swings: they drift apart.");
    const a = uid(), b = uid(), lin_ = uid();
    const s = surface(w, 0.62, () => draw());
    const ctl = controls(w, slider(a, "release angle θ₀:", 2, 150, 1, opt.linear ? 20 : 60) + slider(b, "cart offset x₀:", -0.2, 0.2, 0.01, 0.1) +
      check(lin_, "show linear model", !!opt.linear) + `<button class="btn quiet" type="button" data-act="play">Pause</button><button class="btn quiet" type="button" data-act="reset">Reset</button>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v + "°", [b]: (v) => v.toFixed(2) + " m" });
    const M = 2, m = 1, l = 0.5, k = 50;
    let st, ln, t, hist, playing = !reduce;
    const fNL = ([x, th, xd, thd]) => {
      const c = Math.cos(th), sn = Math.sin(th);
      const a11 = M + m, a12 = m * l * c, a22 = m * l * l, r1 = m * l * thd * thd * sn - k * x, r2 = -m * G * l * sn;
      const det = a11 * a22 - a12 * a12;
      return [xd, thd, (r1 * a22 - a12 * r2) / det, (a11 * r2 - a12 * r1) / det];
    };
    const fL = ([x, th, xd, thd]) => {
      const a11 = M + m, a12 = m * l, a22 = m * l * l, r1 = -k * x, r2 = -m * G * l * th, det = a11 * a22 - a12 * a12;
      return [xd, thd, (r1 * a22 - a12 * r2) / det, (a11 * r2 - a12 * r1) / det];
    };
    const energy = ([x, th, xd, thd]) => 0.5 * (M + m) * xd * xd + 0.5 * m * l * l * thd * thd + m * xd * l * thd * Math.cos(th) + 0.5 * k * x * x - m * G * l * Math.cos(th);
    function reset() {
      const th0 = (+document.getElementById(a).value * Math.PI) / 180, x0 = +document.getElementById(b).value;
      st = [x0, th0, 0, 0]; ln = [x0, th0, 0, 0]; t = 0; hist = []; st.E0 = energy(st);
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const sc = Math.min(s.W / 1.6, s.H * 0.55 / 0.75), cx = s.W / 2, gy = s.H * 0.16;
      const showL = document.getElementById(lin_).checked;
      g.strokeStyle = C.muted; g.lineWidth = 1; g.beginPath(); g.moveTo(10, gy + 20); g.lineTo(s.W - 10, gy + 20); g.stroke();
      const drawCart = ([x, th], col, dash, alpha) => {
        g.globalAlpha = alpha; g.setLineDash(dash ? [5, 4] : []);
        const X = cx + x * sc;
        if (!dash) springPath(g, 12, gy + 4, X - 28, gy + 4, 12, C.ink);
        g.strokeStyle = col; g.lineWidth = 2; g.strokeRect(X - 28, gy - 12, 56, 28);
        const bx = X + l * sc * Math.sin(th), by = gy + 2 + l * sc * Math.cos(th);
        g.strokeStyle = col; g.beginPath(); g.moveTo(X, gy + 2); g.lineTo(bx, by); g.stroke();
        disc(g, bx, by, 9, dash ? null : col, dash ? col : null);
        g.globalAlpha = 1; g.setLineDash([]);
      };
      if (showL) drawCart(ln, C.box, true, 0.85);
      drawCart(st, C.pen, false, 1);
      // theta(t) history
      const px = 10, py = s.H * 0.68, pw = s.W - 20, ph = s.H * 0.28, span = 8;
      axes(g, px, py, pw, ph, "time (last 8 s)", "θ(t)");
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(px, py + ph / 2); g.lineTo(px + pw, py + ph / 2); g.stroke();
      const thMax = Math.max(0.3, (+document.getElementById(a).value * Math.PI) / 180) * 1.15;
      const X = (tt) => px + pw - ((t - tt) / span) * pw, Y = (v) => py + ph / 2 - (v / thMax) * (ph / 2);
      plot(g, hist.map((h) => h[0]), hist.map((h) => h[1]), X, Y, C.pen, 2);
      if (showL) plot(g, hist.map((h) => h[0]), hist.map((h) => h[2]), X, Y, C.box, 1.5, [5, 4]);
      const E = energy(st);
      out.innerHTML = `t = ${t.toFixed(1)} s · θ = ${(st[1] * 180 / Math.PI).toFixed(1)}°` + (showL ? ` (linear: ${(ln[1] * 180 / Math.PI).toFixed(1)}°)` : "") + ` · energy drift ${(Math.abs(E - st.E0) < 1e-6 ? 0 : ((E - st.E0) / Math.abs(st.E0) * 100)).toFixed(4)}% <span style="color:var(--muted)">(E = T + V is conserved: a check on the equations)</span>`;
    }
    reset();
    ctl.querySelector('[data-act="play"]').textContent = playing ? "Pause" : "Play";
    ctl.addEventListener("click", (e) => {
      const act = e.target.dataset && e.target.dataset.act;
      if (act === "play") { playing = !playing; e.target.textContent = playing ? "Pause" : "Play"; }
      if (act === "reset") { reset(); draw(); }
    });
    w.querySelectorAll("input[type=range]").forEach((el) => el.addEventListener("input", () => { reset(); draw(); }));
    document.getElementById(lin_).addEventListener("change", draw);
    loop((dt) => {
      if (!playing) return;
      const n = 8, h = dt / n;
      for (let i = 0; i < n; i++) { const E0 = st.E0; st = rk4(fNL, st, h); st.E0 = E0; ln = rk4(fL, ln, h); }
      t += dt; hist.push([t, st[1], ln[1]]); while (hist.length && t - hist[0][0] > 8) hist.shift();
      draw();
    });
    draw();
  };

  // 5. Rolling with and without slip -------------------------------------------------------
  W.rolling = (host) => {
    const w = frame(host, "A wheel moving right at constant speed. Slide from 'rolls' to 'skids' and watch the contact point.", "With no slip, a point on the rim traces a cycloid, touching the ground with zero speed. That's why friction there does no work.");
    const a = uid();
    const s = surface(w, 0.42, () => draw());
    controls(w, slider(a, "slip:", 0, 1, 0.01, 0));
    const out = readout(w);
    bindOut(w, { [a]: (v) => (v * 100).toFixed(0) + "%" });
    let x = 0, phi = 0, trace = [];
    const r = 0.55, v = 1;
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const sc = s.H / 2.2, gy = s.H * 0.82, span = s.W / sc;
      const slip = +document.getElementById(a).value;
      g.strokeStyle = C.muted; g.lineWidth = 1.2; g.beginPath(); g.moveTo(0, gy); g.lineTo(s.W, gy); g.stroke();
      const X = (xx) => ((xx % span) + span) % span * sc;
      g.fillStyle = C.gold; trace.forEach(([tx, ty]) => { g.fillRect(X(tx) - 1, gy - ty * sc - 1, 2.2, 2.2); });
      const cxp = X(x), cyp = gy - r * sc;
      disc(g, cxp, cyp, r * sc, C.penSoft, C.pen);
      for (let i = 0; i < 4; i++) { const ang = phi + (i * Math.PI) / 2; g.strokeStyle = C.pen; g.lineWidth = 1.5; g.beginPath(); g.moveTo(cxp, cyp); g.lineTo(cxp + r * sc * Math.sin(ang), cyp - r * sc * Math.cos(ang)); g.stroke(); }
      disc(g, cxp + r * sc * Math.sin(phi), cyp - r * sc * Math.cos(phi), 5, C.gold);
      const vp = v * slip;
      arrow(g, cxp, cyp, cxp + v * sc * 0.6, cyp, C.ok, 2); label(g, "v_C", cxp + v * sc * 0.6 + 4, cyp - 4, C.ok);
      if (vp > 0.02) { arrow(g, cxp, gy - 3, cxp + vp * sc * 0.6, gy - 3, C.box, 3); label(g, "v_P", cxp + vp * sc * 0.6 + 4, gy - 8, C.box); }
      else disc(g, cxp, gy, 4, C.box);
      out.innerHTML = slip < 0.005 ? `Rolling without slipping: v<sub>P</sub> = ẋ − rθ̇ = <b>0</b>. Friction acts on a point at rest, so <b>no work</b>, and it drops out of Q.` :
        `Slipping: the contact point slides at v<sub>P</sub> = ẋ − rθ̇ = <b>${(vp).toFixed(2)} v</b>. Friction now does work (power −f·v<sub>P</sub>), so it appears in Q<sub>x</sub> and Q<sub>θ</sub>.`;
    }
    document.getElementById(a).addEventListener("input", () => { trace = []; draw(); });
    let playing = !reduce;
    const btn = controls(w, `<button class="btn quiet" type="button">${playing ? "Pause" : "Play"}</button>`).querySelector("button");
    btn.addEventListener("click", () => { playing = !playing; btn.textContent = playing ? "Pause" : "Play"; });
    loop((dt) => {
      if (!playing) return;
      const slip = +document.getElementById(a).value;
      x += v * dt * 0.8; phi += ((1 - slip) * v * dt * 0.8) / r;
      trace.push([x + r * Math.sin(phi), r + r * Math.cos(phi)]);
      if (trace.length > 900) trace.shift();
      draw();
    });
    draw();
  };

  // 6. Multipliers: the rod force as λ (and what happens without it) ------------------------
  W.constraint = (host, opt) => {
    const w = frame(host, "A pendulum described by dependent coordinates (x, y). The red arrow is the constraint force λ(x, y): the rod's pull.", "Tick the box to drop λ, the wrong equations from Lecture 4: nothing tells the bob about the rod, and it falls freely.");
    const wrongId = uid();
    const s = surface(w, 0.6, () => draw());
    const ctl = controls(w, check(wrongId, "use the wrong equations (no λ)", false) + `<button class="btn quiet" type="button" data-act="reset">Release again</button>`);
    const out = readout(w);
    const l = 1, m = 1;
    let th, thd, free, t;
    const reset = () => { th = (60 * Math.PI) / 180; thd = 0; free = null; t = 0; };
    reset();
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const sc = s.H * 0.38, P = [s.W / 2, s.H * 0.16];
      g.strokeStyle = C.rule; g.setLineDash([5, 5]); g.beginPath(); g.arc(P[0], P[1], l * sc, 0, Math.PI); g.stroke(); g.setLineDash([]);
      g.strokeStyle = C.muted; g.lineWidth = 2; g.beginPath(); g.moveTo(P[0] - 40, P[1]); g.lineTo(P[0] + 40, P[1]); g.stroke();
      if (free) {
        const bx = P[0] + free.x * sc, by = P[1] + free.y * sc;
        g.globalAlpha = 0.4; g.strokeStyle = C.ink; g.setLineDash([3, 4]); g.beginPath(); g.moveTo(P[0], P[1]); g.lineTo(P[0] + free.x0 * sc, P[1] + free.y0 * sc); g.stroke(); g.setLineDash([]); g.globalAlpha = 1;
        disc(g, bx, by, 10, C.box);
        out.innerHTML = `Without λ: mẍ = 0, mÿ = mg. Distance from pivot: <b>${Math.hypot(free.x, free.y).toFixed(2)} m</b> (the rod is ${l} m). The equations never knew about the rod.`;
        return;
      }
      const x = l * Math.sin(th), y = l * Math.cos(th), v2 = (l * thd) ** 2;
      const lam = (-m * (v2 + G * y)) / (l * l);
      const bx = P[0] + x * sc, by = P[1] + y * sc;
      g.strokeStyle = C.ink; g.lineWidth = 2.5; g.beginPath(); g.moveTo(P[0], P[1]); g.lineTo(bx, by); g.stroke();
      disc(g, bx, by, 10, C.pen);
      const R = [lam * x, lam * y], k = sc / 40;
      arrow(g, bx, by, bx + R[0] * k, by + R[1] * k, C.box, 3);
      arrow(g, bx, by, bx, by + m * G * k, C.muted, 2);
      label(g, "R = λ(x, y)", bx + R[0] * k + 6, by + R[1] * k - 6, C.box);
      out.innerHTML = `λ = −m(v² + gy)/ℓ² = <b>${lam.toFixed(2)} N/m</b> &nbsp;→&nbsp; rod tension −λℓ = <b>${(-lam * l).toFixed(2)} N</b> (weight ${(m * G).toFixed(2)} N; extra at the bottom pays for the centripetal force).`;
    }
    ctl.addEventListener("click", (e) => { if (e.target.dataset && e.target.dataset.act === "reset") { reset(); document.getElementById(wrongId).checked = false; draw(); } });
    document.getElementById(wrongId).addEventListener("change", (e) => {
      if (e.target.checked) { const x = l * Math.sin(th), y = l * Math.cos(th); free = { x, y, x0: x, y0: y, vx: l * thd * Math.cos(th), vy: -l * thd * Math.sin(th) }; }
      else reset();
      draw();
    });
    loop((dt) => {
      if (reduce && !free) { draw(); return; }
      if (free) { if (free.y < 2) { free.vy += G * dt; free.x += free.vx * dt; free.y += free.vy * dt; } }
      else { const n = 6, h = dt / n; for (let i = 0; i < n; i++) { const ns = rk4(([a, b]) => [b, -(G / l) * Math.sin(a)], [th, thd], h); th = ns[0]; thd = ns[1]; } }
      draw();
    });
    if (opt.wrong) { /* the toggle starts off; the note explains it */ }
    draw();
  };

  // 7. Spinning pendulum: dynamic equilibrium and the effective potential -------------------
  W["spin-pendulum"] = (host, opt) => {
    const w = frame(host, "A pendulum on a shaft spun at Ω. Right: the landscape U = V − T₀ that the swing angle really sits in.", "Filled dots are stable equilibria (valleys of U), hollow ones unstable (hilltops). Push Ω past √(g/ℓ) and the bottom turns into a hilltop: a pitchfork bifurcation.");
    const a = uid(), b = uid();
    const s = surface(w, 0.55, () => draw());
    controls(w, slider(a, "Ω:", 0, 10, 0.05, opt.omega != null ? opt.omega : 5) + `<label for="${b}">Body<select id="${b}"><option value="point">point mass, ℓ = 0.5 m</option><option value="rod">uniform rod, ℓ = 0.5 m</option></select></label>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) + " rad/s" });
    const l = 0.5;
    let phase = 0;
    function eq(Om, rod) {
      const crit2 = rod ? (3 * G) / (2 * l) : G / l;
      const c = rod ? (3 * G) / (2 * Om * Om * l) : G / (Om * Om * l);
      return { crit: Math.sqrt(crit2), the: Om * Om > crit2 ? Math.acos(c) : 0 };
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const Om = +document.getElementById(a).value, rod = document.getElementById(b).value === "rod";
      const { crit, the } = eq(Om, rod);
      // left: the spinning pendulum, seen from the side
      const lw = s.W * 0.42, top = [lw / 2, s.H * 0.12], L = s.H * 0.7;
      g.strokeStyle = C.muted; g.setLineDash([6, 4]); g.lineWidth = 2; g.beginPath(); g.moveTo(top[0], 6); g.lineTo(top[0], s.H - 6); g.stroke(); g.setLineDash([]);
      const rx = L * Math.sin(the), bx = top[0] + rx * Math.cos(phase), by = top[1] + L * Math.cos(the);
      g.strokeStyle = C.rule; g.beginPath(); g.ellipse(top[0], by, Math.max(1, rx), Math.max(1, rx * 0.22), 0, 0, 2 * Math.PI); g.stroke();
      g.strokeStyle = rod ? C.pen : C.ink; g.lineWidth = rod ? 7 : 2.5; g.lineCap = "round"; g.beginPath(); g.moveTo(top[0], top[1]); g.lineTo(bx, by); g.stroke(); g.lineCap = "butt";
      if (!rod) disc(g, bx, by, 11, C.pen);
      disc(g, top[0], top[1], 4, C.card, C.ink);
      // right: U(theta)
      const px = lw + 10, pw = s.W - lw - 20, py = 14, ph = s.H - 36;
      axes(g, px, py, pw, ph, "θ from −180° to 180°", "U = V − T₀");
      const ths = lin(-Math.PI, Math.PI, 241);
      const U = (t) => rod ? -0.5 * Math.cos(t) - ((Om * Om * l) / (6 * G)) * Math.sin(t) ** 2 : -Math.cos(t) - ((Om * Om * l) / (2 * G)) * Math.sin(t) ** 2;
      const us = ths.map(U), lo = Math.min(...us), hi = Math.max(...us), pad = (hi - lo) * 0.12 + 1e-6;
      const X = (t) => px + ((t + Math.PI) / (2 * Math.PI)) * pw, Y = (u) => py + ph - ((u - lo + pad) / (hi - lo + 2 * pad)) * ph;
      plot(g, ths, us, X, Y, C.box, 2.2);
      const mark = (t, stable) => disc(g, X(t), Y(U(t)), 6, stable ? C.ok : C.card, stable ? null : C.ok);
      const sup = Om > crit;
      mark(0, !sup); mark(Math.PI, false); mark(-Math.PI, false);
      if (sup) { mark(the, true); mark(-the, true); }
      out.innerHTML = `Critical speed √(${rod ? "3g/2ℓ" : "g/ℓ"}) = <b>${crit.toFixed(2)} rad/s</b>. ` + (sup ? `Above it: swung out to <b>θₑ = ${(the * 180 / Math.PI).toFixed(1)}°</b> (cos θₑ = ${Math.cos(the).toFixed(3)}); hanging straight is now unstable.` : `Below it: only θₑ = 0 is stable; the pendulum hangs straight.`);
    }
    w.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", draw));
    loop((dt) => { if (reduce) return; phase += (+document.getElementById(a).value) * dt * 0.5; draw(); });
    draw();
  };

  // 8. The spinning slot: H conserved, E not ------------------------------------------------
  W["spin-disk"] = (host) => {
    const w = frame(host, "A block on springs in a slot, with the disk driven at a fixed Ω. Watch H stay flat while E swings.", "m = 1 kg, k = 25 N/m, block released at x = 0.3 m. E changes because the motor holding Ω constant does work through the slot wall. Set Ω = 0 and the two lines coincide.");
    const a = uid();
    const s = surface(w, 0.55, () => draw());
    controls(w, slider(a, "Ω:", 0, 4.5, 0.05, 3));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) + " rad/s" });
    const m = 1, k = 25, A = 0.3;
    let t = 0, hist = [];
    const state = (Om, tt) => { const wv = Math.sqrt(k / m - Om * Om); return [A * Math.cos(wv * tt), -A * wv * Math.sin(wv * tt)]; };
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const Om = +document.getElementById(a).value;
      const [x, xd] = state(Om, t), ang = Om * t;
      const R = s.H * 0.4, c = [R + 14, s.H / 2];
      disc(g, c[0], c[1], R, C.penSoft, C.pen);
      const u = [Math.cos(ang), Math.sin(ang)];
      g.strokeStyle = C.rule; g.lineWidth = 12; g.lineCap = "round"; g.beginPath(); g.moveTo(c[0] - R * 0.92 * u[0], c[1] - R * 0.92 * u[1]); g.lineTo(c[0] + R * 0.92 * u[0], c[1] + R * 0.92 * u[1]); g.stroke(); g.lineCap = "butt";
      const bpos = [c[0] + (x / 0.45) * R * u[0], c[1] + (x / 0.45) * R * u[1]];
      springPath(g, c[0] - R * 0.92 * u[0], c[1] - R * 0.92 * u[1], bpos[0], bpos[1], 8, C.ink);
      springPath(g, bpos[0], bpos[1], c[0] + R * 0.92 * u[0], c[1] + R * 0.92 * u[1], 8, C.ink);
      disc(g, bpos[0], bpos[1], 9, C.box);
      const E = 0.5 * (m * xd * xd + m * Om * Om * x * x + k * x * x), H = 0.5 * (m * xd * xd - m * Om * Om * x * x + k * x * x);
      const px = 2 * R + 36, pw = s.W - px - 10, py = 14, ph = s.H - 40;
      axes(g, px, py, pw, ph, "time (last 6 s)", "energy (J)");
      const top = 0.5 * (m * Om * Om + k) * A * A * 1.15 + 0.05;
      const X = (tt) => px + pw - ((t - tt) / 6) * pw, Y = (v) => py + ph - (v / top) * ph;
      plot(g, hist.map((h) => h[0]), hist.map((h) => h[1]), X, Y, C.box, 2);
      plot(g, hist.map((h) => h[0]), hist.map((h) => h[2]), X, Y, C.pen, 2.5);
      label(g, "E = T + V", px + 6, Y(hist.length ? hist[hist.length - 1][1] : E) - 6, C.box, "left", 12);
      label(g, "H = T₂ − T₀ + V", px + 6, Y(H) + 16, C.pen, "left", 12);
      out.innerHTML = `x = ${x.toFixed(3)} m · <b style="color:var(--pen)">H = ${H.toFixed(3)} J</b> (constant) · <b>E = ${E.toFixed(3)} J</b> (changes; the motor's work)`;
    }
    document.getElementById(a).addEventListener("input", () => { t = 0; hist = []; draw(); });
    loop((dt) => {
      if (reduce) return;
      t += dt;
      const Om = +document.getElementById(a).value, [x, xd] = state(Om, t);
      hist.push([t, 0.5 * (m * xd * xd + m * Om * Om * x * x + k * x * x), 0.5 * (m * xd * xd - m * Om * Om * x * x + k * x * x)]);
      while (hist.length && t - hist[0][0] > 6) hist.shift();
      draw();
    });
    draw();
  };

  // 9. Orbit: a cyclic coordinate and its conserved momentum ---------------------------------
  W.orbit = (host) => {
    const w = frame(host, "θ is missing from the satellite's Lagrangian, so p_θ = mr²θ̇ never changes: equal areas in equal times.", "Each shaded wedge is swept in the same time. Near Earth the satellite is fast and the wedge is short and fat; far away it's slow and the wedge is long and thin. Same area.");
    const a = uid();
    const s = surface(w, 0.62, () => draw());
    controls(w, slider(a, "eccentricity:", 0, 0.75, 0.01, 0.5));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    let st, t, wedges, T, nextMark, trail;
    const reset = () => {
      const e = +document.getElementById(a).value;
      st = [1, 0, 0, Math.sqrt(1 + e)]; t = 0; wedges = [[1, 0]]; trail = [];
      const aSemi = 1 / (1 - e); T = 2 * Math.PI * Math.pow(aSemi, 1.5); nextMark = T / 12;
    };
    reset();
    const f = ([x, y, vx, vy]) => { const r3 = Math.pow(x * x + y * y, 1.5); return [vx, vy, -x / r3, -y / r3]; };
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const e = +document.getElementById(a).value, aS = 1 / (1 - e);
      const sc = Math.min(s.W / (2 * aS * 1.08), s.H / (2 * aS * Math.sqrt(1 - e * e) * 1.15));
      const ox = s.W / 2 + (aS * e) * sc, oy = s.H / 2;
      for (let i = 0; i + 1 < wedges.length; i += 2) {
        g.fillStyle = C.penSoft; g.beginPath(); g.moveTo(ox, oy);
        const steps = 30;
        const a0 = Math.atan2(wedges[i][1], wedges[i][0]), a1 = Math.atan2(wedges[i + 1][1], wedges[i + 1][0]);
        let da = a1 - a0; if (da < 0) da += 2 * Math.PI;
        for (let j = 0; j <= steps; j++) { const th = a0 + (da * j) / steps, rr = (aS * (1 - e * e)) / (1 + e * Math.cos(th)); g.lineTo(ox + rr * Math.cos(th) * sc, oy - rr * Math.sin(th) * sc); }
        g.closePath(); g.fill();
      }
      g.strokeStyle = C.rule; g.beginPath(); g.ellipse(s.W / 2, oy, aS * sc, aS * Math.sqrt(1 - e * e) * sc, 0, 0, 2 * Math.PI); g.stroke();
      disc(g, ox, oy, 12, C.penSoft, C.pen); label(g, "Earth", ox, oy + 28, C.muted, "center", 11);
      const [x, y, vx, vy] = st;
      g.strokeStyle = C.ink; g.lineWidth = 1; g.beginPath(); g.moveTo(ox, oy); g.lineTo(ox + x * sc, oy - y * sc); g.stroke();
      disc(g, ox + x * sc, oy - y * sc, 6, C.box);
      const r = Math.hypot(x, y), thd = (x * vy - y * vx) / (r * r);
      out.innerHTML = `r = ${r.toFixed(2)}, θ̇ = ${thd.toFixed(3)} rad/s, but <b>r²θ̇ = ${(r * r * thd).toFixed(4)}</b> stays fixed (p<sub>θ</sub>/m).`;
    }
    document.getElementById(a).addEventListener("input", () => { reset(); draw(); });
    loop((dt) => {
      if (reduce) return;
      const n = 40, h = (dt * 1.6) / n;
      for (let i = 0; i < n; i++) {
        st = rk4(f, st, h); t += h;
        if (t >= nextMark) { wedges.push([st[0], st[1]]); nextMark += T / 12; if (wedges.length > 13) { reset(); return; } }
      }
      draw();
    });
    draw();
  };

  // 10. Phase portrait and Hamilton's equations ---------------------------------------------
  W.phase = (host) => {
    const w = frame(host, "A pendulum's state flows along the contour lines of H(θ, p) = p²/2 − cos θ. Click anywhere to start it there.", "The blue arrow is θ̇ = ∂H/∂p, the red one ṗ = −∂H/∂θ. Together they point along the contour. Add damping (a Q_nc) and the state slides across contours, spiralling into the bottom.");
    const dId = uid();
    const s = surface(w, 0.6, () => draw());
    controls(w, check(dId, "add damping (Q<sub>nc</sub> = −0.15 p)", false));
    const out = readout(w);
    let st = [2.2, 0], trail = [];
    const P = 2.6;
    const f = ([q, p]) => [p, -Math.sin(q) - (document.getElementById(dId).checked ? 0.15 * p : 0)];
    const X = (q) => ((q + Math.PI) / (2 * Math.PI)) * s.W, Y = (p) => s.H / 2 - (p / P) * (s.H / 2 - 8);
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      g.strokeStyle = C.rule; g.lineWidth = 1; g.beginPath(); g.moveTo(0, s.H / 2); g.lineTo(s.W, s.H / 2); g.moveTo(s.W / 2, 0); g.lineTo(s.W / 2, s.H); g.stroke();
      label(g, "θ", s.W - 14, s.H / 2 - 6, C.muted); label(g, "p", s.W / 2 + 6, 14, C.muted);
      const qs = lin(-Math.PI, Math.PI, 361);
      [-0.85, -0.5, 0, 0.5, 1, 1.6, 2.4].forEach((Hl) => {
        const up = qs.map((q) => (Hl + Math.cos(q) >= 0 ? Math.sqrt(2 * (Hl + Math.cos(q))) : NaN));
        const col = Math.abs(Hl - 1) < 1e-9 ? C.box : C.muted;
        plot(g, qs, up, X, Y, col, Math.abs(Hl - 1) < 1e-9 ? 1.6 : 1);
        plot(g, qs, up.map((v) => -v), X, Y, col, Math.abs(Hl - 1) < 1e-9 ? 1.6 : 1);
      });
      g.fillStyle = C.gold; trail.forEach(([q, p]) => g.fillRect(X(q) - 1, Y(p) - 1, 2, 2));
      const [q, p] = st, d = f(st), k = 26;
      disc(g, X(q), Y(p), 7, C.ink);
      arrow(g, X(q), Y(p), X(q) + d[0] * k, Y(p), C.pen, 2.5);
      arrow(g, X(q), Y(p), X(q), Y(p) - d[1] * k * (s.H / 2 - 8) / P / (s.W / (2 * Math.PI)), C.box, 2.5);
      const H = p * p / 2 - Math.cos(q);
      out.innerHTML = `θ = ${(q * 180 / Math.PI).toFixed(0)}°, p = ${p.toFixed(2)} · <b>H = ${H.toFixed(3)}</b>` + (H > 1 ? " (above the red separatrix: it swings over the top)" : " (inside the eye: it rocks back and forth)");
    }
    s.cv.addEventListener("pointerdown", (e) => {
      const r = s.cv.getBoundingClientRect();
      st = [((e.clientX - r.left) / s.W) * 2 * Math.PI - Math.PI, ((s.H / 2 - (e.clientY - r.top)) / (s.H / 2 - 8)) * P]; trail = []; draw();
    });
    loop((dt) => {
      if (reduce) return;
      const n = 6, h = (dt * 1.5) / n;
      for (let i = 0; i < n; i++) { st = rk4(f, st, h); if (st[0] > Math.PI) st[0] -= 2 * Math.PI; if (st[0] < -Math.PI) st[0] += 2 * Math.PI; }
      trail.push(st.slice()); if (trail.length > 600) trail.shift();
      draw();
    });
    draw();
  };

  // 11. Variations: length of a curve, or the action of a thrown ball ------------------------
  W.variation = (host, opt) => {
    const action = opt.mode === "action";
    const w = frame(host, action ? "A ball thrown up and caught 1 s later. Bend its path by εη and watch the action S = ∫(T − V) dt." : "A path between two fixed points, bent by εη(x). Watch its length as a function of ε.",
      action ? "Every bent path still starts and ends at the same place (η = 0 at the ends). The true path, ε = 0, sits at the bottom of S(ε): the slope there is zero, which is all Hamilton's principle asks." : "η vanishes at both ends, so every bent path joins the same points. The straight line, ε = 0, is where I(ε) is flat: dI/dε = 0.");
    const a = uid(), b = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "ε:", -1, 1, 0.01, 0.4) + `<label for="${b}">Shape of η<select id="${b}"><option value="1">one bump</option><option value="2">two bumps</option><option value="3">lopsided</option></select></label>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    const eta = (kind, u) => kind === "1" ? Math.sin(Math.PI * u) * 0.35 : kind === "2" ? Math.sin(2 * Math.PI * u) * 0.3 : u * (1 - u) * (1.6 - u) * 1.1;
    const etap = (kind, u) => (eta(kind, u + 1e-5) - eta(kind, u - 1e-5)) / 2e-5;
    const base = (u) => action ? (G / 2) * u * (1 - u) * 0.3 : 0.5 * u;
    const basep = (u) => action ? (G / 2) * (1 - 2 * u) * 0.3 : 0.5;
    function functional(eps, kind) {
      const n = 200; let S = 0;
      for (let i = 0; i < n; i++) {
        const u = (i + 0.5) / n, y = base(u) + eps * eta(kind, u), yp = basep(u) + eps * etap(kind, u);
        S += (action ? 0.5 * yp * yp - G * 0.3 * y : Math.sqrt(1 + yp * yp)) / n;
      }
      return S;
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const eps = +document.getElementById(a).value, kind = document.getElementById(b).value;
      const lw = s.W * 0.56, us = lin(0, 1, 121);
      const yMin = action ? -0.4 : -0.4, yMax = action ? 1.2 : 0.9;
      const X = (u) => 16 + u * (lw - 32), Y = (v) => s.H - 18 - ((v - yMin) / (yMax - yMin)) * (s.H - 36);
      axes(g, 8, 8, lw - 16, s.H - 20, action ? "t" : "x", action ? "y(t)" : "y(x)");
      plot(g, us, us.map(base), X, Y, C.muted, 1.5, [5, 4]);
      plot(g, us, us.map((u) => base(u) + eps * eta(kind, u)), X, Y, C.pen, 2.5);
      disc(g, X(0), Y(base(0)), 5, C.ink); disc(g, X(1), Y(base(1)), 5, C.ink);
      const px = lw + 8, pw = s.W - lw - 16, py = 8, ph = s.H - 28;
      axes(g, px, py, pw, ph, "ε", action ? "S(ε)" : "I(ε)");
      const es = lin(-1, 1, 81), vals = es.map((e) => functional(e, kind)), lo = Math.min(...vals), hi = Math.max(...vals) + 1e-9;
      const PX = (e) => px + ((e + 1) / 2) * pw, PY = (v) => py + ph - 6 - ((v - lo) / (hi - lo)) * (ph - 16);
      plot(g, es, vals, PX, PY, C.box, 2);
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(PX(0), py); g.lineTo(PX(0), py + ph); g.stroke();
      disc(g, PX(eps), PY(functional(eps, kind)), 6, C.pen);
      const d = (functional(1e-3, kind) - functional(-1e-3, kind)) / 2e-3;
      out.innerHTML = `${action ? "S" : "I"}(${eps.toFixed(2)}) = <b>${functional(eps, kind).toFixed(4)}</b> · at ε = 0 the slope is <b>${Math.abs(d) < 5e-4 ? "0" : d.toFixed(4)}</b>, whatever the shape of η.`;
    }
    w.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", draw));
    draw();
  };

  // 12. Brachistochrone race ---------------------------------------------------------------
  W.brachistochrone = (host) => {
    const w = frame(host, "Race beads from (0, 0) to (π, 2) m on frictionless wires. Shape the gold wire yourself.", "Speed depends only on depth (v = √(2gy)), so a steep start buys speed that pays off for the rest of the trip. The cycloid balances the two exactly.");
    const a = uid();
    const s = surface(w, 0.55, () => draw());
    const ctl = controls(w, slider(a, "your wire's steepness:", 1, 6, 0.05, 2.2) + `<button class="btn solid" type="button" data-act="race">Race</button>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    const XE = Math.PI, YE = 2;
    const curves = {
      line: (n) => Array.from({ length: n + 1 }, (_, i) => { const u = (i / n) ** 2; return [XE * u, YE * u]; }),
      cycloid: (n) => Array.from({ length: n + 1 }, (_, i) => { const u = (Math.PI * i) / n; return [u - Math.sin(u), 1 - Math.cos(u)]; }),
      yours: (n, p) => Array.from({ length: n + 1 }, (_, i) => { const u = (i / n) ** 2; return [XE * u, YE * (1 - Math.pow(1 - u, p))]; }),
    };
    function timeline(pts) {
      const ts = [0];
      for (let i = 1; i < pts.length; i++) {
        const ds = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
        const v = (Math.sqrt(2 * G * Math.max(0, pts[i][1])) + Math.sqrt(2 * G * Math.max(0, pts[i - 1][1]))) / 2;
        ts.push(ts[i - 1] + (v > 1e-9 ? ds / v : 0));
      }
      return ts;
    }
    let race = null;
    function build() {
      const p = +document.getElementById(a).value;
      const set = { line: curves.line(3000), cycloid: curves.cycloid(3000), yours: curves.yours(3000, p) };
      return Object.fromEntries(Object.entries(set).map(([k, pts]) => [k, { pts, ts: timeline(pts) }]));
    }
    let data = build();
    function at(d, tt) {
      const ts = d.ts; if (tt >= ts[ts.length - 1]) return d.pts[d.pts.length - 1];
      let lo = 0, hi = ts.length - 1; while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (ts[mid] <= tt) lo = mid; else hi = mid; }
      const f = (tt - ts[lo]) / (ts[hi] - ts[lo] || 1); return [d.pts[lo][0] + f * (d.pts[hi][0] - d.pts[lo][0]), d.pts[lo][1] + f * (d.pts[hi][1] - d.pts[lo][1])];
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const sc = Math.min((s.W - 40) / XE, (s.H - 40) / YE), ox = 20, oy = 18;
      const X = (x) => ox + x * sc, Y = (y) => oy + y * sc;
      const col = { line: C.muted, cycloid: C.box, yours: C.gold };
      Object.entries(data).forEach(([k, d]) => {
        g.strokeStyle = col[k]; g.lineWidth = k === "cycloid" ? 2.6 : 2; g.beginPath();
        d.pts.forEach(([x, y], i) => (i ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y)))); g.stroke();
        const tt = race ? race.t : 0, [bx, by] = at(d, tt);
        disc(g, X(bx), Y(by), 7, col[k]);
      });
      disc(g, X(XE), Y(YE), 5, C.card, C.ink);
      const T = Object.fromEntries(Object.entries(data).map(([k, d]) => [k, d.ts[d.ts.length - 1]]));
      out.innerHTML = `Times: <span style="color:var(--box)">cycloid <b>${T.cycloid.toFixed(3)} s</b></span> (exact π/√g = ${(Math.PI / Math.sqrt(G)).toFixed(3)} s) · straight line ${T.line.toFixed(3)} s · <span style="color:var(--gold)">yours ${T.yours.toFixed(3)} s</span>` + (T.yours < T.cycloid - 1e-4 ? " — faster than the cycloid? Check your rounding: it can't be." : "");
    }
    document.getElementById(a).addEventListener("input", () => { data = build(); race = null; draw(); });
    ctl.querySelector('[data-act="race"]').addEventListener("click", () => { race = { t: 0 }; });
    loop((dt) => { if (!race) return; race.t += dt * 0.6; draw(); if (race.t > 1.6) race = null; });
    draw();
  };

  // 13. Taylor: the parabola under the pendulum's potential ----------------------------------
  W.taylor = (host) => {
    const w = frame(host, "The pendulum's potential 1 − cos θ (blue) and its second-order Taylor parabola θ²/2 (red). Drag the amplitude.", "Linearization replaces the blue curve with the red one. It's excellent near the bottom and poor at large swings, which shows up as the real period growing with amplitude.");
    const a = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "swing amplitude:", 2, 175, 1, 40));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v + "°" });
    const agm = (x, y) => { for (let i = 0; i < 30; i++) { const ax = (x + y) / 2; y = Math.sqrt(x * y); x = ax; } return x; };
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const A = (+document.getElementById(a).value * Math.PI) / 180;
      const ths = lin(-Math.PI, Math.PI, 301);
      const X = (t) => 10 + ((t + Math.PI) / (2 * Math.PI)) * (s.W - 20), Y = (v) => s.H - 16 - (v / 2.6) * (s.H - 30);
      axes(g, 8, 8, s.W - 16, s.H - 20, "θ", "V / mgℓ");
      g.fillStyle = C.penSoft; g.fillRect(X(-A), 8, X(A) - X(-A), s.H - 20);
      plot(g, ths, ths.map((t) => 1 - Math.cos(t)), X, Y, C.pen, 2.5);
      plot(g, ths, ths.map((t) => (t * t) / 2), X, Y, C.box, 2, [6, 4]);
      const ratio = 1 / agm(1, Math.cos(A / 2));
      out.innerHTML = `At θ = ${(A * 180 / Math.PI).toFixed(0)}°: true ${(1 - Math.cos(A)).toFixed(3)}, parabola ${(A * A / 2).toFixed(3)} (error ${(((A * A / 2) - (1 - Math.cos(A))) / (1 - Math.cos(A)) * 100).toFixed(1)}%). Real period ÷ linear period = <b>${ratio.toFixed(4)}</b>.`;
    }
    document.getElementById(a).addEventListener("input", draw);
    draw();
  };

  // 14. Damped free vibration --------------------------------------------------------------
  W.damped = (host, opt) => {
    const w = frame(host, "Released from x = 1 at rest. Slide ζ through 1 to see the three cases, and the roots move in the complex plane.", opt.peaks ? "Two successive peaks X₁ and X₂ are marked: their log ratio gives Δ, and Δ gives ζ back." : "");
    const a = uid();
    const s = surface(w, 0.52, () => draw());
    controls(w, slider(a, "damping ratio ζ:", 0, 2, 0.01, opt.zeta != null ? opt.zeta : 0.2));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    const wn = 2 * Math.PI;
    function x(z, t) {
      if (z < 1 - 1e-6) { const wd = wn * Math.sqrt(1 - z * z); return Math.exp(-z * wn * t) * (Math.cos(wd * t) + ((z * wn) / wd) * Math.sin(wd * t)); }
      if (z <= 1 + 1e-6) return Math.exp(-wn * t) * (1 + wn * t);
      const r = Math.sqrt(z * z - 1), l1 = (-z + r) * wn, l2 = (-z - r) * wn;
      return (l2 * Math.exp(l1 * t) - l1 * Math.exp(l2 * t)) / (l2 - l1);
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const z = +document.getElementById(a).value;
      const pw = s.W * 0.68, ts = lin(0, 4, 600);
      const X = (t) => 10 + (t / 4) * (pw - 20), Y = (v) => s.H / 2 - v * (s.H / 2 - 16);
      axes(g, 8, 8, pw - 16, s.H - 20, "t (s), ωₙ = 2π rad/s", "x(t)");
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(8, s.H / 2); g.lineTo(pw - 8, s.H / 2); g.stroke();
      if (z < 1 && z > 0) { const env = ts.map((t) => Math.exp(-z * wn * t) / Math.sqrt(1 - z * z)); plot(g, ts, env, X, Y, C.gold, 1, [4, 4]); plot(g, ts, env.map((v) => -v), X, Y, C.gold, 1, [4, 4]); }
      plot(g, ts, ts.map((t) => x(z, t)), X, Y, C.pen, 2.4);
      let extra = "";
      if (opt.peaks && z > 0.005 && z < 0.9) {
        const wd = wn * Math.sqrt(1 - z * z), Pd = (2 * Math.PI) / wd;
        const tpk = [0, Pd].map((t0) => { let best = t0, bv = -1e9; for (let t = Math.max(0, t0 - Pd / 2); t < t0 + Pd / 2; t += Pd / 400) { const v = x(z, t); if (v > bv) { bv = v; best = t; } } return [best, bv]; });
        tpk.forEach(([t, v], i) => { disc(g, X(t), Y(v), 5, C.box); label(g, `X${i + 1}`, X(t) + 6, Y(v) - 6, C.box, "left", 12); });
        const D = Math.log(tpk[0][1] / tpk[1][1]);
        extra = ` · X₁/X₂ = ${(tpk[0][1] / tpk[1][1]).toFixed(3)}, Δ = ${D.toFixed(3)} → ζ = Δ/√(4π² + Δ²) = <b>${(D / Math.sqrt(4 * Math.PI ** 2 + D * D)).toFixed(3)}</b>`;
      }
      // complex plane
      const cx = pw + (s.W - pw) / 2 + 10, cy = s.H / 2, R = Math.min((s.W - pw) / 2 - 12, s.H / 2 - 14);
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(pw + 6, cy); g.lineTo(s.W - 4, cy); g.moveTo(cx, 8); g.lineTo(cx, s.H - 8); g.stroke();
      g.setLineDash([3, 3]); g.beginPath(); g.arc(cx, cy, R * 0.45, Math.PI / 2, 1.5 * Math.PI); g.stroke(); g.setLineDash([]);
      label(g, "Re λ", s.W - 6, cy - 6, C.muted, "right", 11); label(g, "Im λ", cx + 4, 18, C.muted, "left", 11);
      const k = (R * 0.45) / wn;
      const roots = z < 1 ? [[-z * wn, wn * Math.sqrt(1 - z * z)], [-z * wn, -wn * Math.sqrt(1 - z * z)]] : [[(-z + Math.sqrt(z * z - 1)) * wn, 0], [(-z - Math.sqrt(z * z - 1)) * wn, 0]];
      roots.forEach(([re, im]) => disc(g, cx + Math.max(-R, re * k), cy - im * k, 6, C.box));
      const kind = z === 0 ? "undamped: it never stops" : z < 1 ? "underdamped: rings down" : Math.abs(z - 1) < 0.005 ? "critically damped: fastest without overshoot" : "overdamped: creeps back";
      out.innerHTML = `ζ = ${z.toFixed(2)} — <b>${kind}</b>` + (z < 1 ? ` · ω<sub>d</sub> = ωₙ√(1 − ζ²) = ${(Math.sqrt(1 - z * z)).toFixed(3)} ωₙ` : "") + extra;
    }
    document.getElementById(a).addEventListener("input", draw);
    draw();
  };

  // 15. Forced response ----------------------------------------------------------------------
  W.forced = (host) => {
    const w = frame(host, "Steady-state amplitude and phase versus forcing frequency ratio r = Ω/ωₙ.", "Faint curves show other damping ratios. Near r = 1 the response is limited only by damping: X = (F₀/k)/(2ζ), with the mass lagging the force by 90°.");
    const a = uid(), b = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "ζ:", 0.02, 1, 0.01, 0.1) + slider(b, "r = Ω/ωₙ:", 0, 3, 0.01, 0.5));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(2) });
    const mag = (r, z) => 1 / Math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2);
    const ph = (r, z) => Math.atan2(2 * z * r, 1 - r * r) * 180 / Math.PI;
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const z = +document.getElementById(a).value, r = +document.getElementById(b).value;
      const rs = lin(0, 3, 400), w1 = s.W * 0.6;
      const X1 = (v) => 10 + (v / 3) * (w1 - 24), Y1 = (v) => s.H - 18 - (Math.min(v, 6) / 6) * (s.H - 34);
      axes(g, 8, 8, w1 - 18, s.H - 20, "r", "X k / F₀");
      [0.05, 0.2, 0.5, 1].forEach((zz) => plot(g, rs, rs.map((v) => mag(v, zz)), X1, Y1, C.rule, 1));
      plot(g, rs, rs.map((v) => mag(v, z)), X1, Y1, C.box, 2.4);
      disc(g, X1(r), Y1(mag(r, z)), 6, C.pen);
      const x2 = w1 + 6, w2 = s.W - x2 - 8;
      const X2 = (v) => x2 + 4 + (v / 3) * (w2 - 8), Y2 = (v) => 14 + (v / 180) * (s.H - 34);
      axes(g, x2, 8, w2, s.H - 20, "r", "phase lag φ");
      plot(g, rs, rs.map((v) => ph(v, z)), X2, Y2, C.pen, 2.2);
      disc(g, X2(r), Y2(ph(r, z)), 6, C.box);
      out.innerHTML = `X k/F₀ = <b>${mag(r, z).toFixed(3)}</b> · φ = <b>${ph(r, z).toFixed(1)}°</b>` + (Math.abs(r - 1) < 0.02 ? ` · at resonance 1/(2ζ) = ${(1 / (2 * z)).toFixed(2)}` : "");
    }
    w.querySelectorAll("input").forEach((el) => el.addEventListener("input", draw));
    draw();
  };

  // 16. Euler's method on an oscillator ------------------------------------------------------
  W.euler = (host) => {
    const w = frame(host, "ẍ = −x integrated for 20 s. Exact motion: the circle. Forward Euler: the spiral.", "Each Euler step goes along the tangent, which lies outside the circle, so energy grows by (1 + h²) per step. Symplectic Euler (update v first, then use the new v for x) keeps the orbit closed.");
    const a = uid(), b = uid();
    const s = surface(w, 0.6, () => draw());
    controls(w, slider(a, "step h:", 0.01, 0.5, 0.01, 0.1) + check(b, "symplectic Euler", false));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) + " s" });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const h = +document.getElementById(a).value, sym = document.getElementById(b).checked, N = Math.round(20 / h);
      const R = Math.min(s.W, s.H) / 2 - 12, sc = R / 3, cx = s.W / 2, cy = s.H / 2;
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(cx - R, cy); g.lineTo(cx + R, cy); g.moveTo(cx, cy - R); g.lineTo(cx, cy + R); g.stroke();
      label(g, "x", cx + R - 8, cy - 6, C.muted); label(g, "v", cx + 6, cy - R + 10, C.muted);
      disc(g, cx, cy, sc, null, C.ok);
      let x = 1, v = 0;
      g.strokeStyle = C.box; g.lineWidth = 1.6; g.beginPath(); g.moveTo(cx + x * sc, cy - v * sc);
      let escaped = false;
      for (let i = 0; i < N; i++) {
        if (sym) { v = v - h * x; x = x + h * v; } else { const nx = x + h * v; v = v - h * x; x = nx; }
        if (Math.hypot(x, v) > 3) { escaped = true; break; }
        g.lineTo(cx + x * sc, cy - v * sc);
      }
      g.stroke();
      disc(g, cx + sc, cy, 4, C.ink);
      const Er = (x * x + v * v);
      out.innerHTML = `${N} steps · energy after 20 s ÷ initial energy = <b>${escaped ? "> 9 (off the plot)" : Er.toFixed(3)}</b>` + (sym ? " (bounded: it wobbles but doesn't grow)" : ` · predicted (1 + h²)<sup>N</sup> = ${Math.pow(1 + h * h, N).toFixed(3)}`);
    }
    w.querySelectorAll("input").forEach((el) => el.addEventListener("input", draw));
    draw();
  };

  // 17. Knife-edge boat: a non-holonomic constraint ------------------------------------------
  W.boat = (host) => {
    const w = frame(host, "A boat that can't move sideways. Drive it, or run the parallel-parking manoeuvre.", "The constraint −ẋ sin θ + ẏ cos θ = 0 holds at every instant, yet the manoeuvre moves the boat purely sideways. Velocities are restricted; reachable positions aren't. That's what non-holonomic means.");
    const s = surface(w, 0.55, () => draw());
    const ctl = controls(w, `<button class="btn quiet" type="button" data-v="1" data-w="0">Forward</button><button class="btn quiet" type="button" data-v="-1" data-w="0">Back</button><button class="btn quiet" type="button" data-v="1" data-w="1.5">Forward-left</button><button class="btn quiet" type="button" data-v="1" data-w="-1.5">Forward-right</button><button class="btn solid" type="button" data-act="park">Parallel-park</button><button class="btn quiet" type="button" data-act="reset">Reset</button>`);
    const out = readout(w);
    let st = [0, 0, 0], trail = [], cmd = null, plan = [];
    const reset = () => { st = [0, 0, 0]; trail = []; cmd = null; plan = []; };
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const sc = s.H / 6, ox = s.W / 2, oy = s.H * 0.62;
      g.strokeStyle = C.rule; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(0, oy); g.lineTo(s.W, oy); g.stroke(); g.setLineDash([]);
      g.fillStyle = C.gold; trail.forEach(([x, y]) => g.fillRect(ox + x * sc - 1, oy - y * sc - 1, 2, 2));
      const [x, y, th] = st, c = [ox + x * sc, oy - y * sc];
      g.save(); g.translate(c[0], c[1]); g.rotate(-th);
      g.fillStyle = C.penSoft; g.strokeStyle = C.pen; g.lineWidth = 2; g.beginPath(); g.moveTo(0.7 * sc, 0); g.lineTo(0.3 * sc, 0.22 * sc); g.lineTo(-0.6 * sc, 0.22 * sc); g.lineTo(-0.6 * sc, -0.22 * sc); g.lineTo(0.3 * sc, -0.22 * sc); g.closePath(); g.fill(); g.stroke();
      g.restore();
      arrow(g, c[0], c[1], c[0] + Math.cos(th) * sc * 0.9, c[1] - Math.sin(th) * sc * 0.9, C.ok, 2);
      const v = cmd ? cmd[0] : 0;
      out.innerHTML = `position (${x.toFixed(2)}, ${y.toFixed(2)}), heading ${(th * 180 / Math.PI).toFixed(0)}° · sideways velocity −ẋ sin θ + ẏ cos θ = <b>${(0).toFixed(3)}</b> always` + (Math.abs(th) < 0.02 && Math.abs(x) < 0.05 && Math.abs(y) > 0.3 ? ` · <b>net sideways shift ${y.toFixed(2)}</b> with the heading restored` : "") + (v ? "" : "");
    }
    ctl.addEventListener("pointerdown", (e) => { const b = e.target.closest("button[data-v]"); if (b) { plan = []; cmd = [+b.dataset.v, +b.dataset.w, 0.6]; } });
    ctl.addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      if (b.dataset.act === "reset") { reset(); draw(); }
      if (b.dataset.act === "park") { reset(); for (let i = 0; i < 3; i++) plan.push([1, 1.5, 0.5], [1, -1.5, 0.5], [-1, -1.5, 0.5], [-1, 1.5, 0.5]); }
    });
    loop((dt) => {
      if (!cmd && plan.length) cmd = plan.shift().slice();
      if (!cmd) return;
      const h = Math.min(dt, cmd[2]); const n = 10;
      for (let i = 0; i < n; i++) { st[0] += cmd[0] * Math.cos(st[2]) * (h / n); st[1] += cmd[0] * Math.sin(st[2]) * (h / n); st[2] += cmd[1] * (h / n); }
      cmd[2] -= h; if (cmd[2] <= 1e-9) cmd = null;
      trail.push([st[0], st[1]]); if (trail.length > 2000) trail.shift();
      draw();
    });
    draw();
  };

  // 18. The fundamental lemma: a bump that finds where g isn't zero ---------------------------
  W.lemma = (host) => {
    const w = frame(host, "Slide a bump η along the interval and watch ∫ η g dx. If it's zero for every bump, g must be zero everywhere.", "Pick 'g hides a patch': most bump positions read ≈ 0, but park the bump over the patch and the integral jumps. That's why the Euler–Lagrange bracket must vanish at every point.");
    const a = uid(), b = uid(), c = uid();
    const s = surface(w, 0.45, () => draw());
    controls(w, slider(a, "bump centre:", 0.05, 0.95, 0.005, 0.3) + slider(b, "bump width:", 0.03, 0.4, 0.005, 0.12) + `<label for="${c}">g(x)<select id="${c}"><option value="patch">g hides a patch</option><option value="zero">g = 0</option><option value="wave">g = sin 6πx</option></select></label>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(2) });
    const gf = (kind, x) => kind === "zero" ? 0 : kind === "wave" ? Math.sin(6 * Math.PI * x) : Math.exp(-(((x - 0.72) / 0.03) ** 2));
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const cen = +document.getElementById(a).value, wd = +document.getElementById(b).value, kind = document.getElementById(c).value;
      const eta = (x) => (Math.abs(x - cen) < wd ? Math.cos((Math.PI / 2) * ((x - cen) / wd)) ** 2 : 0);
      const xs = lin(0, 1, 601);
      const X = (x) => 10 + x * (s.W - 20), Y = (v) => s.H / 2 - v * (s.H / 2 - 16);
      axes(g, 8, 8, s.W - 16, s.H - 20, "x", "");
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(8, s.H / 2); g.lineTo(s.W - 8, s.H / 2); g.stroke();
      g.fillStyle = C.gold; g.globalAlpha = 0.35; g.beginPath(); g.moveTo(X(0), Y(0)); xs.forEach((x) => g.lineTo(X(x), Y(eta(x) * gf(kind, x)))); g.lineTo(X(1), Y(0)); g.closePath(); g.fill(); g.globalAlpha = 1;
      plot(g, xs, xs.map((x) => gf(kind, x)), X, Y, C.box, 2);
      plot(g, xs, xs.map(eta), X, Y, C.pen, 2.2);
      label(g, "g(x)", X(0.02), Y(0.85), C.box); label(g, "η(x)", X(Math.min(0.9, cen + wd)), Y(1) + 14, C.pen);
      const I = xs.reduce((sum, x) => sum + eta(x) * gf(kind, x), 0) / (xs.length - 1);
      out.innerHTML = `∫ η g dx = <b>${Math.abs(I) < 5e-5 ? "0.0000" : I.toFixed(4)}</b>` + (kind === "patch" && Math.abs(I) > 1e-3 ? " — found it: g isn't zero under the bump." : kind === "zero" ? " — zero for every bump, because g is zero." : "");
    }
    w.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", draw));
    draw();
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
