// Live simulators for the MECH 430 atlas. Every one draws on a canvas from the page's colour tokens,
// computes with window.Gas (the JS mirror of content/gas.py), and stops when the reader navigates away.
// Colour code throughout: compression (pressure up, shocks) in --comp, expansion (pressure down) in --exp.
window.Widgets = (function () {
  const loops = new Set();
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const D = Math.PI / 180;
  let C = null;
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  function colors() {
    C = { ink: css("--ink"), muted: css("--muted"), rule: css("--rule"), pen: css("--pen"), comp: css("--comp"), exp: css("--exp"), ok: css("--ok"),
      gold: css("--gold"), card: css("--card"), paper: css("--paper"), penSoft: css("--pen-soft"), compSoft: css("--comp-soft"), expSoft: css("--exp-soft"),
      sans: css("--sans"), mono: css("--mono") };
    return C;
  }
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", colors);
  const rgb = (col) => {
    const m = /rgba?\(([^)]+)\)/.exec(col);
    if (m) return m[1].split(",").slice(0, 3).map((v) => parseFloat(v));
    const h = col.replace("#", ""); const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  };
  function mix(a, b, t) { t = Math.max(0, Math.min(1, t)); const A = rgb(a), B = rgb(b); return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * t)).join(",")})`; }

  // ---------- scaffolding ----------
  function frame(host, title, note) {
    const w = document.createElement("div");
    w.className = "widget";
    w.innerHTML = `<div class="w-title">${title}</div>`;
    host.appendChild(w);
    if (note) { const n = document.createElement("p"); n.className = "w-note"; n.innerHTML = note; w._note = n; }
    return w;
  }
  function surface(w, aspect, draw, minH) {
    const cv = document.createElement("canvas");
    w.appendChild(cv);
    const g = cv.getContext("2d");
    const s = { cv, g, W: 600, H: 600 * aspect };
    const fit = () => {
      const cw = Math.max(260, cv.clientWidth || w.clientWidth - 20 || 600);
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      s.W = cw; s.H = Math.max(minH || 0, Math.round(cw * aspect));
      cv.width = Math.round(cw * dpr); cv.height = Math.round(s.H * dpr); cv.style.height = s.H + "px";
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    fit();
    if (window.ResizeObserver) {
      let last = s.W;
      const ro = new ResizeObserver(() => { if (!cv.isConnected) { ro.disconnect(); return; } if (Math.abs((cv.clientWidth || last) - last) < 1) return; fit(); last = s.W; if (draw) draw(); });
      ro.observe(cv);
    }
    return s;
  }
  function controls(w, html) { const d = document.createElement("div"); d.className = "w-controls"; d.innerHTML = html; w.appendChild(d); return d; }
  function readout(w) { const d = document.createElement("div"); d.className = "w-read"; d.setAttribute("aria-live", "polite"); w.appendChild(d); if (w._note) w.appendChild(w._note); return d; }
  const slider = (id, label, min, max, step, val) => `<label for="${id}">${label} <span data-out="${id}"></span><input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${val}"></label>`;
  const check = (id, label, on) => `<label class="check"><input type="checkbox" id="${id}" ${on ? "checked" : ""}> ${label}</label>`;
  const select = (id, label, opts) => `<label for="${id}">${label}<select id="${id}">${opts.map(([v, t]) => `<option value="${v}">${t}</option>`).join("")}</select></label>`;
  const uid = () => "w" + Math.random().toString(36).slice(2, 8);
  const val = (id) => +document.getElementById(id).value;
  const on = (id) => document.getElementById(id).checked;
  function bindOut(w, fmt) { w.querySelectorAll("input[type=range]").forEach((el) => { const o = w.querySelector(`[data-out="${el.id}"]`); const up = () => { if (o) o.textContent = fmt[el.id] ? fmt[el.id](+el.value) : el.value; }; el.addEventListener("input", up); up(); }); }
  const rerun = (w, f) => w.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", f));
  function loop(fn) {
    const L = { alive: true };
    loops.add(L);
    let last = performance.now();
    const tick = (now) => {
      if (!L.alive) return;
      const dt = Math.min(0.05, (now - last) / 1000); last = now;
      try { fn(dt); } catch (e) { L.alive = false; loops.delete(L); console.error(e); return; }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    return L;
  }
  function arrow(g, x1, y1, x2, y2, color, wdt = 2) {
    const a = Math.atan2(y2 - y1, x2 - x1), h = 7, len = Math.hypot(x2 - x1, y2 - y1);
    g.strokeStyle = color; g.fillStyle = color; g.lineWidth = wdt;
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke();
    if (len < 3) return;
    g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - h * Math.cos(a - 0.4), y2 - h * Math.sin(a - 0.4)); g.lineTo(x2 - h * Math.cos(a + 0.4), y2 - h * Math.sin(a + 0.4)); g.closePath(); g.fill();
  }
  function label(g, s, x, y, color, align = "left", size = 12, weight = 400) { g.fillStyle = color || C.ink; g.font = `${weight} ${size}px ${C.sans}`; g.textAlign = align; g.fillText(s, x, y); g.textAlign = "left"; }
  function disc(g, x, y, r, fill, stroke) { g.beginPath(); g.arc(x, y, r, 0, 2 * Math.PI); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = 1.5; g.stroke(); } }
  function box(g, x, y, w, h, xl, yl) {
    g.strokeStyle = C.rule; g.lineWidth = 1; g.strokeRect(x, y, w, h);
    if (xl) label(g, xl, x + w - 4, y + h - 5, C.muted, "right", 11);
    if (yl) label(g, yl, x + 5, y + 13, C.muted, "left", 11);
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
  const f3 = (x) => !isFinite(x) ? "—" : Math.abs(x) >= 1e4 || (Math.abs(x) < 1e-3 && x !== 0) ? x.toExponential(2) : String(+x.toFixed(3));
  function grid(g, x, y, w, h, nx, ny) { g.strokeStyle = C.rule; g.globalAlpha = 0.5; g.lineWidth = 1; g.beginPath(); for (let i = 1; i < nx; i++) { g.moveTo(x + (w * i) / nx, y); g.lineTo(x + (w * i) / nx, y + h); } for (let j = 1; j < ny; j++) { g.moveTo(x, y + (h * j) / ny); g.lineTo(x + w, y + (h * j) / ny); } g.stroke(); g.globalAlpha = 1; }
  function pointer(cv, onDown, onMove) {
    let drag = false;
    const pos = (e) => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    cv.addEventListener("pointerdown", (e) => { if (onDown(...pos(e))) { drag = true; cv.setPointerCapture(e.pointerId); e.preventDefault(); } });
    cv.addEventListener("pointermove", (e) => { if (drag) onMove(...pos(e)); });
    cv.addEventListener("pointerup", () => { drag = false; });
  }
  const W = {};
  const G = window.Gas;

  // ====================================================================================
  // 1. The converging-diverging nozzle with variable back pressure (the canonical problem)
  // ====================================================================================
  function nozzleShape(xi, AeAt, conv) {
    // area ratio A/At along x in [0, 1]; throat at x = 0.32 (or the exit for a converging nozzle)
    const xt = conv ? 1 : 0.32, Ain = 2.6;
    if (xi <= xt) { const u = xi / xt; return 1 + (Ain - 1) * Math.pow(Math.cos((u * Math.PI) / 2), 2); }
    const u = (xi - xt) / (1 - xt);
    return 1 + (AeAt - 1) * (u * u * (3 - 2 * u));
  }
  function solveNozzle(AeAt, pb, conv) {
    const N = 160, xs = lin(0, 1, N), A = xs.map((x) => nozzleShape(x, AeAt, conv)), xt = conv ? 1 : 0.32;
    const n = conv ? convergingState(pb) : G.nozzle(AeAt, pb);
    const M = [], p = [], T = [], V = [];
    let shockX = null, p0r = 1;
    if (n.regime === "subsonic") {
      const Me = n.Me, As = Me > 1e-6 ? (conv ? 1 : AeAt) / G.A_Astar(Me) : Infinity;
      A.forEach((a) => M.push(Me > 1e-6 ? G.M_from_AR(Math.max(1, a / As), false) : 0));
    } else {
      A.forEach((a, i) => M.push(xs[i] <= xt ? G.M_from_AR(a, false) : G.M_from_AR(a, true)));
      if (n.regime === "shock") {
        p0r = n.p0r;
        const As2 = 1 / p0r;
        let k = xs.findIndex((x, i) => x > xt && A[i] >= n.As);
        if (k < 0) k = N - 1;
        shockX = xs[k];
        for (let i = k; i < N; i++) M[i] = G.M_from_AR(Math.max(1, A[i] / As2), false);
      }
    }
    for (let i = 0; i < N; i++) {
      const after = shockX !== null && xs[i] >= shockX ? p0r : 1;
      p.push(after / G.p0_p(M[i])); T.push(1 / G.T0_T(M[i])); V.push(M[i] * Math.sqrt(1 / G.T0_T(M[i])));
    }
    return { xs, A, M, p, T, V, n, shockX, xt };
  }
  function convergingState(pb) {
    if (pb >= 0.5283) { const Me = pb < 1 ? G.M_from_p0p(1 / pb) : 0; return { regime: "subsonic", Me, pe: pb, mdot: Me > 0 ? G.mass_flux(Me) / G.mass_flux(1) : 0, p3: 0.5283, pd: 0.5283, p4: 0.5283 }; }
    return { regime: "underexpanded", Me: 1, pe: 1 / G.p0_p(1), mdot: 1, p3: 1 / G.p0_p(1), pd: 1 / G.p0_p(1), p4: 1 / G.p0_p(1) };
  }
  const REGIME = {
    subsonic: ["Subsonic", "Not choked: the exit pressure matches the back pressure."], shock: ["Shock in the nozzle", "Choked; a normal shock stands in the diverging section."],
    overexpanded: ["Overexpanded", "Supersonic exit below the back pressure: oblique shocks at the lip."], design: ["Design", "Supersonic exit exactly at the back pressure."],
    underexpanded: ["Underexpanded", "Exit above the back pressure: expansion fans at the lip."],
  };
  W.nozzle = (host, spec) => {
    const preset = spec.preset || "", hero = preset === "hero", conv = preset === "converging";
    const w = frame(host, hero ? "Lower the back pressure and watch the flow choke, shock, and leave the nozzle." : conv ? "A converging nozzle fed from a reservoir. Lower the back pressure." : "A converging–diverging nozzle fed from a reservoir. Lower the back pressure; change the exit area.",
      hero ? null : "Colour is static pressure (warm = high, cool = low). Dots are gas parcels moving at the local speed. The lower plot is p/p₀ along the nozzle with the critical cases dashed: p₃ (sonic throat, subsonic exit), p₄ (shock at the exit) and p_d (design).");
    if (hero) w.classList.add("hero-widget");
    const a = uid(), b = uid(), sc = uid();
    const startPb = preset === "shock" ? 0.75 : preset === "plume" ? 0.12 : hero ? 0.62 : conv ? 0.7 : 0.8;
    const s = surface(w, hero ? 0.62 : 0.72, () => draw(), hero ? 300 : 0);
    controls(w, slider(a, "back pressure p_b/p₀:", 0.01, 1, 0.001, startPb) + (conv || hero ? "" : slider(b, "exit/throat area A_e/A_t:", 1.3, 4, 0.01, 2.5)) + (hero ? "" : check(sc, "schlieren view", false)));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(3), [b]: (v) => v.toFixed(2) });
    let sol = null, parts = [];
    const AeAt = () => (conv ? 1 : hero ? 2.5 : val(b));
    function recompute() { sol = solveNozzle(AeAt(), val(a), conv); }
    function geom() {
      const top = hero ? 18 : 14, nozH = s.H * (hero ? 0.6 : 0.5), mid = top + nozH / 2, xL = 14, xN = s.W * (hero ? 0.66 : 0.62), xR = s.W - 14;
      const Amax = Math.max(2.6, AeAt()), half = (nozH / 2 - 6) / Math.sqrt(Amax);
      const r = (aRatio) => half * Math.sqrt(aRatio);
      return { top, nozH, mid, xL, xN, xR, r, X: (x) => xL + x * (xN - xL) };
    }
    function interp(arr, x) { const N = arr.length, f = Math.max(0, Math.min(N - 1, x * (N - 1))), i = Math.floor(f), t = f - i; return i >= N - 1 ? arr[N - 1] : arr[i] * (1 - t) + arr[i + 1] * t; }
    function draw(dt) {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      if (!sol) recompute();
      const Gm = geom(), { xs, A, p, n } = sol, schl = !hero && !conv && on(sc);
      // pressure field inside the nozzle
      for (let i = 0; i < xs.length - 1; i++) {
        const x0 = Gm.X(xs[i]), x1 = Gm.X(xs[i + 1]) + 1, r0 = Gm.r(A[i]);
        let col;
        if (schl) { const grad = Math.abs(p[i + 1] - p[i]) * xs.length; col = mix(C.paper, C.ink, Math.min(1, grad * 0.9)); }
        else col = mix(C.card, mix(C.exp, C.comp, Math.pow(p[i], 0.6)), 0.38);
        g.fillStyle = col; g.fillRect(x0, Gm.mid - r0, x1 - x0, 2 * r0);
      }
      // walls
      g.strokeStyle = C.ink; g.lineWidth = 2.5;
      [-1, 1].forEach((sg) => { g.beginPath(); xs.forEach((x, i) => { const px = Gm.X(x), py = Gm.mid + sg * Gm.r(A[i]); i ? g.lineTo(px, py) : g.moveTo(px, py); }); g.stroke(); });
      // exhaust region
      const re = Gm.r(AeAt()), xe = Gm.X(1);
      g.save(); g.beginPath(); g.rect(xe, Gm.top - 6, Gm.xR - xe, Gm.nozH + 12); g.clip();
      if (n.regime === "overexpanded" || n.regime === "design" || n.regime === "underexpanded") drawPlume(g, Gm, n, xe, re);
      else { g.fillStyle = mix(C.exp, C.comp, Math.pow(n.pe || val(a), 0.6)); g.globalAlpha = 0.18; g.fillRect(xe, Gm.mid - re, Gm.xR - xe, 2 * re); g.globalAlpha = 1; }
      g.restore();
      // shock
      if (sol.shockX !== null) {
        const xsx = Gm.X(sol.shockX), rs = Gm.r(n.As);
        g.strokeStyle = C.comp; g.lineWidth = 3.5; g.beginPath(); g.moveTo(xsx, Gm.mid - rs); g.lineTo(xsx, Gm.mid + rs); g.stroke();
        label(g, "normal shock", xsx, Gm.mid - rs - 6, C.comp, "center", 11, 600);
      }
      // throat marker and labels
      const xth = Gm.X(sol.xt);
      g.setLineDash([3, 4]); g.strokeStyle = C.muted; g.lineWidth = 1; g.beginPath(); g.moveTo(xth, Gm.mid - Gm.r(1) - 4); g.lineTo(xth, Gm.mid + Gm.r(1) + 4); g.stroke(); g.setLineDash([]);
      label(g, "throat", xth, Gm.mid + Gm.r(1) + 16, C.muted, "center", 11);
      label(g, "reservoir p₀", Gm.xL + 2, Gm.top - 2, C.muted, "left", 11);
      label(g, `back pressure ${(val(a)).toFixed(2)} p₀`, Gm.xR, Gm.top - 2, C.muted, "right", 11);
      // particles
      if (dt !== undefined && !reduce) {
        const speed = 0.5, N = hero ? 150 : 120;
        if (!parts.length) for (let i = 0; i < N; i++) parts.push({ x: Math.random() * 1.4, yr: (Math.random() * 2 - 1) * 0.9, jet: 0 });
        parts.forEach((q) => {
          if (n.mdot <= 0) return;
          q.x += Math.max(0.03, interp(sol.V, Math.min(q.x, 1))) * speed * dt;
          if (q.x > 1.4) { q.x -= 1.4; q.yr = (Math.random() * 2 - 1) * 0.9; }
          q.jet = Math.max(0, q.x - 1);
        });
      }
      g.fillStyle = C.ink;
      parts.forEach((q) => {
        let px, py;
        if (q.x < 1) { px = Gm.X(q.x); py = Gm.mid + q.yr * Gm.r(interp(A, q.x)); }
        else { px = xe + q.jet * (Gm.xR - xe) / 0.4; const spread = n.regime === "underexpanded" ? 1 + q.jet * 0.9 : n.regime === "overexpanded" ? 1 - q.jet * 0.35 : 1; py = Gm.mid + q.yr * re * spread; }
        g.globalAlpha = 0.75; g.beginPath(); g.arc(px, py, 1.6, 0, 6.3); g.fill(); g.globalAlpha = 1;
      });
      // pressure trace
      const top2 = Gm.top + Gm.nozH + (hero ? 16 : 22), h2 = s.H - top2 - 8, Y = (v) => top2 + h2 - v * (h2 - 8);
      box(g, Gm.xL, top2, Gm.xR - Gm.xL, h2, "", "p/p₀");
      if (!conv) {
        const sub = A.map((aa, i) => 1 / G.p0_p(G.M_from_AR(aa, false))), sup = A.map((aa, i) => xs[i] <= sol.xt ? NaN : 1 / G.p0_p(G.M_from_AR(aa, true)));
        plot(g, xs, sub, Gm.X, Y, C.muted, 1, [4, 4]); plot(g, xs, sup, Gm.X, Y, C.muted, 1, [4, 4]);
      }
      plot(g, xs, p, Gm.X, Y, C.pen, 2.6);
      g.setLineDash([2, 3]); g.strokeStyle = C.gold; g.lineWidth = 1.5; g.beginPath(); g.moveTo(xe, Y(val(a))); g.lineTo(Gm.xR - 4, Y(val(a))); g.stroke(); g.setLineDash([]);
      label(g, "p_b", Gm.xR - 6, Y(val(a)) - 4, C.gold, "right", 11);
      if (!conv && !hero) [["p₃", n.p3], ["p₄", n.p4], ["p_d", n.pd]].forEach(([t, v]) => { disc(g, xe, Y(v), 2.5, C.muted); label(g, t, xe + 5, Y(v) + 4, C.muted, "left", 10); });
      const [rn, rd] = REGIME[n.regime] || ["", ""];
      out.innerHTML = `<span class="regime r-${n.regime}">${rn}</span> ${rd} Mass flow <b>${(100 * n.mdot).toFixed(1)}%</b> of choked${n.Me ? `, exit Mach <b>${f3(n.Me)}</b>` : ""}${n.regime === "shock" ? `, shock at A/A_t = <b>${f3(n.As)}</b> (Mach ${f3(n.Ms)} ahead of it)` : ""}.${!conv && !hero ? ` Critical back pressures: p₃ = ${f3(n.p3)}, p₄ = ${f3(n.p4)}, p_d = ${f3(n.pd)} (× p₀).` : ""}`;
    }
    function drawPlume(g, Gm, n, xe, re) {
      const pb = val(a), Me = n.Me, pe = n.pd, L = Gm.xR - xe;
      if (n.regime === "design") { g.fillStyle = C.expSoft; g.fillRect(xe, Gm.mid - re, L, 2 * re); return; }
      if (n.regime === "overexpanded") {
        const ratio = pb / pe, Mn = Math.sqrt(((ratio - 1) * 2.4) / 2.8 + 1), sig = Math.asin(Math.min(1, Mn / Me));
        const dx = re / Math.tan(sig);
        g.fillStyle = C.compSoft; g.fillRect(xe, Gm.mid - re, L, 2 * re);
        g.strokeStyle = C.comp; g.lineWidth = 2;
        for (let k = 0; k < 4; k++) {
          const x0 = xe + k * 2 * dx, fade = Math.pow(0.6, k);
          g.globalAlpha = fade;
          g.beginPath(); g.moveTo(x0, Gm.mid - re); g.lineTo(x0 + dx, Gm.mid); g.lineTo(x0, Gm.mid + re); g.stroke();
          g.strokeStyle = C.exp; g.beginPath(); g.moveTo(x0 + dx, Gm.mid); g.lineTo(x0 + 2 * dx, Gm.mid - re); g.moveTo(x0 + dx, Gm.mid); g.lineTo(x0 + 2 * dx, Gm.mid + re); g.stroke(); g.strokeStyle = C.comp;
        }
        g.globalAlpha = 1;
        label(g, "oblique shocks · Mach diamonds", xe + 6, Gm.mid + re + 14, C.comp, "left", 11, 600);
      } else {
        const Mj = G.M_from_p0p(1 / Math.max(pb, 1e-4)), turn = Math.min(85, G.pm_nu(Mj) - G.pm_nu(Me));
        const mu1 = Math.asin(1 / Math.max(Me, 1.0001)), mu2 = Math.asin(1 / Mj) - turn * D;
        g.fillStyle = C.expSoft;
        g.beginPath(); g.moveTo(xe, Gm.mid - re); g.lineTo(xe + L, Gm.mid - re - L * Math.tan(turn * D) * 0.5); g.lineTo(xe + L, Gm.mid + re + L * Math.tan(turn * D) * 0.5); g.lineTo(xe, Gm.mid + re); g.closePath(); g.fill();
        g.strokeStyle = C.exp; g.lineWidth = 1.4;
        [-1, 1].forEach((sg) => { for (let k = 0; k <= 5; k++) { const ang = mu1 + ((mu2 - mu1) * k) / 5, len = re * 1.6; g.beginPath(); g.moveTo(xe, Gm.mid + sg * re); g.lineTo(xe + len * Math.cos(ang), Gm.mid + sg * re - sg * len * Math.sin(ang)); g.stroke(); } });
        label(g, `expansion fans · jet turns ${turn.toFixed(0)}° outward`, xe + 6, Gm.mid + re + 14, C.exp, "left", 11, 600);
      }
    }
    rerun(w, () => { recompute(); if (reduce) draw(); });
    recompute();
    if (reduce) draw(); else loop((dt) => draw(dt));
  };

  // ====================================================================================
  // 2. x–t diagram: compression waves coalescing into a shock (and the piston-driven shock)
  // ====================================================================================
  W.xt = (host, spec) => {
    const piston = spec.preset === "piston";
    const w = frame(host, piston ? "A piston set suddenly moving at V_p drives a shock into still gas. Lines are gas parcels; the bold line is the shock." : "An x–t diagram: time runs up. The piston (left) accelerates and sends right-running waves. Watch them converge into a shock; switch to 'pull' and they fan out.",
      piston ? "Each parcel sits still until the shock reaches it, then moves at the piston speed. The shock always outruns the piston: the slug of compressed gas between them grows." : "The lower panel is a 'slit' through the diagram at the moving time line: the pressure profile at that instant. The notes suggest doing this with a slit in a sheet of paper.");
    const a = uid(), md = uid(), pl = uid();
    const s = surface(w, 0.82, () => draw(0));
    controls(w, piston ? slider(a, "piston speed V_p/c₀:", 0.05, 3, 0.01, 0.8) : slider(a, "final piston speed V_p/c₀:", 0.05, 0.8, 0.01, 0.45) + select(md, "piston", [["push", "push in (compression)"], ["pull", "pull out (rarefaction)"]]) + `<button type="button" class="btn quiet" id="${pl}">Replay</button>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    const gam = 1.4, c0 = 1, tMax = 4, xMax = 4.4;
    let tNow = 0;
    if (!piston) document.getElementById(pl).addEventListener("click", () => { tNow = 0; });
    function model() {
      const Vp = val(a), sign = piston ? 1 : document.getElementById(md).value === "push" ? 1 : -1, tAcc = piston ? 1e-6 : 1.2;
      const up = (t) => sign * Vp * Math.min(1, t / tAcc);
      const xp = (t) => t <= tAcc ? sign * Vp * t * t / (2 * tAcc) : sign * Vp * (tAcc / 2 + (t - tAcc));
      const nC = piston ? 0 : 22, chars = [];
      for (let k = 0; k <= nC; k++) {
        const tau = (tAcc * k) / nC, u = up(tau), cc = c0 + ((gam - 1) / 2) * u;
        chars.push({ tau, x0: xp(tau), u, sp: u + cc });
      }
      return { Vp, sign, tAcc, up, xp, chars };
    }
    function shockPath(m) {
      if (piston) { const Ms = G.piston_shock_mach(m.Vp); return { t0: 0, x0: 0, pts: [[0, 0], [tMax, Ms * tMax]], Ms }; }
      if (m.sign < 0) return null;
      // first crossing between neighbouring characteristics
      let tb = Infinity, xb = 0;
      for (let i = 0; i + 1 < m.chars.length; i++) {
        const A1 = m.chars[i], B1 = m.chars[i + 1], dsp = B1.sp - A1.sp;
        if (dsp <= 1e-9) continue;
        const t = (A1.x0 - A1.sp * A1.tau - (B1.x0 - B1.sp * B1.tau)) / dsp;
        if (t > B1.tau && t < tb) { tb = t; xb = A1.x0 + A1.sp * (t - A1.tau); }
      }
      if (!isFinite(tb) || tb > tMax) return null;
      const pts = [[tb, xb]], dt = 0.01;
      let xs = xb;
      const at = (ch, t) => ch.x0 + ch.sp * (t - ch.tau);
      for (let t = tb; t < tMax; t += dt) {
        let behind = null, ahead = null;
        m.chars.forEach((ch) => { if (t < ch.tau) return; const x = at(ch, t); if (x >= xs) { if (!behind || ch.tau > behind.tau) behind = ch; } else if (!ahead || x > at(ahead, t)) ahead = ch; });
        const lb = behind ? behind.sp : m.chars[m.chars.length - 1].sp, la = ahead && at(ahead, t) < xs ? c0 : c0;
        const aheadSp = m.chars.filter((ch) => t >= ch.tau && at(ch, t) > xs).reduce((mn, ch) => Math.min(mn, ch.sp), Infinity);
        xs += dt * 0.5 * (lb + (isFinite(aheadSp) ? aheadSp : la));
        pts.push([t + dt, xs]);
      }
      return { t0: tb, x0: xb, pts };
    }
    function draw(dt) {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const m = model(), sh = shockPath(m);
      const x0 = 30, y0 = 10, w0 = s.W - 44, h0 = s.H * 0.6;
      const X = (x) => x0 + ((x + 0.6) / (xMax + 0.6)) * w0, T = (t) => y0 + h0 - (t / tMax) * h0;
      box(g, x0, y0, w0, h0, "x", "t");
      // piston path
      const ts = lin(0, tMax, 200);
      g.fillStyle = C.penSoft; g.beginPath(); g.moveTo(X(-0.6), T(0)); ts.forEach((t) => g.lineTo(X(m.xp(t)), T(t))); g.lineTo(X(-0.6), T(tMax)); g.closePath(); g.fill();
      plot(g, ts, ts.map(m.xp), (t) => 0, () => 0, C.ink, 0);
      g.strokeStyle = C.ink; g.lineWidth = 2.5; g.beginPath(); ts.forEach((t, i) => { const px = X(m.xp(t)), py = T(t); i ? g.lineTo(px, py) : g.moveTo(px, py); }); g.stroke();
      label(g, "piston", X(m.xp(tMax * 0.92)) - 6, T(tMax * 0.92), C.ink, "right", 11, 600);
      const shockX = (t) => { if (!sh || t < sh.pts[0][0]) return null; const p2 = sh.pts; for (let i = 1; i < p2.length; i++) if (p2[i][0] >= t) { const [ta, xa] = p2[i - 1], [tb2, xb2] = p2[i]; return xa + ((xb2 - xa) * (t - ta)) / (tb2 - ta); } return p2[p2.length - 1][1]; };
      if (piston) {
        // particle paths
        g.strokeStyle = C.muted; g.lineWidth = 1;
        for (let xpcl = 0.4; xpcl < xMax; xpcl += 0.4) {
          const tHit = xpcl / sh.Ms;
          g.beginPath(); g.moveTo(X(xpcl), T(0)); g.lineTo(X(xpcl), T(Math.min(tHit, tMax)));
          if (tHit < tMax) g.lineTo(X(xpcl + m.Vp * (tMax - tHit)), T(tMax));
          g.stroke();
        }
      } else {
        m.chars.forEach((ch) => {
          let tEnd = tMax;
          if (sh) { for (const [t, xs] of sh.pts) { if (t >= ch.tau && ch.x0 + ch.sp * (t - ch.tau) >= xs - 1e-3) { tEnd = t; break; } } }
          g.strokeStyle = m.sign > 0 ? C.comp : C.exp; g.globalAlpha = 0.55; g.lineWidth = 1.1;
          g.beginPath(); g.moveTo(X(ch.x0), T(ch.tau)); g.lineTo(X(ch.x0 + ch.sp * (tEnd - ch.tau)), T(tEnd)); g.stroke(); g.globalAlpha = 1;
        });
      }
      if (sh) { g.strokeStyle = C.comp; g.lineWidth = 3.2; g.beginPath(); sh.pts.forEach(([t, x], i) => (i ? g.lineTo(X(x), T(t)) : g.moveTo(X(x), T(t)))); g.stroke(); if (!piston) disc(g, X(sh.x0), T(sh.t0), 4, C.comp); label(g, "shock", X(sh.pts[sh.pts.length - 1][1]) - 4, T(tMax) + 14, C.comp, "right", 11, 600); }
      // time cursor
      if (dt !== undefined && !reduce) { tNow += dt * 0.6; if (tNow > tMax) tNow = 0; } else if (reduce) tNow = tMax * 0.8;
      g.strokeStyle = C.gold; g.lineWidth = 1.5; g.beginPath(); g.moveTo(x0, T(tNow)); g.lineTo(x0 + w0, T(tNow)); g.stroke();
      // slit: pressure profile at tNow
      const y1 = y0 + h0 + 26, h1 = s.H - y1 - 8, P = (v) => y1 + h1 - ((v - 0.3) / 2.7) * h1;
      box(g, x0, y1, w0, h1, "x at the gold time line", "p/p₀");
      const xsGrid = lin(-0.6, xMax, 300), shx = shockX(tNow), xpNow = m.xp(tNow);
      const pr = xsGrid.map((x) => {
        if (x < xpNow) return NaN;
        if (piston) return x <= tNow * sh.Ms ? G.ns_p2p1(sh.Ms) : 1;
        if (shx !== null && x > shx) return 1;
        // simple wave: find the characteristic through (x, tNow)
        let u = 0;
        const cs = m.chars.filter((ch) => tNow >= ch.tau);
        for (let i = cs.length - 1; i >= 0; i--) { const xc = cs[i].x0 + cs[i].sp * (tNow - cs[i].tau); if (xc >= x) { u = cs[i].u; } }
        const head = cs.length ? cs[0].x0 + cs[0].sp * (tNow - cs[0].tau) : -1;
        if (x > head) u = 0;
        if (x < (cs.length ? cs[cs.length - 1].x0 + cs[cs.length - 1].sp * (tNow - cs[cs.length - 1].tau) : -1)) u = m.up(tNow);
        return Math.pow(1 + ((gam - 1) / 2) * u, (2 * gam) / (gam - 1));
      });
      plot(g, xsGrid, pr, X, P, m.sign > 0 ? C.comp : C.exp, 2.4);
      g.setLineDash([3, 3]); g.strokeStyle = C.muted; g.lineWidth = 1; g.beginPath(); g.moveTo(x0, P(1)); g.lineTo(x0 + w0, P(1)); g.stroke(); g.setLineDash([]);
      if (piston) out.innerHTML = `Shock Mach number <b>${f3(sh.Ms)}</b>, pressure ratio <b>${f3(G.ns_p2p1(sh.Ms))}</b>. The shock moves ${f3(sh.Ms / m.Vp)}× faster than the piston.`;
      else out.innerHTML = m.sign > 0 ? (sh ? `The waves converge and a shock forms at t ≈ <b>${f3(sh.t0)}</b> (in units of the time sound crosses one length unit).` : "No shock yet within this window.") : "Rarefaction waves fan apart: no shock can form.";
    }
    rerun(w, () => { tNow = 0; if (reduce) draw(); });
    if (reduce) draw(); else loop((dt) => draw(dt));
  };

  // ====================================================================================
  // 3. Mach cone from a moving beeper
  // ====================================================================================
  W.machcone = (host) => {
    const w = frame(host, "A source beeps while flying left to right. Each beep spreads as a circle from where it was emitted.", "Below Mach 1 the circles crowd ahead (Doppler shift). At Mach 1 they pile up into a front. Above, they're trapped inside a cone of half-angle μ = sin⁻¹(1/M): outside it is the zone of silence.");
    const a = uid();
    const s = surface(w, 0.5, () => {});
    controls(w, slider(a, "Mach number M:", 0, 3, 0.01, 1.6));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    let t = 2.2;
    function draw(dt) {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M = val(a), c = s.W / 9, tau = 0.45, span = 3.6;
      if (dt !== undefined && !reduce) t += dt; else t = 2.5;
      const period = (s.W * 0.75 + 40) / Math.max(c * M, 30);
      const tt = M > 0.02 ? t % period : t % span;
      const sx = M > 0.02 ? -40 + c * M * tt : s.W * 0.5, sy = s.H * 0.55;
      g.strokeStyle = C.pen; g.lineWidth = 1.3;
      for (let k = 0; k * tau <= tt && k < 40; k++) {
        const te = tt - k * tau, ex = M > 0.02 ? -40 + c * M * te : s.W * 0.5, r = c * (tt - te);
        g.globalAlpha = Math.max(0.15, 1 - r / (s.W * 0.9)); g.beginPath(); g.arc(ex, sy, r, 0, 2 * Math.PI); g.stroke();
      }
      g.globalAlpha = 1;
      if (M > 1) {
        const mu = Math.asin(1 / M), len = s.W * 1.5;
        g.fillStyle = C.penSoft; g.beginPath(); g.moveTo(sx, sy); g.lineTo(sx - len * Math.cos(mu), sy - len * Math.sin(mu)); g.lineTo(sx - len * Math.cos(mu), sy + len * Math.sin(mu)); g.closePath(); g.fill();
        g.strokeStyle = C.comp; g.lineWidth = 2.2; g.beginPath(); g.moveTo(sx - len * Math.cos(mu), sy - len * Math.sin(mu)); g.lineTo(sx, sy); g.lineTo(sx - len * Math.cos(mu), sy + len * Math.sin(mu)); g.stroke();
        label(g, "zone of silence", Math.min(s.W - 10, sx + 20), 20, C.muted, "right", 11);
      }
      disc(g, sx, sy, 5, C.comp);
      out.innerHTML = M > 1 ? `Mach angle μ = <b>${(Math.asin(1 / M) / D).toFixed(1)}°</b>.` : M === 1 ? "Mach 1: the wavefronts pile up into a plane front." : `Subsonic: the sound reaches everywhere; ahead of the source the beeps arrive ${(1 / Math.max(1e-3, 1 - M)).toFixed(2)}× faster (Doppler).`;
    }
    if (reduce) { draw(); rerun(w, () => draw()); } else loop((dt) => draw(dt));
  };

  // ====================================================================================
  // 4. A weak wave in two frames
  // ====================================================================================
  W.soundframe = (host) => {
    const w = frame(host, "A wall nudged at dV sends a weak wave into still gas. Switch between the lab frame and the wave's frame.", "In the wave frame the picture is steady: gas arrives at c and leaves at c − dV (compression) or c + |dV| (rarefaction). Pressure, density and temperature are the same in both frames; only velocities change.");
    const fr = uid(), kd = uid();
    const s = surface(w, 0.42, () => {});
    controls(w, select(fr, "frame", [["lab", "lab frame (wave moves)"], ["wave", "wave frame (wave fixed)"]]) + select(kd, "wave", [["comp", "compression: wall pushed in"], ["rare", "rarefaction: wall pulled out"]]));
    const out = readout(w);
    let t = 0;
    const parts = Array.from({ length: 70 }, (_, i) => ({ x0: i / 70 + Math.random() * 0.01, y: Math.random() }));
    function draw(dt) {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const lab = document.getElementById(fr).value === "lab", comp = document.getElementById(kd).value === "comp";
      if (dt !== undefined && !reduce) t = (t + dt * 0.12) % 1; else t = 0.45;
      const x0 = 20, x1 = s.W - 20, top = 26, bot = s.H - 30, L = x1 - x0;
      const c = 1, dV = comp ? 0.22 : -0.22, waveX = lab ? t : 0.5;
      g.strokeStyle = C.ink; g.lineWidth = 2; g.beginPath(); g.moveTo(x0, top); g.lineTo(x1, top); g.moveTo(x0, bot); g.lineTo(x1, bot); g.stroke();
      // shade the processed region
      g.fillStyle = comp ? C.compSoft : C.expSoft; g.fillRect(x0, top, L * waveX, bot - top);
      g.strokeStyle = comp ? C.comp : C.exp; g.lineWidth = 3; g.beginPath(); g.moveTo(x0 + L * waveX, top); g.lineTo(x0 + L * waveX, bot); g.stroke();
      // parcels: in the lab frame, behind the wave they drift at dV; in the wave frame everything streams left
      g.fillStyle = C.ink;
      parts.forEach((p) => {
        let x;
        if (lab) { const behind = p.x0 < waveX; x = behind ? p.x0 + dV * (waveX - p.x0) / c : p.x0; }
        else { const ph = (p.x0 + t) % 1; x = ph < 0.5 ? 0.5 - (0.5 - ph) * (1 - dV / c) : ph; x = 1 - x; }
        disc(g, x0 + L * x, top + 6 + p.y * (bot - top - 12), 2, C.ink);
      });
      const ay = (top + bot) / 2;
      if (lab) {
        arrow(g, x0 + L * waveX + 6, ay, x0 + L * waveX + 70, ay, comp ? C.comp : C.exp, 2.5); label(g, "wave, c", x0 + L * waveX + 74, ay + 4, comp ? C.comp : C.exp, "left", 12, 600);
        if (waveX > 0.15) { arrow(g, x0 + L * waveX * 0.4, ay - 22, x0 + L * waveX * 0.4 + (comp ? 34 : -34), ay - 22, C.ink, 2); label(g, comp ? "gas moves at dV →" : "← gas moves at |dV|", x0 + L * waveX * 0.4, ay - 30, C.ink, "center", 11); }
      } else {
        arrow(g, x1 - 10, ay, x0 + L * 0.5 + 70, ay, C.ink, 2); label(g, "gas arrives at c", x1 - 12, ay - 8, C.ink, "right", 11);
        arrow(g, x0 + L * 0.5 - 8, ay, x0 + 30, ay, C.ink, 2); label(g, comp ? "leaves at c − dV" : "leaves at c + |dV|", x0 + 32, ay - 8, C.ink, "left", 11);
      }
      label(g, comp ? "p + dp, ρ + dρ" : "p − |dp|, ρ − |dρ|", x0 + 8, bot + 18, comp ? C.comp : C.exp, "left", 11, 600);
      label(g, "p, ρ (undisturbed)", x1 - 8, bot + 18, C.muted, "right", 11);
      out.innerHTML = comp ? "Continuity: c·dρ = ρ·dV. Momentum: dp = ρc·dV. Together: <b>c² = dp/dρ</b>, and dp > 0 pushes the gas the way the wave travels." : "Same algebra with dV < 0: dp < 0, and the gas moves opposite to the wave. The wave speed is the same c.";
    }
    if (reduce) { draw(); rerun(w, () => draw()); } else loop((dt) => draw(dt));
  };

  // ====================================================================================
  // 5. Area change: which way does everything go?
  // ====================================================================================
  W.areavel = (host) => {
    const w = frame(host, "A short duct element. Choose the Mach number and whether it converges or diverges.", "The bars show dV/V, dp/(ρV²) and dρ/ρ for a 1% area change. Crossing Mach 1 flips every sign; near Mach 1 the response blows up, which is why Mach 1 only occurs at a throat.");
    const a = uid(), b = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "Mach number M:", 0.05, 3, 0.01, 0.5) + select(b, "duct", [["-1", "converging (dA < 0)"], ["1", "diverging (dA > 0)"]]));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M = val(a), sg = +document.getElementById(b).value, dA = 0.01 * sg, k = 1 / (1 - M * M);
      const dV = -k * dA, dp = k * dA, drho = M * M * k * dA;
      const wL = s.W * 0.42, cx = 16, mid = s.H / 2, h0 = s.H * 0.28;
      const h1 = h0 * (1 + sg * 0.35);
      g.fillStyle = mix(C.exp, C.comp, 0.5); g.globalAlpha = 0.12; g.beginPath(); g.moveTo(cx, mid - h0); g.lineTo(cx + wL, mid - h1); g.lineTo(cx + wL, mid + h1); g.lineTo(cx, mid + h0); g.closePath(); g.fill(); g.globalAlpha = 1;
      g.strokeStyle = C.ink; g.lineWidth = 2.5; g.beginPath(); g.moveTo(cx, mid - h0); g.lineTo(cx + wL, mid - h1); g.moveTo(cx, mid + h0); g.lineTo(cx + wL, mid + h1); g.stroke();
      arrow(g, cx + 10, mid, cx + wL - 10, mid, C.ink, 2); label(g, M < 1 ? "subsonic" : M > 1 ? "supersonic" : "Mach 1", cx + wL / 2, mid - 8, C.muted, "center", 12, 600);
      const bx = cx + wL + 30, bw = s.W - bx - 16, zero = mid, scale = (h0 * 1.6) / 0.05;
      const bars = [["dV/V", dV], ["dp/ρV²", dp], ["dρ/ρ", drho]];
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(bx, zero); g.lineTo(bx + bw, zero); g.stroke();
      bars.forEach(([n, v], i) => {
        const x = bx + 12 + (i * (bw - 24)) / 3, wd = (bw - 24) / 3 - 18, hgt = Math.max(-h0 * 1.6, Math.min(h0 * 1.6, -v * scale));
        g.fillStyle = v > 0 ? C.comp : C.exp; g.fillRect(x, zero, wd, hgt);
        label(g, n, x + wd / 2, s.H - 8, C.ink, "center", 12, 600);
        label(g, (v >= 0 ? "+" : "−") + Math.abs(v * 100).toFixed(2) + "%", x + wd / 2, hgt < 0 ? zero + hgt - 6 : zero + hgt + 14, C.ink, "center", 11);
      });
      out.innerHTML = `For a ${sg > 0 ? "1% increase" : "1% decrease"} in area at Mach ${M.toFixed(2)}: velocity ${dV > 0 ? "rises" : "falls"} by <b>${Math.abs(dV * 100).toFixed(2)}%</b>, pressure ${dp > 0 ? "rises" : "falls"}, density ${drho > 0 ? "rises" : "falls"}.`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 6. Mass flux per unit area, and the two roots of A/A*
  // ====================================================================================
  W.massflux = (host) => {
    const w = frame(host, "Mass flow per unit area (left) peaks at Mach 1. A/A* (right) is its reciprocal: every area ratio above 1 has two Mach numbers.", "Drag the area-ratio line on the right to see both roots move.");
    const a = uid(), b = uid();
    const s = surface(w, 0.46, () => draw());
    controls(w, slider(a, "Mach number M:", 0.05, 4, 0.01, 0.6) + slider(b, "area ratio A/A*:", 1, 5, 0.01, 2));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(2) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M = val(a), ar = val(b), Ms = lin(0.02, 4, 300), half = (s.W - 30) / 2;
      const X1 = (m) => 12 + (m / 4) * (half - 10), Y1 = (v) => s.H - 18 - v * (s.H - 34);
      box(g, 12, 8, half - 10, s.H - 26, "M", "ṁ/ṁ_max");
      grid(g, 12, 8, half - 10, s.H - 26, 4, 4);
      plot(g, Ms, Ms.map((m) => G.mass_flux(m) / G.mass_flux(1)), X1, Y1, C.pen, 2.4);
      disc(g, X1(M), Y1(G.mass_flux(M) / G.mass_flux(1)), 5, C.comp);
      g.setLineDash([3, 3]); g.strokeStyle = C.muted; g.beginPath(); g.moveTo(X1(1), 8); g.lineTo(X1(1), s.H - 18); g.stroke(); g.setLineDash([]);
      label(g, "M = 1", X1(1) + 4, 22, C.muted, "left", 11);
      const x2 = half + 22, X2 = (m) => x2 + (m / 4) * (half - 14), Y2 = (v) => s.H - 18 - ((v - 1) / 5) * (s.H - 34);
      box(g, x2, 8, half - 14, s.H - 26, "M", "A/A*");
      grid(g, x2, 8, half - 14, s.H - 26, 4, 5);
      plot(g, Ms, Ms.map((m) => G.A_Astar(m)), X2, Y2, C.pen, 2.4);
      g.strokeStyle = C.gold; g.lineWidth = 1.5; g.beginPath(); g.moveTo(x2, Y2(ar)); g.lineTo(x2 + half - 14, Y2(ar)); g.stroke();
      const r1 = G.M_from_AR(ar, false), r2 = G.M_from_AR(ar, true);
      disc(g, X2(r1), Y2(ar), 5, C.exp); disc(g, X2(r2), Y2(ar), 5, C.comp); disc(g, X2(M), Y2(G.A_Astar(M)), 3.5, C.ink);
      out.innerHTML = `At M = ${M.toFixed(2)}: ṁ is <b>${(100 * G.mass_flux(M) / G.mass_flux(1)).toFixed(1)}%</b> of the choked maximum, A/A* = <b>${f3(G.A_Astar(M))}</b>. A/A* = ${ar.toFixed(2)} has roots M = <b>${f3(r1)}</b> (subsonic) and <b>${f3(r2)}</b> (supersonic).`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 7. Normal shock
  // ====================================================================================
  W.shock = (host) => {
    const w = frame(host, "A normal shock in the shock's frame. Set the upstream Mach number.", "Dot spacing shows density. Try Mₓ below 1: the algebra still produces a 'shock', but its entropy change is negative, which the second law forbids.");
    const a = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "upstream Mach number Mₓ:", 0.6, 5, 0.01, 2));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const Mx = val(a), ok = Mx >= 1;
      const My = G.ns_M2(Mx), pr = G.ns_p2p1(Mx), rr = G.ns_r2r1(Mx), tr = G.ns_T2T1(Mx), p0r = G.ns_p02p01(Mx), ds = -Math.log(p0r);
      const wL = s.W * 0.46, top = 18, bot = s.H * 0.62, mid = 12 + wL / 2;
      g.strokeStyle = C.ink; g.lineWidth = 2; g.beginPath(); g.moveTo(12, top); g.lineTo(12 + wL, top); g.moveTo(12, bot); g.lineTo(12 + wL, bot); g.stroke();
      g.fillStyle = ok ? C.compSoft : C.expSoft; g.fillRect(mid, top, wL / 2, bot - top);
      g.strokeStyle = ok ? C.comp : C.exp; g.lineWidth = 3.5; g.beginPath(); g.moveTo(mid, top); g.lineTo(mid, bot); g.stroke();
      const sp1 = 14, sp2 = sp1 / Math.max(0.2, rr);
      for (let x = 16; x < mid - 2; x += sp1) for (let y = top + 8; y < bot - 4; y += 14) disc(g, x, y, 1.8, C.ink);
      for (let x = mid + 4; x < 12 + wL - 2; x += sp2) for (let y = top + 8; y < bot - 4; y += 14) disc(g, x, y, 1.8, C.ink);
      label(g, `Mₓ = ${Mx.toFixed(2)}`, 16, bot + 16, C.ink, "left", 12, 600); label(g, `M_y = ${f3(My)}`, 12 + wL, bot + 16, C.ink, "right", 12, 600);
      // entropy plot
      const ex = wL + 40, ew = s.W - ex - 10, Ms = lin(0.6, 5, 200), dsv = Ms.map((m) => -Math.log(G.ns_p02p01(m))), Y = (v) => top + (bot - top) * 0.5 - v * ((bot - top) * 0.5) / 1.4, X = (m) => ex + ((m - 0.6) / 4.4) * ew;
      box(g, ex, top, ew, bot - top, "Mₓ", "Δs/R");
      g.fillStyle = C.expSoft; g.fillRect(ex, Y(0), X(1) - ex, top + bot - top - Y(0) + top - top);
      plot(g, Ms, dsv, X, Y, C.pen, 2.2);
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(ex, Y(0)); g.lineTo(ex + ew, Y(0)); g.stroke();
      disc(g, X(Mx), Y(ds), 5, ok ? C.comp : C.exp);
      label(g, "forbidden: Δs < 0", ex + 6, bot - 6, C.exp, "left", 11, 600);
      // ratio bars (log scale)
      const by = bot + 30, bh = s.H - by - 8, bars = [["p₂/p₁", pr], ["T₂/T₁", tr], ["ρ₂/ρ₁", rr], ["p₀₂/p₀₁", p0r]], bwid = (s.W - 24) / bars.length;
      bars.forEach(([n, v], i) => {
        const x = 12 + i * bwid + 8, hgt = Math.max(-bh / 2, Math.min(bh / 2, (Math.log10(v) / Math.log10(30)) * (bh / 2)));
        g.fillStyle = v >= 1 ? C.comp : C.exp; g.fillRect(x, by + bh / 2, bwid - 16, -hgt);
        label(g, `${n} = ${f3(v)}`, x + (bwid - 16) / 2, by + bh / 2 + (hgt > 0 ? 14 : -6), C.ink, "center", 11, 600);
      });
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(12, by + bh / 2); g.lineTo(s.W - 12, by + bh / 2); g.stroke();
      out.innerHTML = ok ? `Entropy rises by <b>${f3(ds)}</b> R; ${(100 * (1 - p0r)).toFixed(1)}% of the stagnation pressure is lost.` : `<b>Impossible:</b> Δs = ${f3(ds)} R < 0. An adiabatic expansion shock would destroy entropy.`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 8. Rocket nozzle: thrust coefficient versus ambient pressure
  // ====================================================================================
  W.rocket = (host, spec) => {
    const optimal = spec.preset === "optimal";
    const w = frame(host, optimal ? "Thrust against nozzle size at a fixed ambient pressure. The peak is where the exit pressure equals ambient." : "One nozzle, flown from sea level to space. Thrust is split into its momentum and pressure parts.",
      "Thrust coefficient C_F = F/(p₀A_t), γ = 1.4. The dashed envelope is a nozzle re-optimised at every ambient pressure (p_e = p_amb).");
    const a = uid(), b = uid();
    const s = surface(w, 0.56, () => draw());
    controls(w, slider(a, "expansion ratio A_e/A_t:", 1, 100, 0.1, optimal ? 12 : 8) + slider(b, "ambient pressure p_amb/p₀:", 0, 0.06, 0.0005, optimal ? 0.01 : 0.0145));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(1), [b]: (v) => v.toFixed(4) });
    const gm = 1.4, Gam = Math.sqrt(gm) * Math.pow(2 / (gm + 1), (gm + 1) / (2 * (gm - 1)));
    // C_F = F/(p0 At) = momentum part Gam*sqrt(2g/(g-1)*(1-(pe/p0)^((g-1)/g))) + pressure part eps*(pe - pamb)/p0
    const cf = (eps, pa) => { const pe = 1 / G.p0_p(G.M_from_AR(eps, true)); return { pe, mom: Gam * Math.sqrt(((2 * gm) / (gm - 1)) * (1 - Math.pow(pe, (gm - 1) / gm))), pres: (pe - pa) * eps }; };
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const eps = val(a), pa = val(b), now = cf(eps, pa), total = now.mom + now.pres;
      const x0 = 34, y0 = 10, w0 = s.W * 0.62, h0 = s.H - 34;
      if (!optimal) {
        const pas = lin(0, 0.06, 160), X = (v) => x0 + (v / 0.06) * w0, Y = (v) => y0 + h0 - ((v - 0.6) / 1.4) * h0;
        box(g, x0, y0, w0, h0, "p_amb/p₀", "C_F");
        grid(g, x0, y0, w0, h0, 6, 5);
        plot(g, pas, pas.map((p) => { const e = p > 0 ? G.A_Astar(G.M_from_p0p(1 / p)) : NaN; return e ? cf(e, p).mom : NaN; }), X, Y, C.muted, 1.4, [5, 4]);
        plot(g, pas, pas.map((p) => { const c = cf(eps, p); return c.mom + c.pres; }), X, Y, C.pen, 2.6);
        disc(g, X(pa), Y(total), 5, C.comp);
        g.setLineDash([2, 3]); g.strokeStyle = C.gold; g.beginPath(); g.moveTo(X(now.pe), y0); g.lineTo(X(now.pe), y0 + h0); g.stroke(); g.setLineDash([]);
        label(g, "design: p_e", X(now.pe) + 4, y0 + 14, C.gold, "left", 11);
      } else {
        const es = lin(1.05, 100, 300).map((e) => Math.exp(Math.log(1.05) + (Math.log(100) - Math.log(1.05)) * ((e - 1.05) / 98.95))), X = (e) => x0 + ((Math.log(e) - Math.log(1.05)) / (Math.log(100) - Math.log(1.05))) * w0, Y = (v) => y0 + h0 - ((v - 0.6) / 1.4) * h0;
        box(g, x0, y0, w0, h0, "A_e/A_t (log)", "C_F");
        plot(g, es, es.map((e) => { const c = cf(e, pa); return c.mom + c.pres; }), X, Y, C.pen, 2.6);
        const eOpt = pa > 0 ? G.A_Astar(G.M_from_p0p(1 / pa)) : 100;
        disc(g, X(Math.min(eOpt, 100)), Y(cf(Math.min(eOpt, 100), pa).mom + cf(Math.min(eOpt, 100), pa).pres), 5, C.ok);
        disc(g, X(eps), Y(total), 5, C.comp);
        label(g, "optimum: p_e = p_amb", X(Math.min(eOpt, 100)) + 6, Y(cf(Math.min(eOpt, 100), pa).mom) - 8, C.ok, "left", 11, 600);
      }
      // thrust split bar
      const bx = x0 + w0 + 30, bw = s.W - bx - 14, base = y0 + h0 * 0.78, scale = (h0 * 0.7) / 2;
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(bx - 4, base); g.lineTo(bx + bw + 2, base); g.stroke();
      g.fillStyle = C.pen; g.fillRect(bx, base - now.mom * scale, bw * 0.45, now.mom * scale);
      g.fillStyle = now.pres >= 0 ? C.comp : C.exp;
      if (now.pres >= 0) g.fillRect(bx + bw * 0.55, base - now.pres * scale, bw * 0.45, now.pres * scale); else g.fillRect(bx + bw * 0.55, base, bw * 0.45, -now.pres * scale);
      label(g, "momentum", bx + bw * 0.22, y0 + h0 + 14, C.ink, "center", 10, 600); label(g, "pressure", bx + bw * 0.78, y0 + h0 + 14, C.ink, "center", 10, 600);
      const state = Math.abs(now.pe - pa) < 0.02 * Math.max(pa, 1e-4) ? "matched" : now.pe > pa ? "underexpanded" : "overexpanded";
      out.innerHTML = `Exit pressure <b>${f3(now.pe)}</b> p₀ against ambient ${f3(pa)} p₀: <span class="regime r-${state === "matched" ? "design" : state}">${state}</span>. C_F = <b>${f3(total)}</b> (momentum ${f3(now.mom)}, pressure ${now.pres >= 0 ? "+" : "−"}${f3(Math.abs(now.pres))}). dF/dA_e ∝ p_e − p_amb = ${now.pe - pa >= 0 ? "+" : "−"}${f3(Math.abs(now.pe - pa))}.`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 9. Supersonic inlet: start, unstart, hysteresis
  // ====================================================================================
  W.inlet = (host) => {
    const w = frame(host, "A fixed-geometry supersonic inlet. Fly faster and slower and watch its state depend on its history.", "Right: the two Kantrowitz curves. Above the starting curve the shock is swallowed; below the isentropic curve the throat is too small for supersonic flow and the inlet unstarts. In between, either state is possible.");
    const a = uid(), b = uid(), rs = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "flight Mach number:", 1, 3, 0.005, 1.2) + slider(b, "throat/inlet area A_t/A_i:", 0.6, 0.99, 0.005, 0.85) + `<button type="button" class="btn quiet" id="${rs}">Reset to subsonic take-off</button>`);
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(3), [b]: (v) => v.toFixed(3) });
    let started = false, trail = [];
    const mdesign = (r) => G.M_from_AR(1 / r, true), mstart = (r) => { if (r <= G.inlet_start_ratio(50)) return Infinity; return G.bisect((m) => G.inlet_start_ratio(m) - r, 1.0001, 50); };
    document.getElementById(rs).addEventListener("click", () => { started = false; trail = []; document.getElementById(a).value = 1.2; document.querySelector(`[data-out="${a}"]`).textContent = "1.200"; draw(); });
    function step() {
      const M = val(a), r = val(b);
      if (!started && M >= mstart(r)) started = true;
      if (started && r < G.inlet_isentropic_ratio(M) - 1e-9) started = false;
      trail.push([M, r, started]); if (trail.length > 400) trail.shift();
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M = val(a), r = val(b);
      // inlet geometry
      const iw = s.W * 0.4, mid = s.H * 0.5, hi = s.H * 0.32, ht = hi * Math.sqrt(r), x1 = s.W * 0.1, xt = x1 + iw * 0.5, x2 = x1 + iw;
      g.strokeStyle = C.ink; g.lineWidth = 3;
      [-1, 1].forEach((sg) => { g.beginPath(); g.moveTo(x1, mid + sg * hi); g.lineTo(xt, mid + sg * ht); g.lineTo(x2, mid + sg * hi * 1.05); g.stroke(); });
      if (started) {
        g.fillStyle = C.expSoft; g.fillRect(x1, mid - hi, xt - x1, 2 * hi);
        const xs = xt + 10; g.strokeStyle = C.comp; g.lineWidth = 3; g.beginPath(); g.moveTo(xs, mid - ht * 1.03); g.lineTo(xs, mid + ht * 1.03); g.stroke();
        label(g, "started: supersonic to the throat", x1, mid - hi - 10, C.ok, "left", 12, 600);
      } else {
        const xs = x1 - 14 - 12 * Math.max(0, 1.6 - M);
        g.strokeStyle = C.comp; g.lineWidth = 3; g.beginPath(); g.moveTo(xs + 10, mid - hi * 1.3); g.quadraticCurveTo(xs - 8, mid, xs + 10, mid + hi * 1.3); g.stroke();
        g.strokeStyle = C.muted; g.lineWidth = 1.2; [-1, 1].forEach((sg) => { g.beginPath(); g.moveTo(xs + 4, mid + sg * hi * 0.8); g.quadraticCurveTo(x1 - 6, mid + sg * hi * 1.2, x1 + 10, mid + sg * hi * 1.5); g.stroke(); });
        label(g, "unstarted: shock disgorged, flow spills", x1 - 30, mid - hi - 10, C.comp, "left", 12, 600);
      }
      for (let k = -2; k <= 2; k++) arrow(g, 4, mid + k * hi * 0.4, 18, mid + k * hi * 0.4, C.muted, 1.3);
      // Kantrowitz plot
      const px = x2 + 24, pw = s.W - px - 12, py = 12, ph = s.H - 34, Ms = lin(1, 3, 200), X = (m) => px + ((m - 1) / 2) * pw, Y = (v) => py + ph - ((v - 0.5) / 0.5) * ph;
      box(g, px, py, pw, ph, "flight M", "A_t/A_i");
      plot(g, Ms, Ms.map((m) => G.inlet_isentropic_ratio(m)), X, Y, C.pen, 2);
      plot(g, Ms, Ms.map((m) => G.inlet_start_ratio(m)), X, Y, C.comp, 2);
      label(g, "isentropic", X(2.7), Y(G.inlet_isentropic_ratio(2.7)) + 14, C.pen, "center", 10, 600);
      label(g, "starting", X(2.7), Y(G.inlet_start_ratio(2.7)) - 6, C.comp, "center", 10, 600);
      trail.forEach(([m, rr, st]) => disc(g, X(m), Y(rr), 1.6, st ? C.ok : C.comp));
      disc(g, X(M), Y(r), 5.5, started ? C.ok : C.comp, C.card);
      const md = mdesign(r), ms = mstart(r);
      out.innerHTML = `<span class="regime ${started ? "r-design" : "r-shock"}">${started ? "Started" : "Unstarted"}</span> Design Mach number <b>${f3(md)}</b>; starting by overspeed needs Mach <b>${isFinite(ms) ? f3(ms) : "∞ (beyond the Kantrowitz limit)"}</b>.`;
    }
    rerun(w, () => { step(); draw(); }); step(); draw();
  };

  // ====================================================================================
  // 10. Train in a tunnel
  // ====================================================================================
  W.train = (host) => {
    const w = frame(host, "A train enters a tunnel. Set its speed and how much bigger the tunnel is than the train.", "With a tight tunnel the train is a piston; with a gap, air squeezes past (the gap flow chokes) and the shock weakens; with a big enough gap, no shock forms in this model. Air at 300 K, c = 348 m/s.");
    const a = uid(), b = uid();
    const s = surface(w, 0.42, () => {});
    controls(w, slider(a, "train speed (m/s):", 40, 160, 1, 83) + slider(b, "tunnel/train area:", 1, 2.2, 0.01, 1));
    const out = readout(w);
    bindOut(w, { [a]: (v) => `${v} (${(v * 3.6).toFixed(0)} km/h)`, [b]: (v) => v.toFixed(2) });
    const c0 = Math.sqrt(1.4 * (8314 / 28.8) * 300);
    function solve(Vt, ratio) {
      const Mt = Vt / c0, noShock = 1 / (1 - 1 / G.A_Astar(Mt));
      if (ratio >= noShock) return { Ms: 1, none: true, noShock };
      if (ratio <= 1.0001) return { Ms: G.piston_shock_mach(Vt / c0), noShock };
      const f = (Ms) => {
        const vp = G.piston_speed(Ms) * c0, Ty = 300 * G.ns_T2T1(Ms), cy = Math.sqrt(1.4 * (8314 / 28.8) * Ty), Mapp = Math.max(1e-4, (Vt - vp) / cy);
        return (1 - 1 / G.A_Astar(Math.min(Mapp, 1))) - 1 / ratio;
      };
      const hi = G.piston_shock_mach(Vt / c0);
      const Ms = f(1.00001) * f(hi) > 0 ? hi : G.bisect(f, 1.00001, hi);
      return { Ms, noShock };
    }
    let t = 0;
    function draw(dt) {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const Vt = val(a), ratio = val(b), r = solve(Vt, ratio), dp = r.none ? 0 : G.ns_p2p1(r.Ms) - 1, psi = dp * 14.696;
      if (dt !== undefined && !reduce) t = (t + dt * 0.25) % 1; else t = 0.6;
      const top = 18, bot = s.H - 40, x0 = s.W * 0.18, L = s.W - x0 - 10, trainH = (bot - top) / Math.sqrt(ratio);
      g.fillStyle = C.rule; g.fillRect(x0, top - 6, L, 6); g.fillRect(x0, bot, L, 6);
      const tx = x0 - 40 + t * L * 0.55, sx = x0 + (tx - x0 + 40) * (r.none ? 1 : r.Ms * c0 / Vt) * 0.55 + 10;
      g.fillStyle = C.ink; g.beginPath(); g.moveTo(tx - 160, bot - trainH); g.lineTo(tx - 10, bot - trainH); g.quadraticCurveTo(tx + 28, bot - trainH, tx + 34, bot); g.lineTo(tx - 160, bot); g.closePath(); g.fill();
      if (!r.none) {
        const shx = Math.min(x0 + L - 4, Math.max(tx + 40, sx));
        g.fillStyle = C.compSoft; g.fillRect(tx + 34, top, shx - tx - 34, bot - top);
        g.strokeStyle = C.comp; g.lineWidth = 3.5; g.beginPath(); g.moveTo(shx, top); g.lineTo(shx, bot); g.stroke();
        label(g, `shock, Mach ${f3(r.Ms)}`, shx - 4, top + 14, C.comp, "right", 11, 600);
      }
      label(g, "portal", x0, bot + 22, C.muted, "center", 11);
      const lvl = psi < 3 ? "below the 3 psi minor-damage limit" : psi < 5 ? "above 3 psi: temporary hearing damage likely" : "above 5 psi: risk of permanent hearing damage";
      out.innerHTML = r.none ? `No shock in this model: the gap can pass all the air the train pushes (needs a tunnel at least <b>${f3(r.noShock)}</b>× the train's area at this speed).` :
        `Shock Mach <b>${f3(r.Ms)}</b>, overpressure <b>${(100 * dp).toFixed(1)}%</b> (${psi.toFixed(1)} psi): ${lvl}. A shock-free tunnel needs ${f3(r.noShock)}× the train area.`;
    }
    if (reduce) { draw(); rerun(w, () => draw()); } else loop((dt) => draw(dt));
  };

  // ====================================================================================
  // 11. T–s diagram: Fanno and Rayleigh lines
  // ====================================================================================
  W.ts = (host, spec) => {
    const fanno = spec.preset !== "rayleigh";
    const w = frame(host, fanno ? "The Fanno line on a T–s diagram: every state reachable by friction from this inlet. Add pipe length." : "The Rayleigh line: every state reachable by heating or cooling from this inlet. Add heat.",
      "Both lines peak in entropy at Mach 1 (marked). The second law only lets friction move the state toward higher entropy, so friction always drives toward Mach 1 and can't pass it. Heating also moves right; cooling moves left, which is why only cooling can take a sonic flow further.");
    const a = uid(), b = uid();
    const s = surface(w, 0.6, () => draw());
    controls(w, slider(a, "inlet Mach number M₁:", 0.1, 3, 0.01, fanno ? 0.4 : 0.3) + slider(b, fanno ? "friction added, 4fL/D:" : "heat added, Δ(T₀/T₀*):", fanno ? 0 : -0.3, fanno ? 3 : 0.6, 0.001, fanno ? 0.6 : 0.2));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(3) });
    const gm = 1.4;
    const fannoS = (M) => -Math.log(G.fanno_p0(M)) * ((gm - 1) / gm);  // (s - s*)/cp
    const rayS = (M) => Math.log(G.ray_T(M)) - ((gm - 1) / gm) * Math.log(G.ray_p(M));
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M1 = val(a), amt = val(b), sup = M1 > 1;
      const Ms = lin(0.12, 3, 300), x0 = 40, y0 = 10, w0 = s.W - 54, h0 = s.H - 34;
      const X = (v) => x0 + ((v + 1.2) / 1.25) * w0, Y = (v) => y0 + h0 - ((v - 0.2) / 1.2) * h0;
      box(g, x0, y0, w0, h0, "(s − s*)/c_p", "T/T*");
      grid(g, x0, y0, w0, h0, 5, 6);
      plot(g, Ms, Ms.map(fannoS), (v) => 0, () => 0, C.ink, 0);
      const fx = Ms.map(fannoS), fy = Ms.map((m) => G.fanno_T(m)), rx = Ms.map(rayS), ry = Ms.map((m) => G.ray_T(m));
      const drawLine = (xs2, ys2, col, wdt) => { g.strokeStyle = col; g.lineWidth = wdt; g.beginPath(); xs2.forEach((v, i) => (i ? g.lineTo(X(v), Y(ys2[i])) : g.moveTo(X(v), Y(ys2[i])))); g.stroke(); };
      drawLine(fx, fy, fanno ? C.pen : C.rule, fanno ? 2.6 : 1.5); drawLine(rx, ry, fanno ? C.rule : C.comp, fanno ? 1.5 : 2.6);
      label(g, "Fanno", X(fannoS(0.2)) + 4, Y(G.fanno_T(0.2)) - 4, fanno ? C.pen : C.muted, "left", 11, 600);
      label(g, "Rayleigh", X(rayS(0.3)) + 4, Y(G.ray_T(0.3)) + 14, fanno ? C.muted : C.comp, "left", 11, 600);
      disc(g, X(0), Y(1), 4, C.gold); label(g, "M = 1", X(0) + 6, Y(1) - 6, C.gold, "left", 11, 600);
      let M2, choked = false;
      if (fanno) { const fl = G.fanno_fL(M1) - amt; if (fl <= 0) { choked = true; M2 = 1; } else M2 = G.fanno_M(fl, sup); }
      else { const t0 = G.ray_T0(M1) + amt; if (t0 >= 1) { choked = true; M2 = 1; } else if (t0 <= 0.02) M2 = sup ? 50 : 0.12; else M2 = G.ray_M(t0, sup); }
      const sx = fanno ? fannoS : rayS, ty = fanno ? G.fanno_T : G.ray_T;
      disc(g, X(sx(M1)), Y(ty(M1)), 5, C.ink); disc(g, X(sx(M2)), Y(ty(M2)), 6, choked ? C.comp : C.ok, C.card);
      arrow(g, X(sx(M1)), Y(ty(M1)), X(sx(M2)), Y(ty(M2)), C.ink, 1.2);
      out.innerHTML = choked ? `<b>Choked.</b> The flow reaches Mach 1 before the end: ${fanno ? (sup ? "a shock must form in the duct" : "the inlet Mach number and mass flow must drop") : (sup ? "a shock must form upstream of the heater" : "the inlet Mach number and mass flow must drop")}.` :
        `M: ${f3(M1)} → <b>${f3(M2)}</b>. T/T*: ${f3(ty(M1))} → ${f3(ty(M2))}. ${fanno ? `p₀ falls by ${(100 * (1 - G.fanno_p0(M2) / G.fanno_p0(M1))).toFixed(1)}%.` : amt < 0 ? "Cooling: the state moves left, away from Mach 1." : "Heating: the state moves toward Mach 1."}`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 12. Wedge: oblique shock, δ–σ–M curve, detachment
  // ====================================================================================
  W.wedge = (host) => {
    const w = frame(host, "Supersonic flow meets a wedge. Change the Mach number and the wedge angle.", "Right: deflection δ against shock angle σ for this Mach number. Each δ below the peak has a weak and a strong solution; above the peak there's none, and the shock detaches into a curved bow shock standing off the nose.");
    const a = uid(), b = uid(), st = uid();
    const s = surface(w, 0.5, () => draw());
    controls(w, slider(a, "Mach number M₁:", 1.1, 6, 0.01, 3) + slider(b, "wedge angle δ (°):", 0, 50, 0.1, 10) + check(st, "show the strong solution", false));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(1) + "°" });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M = val(a), d = val(b), strong = on(st), [dmax, smax] = G.ob_max(M);
      const ww = s.W * 0.5, base = s.H - 24, ax = 36;
      const r = d <= dmax ? G.ob_after(M, d, strong) : null;
      // flow arrows
      for (let k = 0; k < 6; k++) arrow(g, 6, 18 + k * ((base - 30) / 6), 28, 18 + k * ((base - 30) / 6), C.muted, 1.2);
      // wedge
      g.fillStyle = C.ink; g.beginPath(); g.moveTo(ax + 30, base); g.lineTo(ww, base - (ww - ax - 30) * Math.tan(d * D)); g.lineTo(ww, base); g.closePath(); g.fill();
      if (r) {
        const sg = r.sigma * D, len = (ww - ax - 30) / Math.cos(sg);
        g.fillStyle = C.compSoft; g.beginPath(); g.moveTo(ax + 30, base); g.lineTo(ax + 30 + len * Math.cos(sg), base - len * Math.sin(sg)); g.lineTo(ww, base - (ww - ax - 30) * Math.tan(d * D)); g.closePath(); g.fill();
        g.strokeStyle = C.comp; g.lineWidth = 3; g.beginPath(); g.moveTo(ax + 30, base); g.lineTo(ax + 30 + len * Math.cos(sg), base - len * Math.sin(sg)); g.stroke();
        // a few streamlines turning at the shock
        g.strokeStyle = C.pen; g.lineWidth = 1.1;
        for (let k = 1; k <= 4; k++) {
          const y = base - k * (base - 30) / 5.5, xHit = ax + 30 + (base - y) / Math.tan(sg);
          if (xHit > ww) continue;
          g.beginPath(); g.moveTo(28, y); g.lineTo(xHit, y); g.lineTo(ww, y - (ww - xHit) * Math.tan(d * D)); g.stroke();
        }
      } else {
        g.strokeStyle = C.comp; g.lineWidth = 3; g.beginPath(); g.moveTo(ax + 60, 12); g.quadraticCurveTo(ax - 6, base - 10, ax + 18, base); g.stroke();
        label(g, "detached bow shock", ax + 64, 24, C.comp, "left", 12, 600);
      }
      // delta-sigma plot
      const px = ww + 30, pw = s.W - px - 10, py = 10, ph = s.H - 34, X = (sg) => px + (sg / 90) * pw, Y = (dd) => py + ph - (dd / 50) * ph;
      box(g, px, py, pw, ph, "σ (°)", "δ (°)");
      grid(g, px, py, pw, ph, 6, 5);
      [1.5, 2, 3, 5].forEach((Mm) => { if (Math.abs(Mm - M) < 0.05) return; const sgs = lin(Math.asin(1 / Mm) / D + 0.01, 90, 120); plot(g, sgs, sgs.map((x) => G.ob_delta(Mm, x)), X, Y, C.rule, 1); });
      const sgs = lin(Math.asin(1 / M) / D + 0.001, 90, 200);
      plot(g, sgs, sgs.map((x) => G.ob_delta(M, x)), X, Y, C.pen, 2.4);
      g.setLineDash([3, 3]); g.strokeStyle = C.gold; g.beginPath(); g.moveTo(px, Y(d)); g.lineTo(px + pw, Y(d)); g.stroke(); g.setLineDash([]);
      disc(g, X(smax), Y(dmax), 3.5, C.gold);
      if (r) disc(g, X(r.sigma), Y(d), 5.5, C.comp, C.card);
      out.innerHTML = r ? `${strong ? "Strong" : "Weak"} shock at σ = <b>${f3(r.sigma)}°</b>; M₂ = <b>${f3(r.M2)}</b> (${r.M2 < 1 ? "subsonic" : "supersonic"}), p₂/p₁ = <b>${f3(r.p2p1)}</b>, p₀ recovery ${f3(r.p02p01)}. δ_max at this Mach number is ${f3(dmax)}°.` :
        `<b>Detached:</b> ${d.toFixed(1)}° exceeds δ_max = ${f3(dmax)}° at Mach ${M.toFixed(2)}.`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 13. Shock polars: regular or Mach reflection
  // ====================================================================================
  W.polar = (host, spec) => {
    const w = frame(host, "Shock polars for an oblique shock reflecting off a wall. Increase the incident deflection until regular reflection becomes impossible.", "Blue loop: every shock the free stream could pass through. Red loop: every shock the flow behind the incident shock could pass through, turning back toward the wall. Regular reflection is where the red loop reaches δ = 0; if it can't, the Mach-reflection triple point sits where the red loop crosses the blue loop's strong branch.");
    const a = uid(), b = uid();
    const s = surface(w, 0.62, () => draw());
    controls(w, slider(a, "free-stream Mach M₁:", 1.6, 5, 0.01, 3) + slider(b, "incident deflection δ₁ (°):", 1, 34, 0.1, spec.preset === "mach" ? 30 : 10));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(1) + "°" });
    function polar(M, p0, d0, dir) {
      const pts = [];
      for (const sg of lin(Math.asin(1 / M) / D + 0.02, 89.98, 220)) { const dd = G.ob_delta(M, sg), Mn = M * Math.sin(sg * D); pts.push([d0 + dir * dd, p0 * G.ns_p2p1(Mn), sg]); }
      return pts;
    }
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      let M = val(a), d1 = val(b);
      const [dm] = G.ob_max(M);
      if (d1 > dm - 0.05) d1 = dm - 0.05;
      const inc = G.ob_after(M, d1), p2 = inc.p2p1, M2 = inc.M2;
      const P1 = polar(M, 1, 0, 1).concat(polar(M, 1, 0, -1).reverse()), P2 = polar(M2, p2, d1, -1);
      const pmax = G.ns_p2p1(M) * 1.15, pmax2 = Math.max(...P2.map((q) => q[1])) * 1.05, top = Math.max(pmax, Math.min(pmax2, pmax * 3));
      const x0 = 44, y0 = 10, w0 = s.W - 56, h0 = s.H - 34, dlim = Math.max(dm, d1 + G.ob_max(M2)[0]) + 5;
      const X = (d) => x0 + ((d + dlim) / (2 * dlim)) * w0, Y = (p) => y0 + h0 - ((p - 1) / (top - 1)) * h0;
      box(g, x0, y0, w0, h0, "flow deflection δ (°)", "p/p₁");
      g.strokeStyle = C.rule; g.beginPath(); g.moveTo(X(0), y0); g.lineTo(X(0), y0 + h0); g.stroke();
      const line = (pts, col, wdt) => { g.strokeStyle = col; g.lineWidth = wdt; g.beginPath(); pts.forEach(([d, p], i) => (i ? g.lineTo(X(d), Y(p)) : g.moveTo(X(d), Y(p)))); g.stroke(); };
      line(P1, C.exp, 2.4); line(P2, C.comp, 2.4);
      disc(g, X(d1), Y(p2), 5, C.ink);
      // regular reflection: P2 crossing delta = 0 on its weak side
      let reg = null;
      for (let i = 1; i < P2.length; i++) if ((P2[i - 1][0] - 0) * (P2[i][0] - 0) <= 0) { reg = P2[i - 1]; break; }
      let mach = null;
      if (!reg) {
        // intersection of P2 with the strong branch of P1 (positive delta side, sigma beyond the maximum)
        const smaxM = G.ob_max(M)[1], strongP1 = polar(M, 1, 0, 1).filter((q) => q[2] >= smaxM);
        for (let i = 1; i < P2.length && !mach; i++) for (let j = 1; j < strongP1.length; j++) {
          const [a1, b1] = P2[i - 1], [a2, b2] = P2[i], [c1, d1b] = strongP1[j - 1], [c2, d2] = strongP1[j];
          const den = (a2 - a1) * (d2 - d1b) - (b2 - b1) * (c2 - c1); if (Math.abs(den) < 1e-12) continue;
          const t = ((c1 - a1) * (d2 - d1b) - (d1b - b1) * (c2 - c1)) / den, u = ((c1 - a1) * (b2 - b1) - (d1b - b1) * (a2 - a1)) / den;
          if (t >= 0 && t <= 1 && u >= 0 && u <= 1) { mach = [a1 + t * (a2 - a1), b1 + t * (b2 - b1)]; break; }
        }
      }
      if (reg) { disc(g, X(0), Y(reg[1]), 6, C.ok, C.card); label(g, "regular reflection", X(0) + 8, Y(reg[1]) - 6, C.ok, "left", 12, 600); }
      if (mach) { disc(g, X(mach[0]), Y(mach[1]), 6, C.gold, C.card); label(g, "Mach reflection: triple point", X(mach[0]) + 8, Y(mach[1]) + 16, C.gold, "left", 12, 600); }
      label(g, "incident / Mach stem polar", X(-dm * 0.9), Y(G.ns_p2p1(M) * 0.55), C.exp, "left", 11, 600);
      out.innerHTML = reg ? `Incident shock leaves Mach ${f3(M2)} at ${f3(p2)} p₁. A reflected shock of ${d1.toFixed(1)}° brings the flow back parallel to the wall at <b>${f3(reg[1])}</b> p₁.` :
        `Behind the incident shock (Mach ${f3(M2)}) the flow can turn at most ${f3(G.ob_max(M2)[0])}°, less than ${d1.toFixed(1)}°: <b>no regular reflection</b>. ${mach ? `Mach stem deflection ${f3(mach[0])}°, reflected shock ${f3(d1 - mach[0])}°, pressure ${f3(mach[1])} p₁.` : ""}`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 14. Prandtl–Meyer expansion fan
  // ====================================================================================
  W.pmfan = (host) => {
    const w = frame(host, "Supersonic flow along a wall that turns away. The corner spreads an expansion fan.", "The fan starts at the upstream Mach angle and ends at the downstream Mach angle, measured from the new flow direction. Streamlines bend smoothly through it: isentropic, no losses.");
    const a = uid(), b = uid();
    const s = surface(w, 0.55, () => draw());
    controls(w, slider(a, "upstream Mach M₁:", 1.01, 4, 0.01, 2) + slider(b, "turning angle θ (°):", 0, 60, 0.1, 15));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(1) + "°" });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M1 = val(a), th = val(b), nu1 = G.pm_nu(M1), nmax = G.nu_max();
      const over = nu1 + th >= nmax - 0.01, M2 = over ? Infinity : G.pm_M(nu1 + th);
      const cx = s.W * 0.42, cy = s.H * 0.55, L = s.W;
      const mu1 = Math.asin(1 / M1), mu2 = over ? 0 : Math.asin(1 / M2), t = th * D;
      // wall
      g.fillStyle = C.ink; g.beginPath(); g.moveTo(0, cy); g.lineTo(cx, cy); g.lineTo(cx + L * Math.cos(t), cy + L * Math.sin(t)); g.lineTo(0, s.H + 10); g.closePath(); g.globalAlpha = 0.9; g.fill(); g.globalAlpha = 1;
      // fan
      g.fillStyle = C.expSoft; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + L * Math.cos(-mu1) * -1 * -1, cy - L * Math.sin(mu1)); g.lineTo(cx + L * Math.cos(-(mu2 - t)), cy - L * Math.sin(mu2 - t)); g.closePath(); g.fill();
      g.strokeStyle = C.exp; g.lineWidth = 1.3;
      for (let k = 0; k <= 8; k++) {
        const thk = (th * k) / 8, Mk = nu1 + thk >= nmax - 0.01 ? 50 : G.pm_M(nu1 + thk), ang = Math.asin(1 / Mk) - thk * D;
        g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + L * Math.cos(ang), cy - L * Math.sin(ang)); g.stroke();
      }
      // streamlines
      g.strokeStyle = C.pen; g.lineWidth = 1.4;
      for (let k = 1; k <= 4; k++) {
        const h = k * 26; g.beginPath(); g.moveTo(0, cy - h);
        const xA = cx + h / Math.tan(mu1); g.lineTo(xA, cy - h);
        let x = xA, y = cy - h, r = Math.hypot(x - cx, y - cy);
        for (let j = 1; j <= 24; j++) { const thk = (th * j) / 24, Mk = nu1 + thk >= nmax - 0.01 ? 50 : G.pm_M(nu1 + thk), ang = Math.asin(1 / Mk) - thk * D; const rr = r * (Math.sin(mu1) / Math.sin(Math.asin(1 / Mk))); x = cx + rr * Math.cos(ang); y = cy - rr * Math.sin(ang); g.lineTo(x, y); }
        g.lineTo(x + L * Math.cos(t), y + L * Math.sin(t)); g.stroke();
      }
      out.innerHTML = over ? `<b>Too far:</b> ν(M₁) + θ exceeds ν_max = ${nmax.toFixed(2)}°. The flow can't follow the wall; a vacuum region forms.` :
        `ν(M₁) = ${f3(nu1)}°, ν(M₂) = ${f3(nu1 + th)}° → M₂ = <b>${f3(M2)}</b>, p₂/p₁ = <b>${f3(G.p0_p(M1) / G.p0_p(M2))}</b>, T₂/T₁ = ${f3(G.T0_T(M1) / G.T0_T(M2))}. Fan from ${f3(mu1 / D)}° to ${f3(mu2 / D - th)}° above the original flow direction.`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 15. Method of characteristics in a channel with an expansive corner
  // ====================================================================================
  W.moc = (host) => {
    const w = frame(host, "A characteristics net, computed live: uniform supersonic flow, the upper wall turns away at a corner, the lower boundary is a straight wall (or centreline).", "Each fan wave carries C_I = ν + θ; each wave reflected off the lower wall carries C_II = ν − θ. Where they cross, ν and θ follow by adding and subtracting: the unit process. Colour is Mach number.");
    const a = uid(), b = uid(), c = uid();
    const s = surface(w, 0.58, () => draw());
    controls(w, slider(a, "inlet Mach M₁:", 1.05, 3, 0.01, 1.5) + slider(b, "wall turn θ_w (°):", 2, 20, 0.5, 12) + slider(c, "characteristics:", 3, 14, 1, 7));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2), [b]: (v) => v.toFixed(1) + "°" });
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M1 = val(a), tw = val(b), n = val(c), nu1 = G.pm_nu(M1), H = 1;
      // fan waves i = 1..n with theta_i (flow angle behind wave i, upward positive)
      const thI = (i) => (tw * i) / n, CI = (i) => nu1 + 2 * thI(i), CII = (j) => nu1 + 2 * thI(j);
      const node = {};
      const st = (nu, th) => { const M = G.pm_M(nu); return { nu, th, M, mu: Math.asin(1 / M) / D }; };
      const corner = { x: 0, y: H };
      const inter = (P, angP, Q, angQ) => { const tp = Math.tan(angP * D), tq = Math.tan(angQ * D), x = (Q.y - P.y + tp * P.x - tq * Q.x) / (tp - tq); return { x, y: P.y + tp * (x - P.x) }; };
      for (let i = 1; i <= n; i++) {
        for (let j = 1; j <= i; j++) {
          let S, pos;
          if (j === i) { S = st(CI(i), 0); const prev = j === 1 ? corner : node[`${i},${j - 1}`], prevS = j === 1 ? st(nu1 + thI(i), thI(i)) : prev.s; const ang = ((prevS.th - prevS.mu) + (S.th - S.mu)) / 2; pos = { x: prev.x + (0 - prev.y) / Math.tan(ang * D), y: 0 }; }
          else {
            S = st((CI(i) + CII(j)) / 2, (CI(i) - CII(j)) / 2);
            const P = j === 1 ? corner : node[`${i},${j - 1}`], Ps = j === 1 ? st(nu1 + thI(i), thI(i)) : P.s, Q = node[`${i - 1},${j}`];
            pos = inter(P, ((Ps.th - Ps.mu) + (S.th - S.mu)) / 2, Q, ((Q.s.th + Q.s.mu) + (S.th + S.mu)) / 2);
          }
          node[`${i},${j}`] = { x: pos.x, y: pos.y, s: S };
        }
      }
      // upper-wall points for each reflected wave j after crossing all fan waves
      const wallPts = [];
      for (let j = 1; j <= n; j++) {
        const P = node[`${n},${j}`], S = st(CII(j) + tw, tw), ang = ((P.s.th + P.s.mu) + (S.th + S.mu)) / 2, tp = Math.tan(ang * D), tq = Math.tan(tw * D);
        const x = (H - P.y + tp * P.x) / (tp - tq); wallPts.push({ x, y: H + tq * x, s: S, from: P });
      }
      const allX = Object.values(node).map((p) => p.x).concat(wallPts.map((p) => p.x)), xmax = Math.max(...allX) * 1.08, ymax = H + Math.tan(tw * D) * xmax;
      const pad = 16, sc = Math.min((s.W - 2 * pad) / (xmax + 0.6), (s.H - 2 * pad) / (ymax * 1.05)), X = (x) => pad + (x + 0.6) * sc, Y = (y) => s.H - pad - y * sc;
      g.strokeStyle = C.ink; g.lineWidth = 3;
      g.beginPath(); g.moveTo(X(-0.6), Y(H)); g.lineTo(X(0), Y(H)); g.lineTo(X(xmax), Y(H + Math.tan(tw * D) * xmax)); g.stroke();
      g.beginPath(); g.moveTo(X(-0.6), Y(0)); g.lineTo(X(xmax), Y(0)); g.stroke();
      const Mmax = Math.max(...Object.values(node).map((p) => p.s.M), ...wallPts.map((p) => p.s.M));
      const colM = (M) => mix(C.pen, C.exp, (M - M1) / Math.max(1e-6, Mmax - M1));
      g.lineWidth = 1.2;
      for (let i = 1; i <= n; i++) {
        g.strokeStyle = C.comp; g.globalAlpha = 0.7; g.beginPath(); g.moveTo(X(0), Y(H));
        for (let j = 1; j <= i; j++) g.lineTo(X(node[`${i},${j}`].x), Y(node[`${i},${j}`].y));
        g.stroke(); g.globalAlpha = 1;
      }
      for (let j = 1; j <= n; j++) {
        g.strokeStyle = C.exp; g.globalAlpha = 0.7; g.beginPath(); g.moveTo(X(node[`${j},${j}`].x), Y(0));
        for (let i = j + 1; i <= n; i++) g.lineTo(X(node[`${i},${j}`].x), Y(node[`${i},${j}`].y));
        g.lineTo(X(wallPts[j - 1].x), Y(wallPts[j - 1].y)); g.stroke(); g.globalAlpha = 1;
      }
      Object.values(node).forEach((p) => disc(g, X(p.x), Y(p.y), 3.2, colM(p.s.M)));
      wallPts.forEach((p) => disc(g, X(p.x), Y(p.y), 3.2, colM(p.s.M)));
      const last = node[`${n},${n}`];
      out.innerHTML = `${Object.keys(node).length + wallPts.length} unit processes. Mach number rises from <b>${f3(M1)}</b> to <b>${f3(Mmax)}</b> where the last fan wave meets the lower wall (ν = ${f3(last.s.nu)}° = ν₁ + 2θ_w): the reflection doubles the turning.`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 16. Bernoulli versus compressible
  // ====================================================================================
  W.compress = (host) => {
    const w = frame(host, "How wrong is Bernoulli? The percent by which ½ρV² underestimates p₀ − p, against Mach number.", "The exact isentropic result is above the incompressible one at every Mach number: the binomial series 1 + M²/4 + … The rule of thumb 'incompressible below Mach 0.3' is the 2% point.");
    const a = uid();
    const s = surface(w, 0.42, () => draw());
    controls(w, slider(a, "Mach number M:", 0.01, 1.5, 0.01, 0.3));
    const out = readout(w);
    bindOut(w, { [a]: (v) => v.toFixed(2) });
    const err = (M) => 100 * ((G.p0_p(M) - 1) / (0.7 * M * M) - 1);
    function draw() {
      const g = s.g; colors(); g.clearRect(0, 0, s.W, s.H);
      const M = val(a), Ms = lin(0.01, 1.5, 200), x0 = 40, y0 = 10, w0 = s.W - 52, h0 = s.H - 34, X = (m) => x0 + (m / 1.5) * w0, Y = (v) => y0 + h0 - (v / 70) * h0;
      box(g, x0, y0, w0, h0, "M", "error %");
      grid(g, x0, y0, w0, h0, 6, 7);
      g.fillStyle = C.expSoft; g.fillRect(x0, y0, X(0.3) - x0, h0);
      label(g, "≈ incompressible", x0 + 4, y0 + h0 - 6, C.exp, "left", 11, 600);
      plot(g, Ms, Ms.map(err), X, Y, C.comp, 2.6);
      plot(g, Ms, Ms.map((m) => 100 * (m * m / 4)), X, Y, C.muted, 1.2, [4, 4]);
      disc(g, X(M), Y(err(M)), 5, C.comp);
      out.innerHTML = `At Mach ${M.toFixed(2)}, Bernoulli underestimates p₀ − p by <b>${err(M).toFixed(2)}%</b> (first-order estimate M²/4 = ${(25 * M * M).toFixed(2)}%).${M > 1 ? " Supersonic: with a shock in front of a probe it's worse still." : ""}`;
    }
    rerun(w, draw); draw();
  };

  // ====================================================================================
  // 17. Gas tables calculator
  // ====================================================================================
  const TABLES = {
    isentropic: { name: "Isentropic", inputs: [["M", "Mach number M"], ["AR_sub", "A/A* (subsonic)"], ["AR_sup", "A/A* (supersonic)"], ["p", "p/p₀"], ["T", "T/T₀"]],
      solve: (k, v, g) => k === "M" ? v : k === "AR_sub" ? G.M_from_AR(v, false, g) : k === "AR_sup" ? G.M_from_AR(v, true, g) : k === "p" ? G.M_from_p0p(1 / v, g) : Math.sqrt((2 / (g - 1)) * (1 / v - 1)),
      rows: (M, g) => [["M", M], ["T/T₀", 1 / G.T0_T(M, g)], ["p/p₀", 1 / G.p0_p(M, g)], ["ρ/ρ₀", 1 / G.r0_r(M, g)], ["A/A*", G.A_Astar(M, g)], ["ṁ/ṁ_max", G.mass_flux(M, g) / G.mass_flux(1, g)], ["Mach angle μ (°)", M > 1 ? G.mach_angle(M) : NaN], ["ν (°)", M >= 1 ? G.pm_nu(M, g) : NaN]] },
    shock: { name: "Normal shock", inputs: [["M", "upstream Mₓ"], ["p0r", "p₀y/p₀ₓ"]],
      solve: (k, v, g) => k === "M" ? v : G.bisect((m) => G.ns_p02p01(m, g) - v, 1, 50),
      rows: (M, g) => M < 1 ? [["Mₓ", M], ["note", NaN]] : [["Mₓ", M], ["M_y", G.ns_M2(M, g)], ["p_y/pₓ", G.ns_p2p1(M, g)], ["T_y/Tₓ", G.ns_T2T1(M, g)], ["ρ_y/ρₓ", G.ns_r2r1(M, g)], ["p₀y/p₀ₓ", G.ns_p02p01(M, g)], ["p₀y/pₓ (pitot)", G.pitot_ratio(M, g)], ["Δs/R", -Math.log(G.ns_p02p01(M, g))]] },
    fanno: { name: "Fanno", inputs: [["M", "Mach number M"], ["fl_sub", "4fL*/D (subsonic)"], ["fl_sup", "4fL*/D (supersonic)"]],
      solve: (k, v, g) => k === "M" ? v : G.fanno_M(v, k === "fl_sup", g),
      rows: (M, g) => [["M", M], ["4fL*/D", G.fanno_fL(M, g)], ["T/T*", G.fanno_T(M, g)], ["p/p*", G.fanno_p(M, g)], ["p₀/p₀*", G.fanno_p0(M, g)], ["V/V*", M * Math.sqrt(G.fanno_T(M, g))]] },
    rayleigh: { name: "Rayleigh", inputs: [["M", "Mach number M"], ["t0_sub", "T₀/T₀* (subsonic)"], ["t0_sup", "T₀/T₀* (supersonic)"]],
      solve: (k, v, g) => k === "M" ? v : G.ray_M(v, k === "t0_sup", g),
      rows: (M, g) => [["M", M], ["T₀/T₀*", G.ray_T0(M, g)], ["T/T*", G.ray_T(M, g)], ["p/p*", G.ray_p(M, g)], ["p₀/p₀*", G.ray_p0(M, g)], ["V/V*", Math.pow(M, 2) * G.ray_p(M, g)]] },
    oblique: { name: "Oblique shock", inputs: [["delta", "deflection δ (°), with M₁ below"]], two: true,
      rows: (M, g, d) => { const r = G.ob_after(M, d, false, g), rs = G.ob_after(M, d, true, g), [dm, sm] = G.ob_max(M, g); return r ? [["σ weak (°)", r.sigma], ["M₂ weak", r.M2], ["p₂/p₁ weak", r.p2p1], ["p₀₂/p₀₁ weak", r.p02p01], ["σ strong (°)", rs.sigma], ["M₂ strong", rs.M2], ["δ_max (°)", dm], ["σ at δ_max (°)", sm]] : [["detached: δ_max (°)", dm]]; } },
    pm: { name: "Prandtl–Meyer", inputs: [["M", "Mach number M"], ["nu", "ν (°)"]],
      solve: (k, v, g) => k === "M" ? v : G.pm_M(v, g),
      rows: (M, g) => [["M", M], ["ν (°)", G.pm_nu(M, g)], ["μ (°)", G.mach_angle(M)], ["p/p₀", 1 / G.p0_p(M, g)], ["ν_max (°)", G.nu_max(g)]] },
  };
  W.tables = (host, spec) => {
    const only = spec.preset && spec.preset !== "all" ? (spec.preset === "area" ? "isentropic" : spec.preset) : null;
    const keys = only ? [only] : Object.keys(TABLES);
    const w = frame(host, only ? `${TABLES[only].name} relations: type any one quantity to get the rest.` : "Gas tables: pick a relation, choose what you know, and read every ratio.");
    w.classList.add("tables-widget");
    const tb = uid(), inp = uid(), v = uid(), gm = uid(), m1 = uid();
    controls(w, (only ? "" : select(tb, "relation", keys.map((k) => [k, TABLES[k].name]))) + `<label for="${inp}">I know<select id="${inp}"></select></label>` +
      `<label for="${v}">value<input id="${v}" type="text" inputmode="decimal" value="2" autocomplete="off"></label>` + `<label for="${m1}" class="m1">M₁<input id="${m1}" type="text" inputmode="decimal" value="3"></label>` +
      `<label for="${gm}">γ<input id="${gm}" type="text" inputmode="decimal" value="1.4"></label>`);
    const res = document.createElement("div"); res.className = "table-out"; w.appendChild(res);
    const cur = () => (only || document.getElementById(tb).value);
    const fillInputs = () => {
      const t = TABLES[cur()], sel = document.getElementById(inp);
      sel.innerHTML = t.inputs.map(([k, n]) => `<option value="${k}">${n}</option>`).join("");
      w.querySelector(".m1").hidden = !t.two;
      document.getElementById(v).value = cur() === "oblique" ? "10" : spec.preset === "area" ? "2" : cur() === "shock" ? "2" : "2";
      if (spec.preset === "area") sel.value = "AR_sup";
    };
    function draw() {
      const t = TABLES[cur()], k = document.getElementById(inp).value, x = parseFloat(document.getElementById(v).value), g = parseFloat(document.getElementById(gm).value) || 1.4;
      let rows;
      try {
        if (t.two) { const M = parseFloat(document.getElementById(m1).value); rows = M > 1 && isFinite(x) ? t.rows(M, g, x) : null; }
        else { const M = t.solve(k, x, g); rows = isFinite(M) && M > 0 ? t.rows(M, g) : null; }
      } catch (e) { rows = null; }
      res.innerHTML = rows ? `<table><tbody>${rows.map(([n, y]) => `<tr><th>${n}</th><td>${n === "note" ? "Mₓ must exceed 1" : isFinite(y) ? (+y.toPrecision(5)).toString() : "—"}</td></tr>`).join("")}</tbody></table>` :
        `<p class="small">That value is out of range for this relation (for example A/A* below 1, a pressure ratio above 1, or a deflection beyond δ_max).</p>`;
    }
    if (!only) document.getElementById(tb).addEventListener("input", () => { fillInputs(); draw(); });
    fillInputs();
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
