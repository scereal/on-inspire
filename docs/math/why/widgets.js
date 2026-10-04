// Interactive widgets for the "Why?" panel. Spec: design/specs/2026-10-04-why-network-design.md §4.
// WidgetMath holds the pure math (tested in tests/widget_math_test.js); Widgets.render draws each widget.
(function (root) {
  // Pure math -----------------------------------------------------------------------
  const FUNCTIONS = {
    square: (x) => x * x,
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
    const p0 = el("circle", { r: 5, class: "w-point" }, ui.svg);
    const p1 = el("circle", { r: 5, class: "w-point alt" }, ui.svg);
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
