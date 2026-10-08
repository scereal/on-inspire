// MECH 559 Atlas: concept map, concept pages, the Code lab, step-by-step practice and drills.
(function () {
  const A = window.ATLAS;
  const byId = {}, usedBy = {}, lib = {}, bug = {}, flow = {};
  A.concepts.forEach((c) => { byId[c.id] = c; usedBy[c.id] = []; });
  A.concepts.forEach((c) => c.deeper.forEach((d) => usedBy[d].push(c.id)));
  A.library.forEach((e) => { lib[e.id] = e; });
  A.bugs.forEach((e) => { bug[e.id] = e; });
  A.workflows.forEach((w) => { flow[w.id] = w; });
  const codeFor = {};   // concept id -> {lib:[], bugs:[], flows:[]}
  const slot = (id) => (codeFor[id] = codeFor[id] || { lib: [], bugs: [], flows: [] });
  A.library.forEach((e) => e.concepts.forEach((k) => slot(k).lib.push(e.id)));
  A.bugs.forEach((e) => e.concepts.forEach((k) => slot(k).bugs.push(e.id)));
  A.workflows.forEach((w) => w.concepts.forEach((k) => slot(k).flows.push(w.id)));
  const allConceptProblems = A.concepts.flatMap((c) => c.problems.map((p) => ({ p, c })));
  const $main = document.getElementById("main");

  // ---------- storage (per browser, best effort) ----------
  const KEY = "mech559-atlas:v1";
  let progress = {};
  try { progress = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { progress = {}; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (e) { /* private mode */ } };
  const solved = (pid) => !!progress[pid];
  const conceptStats = (c) => ({ done: c.problems.filter((p) => solved(p.id)).length, total: c.problems.length });

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
  const BUILTIN = new Set("print len range abs min max sum sorted list dict tuple set float int str zip enumerate map isinstance round next".split(" "));
  function highlight(code) {
    const re = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|[rfb]?"(?:\\.|[^"\\\n])*"|[rfb]?'(?:\\.|[^'\\\n])*')|(\b\d+(?:\.\d+)?(?:e[-+]?\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)|([\s\S])/g;
    let out = "", m;
    while ((m = re.exec(code))) {
      if (m[1]) out += `<span class="tk-c">${esc(m[1])}</span>`;
      else if (m[2]) out += `<span class="tk-s">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="tk-n">${esc(m[3])}</span>`;
      else if (m[4]) {
        const w = m[4], after = code.slice(re.lastIndex).match(/^\s*\(/);
        if (KW.has(w)) out += `<span class="tk-k">${w}</span>`;
        else if (BUILTIN.has(w)) out += `<span class="tk-b">${w}</span>`;
        else if (after) out += `<span class="tk-f">${w}</span>`;
        else out += w;
      } else out += esc(m[5]);
    }
    return out;
  }
  function codeBlock(code, label) {
    return `<div class="codeblock">${label ? `<div class="code-label">${esc(label)}</div>` : ""}<button type="button" class="copy" data-copy aria-label="Copy code">Copy</button><pre><code>${highlight(code)}</code></pre></div>`;
  }
  function outputBlock(text) {
    return text ? `<div class="output"><div class="code-label">Output (from a real run)</div><pre>${esc(text)}</pre></div>` : "";
  }
  function routeOf(id) {
    if (byId[id]) return `#/c/${id}`;
    if (lib[id]) return `#/code/lib/${id}`;
    if (bug[id]) return `#/code/bug/${id}`;
    if (flow[id]) return `#/code/flow/${id}`;
    return "#/";
  }
  function labelOf(id) {
    if (byId[id]) return byId[id].short;
    if (lib[id]) return lib[id].name;
    if (bug[id]) return bug[id].title;
    if (flow[id]) return flow[id].title;
    return id;
  }
  function inline(s) {
    const keep = [];
    const stash = (html) => { keep.push(html); return `\u0000${keep.length - 1}\u0000`; };
    let t = String(s).replace(/`([^`\n]+)`/g, (m, c) => stash(`<code class="ic">${esc(c)}</code>`));
    t = t.replace(/\$\$[\s\S]+?\$\$|\$[^$\n]+?\$/g, (m) => stash(esc(m)));
    t = t.replace(/\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)/g, (m, txt, url) => stash(`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(txt)}</a>`));
    t = t.replace(/\[\[([a-z][a-z0-9]*-[a-z0-9-]+)(?:\|([^\]]+))?\]\]/g, (m, id, shown) => stash(`<a class="inline-link" href="${routeOf(id)}">${esc(shown || labelOf(id))}</a>`));
    t = esc(t);
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*\w])\*([^*\s][^*]*?)\*/g, "$1<em>$2</em>");
    return t.replace(/\u0000(\d+)\u0000/g, (m, i) => keep[+i]);
  }
  function md(text) {
    const parts = [];
    String(text).replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code, off) => { parts.push({ code: code.replace(/\n$/, "") }); return ""; });
    const segs = String(text).split(/```\w*\n[\s\S]*?```/g);
    let html = "";
    segs.forEach((seg, i) => {
      html += mdBlocks(seg);
      if (parts[i]) html += codeBlock(parts[i].code);
    });
    return html;
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
      if (lines.every((l) => /^\s*> /.test(l))) return `<blockquote>${inline(lines.map((l) => l.replace(/^\s*> /, "")).join(" "))}</blockquote>`;
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

  // ---------- small UI pieces ----------
  const meter = (c) => { const s = conceptStats(c); return `<span class="meter" aria-hidden="true"><b style="width:${(100 * s.done) / s.total}%"></b></span>`; };
  const chip = (c, extra = "") => {
    const s = conceptStats(c);
    return `<a class="chip ${s.done === s.total ? "done" : ""} ${extra}" href="#/c/${c.id}" data-id="${c.id}" title="${esc(c.title)}"><span>${esc(c.short)}</span>${meter(c)}<span class="sr-only">${s.done} of ${s.total} solved</span></a>`;
  };
  const kindBadge = (k) => `<span class="badge kind-${k}">${k === "silent" ? "silent: wrong answer, no error" : k === "warning" ? "warning only" : "crash"}</span>`;
  function updatePill() {
    const all = allConceptProblems.length + A.codeProblems.length;
    const n = allConceptProblems.filter(({ p }) => solved(p.id)).length + A.codeProblems.filter((p) => solved(p.id)).length;
    document.getElementById("progress-pill").textContent = `${n} / ${all} solved`;
  }
  function setNav(which) {
    document.querySelectorAll("[data-nav]").forEach((a) => { if (a.dataset.nav === which) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  }

  // ---------- map ----------
  function renderMap() {
    setNav("map");
    const groupsOf = (layer) => {
      const g = new Map();
      A.concepts.filter((c) => c.layer === layer).forEach((c) => { if (!g.has(c.group)) g.set(c.group, []); g.get(c.group).push(c); });
      return g;
    };
    const quest = A.concepts.filter((c) => c.layer === 2);
    const exer = groupsOf(3);
    const course = groupsOf(1), found = groupsOf(0);
    const nCourse = A.concepts.filter((c) => c.layer === 1).length;
    const silent = A.bugs.filter((b) => b.kind === "silent").length;
    $main.innerHTML = `
      <section class="hero">
        <div>
          <h1>Engineering systems optimization, from the ground up</h1>
          <p class="lede">All ${nCourse} ideas in the MECH 559 slides, the ${A.concepts.filter((c) => c.layer === 0).length} things from earlier courses they rely on, ${quest.length} exam-style questions, every course exercise as a guided walkthrough, and a Code lab for the assignments: ${A.library.length} library guides, ${A.bugs.length} common bugs (${silent} of them fail silently), and step-by-step workflows. Every answer and every line of code is checked.</p>
        </div>
        <ol class="steps-how">
          <li><b>Hover or focus an idea</b> to light up what it builds on and what builds on it.</li>
          <li><b>Open it</b> for the explanation, a live model, an analogy with where it breaks, and practice you can do without pencil and paper.</li>
          <li><b>Coding?</b> Open the <a href="#/code">Code lab</a>: what each function does, and every way it bites.</li>
        </ol>
      </section>
      <div class="tools">
        <a class="btn solid" href="#/drill">Drill the whole course</a>
        <a class="btn" href="#/code">Code lab</a>
        <span class="legend"><span><i style="background:var(--pen-soft);border:1px solid var(--pen)"></i>builds on</span><span><i style="background:var(--box-soft);border:1px solid var(--box)"></i>used by</span></span>
      </div>
      <div id="map">
        <section class="band quest">
          <div class="band-head"><h2>Questions that join the ideas</h2><p>Exam-style: each needs several concepts at once.</p></div>
          <div class="quest-grid">${quest.map((c) => chip(c)).join("")}</div>
        </section>
        <section class="band exer">
          <div class="band-head"><h2>The course exercises, step by step</h2><p>Every question from Exercises 1–4, broken into pencil-free steps.</p></div>
          <div class="groups">${[...exer].map(([g, cs]) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${cs.map((c) => chip(c)).join("")}</div></div>`).join("")}</div>
        </section>
        <section class="band course">
          <div class="band-head"><h2>MECH 559, lecture by lecture</h2><p>In the order of the slides.</p></div>
          <div class="groups">${[...course].map(([g, cs]) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${cs.map((c) => chip(c)).join("")}</div></div>`).join("")}</div>
        </section>
        <section class="band code-band">
          <div class="band-head"><h2>Code lab</h2><p>For the assignments: libraries, bugs, workflows.</p></div>
          <div class="groups">
            <a class="group card-link" href="#/code#workflows"><h3>Workflows</h3><p>${A.workflows.map((w) => esc(w.title)).join(" · ")}</p></a>
            <a class="group card-link" href="#/code#library"><h3>${A.library.length} library guides</h3><p>${A.library.slice(0, 6).map((e) => esc(e.name)).join(" · ")} …</p></a>
            <a class="group card-link" href="#/code#bugs"><h3>${A.bugs.length} common bugs</h3><p>${A.bugs.slice(0, 4).map((b) => esc(b.title)).join(" · ")} …</p></a>
          </div>
        </section>
        <section class="band found">
          <div class="band-head"><h2>Foundations from earlier courses</h2><p>What the slides assume you already own.</p></div>
          <div class="groups">${A.subjects.filter((s) => found.has(s)).map((g) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${found.get(g).map((c) => chip(c)).join("")}</div></div>`).join("")}</div>
        </section>
      </div>`;
    const map = document.getElementById("map");
    const chips = [...map.querySelectorAll(".chip")];
    const light = (id) => {
      const down = ancestors(id), up = descendants(id);
      map.classList.add("map-dim");
      chips.forEach((ch) => { const i = ch.dataset.id; ch.classList.toggle("self", i === id); ch.classList.toggle("on", down.has(i) || up.has(i)); ch.classList.toggle("down", down.has(i)); ch.classList.toggle("up", up.has(i)); });
    };
    const clear = () => { map.classList.remove("map-dim"); chips.forEach((ch) => ch.classList.remove("self", "on", "down", "up")); };
    chips.forEach((ch) => {
      ch.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") light(ch.dataset.id); });
      ch.addEventListener("pointerleave", clear);
      ch.addEventListener("focus", () => light(ch.dataset.id));
      ch.addEventListener("blur", clear);
    });
  }

  // ---------- problems ----------
  function shuffle(a) { const b = a.slice(); for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } return b; }
  function parseNum(raw) {
    let s = String(raw).trim().replace(/[−–]/g, "-").replace(/[×·]/g, "*").replace(/,/g, "").replace(/[°%$]/g, "").replace(/\s+/g, "");
    if (!s) return NaN;
    s = s.replace(/π|pi/gi, "(PI)").replace(/sqrt/gi, "SQRT").replace(/\^/g, "**");
    if (!/^[0-9+\-*/().eE PISQRT]*$/.test(s)) return NaN;
    s = s.replace(/PI/g, "Math.PI").replace(/SQRT/g, "Math.sqrt");
    try { const v = Function(`"use strict";return (${s});`)(); return typeof v === "number" ? v : NaN; } catch (e) { return NaN; }
  }
  function close(raw, v, ans, tol) {
    if (!isFinite(v)) return false;
    if (ans === 0) return Math.abs(v) <= Math.max(tol, 1e-3);
    if (Math.abs(v - ans) <= tol * Math.abs(ans)) return true;
    const m = String(raw).trim().match(/^-?(\d*)\.?(\d*)$/);
    if (m && (m[1] + m[2]).replace(/^0+/, "").length >= 2) return Math.abs(v - ans) <= 0.5 * Math.pow(10, -m[2].length) * 1.0001;
    return false;
  }
  const fmt = (x) => { const a = Math.abs(x); return a !== 0 && (a < 0.01 || a >= 1e5) ? x.toPrecision(4) : (Math.round(x * 10000) / 10000).toString(); };
  // Math expressions typed by the learner: evaluated numerically against the verified answer.
  const FUNCS = { cot: "__cot", sec: "__sec", csc: "__csc", sin: "Math.sin", cos: "Math.cos", tan: "Math.tan", exp: "Math.exp", log: "Math.log", ln: "Math.log", sqrt: "Math.sqrt", abs: "Math.abs", pi: "Math.PI" };
  function compileExpr(src, vars) {
    let s = String(src).trim().replace(/[−–]/g, "-").replace(/[×·]/g, "*").replace(/\^/g, "**").replace(/π/g, "pi");
    if (!s || /[^0-9a-zA-Z_+\-*/(). ,]/.test(s)) return null;
    const tokens = s.match(/[A-Za-z_][A-Za-z0-9_]*/g) || [];
    for (const t of tokens) if (!vars.includes(t) && !(t in FUNCS) && t !== "e") return { error: `I don't know "${t}". Use ${vars.join(", ")} and functions like sin, exp, sqrt.` };
    if (/\d\s*[A-Za-z(]|\)\s*[\dA-Za-z(]/.test(s)) return { error: "Write multiplication explicitly with *, e.g. 2*x1 rather than 2x1." };
    s = s.replace(/[A-Za-z_][A-Za-z0-9_]*/g, (t) => (vars.includes(t) ? t : t === "e" ? "Math.E" : FUNCS[t]));
    try { return { fn: Function(...vars, `"use strict";const __cot = (v) => 1 / Math.tan(v), __sec = (v) => 1 / Math.cos(v), __csc = (v) => 1 / Math.sin(v);return (${s});`) }; } catch (e) { return { error: "That expression doesn't parse. Check the brackets." }; }
  }
  function sameExpr(step, src) {
    const mine = compileExpr(src, step.vars);
    if (!mine) return { ok: false, msg: "Type an expression using " + step.vars.join(", ") + "." };
    if (mine.error) return { ok: false, msg: mine.error };
    const ref = Function(...step.vars, `"use strict";return (${step.js});`);
    for (let t = 0; t < 8; t++) {
      const args = step.vars.map((v) => { const [a, b] = step.ranges[v] || [-2, 2]; return a + (b - a) * (0.13 + 0.74 * Math.random()); });
      let u, w;
      try { u = mine.fn(...args); w = ref(...args); } catch (e) { return { ok: false, msg: "That expression doesn't evaluate." }; }
      if (!isFinite(u) || Math.abs(u - w) > 1e-6 * Math.max(1, Math.abs(w))) return { ok: false, msg: "Not equivalent to the answer." };
    }
    return { ok: true };
  }
  const normBlank = (s, mode) => mode === "text" ? String(s).trim().toLowerCase().replace(/\s+/g, " ") : String(s).replace(/\s+/g, "").replace(/[‘’]/g, "'").replace(/[“”]/g, '"');

  function renderProblem(p, host, onDone) {
    const box = document.createElement("article");
    box.className = "prob" + (solved(p.id) ? " solved" : "");
    box.dataset.pid = p.id;
    const fig = p.fig && window.Figures ? window.Figures.svg(p.fig) : "";
    box.innerHTML = `<div class="prob-head"><h3>${inline(p.title)}</h3><span class="status">${solved(p.id) ? "Solved" : ""}</span></div>
      <div class="prob-body ${fig ? "has-fig" : ""}"><div>${md(p.stem)}</div>${fig ? `<div class="fig" aria-hidden="true">${fig}</div>` : ""}</div>
      <div class="steps"></div>`;
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
      el.className = "step";
      el.dataset.type = s.type;
      el.innerHTML = `<div class="step-q">${p.steps.length > 1 ? `<span class="n">Step ${i + 1} of ${p.steps.length}</span>` : ""}${md(s.prompt)}</div>`;
      stepsEl.appendChild(el);
      const fb = document.createElement("div");
      const say = (cls, html) => { fb.className = "fb " + cls; fb.innerHTML = html; el.appendChild(fb); typeset(fb); };
      const finish = (msg) => { say("ok", msg ? md(msg) : "<p>Right.</p>"); showStep(i + 1); };
      const miss = (msg) => { clean = false; say("no", md(msg)); };
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
        const wrap = document.createElement("div"); wrap.className = "order";
        const picked = document.createElement("ol"); picked.className = "order-done";
        let nextIdx = 0;
        shuffle(s.items.map((t, k) => ({ t, k }))).forEach((it) => {
          const b = document.createElement("button");
          b.type = "button"; b.className = "order-item"; b.dataset.index = it.k; b.innerHTML = inline(it.t);
          b.addEventListener("click", () => {
            if (it.k === nextIdx) {
              const li = document.createElement("li"); li.innerHTML = inline(it.t); picked.appendChild(li); typeset(li);
              b.remove(); nextIdx++; fb.remove();
              if (nextIdx === s.items.length) finish(s.explain);
            } else miss(`Not yet: something else comes before that. (${nextIdx} of ${s.items.length} placed.)`);
          });
          wrap.appendChild(b);
        });
        el.appendChild(picked); el.appendChild(wrap);
        const hint = document.createElement("p"); hint.className = "hint"; hint.textContent = "Click the steps in the order they happen."; el.insertBefore(hint, picked);
      } else {
        const row = document.createElement("form");
        row.className = "numrow";
        const id = `in-${p.id}-${i}-${Math.random().toString(36).slice(2, 7)}`;
        const ph = s.type === "num" ? "e.g. 3.14 or 2/3" : s.type === "expr" ? `e.g. 2*${s.vars[0]} + 1` : (s.placeholder || "type your answer");
        row.innerHTML = `<label for="${id}" class="sr-only">Your answer</label>${s.type === "blank" ? `<code class="blank-input-wrap"><input id="${id}" class="mono-in" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="${esc(ph)}"></code>` : `<input id="${id}" ${s.type === "num" ? 'inputmode="decimal"' : 'autocapitalize="off" spellcheck="false"'} autocomplete="off" placeholder="${esc(ph)}" class="${s.type === "expr" ? "mono-in wide" : ""}">`}${s.unit ? `<span class="unit">${esc(s.unit)}</span>` : ""}<button class="btn" type="submit">Check</button><button class="btn quiet" type="button" data-reveal hidden>Show answer</button>`;
        el.appendChild(row);
        const preview = document.createElement("div"); preview.className = "expr-preview";
        if (s.type === "expr") { el.appendChild(preview); }
        let misses = 0;
        const input = row.querySelector("input");
        const lock = () => { input.disabled = true; row.querySelectorAll("button").forEach((x) => { x.disabled = true; }); };
        const answerText = () => s.type === "num" ? `${fmt(s.answer)}${s.unit ? " " + s.unit : ""}` : s.type === "expr" ? `$${s.tex}$` : "`" + s.answers[0] + "`";
        row.addEventListener("submit", (e) => {
          e.preventDefault();
          let ok = false, msg = "Not quite.";
          if (s.type === "num") {
            const v = parseNum(input.value); ok = close(input.value, v, s.answer, s.tol);
            if (isNaN(v)) msg = "I couldn't read that as a number. Try a decimal, a fraction like 2/3, or sqrt(2), pi.";
            if (ok && Math.abs(v - s.answer) > 1e-9 * Math.max(1, Math.abs(s.answer))) s._exact = ` (Exact: ${fmt(s.answer)}${s.unit ? " " + s.unit : ""}.)`;
          } else if (s.type === "expr") {
            const r = sameExpr(s, input.value); ok = r.ok; msg = r.msg || msg;
          } else {
            ok = s.answers.some((a) => normBlank(a, s.mode) === normBlank(input.value, s.mode));
            if (!ok && !input.value.trim()) msg = "Type your answer in the box.";
          }
          if (ok) { lock(); fb.remove(); finish((s.explain || "") + (s._exact || "")); }
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

  // ---------- concept page ----------
  function inCodeCard(id) {
    const k = codeFor[id];
    if (!k) return "";
    const link = (i) => `<li><a href="${routeOf(i)}">${esc(labelOf(i))}</a>${bug[i] ? " " + kindBadge(bug[i].kind) : ""}</li>`;
    return `<section class="card incode"><h3>In code</h3>
      ${k.flows.length ? `<p class="small">Worked workflow</p><ul>${k.flows.map(link).join("")}</ul>` : ""}
      ${k.lib.length ? `<p class="small">Library</p><ul>${k.lib.map(link).join("")}</ul>` : ""}
      ${k.bugs.length ? `<p class="small">Bugs to watch for</p><ul>${k.bugs.map(link).join("")}</ul>` : ""}</section>`;
  }
  function renderConcept(id) {
    const c = byId[id];
    if (!c) { location.hash = "#/"; return; }
    setNav("");
    const layerTag = c.layer === 0 ? `<span class="tag">Foundation · ${esc(c.group)}</span>` : c.layer === 1 ? `<span class="tag course">${esc(c.group)}</span>` : c.layer === 3 ? `<span class="tag quest">${esc(c.group)}</span>` : `<span class="tag quest">Exam question</span>`;
    const src = c.source ? `<span class="tag src">Slides: ${esc(c.source)}</span>` : "";
    const path = pathTo(id).map((i) => byId[i]);
    const pathProblems = path.reduce((n, x) => n + x.problems.length, 0);
    const pathDone = path.reduce((n, x) => n + conceptStats(x).done, 0);
    const siblings = A.concepts.filter((x) => x.group === c.group);
    const next = siblings[siblings.indexOf(c) + 1];
    $main.innerHTML = `
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/">Map</a><span>›</span><span>${esc(c.group)}</span></nav>
      <div class="concept">
        <article>
          <header class="c-head"><div class="c-tags">${layerTag}${src}</div><h1>${esc(c.title)}</h1></header>
          <div class="prose">${md(c.body)}</div>
          ${c.math.length ? `<div class="keybox">${c.math.map((m) => `$$${m}$$`).join("")}<p class="k-label">Key results</p></div>` : ""}
          <div id="widget-host"></div>
          <div class="cards">
            ${c.analogy ? `<section class="card analogy"><h3>An analogy</h3><p>${inline(c.analogy.text)}</p><p><span class="breaks">Where it breaks:</span> ${inline(c.analogy.breaks)}</p></section>` : ""}
            ${c.exam ? `<section class="card exam"><h3>Open-book exam lens</h3><p>${inline(c.exam)}</p></section>` : ""}
          </div>
          <section class="practice" aria-labelledby="practice-h">
            <h2 id="practice-h">Practice</h2>
            <p>No pencil needed: each step asks for one choice, one number, one short expression, or one click. Wrong choices explain the misconception behind them.</p>
            <div id="probs"></div>
          </section>
          ${next ? `<p class="next-link">Next in ${esc(c.group)}: <a href="#/c/${next.id}">${esc(next.short)}</a></p>` : ""}
        </article>
        <aside class="rail" aria-label="Connections">
          <section><h3>Builds on</h3>${c.deeper.length ? `<div class="chips">${c.deeper.map((d) => chip(byId[d])).join("")}</div>` : `<p class="empty">Nothing in this atlas: start here.</p>`}</section>
          <section><h3>Used by</h3>${usedBy[id].length ? `<div class="chips">${usedBy[id].map((d) => chip(byId[d])).join("")}</div>` : `<p class="empty">Nothing yet: this is a destination.</p>`}</section>
          ${inCodeCard(id)}
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

  // ---------- Code lab ----------
  function bugCard(b, open) {
    return `<details class="bugcard kind-${b.kind}" ${open ? "open" : ""} id="bug-${b.id}">
      <summary><span class="bug-title">${esc(b.title)}</span><span class="bug-meta">${kindBadge(b.kind)}<span class="badge lib">${esc(b.lib)}</span></span></summary>
      <div class="bug-body">${bugBody(b)}<p><a href="#/code/bug/${b.id}">Open this bug's page and practice →</a></p></div></details>`;
  }
  function bugBody(b) {
    const symptom = b.symptom ? `<div class="symptom"><span class="small">What you see</span><pre>${esc(b.symptom)}</pre></div>` :
      `<div class="symptom"><span class="small">What you see: no error, just this</span><pre>${esc(b.bad_show || "")}</pre></div>`;
    return `${symptom}
      <div class="why">${md("**Why:** " + b.why)}</div>
      <div class="fix">${md("**Fix:** " + b.fix)}</div>
      <div class="pair">
        <div>${codeBlock(b.bad, "Buggy")}${b.bad_show ? `<p class="shows bad">→ ${esc(b.bad_show)}</p>` : ""}</div>
        <div>${codeBlock(b.good, "Fixed")}${b.good_show ? `<p class="shows good">→ ${esc(b.good_show)}</p>` : ""}</div>
      </div>
      ${b.concepts.length ? `<p class="small">Related ideas: ${b.concepts.map((k) => `<a href="#/c/${k}">${esc(byId[k].short)}</a>`).join(" · ")}</p>` : ""}`;
  }
  function renderCodeHome() {
    setNav("code");
    const groups = new Map();
    A.library.forEach((e) => { if (!groups.has(e.group)) groups.set(e.group, []); groups.get(e.group).push(e); });
    const libs = [...new Set(A.bugs.map((b) => b.lib))];
    const v = A.versions || {};
    $main.innerHTML = `
      <header class="c-head"><div class="c-tags"><span class="tag quest">Code lab</span></div><h1>Optimization in code: functions, workflows and every common bug</h1>
        <p class="lede">For the assignments. The workflows teach the same skills on fresh examples (never the homework's own problems). Every snippet on these pages was run (Python ${esc(v.python || "?")}, NumPy ${esc(v.numpy || "?")}, SciPy ${esc(v.scipy || "?")}, scikit-learn ${esc(v["scikit-learn"] || "?")}); outputs and error messages are real, though wording can differ slightly in other versions.</p></header>
      <section class="lab-section" id="workflows"><h2>Workflows</h2>
        <div class="lab-grid">${A.workflows.map((w) => `<a class="labcard" href="#/code/flow/${w.id}"><h3>${esc(w.title)}</h3><p>${inline(w.summary)}</p><span class="small">${w.steps.length} steps</span></a>`).join("")}</div></section>
      <section class="lab-section" id="library"><h2>Library guides</h2>
        ${[...groups].map(([g, es]) => `<h3 class="lab-group">${esc(g)}</h3><div class="lab-grid">${es.map((e) => `<a class="labcard" href="#/code/lib/${e.id}"><h3><code>${esc(e.name)}</code></h3><p>${inline(e.summary)}</p></a>`).join("")}</div>`).join("")}</section>
      <section class="lab-section" id="bugs"><h2>The bug library</h2>
        <p>The dangerous ones are <b>silent</b>: no error, just a wrong answer. Each card shows what you'd actually see, why it happens, and the fix, side by side.</p>
        <div class="bug-tools">
          <input id="bug-search" type="search" placeholder="Search bugs, e.g. args, NaN, linprog, shape" aria-label="Search bugs">
          <div class="filters" role="group" aria-label="Filter by kind">
            ${["all", "silent", "warning", "crash"].map((k) => `<button type="button" class="filter" data-kind="${k}" aria-pressed="${k === "all"}">${k === "all" ? "All" : k}</button>`).join("")}
          </div>
          <div class="filters" role="group" aria-label="Filter by library">
            ${["all"].concat(libs).map((l) => `<button type="button" class="filter" data-lib="${esc(l)}" aria-pressed="${l === "all"}">${l === "all" ? "Any library" : esc(l)}</button>`).join("")}
          </div>
        </div>
        <div id="bug-list">${A.bugs.map((b) => bugCard(b, false)).join("")}</div>
        <p class="small" id="bug-count"></p></section>
      <section class="lab-section"><h2>Practice</h2><p>${A.codeProblems.length} small code problems: spot the bug, fill the blank, choose the fix.</p><a class="btn solid" href="#/drill/code">Drill the code problems</a></section>`;
    let kind = "all", libF = "all";
    const apply = () => {
      const q = document.getElementById("bug-search").value.trim().toLowerCase();
      let n = 0;
      A.bugs.forEach((b) => {
        const el = document.getElementById("bug-" + b.id);
        const hit = (kind === "all" || b.kind === kind) && (libF === "all" || b.lib === libF) &&
          (!q || (b.title + " " + b.why + " " + b.fix + " " + (b.symptom || "") + " " + b.bad).toLowerCase().includes(q));
        el.hidden = !hit; if (hit) n++;
      });
      document.getElementById("bug-count").textContent = `${n} of ${A.bugs.length} bugs shown`;
    };
    $main.querySelectorAll("[data-kind]").forEach((b) => b.addEventListener("click", () => { kind = b.dataset.kind; $main.querySelectorAll("[data-kind]").forEach((x) => x.setAttribute("aria-pressed", x === b)); apply(); }));
    $main.querySelectorAll("[data-lib]").forEach((b) => b.addEventListener("click", () => { libF = b.dataset.lib; $main.querySelectorAll("[data-lib]").forEach((x) => x.setAttribute("aria-pressed", x === b)); apply(); }));
    document.getElementById("bug-search").addEventListener("input", apply);
    apply();
    typeset($main);
  }
  function renderLib(id) {
    const e = lib[id];
    if (!e) return renderCodeHome();
    setNav("code");
    const quizzes = A.codeProblems.filter((p) => p.bug && e.errors.includes(p.bug));
    $main.innerHTML = `
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/code">Code lab</a><span>›</span><a href="#/code#library">${esc(e.group)}</a></nav>
      <div class="concept"><article>
        <header class="c-head"><h1><code>${esc(e.name)}</code></h1><p class="lede">${inline(e.summary)}</p></header>
        <div class="prose">
          <p><b>When to reach for it.</b> ${inline(e.when)}</p>
          ${e.signature ? codeBlock(e.signature, "Signature") : ""}
          ${e.args.length ? `<div class="tablewrap"><table><thead><tr><th>Argument / field</th><th>What it means</th></tr></thead><tbody>${e.args.map(([a, d]) => `<tr><td><code class="ic">${esc(a)}</code></td><td>${inline(d)}</td></tr>`).join("")}</tbody></table></div>` : ""}
          ${md(e.body)}
          ${e.code ? `<h2>Minimal working example</h2>${codeBlock(e.code)}${outputBlock(e.output)}` : ""}
        </div>
        ${quizzes.length ? `<section class="practice"><h2>Practice</h2><div id="probs"></div></section>` : ""}
      </article>
      <aside class="rail">
        ${e.errors.length ? `<section><h3>Watch out for</h3><ul class="plain">${e.errors.map((k) => `<li><a href="#/code/bug/${k}">${esc(bug[k].title)}</a> ${kindBadge(bug[k].kind)}</li>`).join("")}</ul></section>` : ""}
        ${e.concepts.length ? `<section><h3>The ideas behind it</h3><div class="chips">${e.concepts.map((k) => chip(byId[k])).join("")}</div></section>` : ""}
        ${e.matlab ? `<section><h3>MATLAB equivalent</h3><p><code class="ic">${esc(e.matlab)}</code></p></section>` : ""}
      </aside></div>`;
    if (quizzes.length) { const host = document.getElementById("probs"); quizzes.forEach((p) => renderProblem(p, host)); }
    typeset($main);
  }
  function renderBug(id) {
    const b = bug[id];
    if (!b) return renderCodeHome();
    setNav("code");
    const quiz = A.codeProblems.find((p) => p.bug === id);
    const libs = A.library.filter((e) => e.errors.includes(id));
    $main.innerHTML = `
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/code">Code lab</a><span>›</span><a href="#/code#bugs">Bug library</a></nav>
      <div class="concept"><article>
        <header class="c-head"><div class="c-tags">${kindBadge(b.kind)}<span class="badge lib">${esc(b.lib)}</span></div><h1>${esc(b.title)}</h1></header>
        <div class="prose">${bugBody(b)}</div>
        ${quiz ? `<section class="practice"><h2>Practice</h2><div id="probs"></div></section>` : ""}
      </article>
      <aside class="rail">
        ${libs.length ? `<section><h3>Library guides</h3><ul class="plain">${libs.map((e) => `<li><a href="#/code/lib/${e.id}"><code>${esc(e.name)}</code></a></li>`).join("")}</ul></section>` : ""}
        <section><h3>More bugs</h3><ul class="plain">${A.bugs.filter((x) => x.lib === b.lib && x.id !== id).slice(0, 6).map((x) => `<li><a href="#/code/bug/${x.id}">${esc(x.title)}</a></li>`).join("")}</ul></section>
      </aside></div>`;
    if (quiz) renderProblem(quiz, document.getElementById("probs"));
    typeset($main);
  }
  function renderFlow(id) {
    const w = flow[id];
    if (!w) return renderCodeHome();
    setNav("code");
    $main.innerHTML = `
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/code">Code lab</a><span>›</span><a href="#/code#workflows">Workflows</a></nav>
      <div class="concept"><article>
        <header class="c-head"><div class="c-tags"><span class="tag quest">Workflow</span></div><h1>${esc(w.title)}</h1><p class="lede">${inline(w.summary)}</p></header>
        <ol class="flow">${w.steps.map((s) => `<li><div class="prose">${md(s.text)}</div>${codeBlock(s.code)}${outputBlock(s.output)}</li>`).join("")}</ol>
        <p class="small">Each step runs in the same Python session as the steps before it; copy them in order into a notebook to reproduce the outputs.</p>
      </article>
      <aside class="rail"><section><h3>The ideas it uses</h3><div class="chips">${w.concepts.map((k) => chip(byId[k])).join("")}</div></section></aside></div>`;
    typeset($main);
  }

  // ---------- drill ----------
  function renderDrill(target) {
    setNav("drill");
    const isCode = target === "code";
    const order = isCode ? [] : target ? pathTo(target) : courseOrder();
    const queue = isCode ? A.codeProblems.map((p) => ({ p, from: p.bug ? { href: `#/code/bug/${p.bug}`, label: bug[p.bug].title } : { href: "#/code", label: "Code lab" } }))
      : order.flatMap((i) => byId[i].problems.map((p) => ({ p, c: byId[i], from: { href: `#/c/${i}`, label: byId[i].short } })));
    let skipSolved = true, at = 0;
    const title = isCode ? "Code problems" : target ? `Readiness path: ${esc(byId[target].short)}` : "The whole course, foundations first";
    const draw = () => {
      const list = skipSolved ? queue.filter(({ p }) => !solved(p.id)) : queue;
      $main.innerHTML = `
        <header class="c-head"><div class="c-tags"><span class="tag quest">Drill</span></div><h1>${title}</h1></header>
        <div class="drill-top">
          <span class="drill-meta">${queue.filter(({ p }) => solved(p.id)).length} of ${queue.length} solved</span>
          <label class="drill-meta" style="display:flex;gap:0.4rem;align-items:center"><input type="checkbox" id="skip" ${skipSolved ? "checked" : ""}> Skip solved problems</label>
          ${isCode ? "" : `<a class="btn quiet" href="#/drill/code">Code problems instead</a>`}
        </div>
        ${order.length ? `<ul class="pathlist" aria-label="Path">${order.map((i) => { const s = conceptStats(byId[i]); return `<li class="${s.done === s.total ? "done" : ""} ${list[at] && list[at].c && list[at].c.id === i ? "now" : ""}">${esc(byId[i].short)}</li>`; }).join("")}</ul>` : ""}
        <div id="drill-host" class="drill-host"></div>
        <div class="drill-nav"><button class="btn quiet" id="prev" type="button">Previous</button><button class="btn solid" id="next" type="button">Next problem</button></div>`;
      document.getElementById("skip").addEventListener("change", (e) => { skipSolved = e.target.checked; at = 0; draw(); });
      const host = document.getElementById("drill-host");
      if (!list.length) {
        host.innerHTML = `<div class="card"><h3>All done here</h3><p>Every problem in this drill is solved. Untick "Skip solved problems" to go round again.</p></div>`;
        document.querySelector(".drill-nav").hidden = true;
        return;
      }
      at = Math.max(0, Math.min(at, list.length - 1));
      const { p, from } = list[at];
      host.innerHTML = `<p class="drill-meta">Problem ${at + 1} of ${list.length} · from <a href="${from.href}">${esc(from.label)}</a></p>`;
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
    $main.innerHTML = `<header class="c-head"><h1>Where this comes from</h1></header>
      <div class="prose sources"><p>The structure, examples and equations follow the MECH 559 lecture slides. Explanations, analogies, widgets and practice are original, informed by the references below. Assignment skills are taught on different examples than the assignments themselves.</p>
      <ol>${A.sources.map((s) => `<li>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>` : esc(s.title)}<span>${esc(s.note)}</span></li>`).join("")}</ol></div>`;
  }

  // ---------- global search ----------
  const index = [].concat(
    A.concepts.map((c) => ({ href: `#/c/${c.id}`, label: c.short, kind: c.layer === 0 ? "foundation" : c.layer === 2 ? "question" : c.layer === 3 ? "exercise" : "idea", text: (c.short + " " + c.title + " " + c.body).toLowerCase() })),
    A.library.map((e) => ({ href: `#/code/lib/${e.id}`, label: e.name, kind: "library", text: (e.name + " " + e.summary + " " + e.when + " " + e.body).toLowerCase() })),
    A.bugs.map((b) => ({ href: `#/code/bug/${b.id}`, label: b.title, kind: "bug", text: (b.title + " " + b.why + " " + b.fix + " " + (b.symptom || "")).toLowerCase() })),
    A.workflows.map((w) => ({ href: `#/code/flow/${w.id}`, label: w.title, kind: "workflow", text: (w.title + " " + w.summary).toLowerCase() })));
  function setupSearch() {
    const input = document.getElementById("search"), box = document.getElementById("search-results");
    if (!input) return;
    const close = () => { box.hidden = true; };
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) { close(); return; }
      const hits = index.map((it) => ({ it, score: (it.label.toLowerCase().includes(q) ? 10 : 0) + (it.text.includes(q) ? 1 : 0) })).filter((h) => h.score > 0)
        .sort((a, b) => b.score - a.score).slice(0, 12);
      box.innerHTML = hits.length ? hits.map(({ it }) => `<a href="${it.href}"><span class="sk">${it.kind}</span>${esc(it.label)}</a>`).join("") : `<p class="empty">No matches.</p>`;
      box.hidden = false;
    });
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { input.value = ""; close(); } if (e.key === "Enter") { const a = box.querySelector("a"); if (a) { location.hash = a.getAttribute("href"); input.value = ""; close(); } } });
    box.addEventListener("click", () => { input.value = ""; close(); });
    document.addEventListener("click", (e) => { if (!e.target.closest(".search")) close(); });
  }

  // ---------- routing ----------
  function route() {
    window.Widgets.stopAll();
    const raw = location.hash.replace(/^#\/?/, "");
    const [path, anchor] = raw.split("#");
    const [view, sub, arg] = path.split("/");
    if (view === "c" && sub) renderConcept(sub);
    else if (view === "code" && sub === "lib") renderLib(arg);
    else if (view === "code" && sub === "bug") renderBug(arg);
    else if (view === "code" && sub === "flow") renderFlow(arg);
    else if (view === "code") renderCodeHome();
    else if (view === "drill") renderDrill(sub === "code" ? "code" : sub && byId[sub] ? sub : null);
    else if (view === "sources") renderSources();
    else renderMap();
    updatePill();
    const target = anchor && document.getElementById(anchor);
    if (target) target.scrollIntoView(); else window.scrollTo(0, 0);
  }
  document.addEventListener("click", (e) => {
    const c = e.target.closest("[data-copy]");
    if (c) {
      const code = c.parentElement.querySelector("pre").innerText;
      const done = () => { c.textContent = "Copied"; setTimeout(() => { c.textContent = "Copy"; }, 1200); };
      if (navigator.clipboard) navigator.clipboard.writeText(code).then(done, done); else done();
    }
  });
  window.addEventListener("hashchange", route);
  setupSearch();
  route();
})();
