// Interactive widgets for the "Why?" panel. Spec: design/specs/2026-10-04-why-network-design.md §4.
// WidgetMath holds the pure math (tested in tests/widget_math_test.js); Widgets.render draws each widget.
(function (root) {
  // Pure math -----------------------------------------------------------------------
  const FUNCTIONS = {
    square: (x) => x * x,
    fall: (t) => 4.9 * t * t,
    cube: (x) => x * x * x,
    sin: Math.sin,
    cos: Math.cos,
    exp: Math.exp,
    sin2: (x) => Math.sin(x) ** 2,
    cos2: (x) => Math.cos(x) ** 2,
    hole: (x) => (x * x - 1) / (x - 1),
    sinh_over_h: (h) => Math.sin(h) / h,
    cosh_minus_1_over_h: (h) => (Math.cos(h) - 1) / h,
    exph_minus_1_over_h: (h) => (Math.exp(h) - 1) / h,
    abs: Math.abs,
    sqrt: (x) => (x >= 0 ? Math.sqrt(x) : NaN),
    recip: (x) => 1 / x,
  };

  const WidgetMath = {
    fn(name) {
      if (!Object.prototype.hasOwnProperty.call(FUNCTIONS, name)) throw new Error(`unknown function '${name}'`);
      return FUNCTIONS[name];
    },
    secantSlope: (f, x0, h) => (f(x0 + h) - f(x0)) / h,
    riemann(f, a, b, n, rule = "mid") {
      const dx = (b - a) / n;
      let sum = 0;
      for (let i = 0; i < n; i++) {
        const x = rule === "left" ? a + i * dx : rule === "right" ? a + (i + 1) * dx : a + (i + 0.5) * dx;
        sum += f(x) * dx;
      }
      return sum;
    },
    unitPoint: (theta) => ({ x: Math.cos(theta), y: Math.sin(theta) }),
    strength: (cup) => (cup.marks ? cup.conc / cup.marks : 0),
    pour(from, to, marks) {
      const moved = WidgetMath.strength(from) * marks;
      return [{ marks: from.marks - marks, conc: from.conc - moved }, { marks: to.marks + marks, conc: to.conc + moved }];
    },
    combine: (cups) => cups.reduce((s, c) => s + c.conc, 0) / cups.reduce((s, c) => s + c.marks, 0),
    dilute: (cup, water) => ({ marks: cup.marks + water, conc: cup.conc }),
    accumulate: (f, a, x, n = 400) => (x === a ? 0 : WidgetMath.riemann(f, a, x, n)),
    diffPoly: (coeffs) => (coeffs.length <= 1 ? coeffs.map(() => 0) : coeffs.slice(1).map((c, i) => c * (i + 1))),
    stretchArea: (name, a, lo, hi) => WidgetMath.riemann((x) => WidgetMath.fn(name)(a * x), lo, hi, 4000),
    productChange: (u, v, du, dv) => ({ udv: u * dv, vdu: v * du, corner: du * dv }),
    squeeze: (h) => ({ inner: Math.sin(h) / 2, sector: h / 2, outer: Math.tan(h) / 2 }),
    square: (t) => { const s = Math.sin(t); return Math.abs(s) < 1e-12 ? 0 : Math.sign(s); },
    productIntegral: (m, n) => WidgetMath.riemann((t) => Math.sin(m * t) * Math.sin(n * t), 0, 2 * Math.PI, 4000),
    rmsGap: (a) => Math.sqrt(WidgetMath.riemann((t) => (a * Math.sin(t) - WidgetMath.square(t)) ** 2, 0, 2 * Math.PI, 2000) / (2 * Math.PI)),
    errorParabola: (a) => (a * a) / 2 - (4 * a) / Math.PI + 1,
    halfContributions(n) {
      const first = WidgetMath.riemann((t) => WidgetMath.square(t) * Math.sin(n * t), 0, Math.PI, 2000);
      const second = WidgetMath.riemann((t) => WidgetMath.square(t) * Math.sin(n * t), Math.PI, 2 * Math.PI, 2000);
      return { first, second, total: first + second };
    },
    partialSum(N, t) {
      let s = 0;
      for (let k = 0; k < N; k++) { const n = 2 * k + 1; s += (4 / (n * Math.PI)) * Math.sin(n * t); }
      return s;
    },
    peakOf(N) {
      const top = 2 * N - 1, end = Math.min(Math.PI / 2, (4 * Math.PI) / top);
      let best = -Infinity;
      for (let i = 1; i <= 3000; i++) best = Math.max(best, WidgetMath.partialSum(N, (i / 3000) * end));
      return best;
    },
    fractionOf: (a, b) => a * b,
    serial(start, rounds) {
      const out = [];
      let s = start;
      for (let i = 0; i < rounds; i++) { s /= 2; out.push(s); }
      return out;
    },
    toFraction(x, maxDen = 64) {
      for (let d = 1; d <= maxDen; d++) {
        const n = Math.round(x * d);
        if (Math.abs(n / d - x) < 1e-9) return d === 1 ? `${n}` : `${n}/${d}`;
      }
      return x.toFixed(3);
    },
  };

  // Drawing helpers -----------------------------------------------------------------
  const NS = "http://www.w3.org/2000/svg";
  const fmt = (v, d = 3) => (Math.abs(v) < 1e-12 ? "0" : Number(v).toFixed(d).replace(/\.?0+$/, ""));

  function el(name, attrs = {}, parent) {
    const n = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (parent) parent.append(n);
    return n;
  }

  function shell(container, prompt) {
    container.innerHTML = "";
    const p = document.createElement("p");
    p.className = "w-prompt";
    p.textContent = `Try this: ${prompt}`;
    const svg = el("svg", { viewBox: "0 0 480 260", class: "w-svg", role: "img" });
    const controls = document.createElement("div");
    controls.className = "w-controls";
    const readout = document.createElement("p");
    readout.className = "w-readout";
    readout.setAttribute("aria-live", "polite");
    const reset = document.createElement("button");
    reset.type = "button";
    reset.className = "w-reset";
    reset.textContent = "Reset";
    const foot = document.createElement("div");
    foot.className = "w-foot";
    foot.append(readout, reset);
    container.append(p, svg, controls, foot);
    return { svg, controls, readout, reset };
  }

  let sliderCount = 0;
  function slider(controls, label, min, max, step, value, onInput) {
    const id = `w-s-${++sliderCount}`;
    const row = document.createElement("div");
    row.className = "w-slider";
    row.innerHTML = `<label for="${id}">${label}</label>`;
    const input = Object.assign(document.createElement("input"), { type: "range", id, min, max, step, value });
    input.addEventListener("input", () => onInput(Number(input.value)));
    row.append(input);
    controls.append(row);
    return input;
  }

  function button(controls, label, onClick) {
    const b = Object.assign(document.createElement("button"), { type: "button", textContent: label });
    b.addEventListener("click", onClick);
    controls.append(b);
    return b;
  }

  // A 2-D plot area: maps math coordinates into the 480×260 viewBox
  function plotArea(svg, xmin, xmax, ymin, ymax) {
    const L = 36, R = 470, T = 12, B = 238;
    const X = (x) => L + ((x - xmin) / (xmax - xmin)) * (R - L);
    const Y = (y) => B - ((y - ymin) / (ymax - ymin)) * (B - T);
    const axes = el("g", { class: "w-axes" }, svg);
    if (ymin < 0 && ymax > 0) el("line", { x1: L, x2: R, y1: Y(0), y2: Y(0) }, axes);
    if (xmin < 0 && xmax > 0) el("line", { x1: X(0), x2: X(0), y1: T, y2: B }, axes);
    const curve = (f, a = xmin, b = xmax, cls = "w-curve", n = 240) => {
      let d = "";
      let pen = false;
      for (let i = 0; i <= n; i++) {
        const x = a + ((b - a) * i) / n;
        const y = f(x);
        if (!Number.isFinite(y) || y > ymax * 4 + 10 || y < ymin * 4 - 10) { pen = false; continue; }
        d += `${pen ? "L" : "M"}${X(x).toFixed(1)} ${Y(y).toFixed(1)} `;
        pen = true;
      }
      return el("path", { d, class: cls }, svg);
    };
    return { X, Y, curve, L, R, T, B };
  }

  // Widgets -------------------------------------------------------------------------
  const W = {};

  // Secant to tangent (and "trace" mode for reading a function)
  W.secant = function (box, cfg) {
    const f = WidgetMath.fn(cfg.f || "square");
    const x0 = cfg.x0 ?? 1;
    const span = cfg.span ?? (cfg.f === "sin" || cfg.f === "cos" ? Math.PI : 2);
    const xs = [x0 - span, x0 + span];
    let ys = [Infinity, -Infinity];
    for (let i = 0; i <= 100; i++) { const y = f(xs[0] + ((xs[1] - xs[0]) * i) / 100); ys = [Math.min(ys[0], y), Math.max(ys[1], y)]; }
    const pad = (ys[1] - ys[0]) * 0.15 || 1;
    const ui = shell(box, cfg.prompt || (cfg.mode === "trace" ? "Drag along the curve and read each output." : "Drag h toward 0 and watch the secant turn into the tangent."));
    const P = plotArea(ui.svg, xs[0], xs[1], ys[0] - pad, ys[1] + pad);
    P.curve(f);
    const line = el("line", { class: "w-secant" }, ui.svg);
    const lineL = cfg.sides === "both" ? el("line", { class: "w-secant left" }, ui.svg) : null;
    const p0 = el("circle", { r: 5, class: "w-point" }, ui.svg);
    const p1 = el("circle", { r: 5, class: "w-point alt" }, ui.svg);
    const pL = cfg.sides === "both" ? el("circle", { r: 5, class: "w-point alt" }, ui.svg) : null;
    let state;
    const draw = () => {
      if (cfg.mode === "trace") {
        const x = state.x;
        p0.setAttribute("cx", P.X(x)); p0.setAttribute("cy", P.Y(f(x)));
        line.setAttribute("x1", P.X(x)); line.setAttribute("x2", P.X(x)); line.setAttribute("y1", P.Y(0)); line.setAttribute("y2", P.Y(f(x)));
        p1.setAttribute("r", 0);
        ui.readout.textContent = `input x = ${fmt(x, 2)} → output f(x) = ${fmt(f(x), 3)}`;
        return;
      }
      const h = 1.5 * Math.pow(10, -state.s / 30);
      const m = WidgetMath.secantSlope(f, x0, h);
      const ext = span;
      line.setAttribute("x1", P.X(x0 - ext)); line.setAttribute("y1", P.Y(f(x0) - m * ext));
      line.setAttribute("x2", P.X(x0 + ext)); line.setAttribute("y2", P.Y(f(x0) + m * ext));
      p0.setAttribute("cx", P.X(x0)); p0.setAttribute("cy", P.Y(f(x0)));
      p1.setAttribute("cx", P.X(x0 + h)); p1.setAttribute("cy", P.Y(f(x0 + h)));
      if (cfg.sides === "both") {
        const mL = WidgetMath.secantSlope(f, x0, -h);
        lineL.setAttribute("x1", P.X(x0 - ext)); lineL.setAttribute("y1", P.Y(f(x0) - mL * ext));
        lineL.setAttribute("x2", P.X(x0 + ext)); lineL.setAttribute("y2", P.Y(f(x0) + mL * ext));
        pL.setAttribute("cx", P.X(x0 - h)); pL.setAttribute("cy", P.Y(f(x0 - h)));
        ui.readout.textContent = `h = ${h < 0.001 ? h.toExponential(1) : fmt(h, 3)}   slope from the left = ${fmt(mL, 4)}, from the right = ${fmt(m, 4)}${Math.abs(m - mL) > 0.01 ? " (they never agree: no derivative here)" : ""}`;
        return;
      }
      ui.readout.textContent = `h = ${h < 0.001 ? h.toExponential(1) : fmt(h, 3)}   slope of secant = ${fmt(m, 5)}`;
    };
    const init = () => { state = cfg.mode === "trace" ? { x: x0 } : { s: 0 }; input.value = cfg.mode === "trace" ? x0 : 0; draw(); };
    const input = cfg.mode === "trace"
      ? slider(ui.controls, "x", xs[0], xs[1], 0.01, x0, (v) => { state.x = v; draw(); })
      : slider(ui.controls, "Shrink h", 0, 100, 1, 0, (v) => { state.s = v; draw(); });
    ui.reset.addEventListener("click", init);
    init();
    return { reset: init };
  };

  // Limit zoom, with an optional ε band
  W["limit-zoom"] = function (box, cfg) {
    const g = WidgetMath.fn(cfg.g || "sinh_over_h");
    const at = cfg.at ?? 0;
    const L = cfg.limit ?? g(at + 1e-7);
    const ui = shell(box, cfg.prompt || "Zoom in toward the point and watch the values settle.");
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const w = Math.pow(10, -state.z / 25);
      const yr = cfg.epsilon ? Math.max(state.eps * 2.5, 1e-4) : Math.max(w * 2, 1e-4);
      const P = plotArea(ui.svg, at - w, at + w, L - yr, L + yr);
      if (cfg.epsilon) {
        el("rect", { x: P.L, width: P.R - P.L, y: P.Y(L + state.eps), height: Math.max(1, P.Y(L - state.eps) - P.Y(L + state.eps)), class: "w-band" }, ui.svg);
      }
      P.curve(g, at - w, at - w * 1e-3);
      P.curve(g, at + w * 1e-3, at + w);
      el("circle", { cx: P.X(at), cy: P.Y(L), r: 5, class: "w-hole" }, ui.svg);
      let text = `window ±${fmt(w, 4)}:  g(${fmt(at + w / 2, 4)}) = ${fmt(g(at + w / 2), 6)},  approaching ${fmt(L, 4)}`;
      if (cfg.epsilon) {
        let delta = w;
        for (let i = 1; i <= 400; i++) {
          const d = (w * i) / 400;
          if (Math.abs(g(at + d) - L) > state.eps || Math.abs(g(at - d) - L) > state.eps) { delta = (w * (i - 1)) / 400; break; }
        }
        for (const xd of [at - delta, at + delta]) el("line", { x1: P.X(xd), x2: P.X(xd), y1: P.T, y2: P.B, class: "w-delta" }, ui.svg);
        text = `ε = ${fmt(state.eps, 4)}: every x within δ ≈ ${fmt(delta, 4)} of ${fmt(at, 3)} (dashed lines) lands inside the band.`;
      }
      ui.readout.textContent = text;
    };
    const init = () => { state = { z: 0, eps: 0.5 }; zoom.value = 0; if (epsIn) epsIn.value = 0; draw(); };
    const zoom = slider(ui.controls, "Zoom in", 0, 75, 1, 0, (v) => { state.z = v; draw(); });
    const epsIn = cfg.epsilon ? slider(ui.controls, "Shrink ε", 0, 60, 1, 0, (v) => { state.eps = 0.5 * Math.pow(10, -v / 20); draw(); }) : null;
    ui.reset.addEventListener("click", init);
    init();
    return { reset: init };
  };

  // Unit circle: drag the point, or use the slider
  W["unit-circle"] = function (box, cfg) {
    if (cfg.mode === "squeeze") return unitSqueeze(box, cfg);
    if (cfg.mode === "two-angle") return unitTwoAngle(box, cfg);
    const ui = shell(box, cfg.prompt || "Drag the point around the circle.");
    ui.svg.setAttribute("viewBox", "0 0 480 260");
    const cx = 150, cy = 130, r = 105;
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const t = state.t;
      const { x, y } = WidgetMath.unitPoint(t);
      el("line", { x1: cx - r - 15, x2: cx + r + 15, y1: cy, y2: cy, class: "w-axis" }, ui.svg);
      el("line", { x1: cx, x2: cx, y1: cy - r - 15, y2: cy + r + 15, class: "w-axis" }, ui.svg);
      el("circle", { cx, cy, r, class: "w-circle" }, ui.svg);
      const px = cx + r * x, py = cy - r * y;
      const large = (((t % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)) > Math.PI ? 1 : 0;
      el("path", { d: `M${cx + 22} ${cy} A22 22 0 ${large} 0 ${cx + 22 * x} ${cy - 22 * y}`, class: "w-angle" }, ui.svg);
      el("line", { x1: cx, y1: cy, x2: px, y2: py, class: "w-radius" }, ui.svg);
      el("line", { x1: cx, y1: cy, x2: px, y2: cy, class: "w-cos" }, ui.svg);
      el("line", { x1: px, y1: cy, x2: px, y2: py, class: "w-sin" }, ui.svg);
      el("circle", { cx: px, cy: py, r: 8, class: "w-point handle" }, ui.svg);
      const legend = el("text", { x: 300, y: 70, class: "w-label" }, ui.svg);
      legend.textContent = `cos θ = ${fmt(x, 3)}`;
      legend.classList.add("cos");
      const legend2 = el("text", { x: 300, y: 98, class: "w-label sin" }, ui.svg);
      legend2.textContent = `sin θ = ${fmt(y, 3)}`;
      const legend3 = el("text", { x: 300, y: 126, class: "w-label" }, ui.svg);
      legend3.textContent = `cos² + sin² = ${fmt(x * x + y * y, 3)}`;
      ui.readout.textContent = `θ = ${fmt(t, 3)} rad (${fmt((t * 180) / Math.PI, 1)}°): the point is (${fmt(x, 3)}, ${fmt(y, 3)}).`;
    };
    const setT = (t) => { state.t = t; input.value = t; draw(); };
    const input = slider(ui.controls, "Angle θ", 0, (2 * Math.PI).toFixed(3), 0.01, 0.6, (v) => { state.t = v; draw(); });
    const toAngle = (e) => {
      const rect = ui.svg.getBoundingClientRect();
      const sx = ((e.clientX - rect.left) / rect.width) * 480, sy = ((e.clientY - rect.top) / rect.height) * 260;
      let t = Math.atan2(cy - sy, sx - cx);
      if (t < 0) t += 2 * Math.PI;
      setT(Number(t.toFixed(3)));
    };
    let dragging = false;
    ui.svg.addEventListener("pointerdown", (e) => { dragging = true; ui.svg.setPointerCapture(e.pointerId); toAngle(e); });
    ui.svg.addEventListener("pointermove", (e) => { if (dragging) toAngle(e); });
    ui.svg.addEventListener("pointerup", () => { dragging = false; });
    const init = () => { state = { t: 0.6 }; setT(0.6); };
    ui.reset.addEventListener("click", init);
    init();
    return { reset: init };
  };

  // Riemann sums (and plain rectangle/triangle areas in "shapes" mode)
  W.riemann = function (box, cfg) {
    const ui = shell(box, cfg.prompt || "Add rectangles and watch the total approach the exact area.");
    let state;
    if (cfg.mode === "shapes") {
      const draw = () => {
        ui.svg.innerHTML = "";
        const s = 22, x0 = 40, y0 = 230;
        const { w, h } = state;
        for (let i = 0; i <= w; i++) el("line", { x1: x0 + i * s, x2: x0 + i * s, y1: y0, y2: y0 - h * s, class: "w-grid" }, ui.svg);
        for (let j = 0; j <= h; j++) el("line", { x1: x0, x2: x0 + w * s, y1: y0 - j * s, y2: y0 - j * s, class: "w-grid" }, ui.svg);
        el("rect", { x: x0, y: y0 - h * s, width: w * s, height: h * s, class: "w-rect" }, ui.svg);
        el("path", { d: `M${x0} ${y0} L${x0 + w * s} ${y0} L${x0 + w * s} ${y0 - h * s} Z`, class: "w-tri" }, ui.svg);
        ui.readout.textContent = `rectangle ${w} × ${h} = ${w * h} squares; shaded triangle = ½ × ${w} × ${h} = ${fmt((w * h) / 2, 1)}`;
      };
      const init = () => { state = { w: 6, h: 4 }; wi.value = 6; hi.value = 4; draw(); };
      const wi = slider(ui.controls, "Width", 1, 18, 1, 6, (v) => { state.w = v; draw(); });
      const hi = slider(ui.controls, "Height", 1, 9, 1, 4, (v) => { state.h = v; draw(); });
      ui.reset.addEventListener("click", init);
      init();
      return { reset: init };
    }
    const f = WidgetMath.fn(cfg.f || "square");
    const a = cfg.a ?? 0, b = cfg.b ?? 1;
    const exact = WidgetMath.riemann(f, a, b, 20000);
    let ymax = 0, ymin = 0;
    for (let i = 0; i <= 100; i++) { const y = f(a + ((b - a) * i) / 100); ymax = Math.max(ymax, y); ymin = Math.min(ymin, y); }
    const draw = () => {
      ui.svg.innerHTML = "";
      const P = plotArea(ui.svg, a - (b - a) * 0.05, b + (b - a) * 0.05, ymin - (ymax - ymin) * 0.1, ymax + (ymax - ymin) * 0.15);
      const n = state.n, dx = (b - a) / n;
      for (let i = 0; i < n; i++) {
        const y = f(a + (i + 0.5) * dx);
        el("rect", { x: P.X(a + i * dx), width: Math.max(0.5, P.X(a + dx) - P.X(a)), y: Math.min(P.Y(y), P.Y(0)), height: Math.abs(P.Y(y) - P.Y(0)), class: `w-bar${y < 0 ? " neg" : ""}` }, ui.svg);
      }
      P.curve(f, a, b);
      if (cfg.mode === "average") {
        const avg = exact / (b - a);
        el("line", { x1: P.X(a), x2: P.X(b), y1: P.Y(avg), y2: P.Y(avg), class: "w-average" }, ui.svg);
      }
      const sum = WidgetMath.riemann(f, a, b, n);
      ui.readout.textContent = cfg.mode === "average"
        ? `${n} rectangles: area ≈ ${fmt(sum, 4)}, so the average height = area ÷ width ≈ ${fmt(sum / (b - a), 4)}`
        : `${n} rectangle${n > 1 ? "s" : ""}: total = ${fmt(sum, 5)}   (exact area ${fmt(exact, 5)})`;
    };
    const init = () => { state = { n: cfg.n ?? 4 }; ni.value = state.n; draw(); };
    const ni = slider(ui.controls, "Rectangles", 1, 200, 1, cfg.n ?? 4, (v) => { state.n = v; draw(); });
    ui.reset.addEventListener("click", init);
    init();
    return { reset: init };
  };

  // Fraction bars: parts of a whole, and pouring between cups
  W["fraction-bar"] = function (box, cfg) {
    const ui = shell(box, cfg.prompt || "Change the parts.");
    let state;
    const barRow = (y, parts, filled, label, color = "#d4b06a", strength = null) => {
      const x0 = 30, wTot = 420, h = 34, w = wTot / parts;
      for (let i = 0; i < parts; i++) {
        el("rect", { x: x0 + i * w, y, width: w, height: h, class: `w-part${i < filled ? " on" : ""}`, style: i < filled && strength != null ? `fill-opacity:${0.25 + 0.75 * strength}` : "" , fill: color }, ui.svg);
      }
      const t = el("text", { x: x0, y: y - 8, class: "w-label" }, ui.svg);
      t.textContent = label;
    };
    const tea = cfg.color || "#b06222";
    if (cfg.mode === "ratio") {
      const draw = () => {
        ui.svg.innerHTML = "";
        const { a, b } = state;
        const x0 = 30, w = 420 / (a + b);
        for (let i = 0; i < a + b; i++) el("rect", { x: x0 + i * w, y: 100, width: w, height: 40, class: "w-part on", fill: i < a ? tea : "#a8d0d6" }, ui.svg);
        const t = el("text", { x: x0, y: 88, class: "w-label" }, ui.svg);
        t.textContent = `${a} part${a > 1 ? "s" : ""} concentrate : ${b} part${b > 1 ? "s" : ""} water`;
        ui.readout.textContent = `Ratio ${a}:${b} → ${a + b} parts in all → concentrate is ${a}/${a + b} of the drink (not ${a}/${b}).`;
      };
      const init = () => { state = { a: cfg.a ?? 1, b: cfg.b ?? 3 }; ai.value = state.a; bi.value = state.b; draw(); };
      const ai = slider(ui.controls, "Concentrate parts", 1, 5, 1, cfg.a ?? 1, (v) => { state.a = v; draw(); });
      const bi = slider(ui.controls, "Water parts", 1, 7, 1, cfg.b ?? 3, (v) => { state.b = v; draw(); });
      ui.reset.addEventListener("click", init); init();
      return { reset: init };
    }
    if (cfg.mode === "cup" || cfg.mode === "dilute") {
      const draw = () => {
        ui.svg.innerHTML = "";
        const { marks, conc } = state;
        const cap = cfg.mode === "dilute" ? 16 : 8, x0 = 30, w = 420 / cap;
        for (let i = 0; i < cap; i++) el("rect", { x: x0 + i * w, y: 100, width: w, height: 40, class: `w-part${i < marks ? " on" : ""}`, fill: i < conc ? tea : "#a8d0d6" }, ui.svg);
        const t = el("text", { x: x0, y: 88, class: "w-label" }, ui.svg);
        t.textContent = `${conc} mark${conc === 1 ? "" : "s"} of concentrate in ${marks} mark${marks === 1 ? "" : "s"} of drink`;
        const simple = WidgetMath.toFraction(WidgetMath.strength({ marks, conc }));
        ui.readout.textContent = `strength = concentrate ÷ total = ${conc}/${marks}${simple !== `${conc}/${marks}` ? ` = ${simple}` : ""}`;
        if (water) water.disabled = marks * 2 > cap;
      };
      let water = null;
      const init = () => { state = { marks: cfg.marks ?? 4, conc: cfg.conc ?? 1 }; if (mi) { mi.value = state.marks; ci.value = state.conc; } draw(); };
      let mi = null, ci = null;
      if (cfg.mode === "cup") {
        mi = slider(ui.controls, "Total marks", 1, 8, 1, cfg.marks ?? 4, (v) => { state.marks = v; if (state.conc > v) { state.conc = v; ci.value = v; } draw(); });
        ci = slider(ui.controls, "Concentrate marks", 0, 8, 1, cfg.conc ?? 1, (v) => { state.conc = Math.min(v, state.marks); draw(); });
      } else {
        water = button(ui.controls, "Add an equal amount of water", () => { state = WidgetMath.dilute(state, state.marks); draw(); });
      }
      ui.reset.addEventListener("click", init); init();
      return { reset: init };
    }
    if (cfg.mode === "grid") {
      const draw = () => {
        ui.svg.innerHTML = "";
        const { p, q, k } = state;
        const x0 = 140, y0 = 30, S = 200;
        const cols = cfg.kind === "equivalent" ? q * k : q, rows = cfg.kind === "equivalent" ? 1 : p;
        const shadeCols = cfg.kind === "equivalent" ? (cfg.num ?? 1) * k : 1;
        for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
          const on = cfg.kind === "equivalent" ? i < shadeCols : i < 1 && j < 1;
          const half = cfg.kind !== "equivalent" && i < 1;
          el("rect", { x: x0 + (i * S) / cols, y: y0 + (j * S) / rows, width: S / cols, height: S / rows, class: `w-part${on ? " on" : half ? " half" : ""}`, fill: tea }, ui.svg);
        }
        if (cfg.kind === "equivalent") {
          const n = cfg.num ?? 1;
          ui.readout.textContent = `${n}/${q} = ${n * k}/${q * k}: cutting every part into ${k} keeps the same shaded amount.`;
        } else {
          ui.readout.textContent = `1/${p} of 1/${q}: one row of the first column = 1 of ${p * q} small parts = 1/${p * q}`;
        }
      };
      let kIn, pIn, qIn;
      if (cfg.kind === "equivalent") {
        kIn = slider(ui.controls, "Cut each part into", 1, 6, 1, 2, (v) => { state.k = v; draw(); });
      } else {
        pIn = slider(ui.controls, "Take 1 of how many rows", 1, 6, 1, cfg.p ?? 2, (v) => { state.p = v; draw(); });
        qIn = slider(ui.controls, "Columns (the first fraction)", 1, 8, 1, cfg.q ?? 4, (v) => { state.q = v; draw(); });
      }
      const init = () => {
        state = { p: cfg.p ?? 2, q: cfg.q ?? 4, k: cfg.kind === "equivalent" ? 2 : 1 };
        if (kIn) kIn.value = state.k; else { pIn.value = state.p; qIn.value = state.q; }
        draw();
      };
      ui.reset.addEventListener("click", init); init();
      return { reset: init };
    }
    if (cfg.mode === "serial") {
      const draw = () => {
        ui.svg.innerHTML = "";
        const chain = [1, ...WidgetMath.serial(1, state.rounds)];
        chain.forEach((s, i) => {
          const x = 20 + i * 92;
          el("rect", { x, y: 90, width: 70, height: 90, class: "w-part on", fill: tea, style: `fill-opacity:${0.12 + 0.88 * s}` }, ui.svg);
          const t = el("text", { x: x + 35, y: 205, class: "w-label", "text-anchor": "middle" }, ui.svg);
          t.textContent = WidgetMath.toFraction(s);
          if (i) { const a = el("text", { x: x - 12, y: 140, class: "w-label", "text-anchor": "middle" }, ui.svg); a.textContent = "→"; }
        });
        ui.readout.textContent = `${state.rounds} round${state.rounds === 1 ? "" : "s"} of "take 1 mark, add 1 mark of water": strength = (1/2)^${state.rounds} = ${WidgetMath.toFraction(chain[chain.length - 1])}`;
      };
      const init = () => { state = { rounds: cfg.rounds ?? 3 }; ri.value = state.rounds; draw(); };
      const ri = slider(ui.controls, "Rounds", 1, 4, 1, cfg.rounds ?? 3, (v) => { state.rounds = v; draw(); });
      ui.reset.addEventListener("click", init); init();
      return { reset: init };
    }
    if (cfg.mode === "combine") {
      const s1 = cfg.s1 ?? 0.5, s2 = cfg.s2 ?? 0.25;
      const draw = () => {
        ui.svg.innerHTML = "";
        const { m1, m2 } = state;
        const mix = WidgetMath.combine([{ marks: m1, conc: m1 * s1 }, { marks: m2, conc: m2 * s2 }]);
        barRow(50, 6, m1, `${m1} mark${m1 === 1 ? "" : "s"} at ${WidgetMath.toFraction(s1)}`, tea, s1);
        barRow(120, 6, m2, `${m2} mark${m2 === 1 ? "" : "s"} at ${WidgetMath.toFraction(s2)}`, tea, s2);
        barRow(200, 12, m1 + m2, `mixed: ${m1 + m2} marks at ${WidgetMath.toFraction(mix)}`, tea, mix);
        ui.readout.textContent = `(${m1}·${WidgetMath.toFraction(s1)} + ${m2}·${WidgetMath.toFraction(s2)}) ÷ ${m1 + m2} = ${WidgetMath.toFraction(mix)}  (plain average would be ${WidgetMath.toFraction((s1 + s2) / 2)})`;
      };
      const init = () => { state = { m1: cfg.m1 ?? 1, m2: cfg.m2 ?? 1 }; a1.value = state.m1; a2.value = state.m2; draw(); };
      const a1 = slider(ui.controls, `Marks at ${WidgetMath.toFraction(s1)}`, 1, 6, 1, cfg.m1 ?? 1, (v) => { state.m1 = v; draw(); });
      const a2 = slider(ui.controls, `Marks at ${WidgetMath.toFraction(s2)}`, 1, 6, 1, cfg.m2 ?? 1, (v) => { state.m2 = v; draw(); });
      ui.reset.addEventListener("click", init); init();
      return { reset: init };
    }
    if (cfg.mode === "pour") {
      const draw = () => {
        ui.svg.innerHTML = "";
        const [A, B] = state.cups;
        barRow(60, 4, A.marks, `Cup A: ${A.marks} mark${A.marks === 1 ? "" : "s"}, strength ${WidgetMath.toFraction(WidgetMath.strength(A))}`, "#b06222", WidgetMath.strength(A));
        barRow(160, 4, B.marks, `Cup B: ${B.marks} mark${B.marks === 1 ? "" : "s"}, strength ${WidgetMath.toFraction(WidgetMath.strength(B))}`, "#b06222", WidgetMath.strength(B));
        ui.readout.textContent = `Total concentrate: ${WidgetMath.toFraction(A.conc + B.conc)} mark, the same after every pour.`;
        ab.disabled = A.marks < 1 || B.marks > 3;
        ba.disabled = B.marks < 1 || A.marks > 3;
      };
      const ab = button(ui.controls, "Pour 1 mark A → B", () => { state.cups = WidgetMath.pour(state.cups[0], state.cups[1], 1); draw(); });
      const ba = button(ui.controls, "Pour 1 mark B → A", () => { const [b2, a2] = WidgetMath.pour(state.cups[1], state.cups[0], 1); state.cups = [a2, b2]; draw(); });
      const init = () => { state = { cups: [{ marks: 2, conc: 1 }, { marks: 1, conc: 0 }] }; draw(); };
      ui.reset.addEventListener("click", init);
      init();
      return { reset: init };
    }
    const draw = () => {
      ui.svg.innerHTML = "";
      const { parts, filled } = state;
      barRow(110, parts, Math.min(filled, parts), `${Math.min(filled, parts)} of ${parts} equal parts`);
      const f = Math.min(filled, parts);
      ui.readout.textContent = `${f}/${parts} = ${f} ÷ ${parts} = ${fmt(f / parts, 4)}`;
    };
    const init = () => { state = { parts: cfg.parts ?? 4, filled: cfg.filled ?? 3 }; pi.value = state.parts; fi.value = state.filled; draw(); };
    const pi = slider(ui.controls, "Equal parts", 1, 12, 1, cfg.parts ?? 4, (v) => { state.parts = v; fi.max = v; if (state.filled > v) { state.filled = v; fi.value = v; } draw(); });
    const fi = slider(ui.controls, "Parts taken", 0, cfg.parts ?? 4, 1, cfg.filled ?? 3, (v) => { state.filled = v; draw(); });
    ui.reset.addEventListener("click", init);
    init();
    return { reset: init };
  };


  // Unit circle, squeeze picture for sin h / h → 1
  function unitSqueeze(box, cfg) {
    const ui = shell(box, cfg.prompt || "Shrink the angle h. The three areas squeeze sin h / h toward 1.");
    const cx = 60, cy = 230, r = 200;
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const h = state.h, P = WidgetMath.unitPoint(h), sq = WidgetMath.squeeze(h);
      el("path", { d: `M${cx} ${cy} L${cx + r} ${cy} L${cx + r} ${cy - r * Math.tan(h)} Z`, class: "w-tri outer" }, ui.svg);
      el("path", { d: `M${cx} ${cy} L${cx + r} ${cy} A${r} ${r} 0 0 0 ${cx + r * P.x} ${cy - r * P.y} Z`, class: "w-sector" }, ui.svg);
      el("path", { d: `M${cx} ${cy} L${cx + r} ${cy} L${cx + r * P.x} ${cy - r * P.y} Z`, class: "w-tri inner" }, ui.svg);
      el("path", { d: `M${cx + r} ${cy} A${r} ${r} 0 0 0 ${cx} ${cy - r}`, class: "w-circle" }, ui.svg);
      const t = el("text", { x: 300, y: 40, class: "w-label" }, ui.svg);
      t.textContent = `½ sin h = ${fmt(sq.inner, 4)}`;
      const t2 = el("text", { x: 300, y: 64, class: "w-label sin" }, ui.svg);
      t2.textContent = `½ h = ${fmt(sq.sector, 4)}`;
      const t3 = el("text", { x: 300, y: 88, class: "w-label cos" }, ui.svg);
      t3.textContent = `½ tan h = ${fmt(sq.outer, 4)}`;
      ui.readout.textContent = `h = ${fmt(h, 3)}:  cos h = ${fmt(Math.cos(h), 4)} ≤ sin h / h = ${fmt(Math.sin(h) / h, 4)} ≤ 1`;
    };
    const init = () => { state = { h: 0.9 }; hi.value = 0.9; draw(); };
    const hi = slider(ui.controls, "Angle h", 0.02, 1.2, 0.01, 0.9, (v) => { state.h = v; draw(); });
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  }

  // Unit circle, two angles: rotating by a then b lands at a + b
  function unitTwoAngle(box, cfg) {
    const ui = shell(box, cfg.prompt || "Set two angles. The point for a + b matches the angle-addition formula.");
    const cx = 130, cy = 130, r = 105;
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const { a, b } = state;
      el("circle", { cx, cy, r, class: "w-circle" }, ui.svg);
      el("line", { x1: cx - r - 10, x2: cx + r + 10, y1: cy, y2: cy, class: "w-axis" }, ui.svg);
      el("line", { x1: cx, x2: cx, y1: cy - r - 10, y2: cy + r + 10, class: "w-axis" }, ui.svg);
      const pa = WidgetMath.unitPoint(a), pab = WidgetMath.unitPoint(a + b);
      el("line", { x1: cx, y1: cy, x2: cx + r * pa.x, y2: cy - r * pa.y, class: "w-cos" }, ui.svg);
      el("line", { x1: cx, y1: cy, x2: cx + r * pab.x, y2: cy - r * pab.y, class: "w-sin" }, ui.svg);
      el("circle", { cx: cx + r * pab.x, cy: cy - r * pab.y, r: 6, class: "w-point" }, ui.svg);
      const f = Math.sin(a) * Math.cos(b) + Math.cos(a) * Math.sin(b);
      const t = el("text", { x: 270, y: 70, class: "w-label sin" }, ui.svg);
      t.textContent = `sin(a + b) = ${fmt(pab.y, 4)}`;
      const t2 = el("text", { x: 270, y: 96, class: "w-label" }, ui.svg);
      t2.textContent = `sin a cos b + cos a sin b = ${fmt(f, 4)}`;
      ui.readout.textContent = `a = ${fmt(a, 2)}, b = ${fmt(b, 2)}: both sides agree.`;
    };
    const init = () => { state = { a: 0.6, b: 0.5 }; ai.value = 0.6; bi.value = 0.5; draw(); };
    const ai = slider(ui.controls, "Angle a", 0, 3.14, 0.01, 0.6, (v) => { state.a = v; draw(); });
    const bi = slider(ui.controls, "Angle b", 0, 3.14, 0.01, 0.5, (v) => { state.b = v; draw(); });
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  }

  // Area accumulator: the area so far, graphed; its slope is f (FTC). "shift" mode shows +C.
  W.accumulator = function (box, cfg) {
    const f = WidgetMath.fn(cfg.f || "cos");
    const a = cfg.a ?? 0, b = cfg.b ?? 2 * Math.PI;
    const ui = shell(box, cfg.prompt || (cfg.mode === "shift"
      ? "Shift the curve up or down. Every shifted copy has the same slopes, so the same derivative."
      : "Sweep x. The lower graph is the area so far; its slope always equals the height of f."));
    let state;
    const vals = [];
    for (let i = 0; i <= 200; i++) { const x = a + ((b - a) * i) / 200; vals.push([x, WidgetMath.accumulate(f, a, x, 300)]); }
    const Amin = Math.min(...vals.map((v) => v[1])), Amax = Math.max(...vals.map((v) => v[1]));
    const draw = () => {
      ui.svg.innerHTML = "";
      const x = state.x;
      const top = { X: (t) => 36 + ((t - a) / (b - a)) * 434, Y: (y) => 70 - y * 50 };
      const lowSpan = Math.max(Amax - Amin, 1) + (cfg.mode === "shift" ? 3 : 0);
      const low = { Y: (y) => 245 - ((y - Amin + (cfg.mode === "shift" ? 1.5 : 0)) / lowSpan) * 100 };
      el("line", { x1: 36, x2: 470, y1: top.Y(0), y2: top.Y(0), class: "w-axis" }, ui.svg);
      let d = "", shade = `M${top.X(a)} ${top.Y(0)} `;
      for (let i = 0; i <= 200; i++) {
        const t = a + ((b - a) * i) / 200;
        d += `${i ? "L" : "M"}${top.X(t)} ${top.Y(f(t))} `;
        if (t <= x) shade += `L${top.X(t)} ${top.Y(f(t))} `;
      }
      shade += `L${top.X(x)} ${top.Y(0)} Z`;
      if (cfg.mode !== "shift") el("path", { d: shade, class: "w-bar" }, ui.svg);
      el("path", { d, class: "w-curve" }, ui.svg);
      const lbl = el("text", { x: 40, y: 14, class: "w-label" }, ui.svg); lbl.textContent = "f(x)";
      const lbl2 = el("text", { x: 40, y: 140, class: "w-label" }, ui.svg); lbl2.textContent = cfg.mode === "shift" ? "F(x) + C" : "area so far, A(x)";
      const shifts = cfg.mode === "shift" ? [-1, 0, 1].map((k) => k + state.c) : [0];
      for (const c of shifts) {
        let dl = "";
        vals.forEach(([t, A], i) => { if (cfg.mode === "shift" || t <= x) dl += `${i ? "L" : "M"}${top.X(t)} ${low.Y(A + c)} `; });
        el("path", { d: dl, class: `w-curve alt${c === state.c ? "" : " faint"}` }, ui.svg);
      }
      const Ax = WidgetMath.accumulate(f, a, x, 600);
      const slope = (WidgetMath.accumulate(f, a, x + 1e-3, 600) - WidgetMath.accumulate(f, a, x - 1e-3, 600)) / 2e-3;
      const scale = 100 / lowSpan / (434 / (b - a));
      el("line", { x1: top.X(x) - 30, x2: top.X(x) + 30, y1: low.Y(Ax + state.c) + 30 * slope * scale, y2: low.Y(Ax + state.c) - 30 * slope * scale, class: "w-secant" }, ui.svg);
      el("circle", { cx: top.X(x), cy: top.Y(f(x)), r: 4, class: "w-point" }, ui.svg);
      el("circle", { cx: top.X(x), cy: low.Y(Ax + state.c), r: 4, class: "w-point" }, ui.svg);
      ui.readout.textContent = cfg.mode === "shift"
        ? `C = ${fmt(state.c, 2)}: at x = ${fmt(x, 2)} every copy has slope ${fmt(slope, 3)} = f(x).`
        : `x = ${fmt(x, 2)}: area so far = ${fmt(Ax, 3)}, its slope = ${fmt(slope, 3)}, and f(x) = ${fmt(f(x), 3)}`;
    };
    const init = () => { state = { x: (a + b) / 3, c: 0 }; xi.value = state.x; if (ci) ci.value = 0; draw(); };
    const xi = slider(ui.controls, "x", a + 0.01, b - 0.01, 0.01, (a + b) / 3, (v) => { state.x = v; draw(); });
    const ci = cfg.mode === "shift" ? slider(ui.controls, "Shift C", -1.5, 1.5, 0.05, 0, (v) => { state.c = v; draw(); }) : null;
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  };

  // Product rectangle: d(uv) = u dv + v du (+ a vanishing corner). "parts" mode: uv = ∫u dv + ∫v du.
  W["product-rectangle"] = function (box, cfg) {
    const ui = shell(box, cfg.prompt || (cfg.mode === "parts"
      ? "Move the end point. The two shaded regions always add up to the rectangle uv."
      : "Grow u and v a little. The change in area is two strips plus a tiny corner."));
    let state;
    const S = 40, x0 = 40, y0 = 235;
    if (cfg.mode === "parts") {
      const curve = (u) => 0.2 * u * u + 0.5;  // v as a function of u
      const draw = () => {
        ui.svg.innerHTML = "";
        const u1 = state.u, v1 = curve(u1);
        let under = `M${x0} ${y0} `, left = `M${x0} ${y0 - curve(0) * S} `, line = "";
        for (let i = 0; i <= 100; i++) {
          const u = (u1 * i) / 100, v = curve(u);
          under += `L${x0 + u * S} ${y0 - v * S} `;
          left += `L${x0 + u * S} ${y0 - v * S} `;
          line += `${i ? "L" : "M"}${x0 + u * S} ${y0 - v * S} `;
        }
        under += `L${x0 + u1 * S} ${y0} Z`;
        left += `L${x0} ${y0 - v1 * S} Z`;
        el("path", { d: under, class: "w-bar" }, ui.svg);
        el("path", { d: left, class: "w-tri" }, ui.svg);
        el("rect", { x: x0, y: y0 - curve(0) * S, width: 0.1, height: curve(0) * S, class: "w-rect" }, ui.svg);
        el("rect", { x: x0, y: y0 - v1 * S, width: u1 * S, height: v1 * S, class: "w-rect" }, ui.svg);
        el("path", { d: line, class: "w-curve" }, ui.svg);
        const vdu = WidgetMath.riemann(curve, 0, u1, 400);
        const udv = u1 * v1 - vdu;  // the curve starts at u = 0, so the whole is just u·v
        ui.readout.textContent = `∫u dv (gold) ${fmt(udv, 3)} + ∫v du (teal) ${fmt(vdu, 3)} = ${fmt(udv + vdu, 3)} = u·v, so ∫u dv = uv − ∫v du.`;
      };
      const init = () => { state = { u: 4 }; ui1.value = 4; draw(); };
      const ui1 = slider(ui.controls, "End point u", 0.5, 9.5, 0.1, 4, (v) => { state.u = v; draw(); });
      ui.reset.addEventListener("click", init); init();
      return { reset: init };
    }
    const draw = () => {
      ui.svg.innerHTML = "";
      const { u, v, du, dv } = state;
      el("rect", { x: x0, y: y0 - v * S, width: u * S, height: v * S, class: "w-rect" }, ui.svg);
      el("rect", { x: x0 + u * S, y: y0 - v * S, width: du * S, height: v * S, class: "w-bar" }, ui.svg);
      el("rect", { x: x0, y: y0 - (v + dv) * S, width: u * S, height: dv * S, class: "w-tri" }, ui.svg);
      el("rect", { x: x0 + u * S, y: y0 - (v + dv) * S, width: du * S, height: dv * S, class: "w-corner" }, ui.svg);
      const pc = WidgetMath.productChange(u, v, du, dv);
      ui.readout.textContent = `Δ(uv) = u·dv (gold) ${fmt(pc.udv, 3)} + v·du (teal) ${fmt(pc.vdu, 3)} + corner ${fmt(pc.corner, 4)}. The corner shrinks fastest, so d(uv) = u dv + v du.`;
    };
    const init = () => { state = { u: 4, v: 3, du: 1, dv: 1 }; gi.value = 1; draw(); };
    const gi = slider(ui.controls, "Size of the change", 0.02, 1.5, 0.01, 1, (x) => { state.du = x; state.dv = x; draw(); });
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  };

  // Chain stretch: g(x) vs g(ax). Slopes scale by a; areas by 1/a ("area" mode).
  W["chain-stretch"] = function (box, cfg) {
    const name = cfg.f || "sin";
    const g = WidgetMath.fn(name);
    const ui = shell(box, cfg.prompt || (cfg.mode === "area"
      ? "Squeeze the wave by a. One hump gets a times narrower, so its area is divided by a."
      : "Squeeze the curve by a. Its slopes get a times steeper."));
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const a = state.a;
      const P = plotArea(ui.svg, 0, 2 * Math.PI, -1.4 * (cfg.mode === "area" ? 1 : Math.max(1, a * 0.6)), 1.4 * (cfg.mode === "area" ? 1 : Math.max(1, a * 0.6)));
      P.curve(g, 0, 2 * Math.PI, "w-curve faint");
      if (cfg.mode === "area") {
        const end = Math.PI / a;
        let d = `M${P.X(0)} ${P.Y(0)} `;
        for (let i = 0; i <= 100; i++) { const x = (end * i) / 100; d += `L${P.X(x)} ${P.Y(g(a * x))} `; }
        d += `L${P.X(end)} ${P.Y(0)} Z`;
        el("path", { d, class: "w-bar" }, ui.svg);
        P.curve((x) => g(a * x), 0, 2 * Math.PI, "w-curve alt");
        ui.readout.textContent = `one hump of ${name}(${fmt(a, 2)}x) has area ${fmt(WidgetMath.stretchArea(name, a, 0, Math.PI / a), 4)} = 2 ÷ ${fmt(a, 2)}: integrating g(ax) brings out 1/a.`;
      } else {
        P.curve((x) => g(a * x), 0, 2 * Math.PI, "w-curve alt");
        const x0 = 0.4, h = 1e-5;
        const s2 = (g(a * (x0 + h)) - g(a * x0)) / h;
        ui.readout.textContent = `slope of ${name}(x) at a·x₀: ${fmt((g(a * x0 + h) - g(a * x0)) / h, 3)}; slope of ${name}(${fmt(a, 2)}x) at x₀: ${fmt(s2, 3)} = ${fmt(a, 2)} × that.`;
      }
    };
    const init = () => { state = { a: cfg.a ?? 2 }; ai.value = state.a; draw(); };
    const ai = slider(ui.controls, "Squeeze factor a", 0.5, 4, 0.05, cfg.a ?? 2, (v) => { state.a = v; draw(); });
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  };

  // Derivative ladder: polynomials step down to 0; exponentials and sines never do.
  W["derivative-ladder"] = function (box, cfg) {
    const ui = shell(box, cfg.prompt || "Differentiate again and again. Which column ever reaches 0?");
    ui.svg.setAttribute("viewBox", "0 0 480 150");
    const sup = ["", "", "²", "³", "⁴", "⁵"];
    const polyText = (c) => {
      const terms = [];
      for (let i = c.length - 1; i >= 0; i--) if (c[i]) terms.push(i === 0 ? `${c[i]}` : `${c[i] === 1 ? "" : c[i]}x${sup[i]}`);
      return terms.join(" + ") || "0";
    };
    const trig = ["sin x", "cos x", "−sin x", "−cos x"];
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const cols = [["polynomial", polyText(state.poly)], ["exponential", `${2 ** state.k === 1 ? "" : 2 ** state.k}e²ˣ`], ["sine", trig[state.k % 4]]];
      cols.forEach(([head, val], i) => {
        const x = 20 + i * 155;
        el("rect", { x, y: 30, width: 140, height: 80, rx: 10, class: `w-cell${val === "0" ? " done" : ""}` }, ui.svg);
        const t = el("text", { x: x + 70, y: 22, class: "w-label", "text-anchor": "middle" }, ui.svg); t.textContent = head;
        const v = el("text", { x: x + 70, y: 78, class: "w-big", "text-anchor": "middle" }, ui.svg); v.textContent = val;
      });
      ui.readout.textContent = `after ${state.k} derivative${state.k === 1 ? "" : "s"}: the polynomial ${state.poly.every((c) => c === 0) ? "has reached 0, so that's when parts stops" : "is getting simpler"}; the others never get simpler.`;
    };
    button(ui.controls, "Differentiate", () => { state.poly = WidgetMath.diffPoly(state.poly); state.k += 1; draw(); });
    const init = () => { state = { poly: cfg.poly || [0, 0, 0, 1], k: 0 }; draw(); };
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  };


  // Wave mixer: sines against the square wave. Modes: single, gap, product, shift, partials, zoom.
  W["wave-mixer"] = function (box, cfg) {
    const M = WidgetMath, mode = cfg.mode || "single";
    const prompts = {
      single: "Change the height and the number of wiggles per period.",
      gap: "Change the height. Compare the plain average gap with the average squared gap.",
      product: "Pick two frequencies. When they differ, the shaded areas cancel exactly.",
      shift: "Pick a frequency. The dashed curve is the second half of square·sin(nt), shifted back onto the first.",
      partials: "Add more sines and watch the sum close in on the square wave.",
      zoom: "Add sines while zoomed in on the jump. The overshoot narrows but never shrinks.",
    };
    const ui = shell(box, cfg.prompt || prompts[mode]);
    let state;
    const draw = () => {
      ui.svg.innerHTML = "";
      const zoom = mode === "zoom";
      const P = zoom ? plotArea(ui.svg, -0.15, 0.9, -0.3, 1.35)
        : mode === "shift" ? plotArea(ui.svg, 0, Math.PI, -1.3, 1.3)
        : plotArea(ui.svg, 0, 2 * Math.PI, -1.6, 1.6);
      const span = zoom ? [-0.15, 0.9] : [0, 2 * Math.PI];
      if (mode !== "product" && mode !== "shift") P.curve(M.square, span[0], span[1], "w-curve alt");
      if (mode === "single") {
        P.curve((t) => state.a * Math.sin(state.n * t), 0, 2 * Math.PI);
        ui.readout.textContent = `${fmt(state.a, 2)}·sin(${state.n}t): height ${fmt(state.a, 2)}, ${state.n} full wiggle${state.n === 1 ? "" : "s"} per 2π (period ${fmt((2 * Math.PI) / state.n, 3)}).`;
      } else if (mode === "gap") {
        const f = (t) => state.a * Math.sin(t);
        let d = "";
        for (let i = 0; i <= 240; i++) { const t = (2 * Math.PI * i) / 240; d += `M${P.X(t)} ${P.Y(f(t))} L${P.X(t)} ${P.Y(M.square(t))} `; }
        el("path", { d, class: "w-gapline" }, ui.svg);
        P.curve(f, 0, 2 * Math.PI);
        const mean = M.riemann((t) => f(t) - M.square(t), 0, 2 * Math.PI, 2000) / (2 * Math.PI);
        ui.readout.textContent = `height ${fmt(state.a, 2)}: average gap ${fmt(mean, 3)} (pluses and minuses cancel), average squared gap ${fmt(M.rmsGap(state.a) ** 2, 3)}, gap readout ${fmt(M.rmsGap(state.a), 3)}`;
      } else if (mode === "product") {
        const { m, n } = state;
        const g = (t) => Math.sin(m * t) * Math.sin(n * t);
        let pos = "", neg = "";
        for (let i = 0; i < 240; i++) {
          const t = (2 * Math.PI * i) / 240, w = (2 * Math.PI) / 240, y = g(t + w / 2);
          const r = `M${P.X(t)} ${P.Y(0)} L${P.X(t)} ${P.Y(y)} L${P.X(t + w)} ${P.Y(y)} L${P.X(t + w)} ${P.Y(0)} Z `;
          if (y >= 0) pos += r; else neg += r;
        }
        el("path", { d: pos, class: "w-bar" }, ui.svg);
        el("path", { d: neg, class: "w-bar neg" }, ui.svg);
        P.curve((t) => Math.sin(m * t), 0, 2 * Math.PI, "w-curve faint");
        P.curve((t) => Math.sin(n * t), 0, 2 * Math.PI, "w-curve alt faint");
        P.curve(g, 0, 2 * Math.PI);
        ui.readout.textContent = `∫ sin(${m}t)·sin(${n}t) over a period = ${fmt(M.productIntegral(m, n), 4)}${m === n ? " = π (same frequency)" : " (different frequencies cancel)"}`;
      } else if (mode === "shift") {
        // Overlay the second half (shifted back by π) on the first: odd n coincide, even n mirror.
        const n = state.n;
        const first = (t) => M.square(t) * Math.sin(n * t);
        const second = (t) => M.square(t + Math.PI) * Math.sin(n * (t + Math.PI));
        P.curve(first, 0.001, Math.PI - 0.001);
        P.curve(second, 0.001, Math.PI - 0.001, "w-curve alt dashed");
        const h = M.halfContributions(n);
        ui.readout.textContent = n % 2
          ? `n = ${n} (odd): the second half (dashed) lies exactly on the first, so the halves add: total ${fmt(h.total, 3)}`
          : `n = ${n} (even): the second half (dashed) is the first flipped upside down, point by point, so the halves cancel: total ${fmt(h.total, 3)}`;
      } else {
        const N = state.N;
        P.curve((t) => M.partialSum(N, t), span[0], span[1], "w-curve", zoom ? 600 : 480);
        if (zoom) el("line", { x1: P.X(span[0]), x2: P.X(span[1]), y1: P.Y(1.179), y2: P.Y(1.179), class: "w-average" }, ui.svg);
        ui.readout.textContent = zoom
          ? `${N} sines: peak ${fmt(M.peakOf(N), 3)} (dashed line: 1.179, the limit it never drops below)`
          : `${N} sine${N === 1 ? "" : "s"} (up to sin ${2 * N - 1}t): the sum hugs the square wave more closely everywhere except at the jumps.`;
      }
    };
    const inputs = [];
    const add = (...args) => inputs.push(slider(ui.controls, ...args));
    const defaults = { single: { a: 1, n: 1 }, gap: { a: 1 }, product: { m: cfg.m ?? 2, n: cfg.n ?? 3 }, shift: { n: 2 }, partials: { N: 3 }, zoom: { N: 5 } }[mode];
    if (mode === "single") { add("Height", 0, 1.6, 0.01, 1, (v) => { state.a = v; draw(); }); add("Wiggles per period", 1, 6, 1, 1, (v) => { state.n = v; draw(); }); }
    if (mode === "gap") add("Height of sin t", 0, 1.8, 0.01, 1, (v) => { state.a = v; draw(); });
    if (mode === "product") { add("First frequency m", 1, 5, 1, defaults.m, (v) => { state.m = v; draw(); }); add("Second frequency n", 1, 5, 1, defaults.n, (v) => { state.n = v; draw(); }); }
    if (mode === "shift") add("Frequency n", 1, 6, 1, 2, (v) => { state.n = v; draw(); });
    if (mode === "partials" || mode === "zoom") add("Number of sines", 1, 60, 1, defaults.N, (v) => { state.N = v; draw(); });
    const init = () => { state = { ...defaults }; inputs.forEach((x, i) => (x.value = Object.values(defaults)[i])); draw(); };
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  };

  // Parabola minimum: the square-wave error E(a) is a parabola; its lowest point is the best height.
  W["parabola-min"] = function (box, cfg) {
    const M = WidgetMath;
    const ui = shell(box, cfg.prompt || (cfg.mode === "projection"
      ? "The best height is (area of square·sin) ÷ (area of sin²). Move a and see why nothing beats it."
      : "Drag a. The average squared gap traces a parabola; its lowest point is the best fit."));
    let state;
    const best = 4 / Math.PI;
    const draw = () => {
      ui.svg.innerHTML = "";
      const P = plotArea(ui.svg, 0, 2.4, 0, 1.2);
      P.curve(M.errorParabola, 0, 2.4);
      const a = state.a, E = M.errorParabola(a), slope = a - 4 / Math.PI;
      el("line", { x1: P.X(a - 0.4), x2: P.X(a + 0.4), y1: P.Y(E - 0.4 * slope), y2: P.Y(E + 0.4 * slope), class: "w-secant" }, ui.svg);
      el("line", { x1: P.X(best), x2: P.X(best), y1: P.Y(0), y2: P.Y(M.errorParabola(best)), class: "w-average" }, ui.svg);
      el("circle", { cx: P.X(a), cy: P.Y(E), r: 6, class: "w-point" }, ui.svg);
      const t = el("text", { x: P.X(best) + 6, y: P.Y(0) - 8, class: "w-label" }, ui.svg);
      t.textContent = "4/π";
      ui.readout.textContent = cfg.mode === "projection"
        ? `a = ${fmt(a, 3)}: E = ${fmt(E, 4)}. Best: ∫square·sin ÷ ∫sin² = 4 ÷ π = ${fmt(best, 4)}, where E bottoms out at ${fmt(M.errorParabola(best), 4)}.`
        : `a = ${fmt(a, 3)}: average squared gap E = ${fmt(E, 4)}, slope dE/da = ${fmt(slope, 4)}${Math.abs(slope) < 0.005 ? " (flat: the minimum)" : ""}`;
    };
    const init = () => { state = { a: 1 }; ai.value = 1; draw(); };
    const ai = slider(ui.controls, "Height a", 0, 2.4, 0.005, 1, (v) => { state.a = v; draw(); });
    ui.reset.addEventListener("click", init); init();
    return { reset: init };
  };

  const Widgets = {
    types: () => Object.keys(W),
    render(type, container, config) {
      if (!W[type]) {
        container.innerHTML = `<p class="why-placeholder">Interactive coming soon: ${type}</p>`;
        return { reset() {} };
      }
      return W[type](container, config || {});
    },
  };

  root.WidgetMath = WidgetMath;
  root.Widgets = Widgets;
})(typeof window !== "undefined" ? window : globalThis);
