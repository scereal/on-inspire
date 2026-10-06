// One scene renderer per framework. Each takes (container, problem) and returns a controller:
//   update(param, value)  redraws for a slider value (projectile)
//   bench                 the interactive cups (mixing), or undefined
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const svgEl = (name, attrs = {}) => {
    const n = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  };
  const fmt = (v, d = 2) => Number(v).toFixed(d).replace(/\.?0+$/, "");

  // Integral: the problem itself is the scene ------------------------------------
  function integral(box, problem) {
    const s = problem.scene;
    box.innerHTML = `<div class="integral-scene">$$${s.tex}$$</div>` + (s.rule ? `<p class="rule">The rule: $${s.rule}$</p>` : "");
    return {};
  }

  // Projectile: draw the arc for the current slider value -------------------------
  function projectile(box, problem) {
    const s = problem.scene;
    const step = problem.steps.find((st) => st.format === "slider");
    const W = 640, H = 300, PAD = 28;
    const launch = (value) => {
      const p = { vx: s.fixed.vx ?? 0, vy: s.fixed.vy ?? 0 };
      if (s.slider === "vx") p.vx = value;
      if (s.slider === "vy") p.vy = value;
      if (s.slider === "angle") {
        const a = (value * Math.PI) / 180;
        p.vx = s.fixed.speed * Math.cos(a);
        p.vy = s.fixed.speed * Math.sin(a);
      }
      return p;
    };
    const flight = ({ vx, vy }) => {
      // time to reach the ground from height y0
      const t = (vy + Math.sqrt(vy * vy + 2 * s.g * s.y0)) / s.g;
      return { t, land: vx * t, apex: s.y0 + (vy > 0 ? (vy * vy) / (2 * s.g) : 0) };
    };
    const best = flight(launch(step.answer));
    const xMax = Math.max((s.target || 0) * 1.35, s.wall ? s.wall.x * 1.8 : 0, best.land * 1.1, 2);
    const yMax = Math.max(best.apex * 1.35, s.wall ? s.wall.h * 1.4 : 0, s.y0 * 1.2, 1);
    const k = Math.min((W - 2 * PAD) / xMax, (H - 2 * PAD) / yMax);
    const X = (x) => PAD + x * k;
    const Y = (y) => H - PAD - y * k;

    const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Launch scene" });
    const color = problem.theme?.visuals?.color || "#d4b06a";
    svg.append(svgEl("line", { x1: 0, x2: W, y1: Y(0), y2: Y(0), class: "ground" }));
    if (s.y0 > 0) svg.append(svgEl("rect", { x: 0, y: Y(s.y0), width: X(0), height: s.y0 * k, class: "ledge" }));
    if (s.target != null) {
      svg.append(svgEl("rect", { x: X(s.target - s.radius), y: Y(0) - 3, width: Math.max(2 * s.radius * k, 6), height: 6, class: "target" }));
      const lbl = svgEl("text", { x: X(s.target), y: Y(0) + 18, class: "tick", "text-anchor": "middle" });
      lbl.textContent = `${fmt(s.target)} m`;
      svg.append(lbl);
    }
    if (s.wall) {
      svg.append(svgEl("rect", { x: X(s.wall.x) - 4, y: Y(s.wall.h), width: 8, height: s.wall.h * k, class: "wall" }));
      const lbl = svgEl("text", { x: X(s.wall.x), y: Y(s.wall.h) - 8, class: "tick", "text-anchor": "middle" });
      lbl.textContent = `${fmt(s.wall.h)} m`;
      svg.append(lbl);
    }
    const path = svgEl("path", { class: "arc", stroke: color });
    const ball = svgEl("circle", { r: 6, fill: color });
    const readout = svgEl("text", { x: W - PAD, y: PAD, class: "tick readout", "text-anchor": "end" });
    svg.append(path, ball, readout);
    box.replaceChildren(svg);

    const update = (_param, value) => {
      const p = launch(value);
      const f = flight(p);
      const tEnd = s.wall ? Math.min(f.t, (xMax / Math.max(p.vx, 1e-6))) : f.t;
      let d = "";
      for (let i = 0; i <= 120; i++) {
        const t = (tEnd * i) / 120;
        const x = p.vx * t, y = s.y0 + p.vy * t - 0.5 * s.g * t * t;
        if (x > xMax) break;
        d += `${i ? "L" : "M"}${X(x).toFixed(1)} ${Y(Math.max(y, 0)).toFixed(1)} `;
      }
      path.setAttribute("d", d);
      const landX = Math.min(f.land, xMax);
      ball.setAttribute("cx", X(landX));
      ball.setAttribute("cy", Y(0) - 6);
      if (s.wall) {
        const tw = s.wall.x / Math.max(p.vx, 1e-6);
        const yw = s.y0 + p.vy * tw - 0.5 * s.g * tw * tw;
        readout.textContent = `At the wall: ${fmt(yw)} m high`;
      } else {
        readout.textContent = `Lands at ${fmt(f.land)} m`;
      }
    };
    update(null, step.slider.min + (step.slider.max - step.slider.min) * 0.25);
    return { update };
  }

  // Bounce: the first few bounces drawn to scale ----------------------------------
  function bounce(box, problem) {
    const s = problem.scene;
    const W = 640, H = 260, PAD = 26;
    const color = s.color || problem.theme?.visuals?.color || "#d4b06a";
    const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Bounce heights for r = ${s.r}` });
    const Y = (y) => H - PAD - (y / s.h) * (H - 2 * PAD - 10);
    svg.append(svgEl("line", { x1: 0, x2: W, y1: Y(0), y2: Y(0), class: "ground" }));
    let x = PAD + 10, d = `M${x} ${Y(s.h)}`, height = s.h;
    const firstDrop = 50;
    x += firstDrop * 0.4;
    d += ` Q ${x - 4} ${Y(s.h * 0.3)} ${x} ${Y(0)}`;
    for (let i = 0; i < 9 && height > s.h * 0.01; i++) {
      height *= s.r;
      const span = 40 + 90 * Math.sqrt(height / s.h);
      d += ` Q ${x + span / 2} ${Y(height * 2)} ${x + span} ${Y(0)}`;
      // Bounce heights are the answers, so they stay unlabeled.
      x += span;
      if (x > W - PAD) break;
    }
    svg.append(svgEl("path", { d, class: "arc", stroke: color }));
    svg.append(svgEl("circle", { cx: PAD + 10, cy: Y(s.h), r: 8, fill: color }));
    const t0 = svgEl("text", { x: PAD + 24, y: Y(s.h) + 4, class: "tick" });
    t0.textContent = `${fmt(s.h)} m`;
    svg.append(t0);
    box.replaceChildren(svg);
    return {};
  }

  // Rate: the graph of the quantity, with the secant over [t1, t2] ----------------
  function rate(box, problem) {
    const s = problem.scene;
    const W = 640, H = 280, PAD = 34;
    const color = problem.theme?.visuals?.color || "#d4b06a";
    const ts = s.curve.map((p) => p[0]), ys = s.curve.map((p) => p[1]);
    const tMax = Math.max(...ts), yMax = Math.max(...ys);
    // Start the axis at 0 unless that would flatten the curve (a town of 1000+ people growing by a few hundred).
    const lo = Math.min(...ys), yMin = lo >= 0 && lo < 0.5 * yMax ? 0 : lo - 0.1 * (yMax - lo);
    const X = (t) => PAD + (t / tMax) * (W - 2 * PAD);
    const Y = (y) => H - PAD - ((y - yMin) / (yMax - yMin || 1)) * (H - 2 * PAD);
    const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Graph of ${s.symbol}(t) with the secant from t = ${s.t1} to t = ${s.t2}` });
    const base = H - PAD;
    svg.append(svgEl("line", { x1: PAD, x2: W - PAD, y1: base, y2: base, class: "ground" }));
    svg.append(svgEl("path", { d: s.curve.map((p, i) => `${i ? "L" : "M"}${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" "), class: "arc", stroke: color }));
    // The two readings are part of the answer, so the secant is drawn but its endpoints stay unlabeled.
    svg.append(svgEl("line", { x1: X(s.t1), y1: Y(s.y1), x2: X(s.t2), y2: Y(s.y2), class: "arc secant", stroke: "var(--gold)", "stroke-dasharray": "8 6" }));
    for (const [t, y] of [[s.t1, s.y1], [s.t2, s.y2]]) {
      svg.append(svgEl("line", { x1: X(t), x2: X(t), y1: Y(y), y2: base, class: "ground", "stroke-dasharray": "3 5" }));
      svg.append(svgEl("circle", { cx: X(t), cy: Y(y), r: 7, fill: "var(--gold)" }));
      const label = svgEl("text", { x: X(t), y: base + 26, class: "tick", "text-anchor": "middle", style: "font-size: 22px" });
      label.textContent = `t = ${fmt(t)}`;
      svg.append(label);
    }
    box.replaceChildren(svg);
    box.append(Object.assign(document.createElement("p"), { className: "rule", textContent: `$${s.symbol}(t) = ${s.tex}$` }));
    return {};
  }

  // Graph: pieces of a function with open/closed dots, for reading limits off a graph --
  function graph(box, problem) {
    const s = problem.scene;
    const W = 640, H = 340, PAD = 38;
    const X = (x) => PAD + ((x - s.xmin) / (s.xmax - s.xmin)) * (W - 2 * PAD);
    const Y = (y) => H - PAD - ((y - s.ymin) / (s.ymax - s.ymin)) * (H - 2 * PAD);
    const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": s.label || "Graph of f" });
    const tickStyle = "font-size: 17px";
    const span = s.ymax - s.ymin, every = span <= 7 ? 1 : span <= 14 ? 2 : 5;
    for (let gx = Math.ceil(s.xmin); gx <= s.xmax; gx++) {
      svg.append(svgEl("line", { x1: X(gx), x2: X(gx), y1: PAD, y2: H - PAD, stroke: "rgba(243, 234, 214, 0.08)" }));
    }
    for (let gy = Math.ceil(s.ymin); gy <= s.ymax; gy++) {
      svg.append(svgEl("line", { x1: PAD, x2: W - PAD, y1: Y(gy), y2: Y(gy), stroke: "rgba(243, 234, 214, 0.08)" }));
      if (gy !== 0 && gy % every === 0) {
        const t = svgEl("text", { x: X(0) - 8, y: Y(gy) + 7, class: "tick", "text-anchor": "end", style: tickStyle });
        t.textContent = gy;
        svg.append(t);
      }
    }
    svg.append(svgEl("line", { x1: PAD, x2: W - PAD, y1: Y(0), y2: Y(0), class: "ground" }));
    svg.append(svgEl("line", { x1: X(0), x2: X(0), y1: PAD, y2: H - PAD, class: "ground" }));
    if (s.mark !== undefined) {
      svg.append(svgEl("line", { x1: X(s.mark), x2: X(s.mark), y1: PAD, y2: H - PAD, class: "ground", "stroke-dasharray": "4 6" }));
      const t = svgEl("text", { x: X(s.mark), y: H - PAD + 26, class: "tick", "text-anchor": "middle", style: tickStyle });
      t.textContent = `x = ${s.mark}`;
      svg.append(t);
    }
    for (const piece of s.pieces) {
      svg.append(svgEl("path", { d: piece.map((p, i) => `${i ? "L" : "M"}${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" "), class: "arc", stroke: "var(--aurora)" }));
    }
    for (const d of s.dots || []) {
      svg.append(svgEl("circle", { cx: X(d.x), cy: Y(d.y), r: 7, fill: d.open ? "var(--void, #0b1416)" : "var(--gold)", stroke: "var(--gold)", "stroke-width": 2.5 }));
    }
    box.replaceChildren(svg);
    return {};
  }

  // Mixing: two marked cups the learner pours between ------------------------------
  const gcd = (a, b) => (b ? gcd(b, a % b) : Math.abs(a));
  const frac = (n, d) => { const g = gcd(n, d) || 1; return { n: n / g, d: d / g }; };
  const add = (a, b) => frac(a.n * b.d + b.n * a.d, a.d * b.d);
  const sub = (a, b) => frac(a.n * b.d - b.n * a.d, a.d * b.d);
  const div = (a, k) => frac(a.n, a.d * k);
  const show = (f) => (f.n === 0 ? "0" : f.n === f.d ? "1 (pure)" : `${f.n}/${f.d}`);
  const parse = (s) => { const [n, d = "1"] = String(s).split("/"); return frac(Number(n), Number(d)); };

  function mixing(box, problem) {
    const s = problem.scene;
    const caps = s.cups;
    const color = s.color || "#b06222";
    let cups = [{ v: 0, c: frac(0, 1) }, { v: 0, c: frac(0, 1) }];
    let history = [], enabled = false, onChange = () => {};
    const wrap = document.createElement("div");
    wrap.className = "bench";
    const views = caps.map((cap, i) => {
      const cell = document.createElement("div");
      cell.className = "cup";
      cell.innerHTML = `<div class="name">Cup ${"AB"[i]}</div>`;
      const svg = svgEl("svg", { viewBox: "0 0 120 170", role: "img" });
      const liquid = svgEl("rect", { x: 22, width: 76, rx: 3 });
      svg.append(liquid, svgEl("path", { d: "M16 12 L22 158 L98 158 L104 12", class: "glass" }));
      for (let m = 1; m <= cap; m++) {
        const y = 158 - (m / cap) * 146;
        svg.append(svgEl("line", { x1: 92, x2: 102, y1: y, y2: y, class: "mark" }));
      }
      const reading = document.createElement("div");
      reading.className = "reading";
      const acts = document.createElement("div");
      acts.className = "acts";
      const btn = (label, action) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = label;
        b.addEventListener("click", () => act(action, i));
        acts.append(b);
        return b;
      };
      const buttons = [btn("Add concentrate", "concentrate"), btn("Add water", "water"), btn(`Pour into ${"BA"[i]}`, "pour"), btn("Empty", "empty")];
      cell.append(svg, reading, acts);
      wrap.append(cell);
      return { liquid, reading, buttons, cap };
    });
    const tools = document.createElement("div");
    tools.className = "row center";
    const undo = Object.assign(document.createElement("button"), { type: "button", textContent: "Undo" });
    const reset = Object.assign(document.createElement("button"), { type: "button", textContent: "Start over" });
    tools.append(undo, reset);
    box.replaceChildren(wrap, tools);

    const strength = (cup) => (cup.v ? div(cup.c, cup.v) : null);
    const mixColor = (f) => {
      const k = f ? f.n / f.d : 0;
      const a = [168, 208, 214];
      const b = [parseInt(color.slice(1, 3), 16), parseInt(color.slice(3, 5), 16), parseInt(color.slice(5, 7), 16)];
      return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * k)).join(",")})`;
    };
    const legal = (action, i) => {
      const cup = cups[i], other = cups[1 - i];
      if (action === "concentrate" || action === "water") return cup.v < caps[i];
      if (action === "pour") return cup.v >= 1 && other.v < caps[1 - i];
      return cup.v > 0;
    };
    const paint = () => {
      views.forEach((view, i) => {
        const cup = cups[i];
        const hgt = (cup.v / view.cap) * 146;
        view.liquid.setAttribute("y", 158 - hgt);
        view.liquid.setAttribute("height", hgt);
        view.liquid.setAttribute("fill", mixColor(strength(cup)));
        view.reading.textContent = cup.v ? `${show(strength(cup))} concentrate, ${cup.v} of ${view.cap} marks` : "Empty";
        ["concentrate", "water", "pour", "empty"].forEach((a, j) => (view.buttons[j].disabled = !enabled || !legal(a, i)));
      });
      undo.disabled = !enabled || !history.length;
      reset.disabled = !enabled;
    };
    const act = (action, i) => {
      if (!enabled || !legal(action, i)) return;
      history.push(cups.map((c) => ({ ...c })));
      const cup = cups[i], other = cups[1 - i];
      if (action === "concentrate") { cup.v += 1; cup.c = add(cup.c, frac(1, 1)); }
      if (action === "water") cup.v += 1;
      if (action === "pour") {
        const moved = div(cup.c, cup.v);
        cup.v -= 1; cup.c = cup.v ? sub(cup.c, moved) : frac(0, 1);
        other.v += 1; other.c = add(other.c, moved);
      }
      if (action === "empty") { cup.v = 0; cup.c = frac(0, 1); }
      paint();
      onChange(cups.map(strength), history.length);
    };
    undo.addEventListener("click", () => { if (history.length) { cups = history.pop(); paint(); onChange(cups.map(strength), history.length); } });
    reset.addEventListener("click", () => { cups = [{ v: 0, c: frac(0, 1) }, { v: 0, c: frac(0, 1) }]; history = []; paint(); onChange([null, null], 0); });
    paint();
    return {
      bench: {
        enable(fn) { enabled = true; onChange = fn; paint(); },
        disable() { enabled = false; paint(); },
        matches(strengths, target) { const t = parse(target); return strengths.some((x) => x && x.n === t.n && x.d === t.d); },
      },
    };
  }

  window.Scenes = { integral, projectile, bounce, mixing, rate, graph };
})();
