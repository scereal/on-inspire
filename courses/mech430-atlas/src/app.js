// MECH 430 Atlas: concept map, concept pages, the flow lab, the coding track, practice and drills.
(function () {
  const A = window.ATLAS;
  const byId = {}, usedBy = {};
  A.concepts.forEach((c) => { byId[c.id] = c; usedBy[c.id] = []; });
  A.concepts.forEach((c) => c.deeper.forEach((d) => usedBy[d].push(c.id)));
  const allProblems = A.concepts.flatMap((c) => c.problems.map((p) => ({ p, c })));
  const probById = {};
  allProblems.forEach(({ p, c }) => { probById[p.id] = { p, c }; });
  const $main = document.getElementById("main");

  // ---------- storage (per browser, best effort) ----------
  const KEY = "mech430-atlas:v1";
  let progress = {};
  try { progress = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { progress = {}; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (e) { /* private mode */ } };
  const solved = (pid) => !!(progress[pid] && progress[pid].at);
  const missed = (pid) => !!(progress[pid] && progress[pid].first === false);
  const conceptStats = (c) => ({ done: c.problems.filter((p) => solved(p.id)).length, total: c.problems.length });
  const codeKey = (pid, i) => `code:${pid}:${i}`;
  const getDraft = (k) => { try { return localStorage.getItem(KEY + ":" + k); } catch (e) { return null; } };
  const setDraft = (k, v) => { try { localStorage.setItem(KEY + ":" + k, v); } catch (e) { /* ignore */ } };

  // ---------- graph helpers ----------
  function closure(id, next) {
    const out = new Set();
    const walk = (i) => next(i).forEach((d) => { if (!out.has(d)) { out.add(d); walk(d); } });
    walk(id);
    return out;
  }
  const ancestors = (id) => closure(id, (i) => byId[i].deeper);
  const descendants = (id) => closure(id, (i) => usedBy[i]);
  function postOrder(ids) {
    const order = [], seen = new Set();
    const visit = (i) => { if (seen.has(i)) return; seen.add(i); byId[i].deeper.forEach(visit); order.push(i); };
    ids.forEach(visit);
    return order;
  }
  const pathTo = (id) => postOrder([id]);
  const courseOrder = () => postOrder(A.concepts.filter((c) => c.layer >= 1).map((c) => c.id));

  // ---------- text rendering ----------
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const KW = new Set("False None True and as assert break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield".split(" "));
  const BUILTIN = new Set("print len range abs min max sum sorted list dict tuple set float int str zip enumerate map isinstance round".split(" "));
  function highlight(code) {
    const re = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|[rfb]?"(?:\\.|[^"\\\n])*"|[rfb]?'(?:\\.|[^'\\\n])*')|(\b\d+(?:\.\d+)?(?:e[-+]?\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)|([\s\S])/g;
    let out = "", m;
    while ((m = re.exec(code))) {
      if (m[1]) out += `<span class="tk-c">${esc(m[1])}</span>`;
      else if (m[2]) out += `<span class="tk-s">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="tk-n">${esc(m[3])}</span>`;
      else if (m[4]) {
        const w = m[4], after = code.slice(re.lastIndex).match(/^\s*\(/);
        out += KW.has(w) ? `<span class="tk-k">${w}</span>` : BUILTIN.has(w) ? `<span class="tk-b">${w}</span>` : after ? `<span class="tk-f">${w}</span>` : w;
      } else out += esc(m[5]);
    }
    return out;
  }
  const codeBlock = (code, label) => `<div class="codeblock">${label ? `<div class="code-label">${esc(label)}</div>` : ""}<button type="button" class="copy" data-copy>Copy</button><pre><code>${highlight(code)}</code></pre></div>`;
  function inline(s) {
    const keep = [];
    const stash = (html) => { keep.push(html); return `\u0000${keep.length - 1}\u0000`; };
    let t = String(s).replace(/`([^`\n]+)`/g, (m, c) => stash(`<code class="ic">${esc(c)}</code>`));
    t = t.replace(/\$\$[\s\S]+?\$\$|\$[^$\n]+?\$/g, (m) => stash(esc(m)));
    t = t.replace(/\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)/g, (m, txt, url) => stash(`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(txt)}</a>`));
    t = t.replace(/\[\[([a-z][a-z0-9]*-[a-z0-9-]+)(?:\|([^\]]+))?\]\]/g, (m, id, shown) => stash(`<a class="inline-link" href="#/c/${id}">${esc(shown || (byId[id] ? byId[id].short : id))}</a>`));
    t = esc(t);
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*\w])\*([^*\s][^*]*?)\*/g, "$1<em>$2</em>");
    return t.replace(/\u0000(\d+)\u0000/g, (m, i) => keep[+i]);
  }
  function md(text) {
    const codes = [];
    String(text).replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => { codes.push(code.replace(/\n$/, "")); return ""; });
    const segs = String(text).split(/```\w*\n[\s\S]*?```/g);
    return segs.map((seg, i) => mdBlocks(seg) + (codes[i] !== undefined ? codeBlock(codes[i]) : "")).join("");
  }
  function mdBlocks(text) {
    return text.split(/\n\s*\n/).map((block) => {
      const lines = block.trim().split("\n").filter((l) => l.length);
      if (!lines.length) return "";
      if (lines.every((l) => l.trim().startsWith("|"))) {
        const rows = lines.filter((l) => !/^\|\s*:?-/.test(l.trim())).map((l) => l.trim().replace(/^\||\|$/g, "").split("|"));
        const [head, ...body] = rows;
        return `<div class="tablewrap"><table><thead><tr>${head.map((h) => `<th>${inline(h.trim())}</th>`).join("")}</tr></thead><tbody>${body.map((r) => `<tr>${r.map((d) => `<td>${inline(d.trim())}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
      }
      const listAt = lines.findIndex((l) => /^\s*(- |\d+\. )/.test(l));
      if (listAt >= 0 && lines.slice(listAt).every((l) => /^\s*(- |\d+\. )/.test(l) || /^\s{2,}\S/.test(l))) {
        const items = [];
        lines.slice(listAt).forEach((l) => { if (/^\s*(- |\d+\. )/.test(l)) items.push(l.replace(/^\s*(- |\d+\. )/, "")); else items[items.length - 1] += " " + l.trim(); });
        const tag = /^\s*\d+\. /.test(lines[listAt]) ? "ol" : "ul";
        const pre = listAt > 0 ? `<p>${inline(lines.slice(0, listAt).join(" "))}</p>` : "";
        return pre + `<${tag}>${items.map((it) => `<li>${inline(it)}</li>`).join("")}</${tag}>`;
      }
      return `<p>${inline(lines.join(" "))}</p>`;
    }).join("");
  }
  function typeset(el) {
    const run = () => window.MathJax.typesetPromise([el]).catch(() => {});
    if (window.MathJax && window.MathJax.typesetPromise) run();
    else { let n = 0; const t = setInterval(() => { n++; if (window.MathJax && window.MathJax.typesetPromise) { clearInterval(t); run(); } else if (n > 100) clearInterval(t); }, 100); }
  }

  // ---------- a small expression language (no eval) ----------
  // Grammar: sum := prod (('+'|'-') prod)* ; prod := unary (('*'|'/') unary)* ; unary := ('-'|'+') unary | pow ;
  // pow := atom (('**'|'^') unary)? ; atom := number | name | name '(' sum ')' | '(' sum ')'
  const FN = { sin: Math.sin, cos: Math.cos, tan: Math.tan, asin: Math.asin, acos: Math.acos, atan: Math.atan, exp: Math.exp, log: Math.log, ln: Math.log,
    sqrt: Math.sqrt, abs: Math.abs, cot: (v) => 1 / Math.tan(v), sec: (v) => 1 / Math.cos(v), csc: (v) => 1 / Math.sin(v) };
  const CONST = { pi: Math.PI, e: Math.E, E: Math.E };
  function compile(src, vars) {
    const s = String(src).replace(/[−–]/g, "-").replace(/[×·]/g, "*").replace(/π/g, "pi").replace(/γ/g, "gamma");
    const toks = [];
    const re = /\s*(?:(\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|(\*\*|[-+*/^(),]))/y;
    let pos = 0, m;
    while (pos < s.length) {
      re.lastIndex = pos;
      if (!(m = re.exec(s))) { if (/^\s*$/.test(s.slice(pos))) break; return { error: `I can't read "${s.slice(pos).trim().slice(0, 8)}".` }; }
      pos = re.lastIndex;
      toks.push(m[1] !== undefined ? { t: "n", v: parseFloat(m[1]) } : m[2] !== undefined ? { t: "id", v: m[2] } : { t: m[3] });
    }
    let i = 0;
    const peek = () => toks[i], take = () => toks[i++];
    const fail = (msg) => { throw new Error(msg); };
    function sum() { let a = prod(); while (peek() && (peek().t === "+" || peek().t === "-")) { const op = take().t, b = prod(), x = a; a = op === "+" ? (env) => x(env) + b(env) : (env) => x(env) - b(env); } return a; }
    function prod() {
      let a = unary();
      for (;;) {
        const t = peek();
        if (t && (t.t === "*" || t.t === "/")) { const op = take().t, b = unary(), x = a; a = op === "*" ? (env) => x(env) * b(env) : (env) => x(env) / b(env); }
        else if (t && (t.t === "n" || t.t === "id" || t.t === "(")) fail("Write multiplication explicitly with *, e.g. 2*M rather than 2M.");
        else return a;
      }
    }
    function unary() { const t = peek(); if (t && (t.t === "-" || t.t === "+")) { take(); const a = unary(); return t.t === "-" ? (env) => -a(env) : a; } return pow(); }
    function pow() { const a = atom(), t = peek(); if (t && (t.t === "**" || t.t === "^")) { take(); const b = unary(); return (env) => Math.pow(a(env), b(env)); } return a; }
    function atom() {
      const t = take();
      if (!t) fail("The expression ends too early.");
      if (t.t === "n") return () => t.v;
      if (t.t === "(") { const a = sum(); if (!peek() || take().t !== ")") fail("A bracket isn't closed."); return a; }
      if (t.t === "id") {
        if (peek() && peek().t === "(") {
          const f = FN[t.v];
          if (!f) fail(`I don't know the function "${t.v}".`);
          take(); const a = sum(); if (!peek() || take().t !== ")") fail("A bracket isn't closed.");
          return (env) => f(a(env));
        }
        if (vars.includes(t.v)) return (env) => env[t.v];
        if (t.v in CONST) return () => CONST[t.v];
        fail(`I don't know "${t.v}". Use ${vars.map((v) => "`" + v + "`").join(", ")}.`);
      }
      fail("Something is missing before " + (t.t || "this") + ".");
    }
    try { const f = sum(); if (i < toks.length) fail("There's something extra at the end."); return { fn: f }; } catch (e) { return { error: e.message }; }
  }
  function sameExpr(step, src) {
    const mine = compile(src, step.vars);
    if (mine.error) return { ok: false, msg: mine.error };
    const ref = compile(step.ref, step.vars);
    for (let k = 0; k < 10; k++) {
      const env = {};
      step.vars.forEach((v) => { const [a, b] = step.ranges[v] || [0.5, 2.5]; env[v] = a + (b - a) * (0.11 + 0.78 * Math.random()); });
      const u = mine.fn(env), w = ref.fn(env);
      if (!isFinite(u) || Math.abs(u - w) > 1e-6 * Math.max(1, Math.abs(w))) return { ok: false, msg: "Not equivalent to the answer." };
    }
    return { ok: true };
  }
  function parseNum(raw) {
    const r = compile(String(raw).replace(/,/g, "").replace(/[°%]/g, ""), []);
    if (r.error) return NaN;
    try { return r.fn({}); } catch (e) { return NaN; }
  }
  function close(raw, v, ans, tol) {
    if (!isFinite(v)) return false;
    if (ans === 0) return Math.abs(v) <= Math.max(tol, 1e-3);
    if (Math.abs(v - ans) <= tol * Math.abs(ans)) return true;
    const m = String(raw).trim().match(/^-?(\d*)\.?(\d*)$/);
    if (m && (m[1] + m[2]).replace(/^0+/, "").length >= 2) return Math.abs(v - ans) <= 0.5 * Math.pow(10, -m[2].length) * 1.0001;
    return false;
  }
  const fmt = (x) => { const a = Math.abs(x); return a !== 0 && (a < 0.01 || a >= 1e5) ? x.toPrecision(4) : String(Math.round(x * 10000) / 10000); };
  const normBlank = (s, mode) => mode === "text" ? String(s).trim().toLowerCase().replace(/[-\s]+/g, " ") : String(s).replace(/\s+/g, "");

  // ---------- dial models (mirror content/lib.py DIAL_MODELS) ----------
  const DIAL = {
    A_Astar: (x, a) => Gas.A_Astar(x, a.g || 1.4), p_p0: (x, a) => 1 / Gas.p0_p(x, a.g || 1.4), T_T0: (x, a) => 1 / Gas.T0_T(x, a.g || 1.4),
    mass_flux: (x) => Gas.mass_flux(x) / Gas.mass_flux(1), ns_p2p1: (x) => Gas.ns_p2p1(x), ns_p02p01: (x) => Gas.ns_p02p01(x),
    fanno_fL: (x) => Gas.fanno_fL(x), ray_T0: (x) => Gas.ray_T0(x), pm_nu: (x) => Gas.pm_nu(x), mach_angle: (x) => Gas.mach_angle(x),
    ob_delta: (x, a) => Gas.ob_delta(a.M, x), nozzle_shock: (x, a) => { const n = Gas.nozzle(a.AeAt, x); return n.regime === "shock" ? n.As : NaN; },
    piston: (x, a) => Gas.piston_shock_mach(x / a.c),
  };
  window.__atlasDial = DIAL;

  // ---------- Python in the browser (Skulpt, loaded on first use) ----------
  let skulpt = null;
  function loadScript(src) { return new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = () => rej(new Error("load failed: " + src)); document.head.appendChild(s); }); }
  function loadPython() {
    if (!skulpt) skulpt = loadScript("https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt.min.js").then(() => loadScript("https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt-stdlib.js"));
    return skulpt;
  }
  async function runPython(src) {
    await loadPython();
    let out = "";
    window.Sk.configure({
      output: (t) => { out += t; },
      read: (f) => { if (!window.Sk.builtinFiles || !window.Sk.builtinFiles.files[f]) throw new Error("File not found: '" + f + "'"); return window.Sk.builtinFiles.files[f]; },
      __future__: window.Sk.python3, execLimit: 8000,
    });
    try { await window.Sk.misceval.asyncToPromise(() => window.Sk.importMainWithBody("<exercise>", false, src, true)); return { out }; }
    catch (e) { return { out, error: String(e.toString ? e.toString() : e) }; }
  }
  window.__atlasRunPython = runPython;
  function parseReport(text) {
    return text.split("\n").filter((l) => /^(PASS|FAIL) /.test(l)).map((l) => { const [head, got, want] = l.split(" | "); return { ok: head.startsWith("PASS"), label: head.slice(5), got: (got || "").replace(/^got /, ""), want: (want || "").replace(/^want /, "") }; });
  }

  // ---------- small UI pieces ----------
  const meter = (c) => { const s = conceptStats(c); return `<span class="meter" aria-hidden="true"><b style="width:${(100 * s.done) / s.total}%"></b></span>`; };
  const chip = (c) => {
    const s = conceptStats(c);
    return `<a class="chip ${s.done === s.total ? "done" : ""}" href="#/c/${c.id}" data-id="${c.id}" title="${esc(c.title)}"><span>${esc(c.short)}</span>${meter(c)}<span class="sr-only">${s.done} of ${s.total} solved</span></a>`;
  };
  const kindTag = (k) => k === "notes" ? `<span class="ptag notes">Worked example from the notes</span>` : k === "variant" ? `<span class="ptag variant">Problem-set skill, new numbers</span>` : "";
  function updatePill() {
    const n = allProblems.filter(({ p }) => solved(p.id)).length;
    document.getElementById("progress-pill").textContent = `${n} / ${allProblems.length} solved`;
  }
  function setNav(which) { document.querySelectorAll("[data-nav]").forEach((a) => { if (a.dataset.nav === which) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); }); }

  // ---------- map ----------
  function renderMap() {
    setNav("map");
    const groupsOf = (layer) => { const g = new Map(); A.concepts.filter((c) => c.layer === layer).forEach((c) => { if (!g.has(c.group)) g.set(c.group, []); g.get(c.group).push(c); }); return g; };
    const course = groupsOf(1), found = groupsOf(0), quest = A.concepts.filter((c) => c.layer === 2);
    const nNotes = allProblems.filter(({ p }) => p.kind === "notes").length, nCode = A.codeSteps.length;
    $main.innerHTML = `
      <section class="hero">
        <div class="hero-text">
          <h1>Compressible flow, one nozzle at a time</h1>
          <p class="lede">Every idea in the MECH 430 notes, from the speed of sound to the method of characteristics. Each has a simulator you can push around and practice you can do without pencil and paper, ${nCode} of the exercises in real Python. All ${nNotes} worked examples from the notes are rebuilt step by step, and every number here is recomputed and checked before the page is built.</p>
          <div class="tools"><a class="btn solid" href="#/drill">Start the course drill</a><a class="btn" href="#/lab">Open the flow lab</a><a class="btn" href="#/code">Code track</a></div>
        </div>
        <div class="hero-sim" id="hero-sim"></div>
      </section>
      <p class="legend-line"><span class="legend"><span><i class="lg-down"></i>builds on</span><span><i class="lg-up"></i>used by</span></span> Hover or focus an idea to light up its connections.</p>
      <div id="map">
        <section class="band course">
          <div class="band-head"><h2>The course, chapter by chapter</h2><p>In the order of the notes.</p></div>
          <div class="groups">${[...course].map(([g, cs]) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${cs.map(chip).join("")}</div></div>`).join("")}</div>
        </section>
        <section class="band quest">
          <div class="band-head"><h2>Questions that join the ideas</h2><p>Exam-style: each needs several chapters at once.</p></div>
          <div class="quest-grid">${quest.map(chip).join("")}</div>
        </section>
        <section class="band found">
          <div class="band-head"><h2>Foundations from earlier courses</h2><p>What the notes assume you already own.</p></div>
          <div class="groups">${A.subjects.filter((s) => found.has(s)).map((g) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${found.get(g).map(chip).join("")}</div></div>`).join("")}</div>
        </section>
      </div>`;
    window.Widgets.render(document.getElementById("hero-sim"), { type: "nozzle", preset: "hero" });
    const map = document.getElementById("map"), chips = [...map.querySelectorAll(".chip")];
    const light = (id) => {
      const down = ancestors(id), up = descendants(id);
      map.classList.add("map-dim");
      chips.forEach((ch) => { const i = ch.dataset.id; ch.classList.toggle("self", i === id); ch.classList.toggle("on", down.has(i) || up.has(i)); ch.classList.toggle("down", down.has(i)); ch.classList.toggle("up", up.has(i)); });
    };
    const clear = () => { map.classList.remove("map-dim"); chips.forEach((ch) => ch.classList.remove("self", "on", "down", "up")); };
    chips.forEach((ch) => {
      ch.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") light(ch.dataset.id); });
      ch.addEventListener("pointerleave", clear); ch.addEventListener("focus", () => light(ch.dataset.id)); ch.addEventListener("blur", clear);
    });
  }

  // ---------- problems ----------
  function shuffle(a) { const b = a.slice(); for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } return b; }

  function renderProblem(p, host, onDone) {
    const box = document.createElement("article");
    box.className = "prob" + (solved(p.id) ? " solved" : "");
    box.dataset.pid = p.id;
    box.innerHTML = `<div class="prob-head"><h3>${inline(p.title)}</h3><span class="status">${solved(p.id) ? "Solved" : ""}</span></div>${kindTag(p.kind)}
      <div class="prob-body">${md(p.stem)}</div><div class="steps"></div>`;
    host.appendChild(box);
    const stepsEl = box.querySelector(".steps");
    let clean = true;
    const showStep = (i) => {
      if (i >= p.steps.length) {
        if (!solved(p.id)) { progress[p.id] = { first: clean, at: Date.now() }; save(); updatePill(); }
        box.classList.add("solved");
        box.querySelector(".status").textContent = clean ? "Solved first time" : "Solved";
        if (onDone) onDone();
        return;
      }
      const s = p.steps[i];
      const el = document.createElement("div");
      el.className = "step"; el.dataset.type = s.type;
      el.innerHTML = `<div class="step-q">${p.steps.length > 1 ? `<span class="n">Step ${i + 1} of ${p.steps.length}</span>` : ""}${md(s.prompt)}</div>`;
      stepsEl.appendChild(el);
      const fb = document.createElement("div");
      const say = (cls, html) => { fb.className = "fb " + cls; fb.innerHTML = html; el.appendChild(fb); typeset(fb); };
      const finish = (msg) => { say("ok", msg ? md(msg) : "<p>Right.</p>"); showStep(i + 1); };
      const miss = (msg) => { clean = false; if (!progress[p.id]) { progress[p.id] = { first: false }; save(); } say("no", md(msg)); };
      if (s.type === "choice") {
        const wrap = document.createElement("div"); wrap.className = "opts";
        shuffle(s.options.map((o, k) => ({ ...o, k }))).forEach((o) => {
          const b = document.createElement("button");
          b.type = "button"; b.className = "opt"; b.dataset.index = o.k; b.innerHTML = md(o.label);
          b.addEventListener("click", () => {
            if (o.correct) { wrap.querySelectorAll(".opt").forEach((x) => { x.disabled = true; }); b.classList.add("right"); finish(s.explain); }
            else { b.classList.add("wrong"); b.disabled = true; miss(o.why || "Not this one."); }
          });
          wrap.appendChild(b);
        });
        el.appendChild(wrap);
      } else if (s.type === "spot") {
        const wrap = document.createElement("div"); wrap.className = "spot" + (s.code ? " code" : "");
        s.lines.forEach((ln, k) => {
          const b = document.createElement("button");
          b.type = "button"; b.className = "spot-line"; b.dataset.index = k;
          b.innerHTML = s.code ? `<code>${highlight(ln.text)}</code>` : inline(ln.text);
          b.addEventListener("click", () => {
            if (ln.wrong) { wrap.querySelectorAll(".spot-line").forEach((x) => { x.disabled = true; }); b.classList.add("right"); finish(ln.why + (s.explain ? " " + s.explain : "")); }
            else { b.classList.add("fine"); b.disabled = true; miss("That line is correct. Keep looking."); }
          });
          wrap.appendChild(b);
        });
        el.appendChild(wrap);
      } else if (s.type === "order") {
        const hint = document.createElement("p"); hint.className = "hint"; hint.textContent = "Click the steps in the order they happen.";
        const picked = document.createElement("ol"); picked.className = "order-done";
        const wrap = document.createElement("div"); wrap.className = "order";
        let nextIdx = 0;
        shuffle(s.items.map((t, k) => ({ t, k }))).forEach((it) => {
          const b = document.createElement("button");
          b.type = "button"; b.className = "order-item"; b.dataset.index = it.k; b.innerHTML = inline(it.t);
          b.addEventListener("click", () => {
            if (it.k === nextIdx) { const li = document.createElement("li"); li.innerHTML = inline(it.t); picked.appendChild(li); typeset(li); b.remove(); nextIdx++; fb.remove(); if (nextIdx === s.items.length) finish(s.explain); }
            else miss(`Not yet: something else comes before that. (${nextIdx} of ${s.items.length} placed.)`);
          });
          wrap.appendChild(b);
        });
        el.append(hint, picked, wrap);
      } else if (s.type === "dial") {
        renderDial(s, el, finish, miss);
      } else if (s.type === "code") {
        renderCode(s, p, i, el, finish, miss);
      } else {
        const row = document.createElement("form");
        row.className = "numrow";
        const id = `in-${p.id}-${i}`;
        const ph = s.type === "num" ? "e.g. 3.14 or 2/3" : s.type === "expr" ? `e.g. ${s.vars[0]}**2/2` : (s.placeholder || "type your answer");
        row.innerHTML = `<label for="${id}" class="sr-only">Your answer</label><input id="${id}" ${s.type === "num" ? 'inputmode="decimal"' : 'autocapitalize="off" spellcheck="false"'} autocomplete="off" placeholder="${esc(ph)}" class="${s.type === "expr" ? "mono-in wide" : s.type === "blank" ? "mono-in" : ""}">${s.unit ? `<span class="unit">${esc(s.unit)}</span>` : ""}<button class="btn" type="submit">Check</button><button class="btn quiet" type="button" data-reveal hidden>Show answer</button>`;
        el.appendChild(row);
        if (s.type === "expr") { const v = document.createElement("p"); v.className = "hint"; v.innerHTML = `Variables: ${s.vars.map((x) => `<code class="ic">${esc(x)}</code>`).join(" ")}. Use <code class="ic">*</code>, <code class="ic">/</code>, <code class="ic">**</code>, <code class="ic">sqrt()</code>, <code class="ic">log()</code>.`; el.appendChild(v); }
        let misses = 0;
        const input = row.querySelector("input");
        const lock = () => { input.disabled = true; row.querySelectorAll("button").forEach((x) => { x.disabled = true; }); };
        const answerText = () => s.type === "num" ? `${fmt(s.answer)}${s.unit ? " " + s.unit : ""}` : s.type === "expr" ? `$${s.tex}$` : "`" + s.answers[0] + "`";
        row.addEventListener("submit", (e) => {
          e.preventDefault();
          let ok = false, msg = "Not quite.", extra = "";
          if (s.type === "num") {
            const v = parseNum(input.value); ok = close(input.value, v, s.answer, s.tol);
            if (isNaN(v)) msg = "I couldn't read that as a number. Try a decimal, a fraction like 2/3, or an expression like 1.4*287.";
            if (ok && Math.abs(v - s.answer) > 1e-9 * Math.max(1, Math.abs(s.answer))) extra = ` (More precisely: ${fmt(s.answer)}${s.unit ? " " + s.unit : ""}.)`;
          } else if (s.type === "expr") { const r = sameExpr(s, input.value); ok = r.ok; msg = r.msg || msg; }
          else { ok = s.answers.some((a) => normBlank(a, s.mode) === normBlank(input.value, s.mode)); if (!ok && !input.value.trim()) msg = "Type your answer in the box."; }
          if (ok) { lock(); fb.remove(); finish((s.explain || "") + extra); }
          else { misses++; miss(msg + (s.hint ? " Hint: " + s.hint : "")); if (misses >= 2) row.querySelector("[data-reveal]").hidden = false; }
        });
        row.querySelector("[data-reveal]").addEventListener("click", () => { lock(); fb.remove(); finish(`The answer is ${answerText()}. ${s.explain || ""}`); });
      }
      typeset(el);
    };
    showStep(0);
    typeset(box);
    return box;
  }

  function renderDial(s, el, finish, miss) {
    const f = DIAL[s.model], id = "d" + Math.random().toString(36).slice(2, 8);
    const start = s.lo + (s.hi - s.lo) * 0.25;
    const wrap = document.createElement("div");
    wrap.className = "dial";
    wrap.innerHTML = `<label for="${id}">${esc(s.var)}${s.unit ? " (" + esc(s.unit) + ")" : ""}: <b data-x></b></label>
      <input type="range" id="${id}" min="${s.lo}" max="${s.hi}" step="${s.step}" value="${start}">
      <div class="dial-read"><span>${esc(s.shows)}</span><b data-y></b><span class="dial-target">target ${fmt(s.target)}</span></div>
      <div class="dial-bar" aria-hidden="true"><i data-bar></i><em></em></div>
      <div class="dial-act"><button type="button" class="btn" data-lock>Lock in</button><button type="button" class="btn quiet" data-reveal hidden>Show answer</button></div>`;
    el.appendChild(wrap);
    const r = wrap.querySelector("input"), X = wrap.querySelector("[data-x]"), Y = wrap.querySelector("[data-y]"), bar = wrap.querySelector("[data-bar]");
    const upd = () => {
      const x = +r.value, y = f(x, s.args);
      X.textContent = fmt(x); Y.textContent = isFinite(y) ? fmt(y) : "—";
      const err = isFinite(y) ? (y - s.target) / Math.max(Math.abs(s.target), 1e-9) : 1;
      bar.style.left = `${50 + Math.max(-48, Math.min(48, err * 150))}%`;
      bar.classList.toggle("near", Math.abs(err) < 0.01);
    };
    r.addEventListener("input", upd); upd();
    let misses = 0;
    const lock = () => wrap.querySelectorAll("input,button").forEach((x) => { x.disabled = true; });
    wrap.querySelector("[data-lock]").addEventListener("click", () => {
      const x = +r.value;
      if (Math.abs(x - s.answer) <= s.tol * Math.max(1, Math.abs(s.answer))) { lock(); finish(`${esc(s.var)} ≈ ${fmt(s.answer)}${s.unit ? " " + s.unit : ""}. ${s.explain || ""}`); }
      else { misses++; miss("Not there yet: watch the marker and bring it to the centre line."); if (misses >= 2) wrap.querySelector("[data-reveal]").hidden = false; }
    });
    wrap.querySelector("[data-reveal]").addEventListener("click", () => { r.value = s.answer; upd(); lock(); finish(`The answer is ${fmt(s.answer)}${s.unit ? " " + s.unit : ""}. ${s.explain || ""}`); });
  }

  function renderCode(s, p, i, el, finish, miss) {
    const k = codeKey(p.id, i);
    const draft = getDraft(k);
    const wrap = document.createElement("div");
    wrap.className = "code-ex";
    const lines = (draft || s.starter).split("\n").length;
    wrap.innerHTML = `<div class="editor"><div class="gutter" aria-hidden="true"></div><textarea spellcheck="false" autocapitalize="off" autocomplete="off" aria-label="Python code" rows="${Math.max(8, lines + 1)}"></textarea></div>
      <div class="code-act"><button type="button" class="btn solid" data-run>Run tests</button><button type="button" class="btn quiet" data-reset>Reset</button><button type="button" class="btn quiet" data-hint>Hint</button><button type="button" class="btn quiet" data-sol hidden>Show a solution</button><span class="code-status" aria-live="polite"></span></div>
      <div class="code-out" hidden></div>
      <details class="code-tests"><summary>See the tests (${s.n_checks} checks)</summary>${codeBlock(s.tests, "Tests run against your code")}</details>`;
    el.appendChild(wrap);
    const ta = wrap.querySelector("textarea"), gutter = wrap.querySelector(".gutter"), out = wrap.querySelector(".code-out"), status = wrap.querySelector(".code-status");
    ta.value = draft || s.starter;
    const syncGutter = () => { const n = ta.value.split("\n").length; gutter.textContent = Array.from({ length: n }, (_, j) => j + 1).join("\n"); ta.rows = Math.max(8, n + 1); };
    ta.addEventListener("input", () => { setDraft(k, ta.value); syncGutter(); });
    ta.addEventListener("scroll", () => { gutter.scrollTop = ta.scrollTop; });
    ta.addEventListener("keydown", (e) => {
      if (e.key === "Tab" && !e.shiftKey) { e.preventDefault(); const a = ta.selectionStart, b = ta.selectionEnd; ta.value = ta.value.slice(0, a) + "    " + ta.value.slice(b); ta.selectionStart = ta.selectionEnd = a + 4; setDraft(k, ta.value); syncGutter(); }
      if (e.key === "Enter" && !e.shiftKey && !e.metaKey && !e.ctrlKey) {
        const a = ta.selectionStart, lineStart = ta.value.lastIndexOf("\n", a - 1) + 1, line = ta.value.slice(lineStart, a);
        const indent = (line.match(/^\s*/) || [""])[0] + (/:\s*$/.test(line) ? "    " : "");
        e.preventDefault(); ta.value = ta.value.slice(0, a) + "\n" + indent + ta.value.slice(ta.selectionEnd); ta.selectionStart = ta.selectionEnd = a + 1 + indent.length; setDraft(k, ta.value); syncGutter();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") { e.preventDefault(); run(); }
    });
    syncGutter();
    let hintAt = 0, fails = 0;
    wrap.querySelector("[data-hint]").addEventListener("click", () => {
      if (!s.hints.length) return;
      const h = document.createElement("p"); h.className = "hint"; h.innerHTML = "Hint: " + inline(s.hints[hintAt % s.hints.length]); hintAt++;
      wrap.insertBefore(h, out);
    });
    wrap.querySelector("[data-reset]").addEventListener("click", () => { ta.value = s.starter; setDraft(k, ta.value); syncGutter(); });
    wrap.querySelector("[data-sol]").addEventListener("click", () => { ta.value = s.solution; setDraft(k, ta.value); syncGutter(); });
    async function run() {
      const btn = wrap.querySelector("[data-run]");
      btn.disabled = true; status.textContent = window.Sk ? "Running…" : "Loading Python (first run only)…";
      let res;
      try { res = await runPython(s.harness + "\n" + ta.value + "\n" + s.tests + "\n" + s.report); }
      catch (e) { res = { out: "", error: "Python couldn't load here (" + e.message + "). The solution and tests are below, so you can run them on your own machine." }; wrap.querySelector("[data-sol]").hidden = false; }
      btn.disabled = false; status.textContent = "";
      const rep = parseReport(res.out), passed = rep.filter((r) => r.ok).length;
      const printed = res.out.split("\n").filter((l) => l && !/^(PASS|FAIL) /.test(l)).join("\n");
      out.hidden = false;
      out.innerHTML = (res.error ? `<div class="py-err"><b>Python error</b><pre>${esc(res.error)}</pre></div>` : "") +
        (rep.length ? `<ul class="checks">${rep.map((r) => `<li class="${r.ok ? "pass" : "fail"}"><span>${r.ok ? "✓" : "✗"}</span> ${esc(r.label)}${r.ok ? "" : ` <small>got ${esc(r.got)}, expected ${esc(r.want)}</small>`}</li>`).join("")}</ul>` : "") +
        (printed ? `<div class="py-print"><b>Your printed output</b><pre>${esc(printed)}</pre></div>` : "");
      if (!res.error && rep.length === s.n_checks && passed === rep.length) {
        ta.readOnly = true; wrap.querySelectorAll("button:not([data-sol])").forEach((b) => { b.disabled = true; });
        finish(`All ${rep.length} checks pass. ${s.explain || ""}`);
      } else {
        fails++;
        if (fails >= 2) wrap.querySelector("[data-sol]").hidden = false;
        miss(res.error ? "Your code raised an error before the tests could finish. Read the message above." : `${passed} of ${s.n_checks} checks pass. Fix the failing ones and run again.`);
      }
    }
    wrap.querySelector("[data-run]").addEventListener("click", run);
  }

  // ---------- concept page ----------
  function renderConcept(id) {
    const c = byId[id];
    if (!c) { location.hash = "#/"; return; }
    setNav("");
    const tag = c.layer === 0 ? `<span class="tag">Foundation · ${esc(c.group)}</span>` : c.layer === 1 ? `<span class="tag course">${esc(c.group)}</span>` : `<span class="tag quest">Exam question</span>`;
    const src = c.source ? `<span class="tag src">${esc(c.source)}</span>` : "";
    const path = pathTo(id).map((i) => byId[i]);
    const pathProblems = path.reduce((n, x) => n + x.problems.length, 0), pathDone = path.reduce((n, x) => n + conceptStats(x).done, 0);
    const siblings = A.concepts.filter((x) => x.group === c.group), next = siblings[siblings.indexOf(c) + 1];
    const nCode = c.problems.reduce((n, p) => n + p.steps.filter((s) => s.type === "code").length, 0);
    $main.innerHTML = `
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/">Map</a><span>›</span><span>${esc(c.group)}</span></nav>
      <div class="concept">
        <article>
          <header class="c-head"><div class="c-tags">${tag}${src}</div><h1>${esc(c.title)}</h1></header>
          <div class="prose">${md(c.body)}</div>
          ${c.math.length ? `<div class="keybox">${c.math.map((m) => `$$${m}$$`).join("")}<p class="k-label">Key results</p></div>` : ""}
          <div id="widget-host"></div>
          <div class="cards">
            ${c.analogy ? `<section class="card analogy"><h3>An analogy</h3><p>${inline(c.analogy.text)}</p><p><span class="breaks">Where it breaks:</span> ${inline(c.analogy.breaks)}</p></section>` : ""}
            ${c.exam ? `<section class="card exam"><h3>On the exam</h3><p>${inline(c.exam)}</p></section>` : ""}
          </div>
          <section class="practice" aria-labelledby="practice-h">
            <h2 id="practice-h">Practice</h2>
            <p>One decision per step: a choice, a number, an expression, a slider, a click${nCode ? ", or a short Python function that runs right here" : ""}. Wrong choices explain the misconception behind them.</p>
            <div id="probs"></div>
          </section>
          ${next ? `<p class="next-link">Next in ${esc(c.group)}: <a href="#/c/${next.id}">${esc(next.short)}</a></p>` : ""}
        </article>
        <aside class="rail" aria-label="Connections">
          <section><h3>Builds on</h3>${c.deeper.length ? `<div class="chips">${c.deeper.map((d) => chip(byId[d])).join("")}</div>` : `<p class="empty">Nothing in this atlas: start here.</p>`}</section>
          <section><h3>Used by</h3>${usedBy[id].length ? `<div class="chips">${usedBy[id].map((d) => chip(byId[d])).join("")}</div>` : `<p class="empty">Nothing yet: this is a destination.</p>`}</section>
          <section><h3>Readiness path</h3>
            <p class="small">${path.length - 1 ? `${path.length - 1} ideas lead here. ${pathDone} of ${pathProblems} problems along the path solved.` : "No prerequisites in this atlas."}</p>
            <div class="ready-bar" aria-hidden="true"><b style="width:${(100 * pathDone) / pathProblems}%"></b></div>
            <a class="btn solid" href="#/drill/${id}">Drill this path</a>
          </section>
        </aside>
      </div>`;
    if (c.widget) window.Widgets.render(document.getElementById("widget-host"), c.widget);
    const host = document.getElementById("probs");
    c.problems.forEach((p) => renderProblem(p, host));
    typeset($main);
  }

  // ---------- the flow lab ----------
  const SIMS = [
    ["nozzle", {}, "Converging–diverging nozzle", "Drag the back pressure through every regime, with the shock, the pressure trace and the exhaust.", "c-back-pressure-regimes"],
    ["xt", {}, "Shock formation (x–t diagram)", "An accelerating piston's waves catch up into a shock; pull it back and they fan out.", "c-shock-formation"],
    ["machcone", {}, "Mach cone", "A beeping source from subsonic to supersonic: Doppler crowding, then the cone.", "c-mach-cone"],
    ["soundframe", {}, "Sound wave in two frames", "The same wave seen from the lab and from the wave.", "c-sound-derivation"],
    ["areavel", {}, "Area change", "How V, p and ρ respond to dA, subsonic versus supersonic.", "c-area-velocity"],
    ["massflux", {}, "Mass flux and choking", "Why mass flow per unit area peaks at Mach 1.", "c-choking"],
    ["shock", {}, "Normal shock", "Every ratio across a normal shock, and the entropy that forbids expansion shocks.", "c-normal-shock-relations"],
    ["rocket", {}, "Rocket nozzle", "Thrust against altitude: momentum versus pressure term, and the plume.", "c-rocket-thrust"],
    ["inlet", {}, "Supersonic inlet", "Start, unstart and hysteresis as the flight Mach number changes.", "c-supersonic-inlet"],
    ["train", {}, "Train in a tunnel", "Train speed and tunnel size set the shock that runs ahead.", "c-shinkansen"],
    ["ts", { preset: "fanno" }, "Fanno and Rayleigh lines", "Friction and heating on a T–s diagram, both heading to Mach 1.", "c-fanno-effects"],
    ["wedge", {}, "Wedge in supersonic flow", "Oblique shock angle, the δ–σ–M curve, and detachment.", "c-theta-beta-mach"],
    ["polar", { preset: "mach" }, "Shock polars and reflection", "Regular or Mach reflection, read off intersecting polars.", "c-mach-reflection"],
    ["pmfan", {}, "Prandtl–Meyer fan", "Turn a supersonic flow around a corner.", "c-prandtl-meyer"],
    ["moc", {}, "Method of characteristics", "A characteristic net computed live in a diverging channel.", "c-moc-unit-processes"],
    ["compress", {}, "Bernoulli versus compressible", "The compressibility error as Mach number grows.", "c-compressibility"],
  ];
  function renderLab(which) {
    setNav("lab");
    $main.innerHTML = `
      <header class="c-head"><div class="c-tags"><span class="tag quest">Flow lab</span></div><h1>Gas tables and simulators</h1>
        <p class="lede">The tables replace the notes' appendix: type any Mach number, area ratio, pressure ratio or angle and read every related ratio. The simulators run the same relations live (γ is adjustable in the tables).</p></header>
      <section class="lab-section" id="tables-host"></section>
      <section class="lab-section"><h2>Simulators</h2>
        <div class="sim-grid">${SIMS.map(([t, , name, what, cid], k) => `<button type="button" class="simcard ${which === t ? "on" : ""}" data-sim="${k}"><span class="sim-name">${esc(name)}</span><span class="sim-what">${esc(what)}</span></button>`).join("")}</div>
        <div id="sim-host" class="sim-host"></div></section>`;
    window.Widgets.render(document.getElementById("tables-host"), { type: "tables", preset: "all" });
    const open = (k) => {
      window.Widgets.stopAll();
      const [t, opts, name, , cid] = SIMS[k], host = document.getElementById("sim-host");
      host.innerHTML = `<p class="small">From <a href="#/c/${cid}">${esc(byId[cid].short)}</a></p>`;
      window.Widgets.render(host, Object.assign({ type: t }, opts));
      $main.querySelectorAll(".simcard").forEach((b, j) => b.classList.toggle("on", j === k));
      typeset(host);
    };
    $main.querySelectorAll(".simcard").forEach((b) => b.addEventListener("click", () => { open(+b.dataset.sim); document.getElementById("sim-host").scrollIntoView({ block: "nearest" }); }));
    const start = Math.max(0, SIMS.findIndex(([t]) => t === which));
    open(start);
    typeset($main);
  }

  // ---------- the code track ----------
  function renderCodeTrack() {
    setNav("code");
    const items = A.codeSteps.map((cs) => ({ ...cs, c: byId[cs.concept], p: probById[cs.problem].p }));
    const done = items.filter((it) => solved(it.p.id)).length;
    $main.innerHTML = `
      <header class="c-head"><div class="c-tags"><span class="tag quest">Code track</span></div><h1>Build your own gas tables in Python</h1>
        <p class="lede">${items.length} short exercises that add up to a compressible-flow toolkit: isentropic ratios, A/A* and its inverse, normal and oblique shocks, Fanno and Rayleigh flow, Prandtl–Meyer, a characteristics unit process, and finally a solver for the nozzle with any back pressure. Your code runs here, in plain Python (no NumPy), against tests that were checked against the notes. Drafts are kept in this browser.</p></header>
      <p class="drill-meta">${done} of ${items.length} done</p>
      <ol class="code-list">${items.map((it, k) => `<li class="${solved(it.p.id) ? "done" : ""}"><button type="button" class="code-item" data-k="${k}"><span class="ci-fn"><code>${esc(it.p.steps[it.index].fn || "")}</code></span><span class="ci-title">${esc(it.p.title)}</span><span class="ci-from">${esc(it.c.group)}</span></button></li>`).join("")}</ol>
      <div id="code-host"></div>`;
    $main.querySelectorAll(".code-item").forEach((b) => b.addEventListener("click", () => {
      const it = items[+b.dataset.k], host = document.getElementById("code-host");
      host.innerHTML = `<p class="drill-meta">From <a href="#/c/${it.c.id}">${esc(it.c.short)}</a></p>`;
      renderProblem(it.p, host, () => { b.parentElement.classList.add("done"); });
      host.scrollIntoView({ block: "start" });
    }));
    typeset($main);
  }

  // ---------- drill ----------
  function renderDrill(target) {
    setNav("drill");
    const isCode = target === "code", isMissed = target === "missed";
    const order = isCode || isMissed ? [] : target ? pathTo(target) : courseOrder();
    const queue = isCode ? A.codeSteps.map((cs) => ({ p: probById[cs.problem].p, c: byId[cs.concept] }))
      : isMissed ? allProblems.filter(({ p }) => missed(p.id))
      : order.flatMap((i) => byId[i].problems.map((p) => ({ p, c: byId[i] })));
    let skipSolved = !isMissed, at = 0;
    const title = isCode ? "Coding exercises" : isMissed ? "Problems you missed the first time" : target ? `Readiness path: ${esc(byId[target].short)}` : "The whole course, foundations first";
    const draw = () => {
      const list = skipSolved ? queue.filter(({ p }) => !solved(p.id)) : queue;
      $main.innerHTML = `
        <header class="c-head"><div class="c-tags"><span class="tag quest">Drill</span></div><h1>${title}</h1></header>
        <div class="drill-top">
          <span class="drill-meta">${queue.filter(({ p }) => solved(p.id)).length} of ${queue.length} solved</span>
          <label class="drill-meta checkline"><input type="checkbox" id="skip" ${skipSolved ? "checked" : ""}> Skip solved problems</label>
          <a class="btn quiet" href="#/drill/missed">Retry missed</a><a class="btn quiet" href="#/drill/code">Coding only</a>
        </div>
        ${order.length ? `<ul class="pathlist" aria-label="Path">${order.map((i) => { const s = conceptStats(byId[i]); return `<li class="${s.done === s.total ? "done" : ""} ${list[at] && list[at].c.id === i ? "now" : ""}">${esc(byId[i].short)}</li>`; }).join("")}</ul>` : ""}
        <div id="drill-host" class="drill-host"></div>
        <div class="drill-nav"><button class="btn quiet" id="prev" type="button">Previous</button><button class="btn solid" id="next" type="button">Next problem</button></div>`;
      document.getElementById("skip").addEventListener("change", (e) => { skipSolved = e.target.checked; at = 0; draw(); });
      const host = document.getElementById("drill-host");
      if (!list.length) {
        host.innerHTML = `<div class="card"><h3>${isMissed && !queue.length ? "Nothing missed yet" : "All done here"}</h3><p>${isMissed && !queue.length ? "Problems you get wrong on the first try collect here for another go." : "Every problem in this drill is solved. Untick \"Skip solved problems\" to go round again."}</p></div>`;
        document.querySelector(".drill-nav").hidden = true;
        return;
      }
      at = Math.max(0, Math.min(at, list.length - 1));
      const { p, c } = list[at];
      host.innerHTML = `<p class="drill-meta">Problem ${at + 1} of ${list.length} · from <a href="#/c/${c.id}">${esc(c.short)}</a></p>`;
      renderProblem(p, host);
      document.getElementById("prev").disabled = at === 0;
      document.getElementById("prev").onclick = () => { at--; draw(); };
      document.getElementById("next").onclick = () => { if (!(skipSolved && solved(p.id))) at++; draw(); };
      typeset($main);
    };
    draw();
  }

  function renderSources() {
    setNav("sources");
    const d = A.notesDiscrepancy;
    $main.innerHTML = `<header class="c-head"><h1>Where this comes from</h1></header>
      <div class="prose sources"><p>The structure, examples and equations follow the MECH 430 notes. Explanations, analogies, simulators and practice are original. The problem sets' skills are taught on different numbers and gases, so no problem-set answers appear here.</p>
      <h2>How it was checked</h2>
      <ul><li>A reference library of the course's relations reproduces every numerical example in the notes (stagnation and duct examples, the nuclear thermal rocket, nozzle shocks, the Mach 3 moving shock, the Shinkansen estimates, inlet starting, Fanno and Rayleigh examples, oblique shocks and their reflection, the Mach reflection polars, Prandtl–Meyer and the characteristics tables) before anything is built.</li>
      <li>Every number in the practice is computed by that library, never typed. Every coding exercise's reference solution passes its tests, and deliberately wrong versions are confirmed to fail.</li>
      <li>The simulators run a JavaScript copy of the library, which a browser test compares with the Python original at hundreds of points.</li>
      <li>One discrepancy turned up: the notes give ${d.deltaMaxLimitNotes}° as the hypersonic limit of the maximum wedge angle; the exact limit for γ = 1.4 is sin⁻¹(1/γ) = ${d.deltaMaxLimitExact.toFixed(2)}°. Elsewhere, where the notes interpolate (the 8.2.1 shock position, the 10.4.1 friction shock), the atlas gives the exact value and says so.</li></ul>
      <h2>References</h2>
      <ol>${A.sources.map((s) => `<li>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>` : esc(s.title)}<span>${esc(s.note)}</span></li>`).join("")}</ol></div>`;
  }

  // ---------- search ----------
  const index = A.concepts.map((c) => ({ href: `#/c/${c.id}`, label: c.short, kind: c.layer === 0 ? "foundation" : c.layer === 2 ? "question" : c.group.split(" · ")[0], text: (c.short + " " + c.title + " " + c.body).toLowerCase() }))
    .concat(SIMS.map(([t, , name, what]) => ({ href: `#/lab/${t}`, label: name, kind: "simulator", text: (name + " " + what).toLowerCase() })));
  function setupSearch() {
    const input = document.getElementById("search"), box = document.getElementById("search-results");
    const close = () => { box.hidden = true; };
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) { close(); return; }
      const hits = index.map((it) => ({ it, score: (it.label.toLowerCase().includes(q) ? 10 : 0) + (it.text.includes(q) ? 1 : 0) })).filter((h) => h.score > 0).sort((a, b) => b.score - a.score).slice(0, 12);
      box.innerHTML = hits.length ? hits.map(({ it }) => `<a href="${it.href}"><span class="sk">${esc(it.kind)}</span>${esc(it.label)}</a>`).join("") : `<p class="empty">No matches.</p>`;
      box.hidden = false;
    });
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { input.value = ""; close(); } if (e.key === "Enter") { const a = box.querySelector("a"); if (a) { location.hash = a.getAttribute("href"); input.value = ""; close(); } } });
    box.addEventListener("click", () => { input.value = ""; close(); });
    document.addEventListener("click", (e) => { if (!e.target.closest(".search")) close(); });
  }

  // ---------- routing ----------
  function route() {
    window.Widgets.stopAll();
    const [view, sub] = location.hash.replace(/^#\/?/, "").split("/");
    if (view === "c" && sub) renderConcept(sub);
    else if (view === "lab") renderLab(sub);
    else if (view === "code") renderCodeTrack();
    else if (view === "drill") renderDrill(sub === "code" || sub === "missed" ? sub : sub && byId[sub] ? sub : null);
    else if (view === "sources") renderSources();
    else renderMap();
    updatePill();
    window.scrollTo(0, 0);
  }
  document.addEventListener("click", (e) => {
    const c = e.target.closest("[data-copy]");
    if (!c) return;
    const code = c.parentElement.querySelector("pre").innerText;
    const done = () => { c.textContent = "Copied"; setTimeout(() => { c.textContent = "Copy"; }, 1200); };
    try { navigator.clipboard.writeText(code).then(done, () => { c.textContent = "Select and copy"; }); } catch (err) { c.textContent = "Select and copy"; }
  });
  window.addEventListener("hashchange", route);
  setupSearch();
  route();
})();
