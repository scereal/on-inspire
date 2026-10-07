// MECH 419 Atlas: map, concept pages, step-by-step practice and path drills.
(function () {
  const A = window.ATLAS;
  const byId = {};
  const usedBy = {};
  A.concepts.forEach((c) => { byId[c.id] = c; usedBy[c.id] = []; });
  A.concepts.forEach((c) => c.deeper.forEach((d) => usedBy[d].push(c.id)));
  const allProblems = A.concepts.flatMap((c) => c.problems.map((p) => ({ p, c })));
  const $main = document.getElementById("main");

  // ---------- storage (per browser, best effort) ----------
  const KEY = "mech419-atlas:v1";
  let progress = {};
  try { progress = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { progress = {}; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (e) { /* private mode */ } };
  const solved = (pid) => !!progress[pid];
  const conceptStats = (c) => ({ done: c.problems.filter((p) => solved(p.id)).length, total: c.problems.length });

  // ---------- graph helpers ----------
  function ancestors(id) {
    const out = new Set();
    const walk = (i) => byId[i].deeper.forEach((d) => { if (!out.has(d)) { out.add(d); walk(d); } });
    walk(id);
    return out;
  }
  function descendants(id) {
    const out = new Set();
    const walk = (i) => usedBy[i].forEach((d) => { if (!out.has(d)) { out.add(d); walk(d); } });
    walk(id);
    return out;
  }
  // Prerequisites first: depth-first post-order over "builds on".
  function pathTo(id) {
    const order = [], seen = new Set();
    const visit = (i) => { if (seen.has(i)) return; seen.add(i); byId[i].deeper.forEach(visit); order.push(i); };
    visit(id);
    return order;
  }
  function courseOrder() {
    const order = [], seen = new Set();
    const visit = (i) => { if (seen.has(i)) return; seen.add(i); byId[i].deeper.forEach(visit); order.push(i); };
    A.concepts.filter((c) => c.layer === 1).forEach((c) => visit(c.id));
    A.concepts.filter((c) => c.layer === 2).forEach((c) => visit(c.id));
    return order;
  }

  // ---------- text rendering ----------
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  function inline(s) {
    const math = [];
    let t = esc(s).replace(/\$\$[\s\S]+?\$\$|\$[^$]+?\$/g, (m) => { math.push(m); return `\u0000${math.length - 1}\u0000`; });
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*\s][^*]*?)\*/g, "$1<em>$2</em>");
    t = t.replace(/\[\[([a-z0-9-]+)(?:\|([^\]]+))?\]\]/g, (m, id, label) =>
      `<button type="button" class="inline-link" data-go="${id}">${label || esc(byId[id] ? byId[id].short : id)}</button>`);
    return t.replace(/\u0000(\d+)\u0000/g, (m, i) => math[+i]);
  }
  function md(text) {
    return text.split(/\n\s*\n/).map((block) => {
      const lines = block.trim().split("\n");
      if (lines.every((l) => l.trim().startsWith("|"))) {
        const rows = lines.filter((l) => !/^\|\s*-/.test(l.trim())).map((l) => l.trim().replace(/^\||\|$/g, "").split("|"));
        const [head, ...body] = rows;
        return `<table><thead><tr>${head.map((h) => `<th>${inline(h.trim())}</th>`).join("")}</tr></thead><tbody>${body.map((r) => `<tr>${r.map((d) => `<td>${inline(d.trim())}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
      }
      if (lines.every((l) => /^\s*- /.test(l))) return `<ul>${lines.map((l) => `<li>${inline(l.replace(/^\s*- /, ""))}</li>`).join("")}</ul>`;
      if (lines.every((l) => /^\s*\d+\. /.test(l))) return `<ol>${lines.map((l) => `<li>${inline(l.replace(/^\s*\d+\. /, ""))}</li>`).join("")}</ol>`;
      // a paragraph may end in a list: split off list lines
      const firstList = lines.findIndex((l) => /^\s*(- |\d+\. )/.test(l));
      if (firstList > 0 && lines.slice(firstList).every((l) => /^\s*(- |\d+\. )/.test(l))) {
        const ordered = /^\s*\d+\. /.test(lines[firstList]);
        const items = lines.slice(firstList).map((l) => `<li>${inline(l.replace(/^\s*(- |\d+\. )/, ""))}</li>`).join("");
        return `<p>${inline(lines.slice(0, firstList).join(" "))}</p>${ordered ? `<ol>${items}</ol>` : `<ul>${items}</ul>`}`;
      }
      return `<p>${inline(lines.join(" "))}</p>`;
    }).join("");
  }
  function typeset(el) {
    const run = () => window.MathJax.typesetPromise([el]).catch(() => {});
    if (window.MathJax && window.MathJax.typesetPromise) run();
    else { let tries = 0; const t = setInterval(() => { tries++; if (window.MathJax && window.MathJax.typesetPromise) { clearInterval(t); run(); } else if (tries > 100) clearInterval(t); }, 100); }
  }

  // ---------- small UI pieces ----------
  const meter = (c) => { const s = conceptStats(c); return `<span class="meter" aria-hidden="true"><b style="width:${(100 * s.done) / s.total}%"></b></span>`; };
  const chip = (c, extra = "") => {
    const s = conceptStats(c);
    return `<a class="chip ${s.done === s.total ? "done" : ""} ${extra}" href="#/c/${c.id}" data-id="${c.id}" title="${esc(c.title)}"><span>${esc(c.short)}</span>${meter(c)}<span class="sr-only" style="position:absolute;left:-9999px">${s.done} of ${s.total} problems solved</span></a>`;
  };
  function updatePill() {
    const n = allProblems.filter(({ p }) => solved(p.id)).length;
    document.getElementById("progress-pill").textContent = `${n} / ${allProblems.length} problems solved`;
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
    const course = groupsOf(1);
    const found = groupsOf(0);
    const foundOrder = A.subjects.filter((s) => found.has(s));
    const nCourse = A.concepts.filter((c) => c.layer === 1).length;
    $main.innerHTML = `
      <section class="hero">
        <div>
          <h1>Analytical dynamics, from the ground up</h1>
          <p class="lede">All ${nCourse} ideas in the MECH 419 notes, the ${A.concepts.filter((c) => c.layer === 0).length} things from earlier courses they quietly assume, and ${quest.length} exam-style questions that need several at once. Every idea has practice, and every answer is checked.</p>
        </div>
        <ol class="steps-how">
          <li><b>Hover or focus an idea</b> to light up what it builds on (blue) and what builds on it (red).</li>
          <li><b>Open it</b> for the explanation, a live model, an analogy with where it breaks, and practice.</li>
          <li><b>Drill a path</b>: practise every prerequisite of an idea, foundations first.</li>
        </ol>
      </section>
      <div class="tools">
        <input id="map-search" type="search" placeholder="Find an idea: e.g. multiplier, damping, cycloid" aria-label="Find an idea">
        <a class="btn solid" href="#/drill">Drill the whole course</a>
        <span class="legend"><span><i style="background:var(--pen-soft);border:1px solid var(--pen)"></i>builds on</span><span><i style="background:var(--box-soft);border:1px solid var(--box)"></i>used by</span></span>
      </div>
      <div id="map">
        <section class="band quest">
          <div class="band-head"><h2>Questions that join the ideas</h2><p>Exam-style: each needs several concepts at once.</p></div>
          <div class="quest-grid">${quest.map((c) => chip(c)).join("")}</div>
        </section>
        <section class="band course">
          <div class="band-head"><h2>MECH 419, lecture by lecture</h2><p>In the order of the notes.</p></div>
          <div class="groups">${[...course].map(([g, cs]) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${cs.map((c) => chip(c)).join("")}</div></div>`).join("")}</div>
        </section>
        <section class="band found">
          <div class="band-head"><h2>Foundations from earlier courses</h2><p>What the notes assume you already own.</p></div>
          <div class="groups">${foundOrder.map((g) => `<div class="group"><h3>${esc(g)}</h3><div class="chips">${found.get(g).map((c) => chip(c)).join("")}</div></div>`).join("")}</div>
        </section>
      </div>`;
    const map = document.getElementById("map");
    const chips = [...map.querySelectorAll(".chip")];
    const light = (id) => {
      const down = ancestors(id), up = descendants(id);
      map.classList.add("map-dim");
      chips.forEach((ch) => {
        const i = ch.dataset.id;
        ch.classList.toggle("self", i === id);
        ch.classList.toggle("on", down.has(i) || up.has(i));
        ch.classList.toggle("down", down.has(i));
        ch.classList.toggle("up", up.has(i));
      });
    };
    const clear = () => { map.classList.remove("map-dim"); chips.forEach((ch) => ch.classList.remove("self", "on", "down", "up")); };
    chips.forEach((ch) => {
      ch.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") light(ch.dataset.id); });
      ch.addEventListener("pointerleave", clear);
      ch.addEventListener("focus", () => light(ch.dataset.id));
      ch.addEventListener("blur", clear);
    });
    document.getElementById("map-search").addEventListener("input", (e) => {
      const q = e.target.value.trim().toLowerCase();
      chips.forEach((ch) => {
        const c = byId[ch.dataset.id];
        const hit = !q || (c.short + " " + c.title + " " + c.body).toLowerCase().includes(q);
        ch.classList.toggle("hidden", !hit);
      });
    });
  }

  // ---------- problems ----------
  function shuffle(a) { const b = a.slice(); for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } return b; }
  function parseNum(raw) {
    let s = String(raw).trim().replace(/[−–]/g, "-").replace(/[×·]/g, "*").replace(/,/g, "").replace(/[°%]/g, "").replace(/\s+/g, "");
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
    // accept honest rounding when at least 2 significant figures were typed
    const m = String(raw).trim().match(/^-?(\d*)\.?(\d*)$/);
    if (m) {
      const digits = (m[1] + m[2]).replace(/^0+/, "");
      if (digits.length >= 2) return Math.abs(v - ans) <= 0.5 * Math.pow(10, -m[2].length) * 1.0001;
    }
    return false;
  }
  function fmt(x) { const a = Math.abs(x); return a !== 0 && (a < 0.01 || a >= 1e5) ? x.toPrecision(3) : (Math.round(x * 1000) / 1000).toString(); }

  function renderProblem(p, c, host, onDone) {
    const box = document.createElement("article");
    box.className = "prob" + (solved(p.id) ? " solved" : "");
    const fig = p.fig ? window.Figures.svg(p.fig) : "";
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
        if (p.takeaway) { const t = document.createElement("p"); t.className = "takeaway"; t.innerHTML = inline(p.takeaway); stepsEl.appendChild(t); typeset(t); }
        if (onDone) onDone();
        return;
      }
      const s = p.steps[i];
      const el = document.createElement("div");
      el.className = "step";
      const label = p.steps.length > 1 ? `<span class="n">Step ${i + 1} of ${p.steps.length}</span>` : "";
      el.innerHTML = `<div class="step-q">${label}${inline(s.prompt)}</div>`;
      stepsEl.appendChild(el);
      const fb = document.createElement("div");
      const finish = (msg) => {
        fb.className = "fb ok"; fb.innerHTML = msg ? `<p>${inline(msg)}</p>` : "<p>Right.</p>"; el.appendChild(fb); typeset(fb);
        showStep(i + 1);
      };
      if (s.type === "choice") {
        const wrap = document.createElement("div"); wrap.className = "opts";
        shuffle(s.options.map((o, k) => ({ ...o, k }))).forEach((o) => {
          const b = document.createElement("button");
          b.type = "button"; b.className = "opt"; b.dataset.index = o.k; b.innerHTML = inline(o.label);
          b.addEventListener("click", () => {
            if (o.correct) {
              wrap.querySelectorAll(".opt").forEach((x) => { x.disabled = true; });
              b.classList.add("right");
              fb.remove();
              finish(s.explain);
            } else {
              clean = false;
              b.classList.add("wrong"); b.disabled = true;
              fb.className = "fb no"; fb.innerHTML = `<p>${inline(o.why || "Not this one.")}</p>`; el.appendChild(fb); typeset(fb);
            }
          });
          wrap.appendChild(b);
        });
        el.appendChild(wrap);
      } else {
        const row = document.createElement("form");
        row.className = "numrow";
        const id = `in-${p.id}-${i}-${Math.random().toString(36).slice(2, 7)}`;
        row.innerHTML = `<label for="${id}" style="position:absolute;left:-9999px">Your answer</label><input id="${id}" inputmode="decimal" autocomplete="off" placeholder="e.g. 3.14 or 2/3">${s.unit ? `<span class="unit">${esc(s.unit)}</span>` : ""}<button class="btn" type="submit">Check</button><button class="btn quiet" type="button" data-reveal hidden>Show answer</button>`;
        el.appendChild(row);
        let misses = 0;
        const input = row.querySelector("input");
        row.addEventListener("submit", (e) => {
          e.preventDefault();
          const v = parseNum(input.value);
          if (close(input.value, v, s.answer, s.tol)) {
            input.disabled = true; row.querySelectorAll("button").forEach((x) => { x.disabled = true; });
            fb.remove();
            finish((s.explain ? s.explain + " " : "") + (Math.abs(v - s.answer) > 1e-9 * Math.max(1, Math.abs(s.answer)) ? `(Exact: ${fmt(s.answer)}${s.unit ? " " + s.unit : ""}.)` : ""));
          } else {
            clean = false; misses++;
            fb.className = "fb no";
            fb.innerHTML = `<p>${isNaN(v) ? "I couldn't read that as a number. Try a decimal, a fraction like 2/3, or sqrt(2), pi." : "Not quite."} ${s.hint && misses >= 1 ? inline("Hint: " + s.hint) : ""}</p>`;
            el.appendChild(fb); typeset(fb);
            if (misses >= 2) row.querySelector("[data-reveal]").hidden = false;
          }
        });
        row.querySelector("[data-reveal]").addEventListener("click", () => {
          input.value = fmt(s.answer); input.disabled = true; row.querySelectorAll("button").forEach((x) => { x.disabled = true; });
          fb.remove();
          finish(`The answer is ${fmt(s.answer)}${s.unit ? " " + s.unit : ""}. ${s.explain || ""}`);
        });
      }
      typeset(el);
    };
    showStep(0);
    typeset(box);
    return box;
  }

  // ---------- concept page ----------
  function renderConcept(id) {
    const c = byId[id];
    if (!c) { location.hash = "#/"; return; }
    setNav("");
    const layerTag = c.layer === 0 ? `<span class="tag">Foundation · ${esc(c.group)}</span>` : c.layer === 1 ? `<span class="tag course">${esc(c.group)}</span>` : `<span class="tag quest">Exam question</span>`;
    const src = c.source ? `<span class="tag quest" style="background:transparent;border:1px solid var(--rule);color:var(--muted)">Notes: ${esc(c.source)}</span>` : "";
    const beyond = c.beyond ? `<span class="tag beyond">Goes a step past the notes</span>` : "";
    const path = pathTo(id);
    const pathConcepts = path.map((i) => byId[i]);
    const pathProblems = pathConcepts.reduce((n, x) => n + x.problems.length, 0);
    const pathDone = pathConcepts.reduce((n, x) => n + conceptStats(x).done, 0);
    const siblings = A.concepts.filter((x) => x.group === c.group);
    const next = siblings[siblings.indexOf(c) + 1];
    $main.innerHTML = `
      <nav class="crumbs" aria-label="Breadcrumb"><a href="#/">Map</a><span>›</span><span>${esc(c.group)}</span></nav>
      <div class="concept">
        <article>
          <header class="c-head"><div class="c-tags">${layerTag}${src}${beyond}</div><h1>${esc(c.title)}</h1></header>
          <div class="prose">${md(c.body)}</div>
          ${c.math.length ? `<div class="keybox">${c.math.map((m) => `$$${m}$$`).join("")}<p class="k-label">Key results, boxed the way the notes box them</p></div>` : ""}
          <div id="widget-host"></div>
          <div class="cards">
            ${c.analogy ? `<section class="card analogy"><h3>An analogy</h3><p>${inline(c.analogy.text)}</p><p><span class="breaks">Where it breaks:</span> ${inline(c.analogy.breaks)}</p></section>` : ""}
            ${c.exam ? `<section class="card exam"><h3>Open-book exam lens</h3><p>${inline(c.exam)}</p></section>` : ""}
          </div>
          <section class="practice" aria-labelledby="practice-h">
            <h2 id="practice-h">Practice</h2>
            <p>Work each step in order. Wrong choices explain the misconception behind them; numeric answers accept fractions, sqrt() and pi.</p>
            <div id="probs"></div>
          </section>
          ${next ? `<p style="margin-top:2rem;font-family:var(--sans)">Next in ${esc(c.group)}: <a href="#/c/${next.id}">${esc(next.short)}</a></p>` : ""}
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
    c.problems.forEach((p) => renderProblem(p, c, host, () => updateRail(c)));
    typeset($main);
  }
  function updateRail() { /* meters refresh on next navigation; keep the page stable while working */ }

  // ---------- drill ----------
  function renderDrill(target) {
    setNav("drill");
    const order = target ? pathTo(target) : courseOrder();
    const queue = order.flatMap((i) => byId[i].problems.map((p) => ({ p, c: byId[i] })));
    let skipSolved = true;
    let at = 0;
    const title = target ? `Readiness path: ${esc(byId[target].short)}` : "The whole course, foundations first";
    const draw = () => {
      const list = skipSolved ? queue.filter(({ p }) => !solved(p.id)) : queue;
      $main.innerHTML = `
        <header class="c-head"><div class="c-tags"><span class="tag quest">Drill</span></div><h1>${title}</h1></header>
        <div class="drill-top">
          <span class="drill-meta">${queue.filter(({ p }) => solved(p.id)).length} of ${queue.length} problems solved on this path</span>
          <label class="drill-meta" style="display:flex;gap:0.4rem;align-items:center"><input type="checkbox" id="skip" ${skipSolved ? "checked" : ""}> Skip solved problems</label>
          ${target ? `<a class="btn quiet" href="#/c/${target}">Back to ${esc(byId[target].short)}</a>` : ""}
        </div>
        <ul class="pathlist" aria-label="Path">${order.map((i) => { const s = conceptStats(byId[i]); return `<li class="${s.done === s.total ? "done" : ""} ${list[at] && list[at].c.id === i ? "now" : ""}">${esc(byId[i].short)}</li>`; }).join("")}</ul>
        <div id="drill-host" style="max-width:46rem"></div>
        <div class="drill-nav"><button class="btn quiet" id="prev" type="button">Previous</button><button class="btn solid" id="next" type="button">Next problem</button></div>`;
      document.getElementById("skip").addEventListener("change", (e) => { skipSolved = e.target.checked; at = 0; draw(); });
      const host = document.getElementById("drill-host");
      if (!list.length) {
        host.innerHTML = `<div class="card"><h3>Path complete</h3><p>Every problem on this path is solved. Untick "Skip solved problems" to go round again, or pick another idea on the <a href="#/">map</a>.</p></div>`;
        document.querySelector(".drill-nav").hidden = true;
        return;
      }
      at = Math.max(0, Math.min(at, list.length - 1));
      const { p, c } = list[at];
      host.innerHTML = `<p class="drill-meta">Problem ${at + 1} of ${list.length} · from <a href="#/c/${c.id}">${esc(c.short)}</a></p>`;
      renderProblem(p, c, host, null);
      document.getElementById("prev").disabled = at === 0;
      document.getElementById("prev").onclick = () => { at--; draw(); };
      document.getElementById("next").onclick = () => { if (!(skipSolved && solved(p.id))) at++; draw(); };
      typeset($main);
    };
    draw();
  }

  function renderSources() {
    setNav("sources");
    $main.innerHTML = `<header class="c-head"><h1>Where the explanations come from</h1></header>
      <div class="prose sources"><p>The structure and every equation follow the MECH 419 handwritten notes. The analogies, visual models and 'where it breaks' notes draw on these explanations, chosen because they are among the clearest available treatments of these topics.</p>
      <ol>${A.sources.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a><span>${esc(s.note)}</span></li>`).join("")}</ol></div>`;
  }

  // ---------- routing ----------
  function route() {
    window.Widgets.stopAll();
    const h = location.hash.replace(/^#\/?/, "");
    const [view, arg] = h.split("/");
    if (view === "c" && arg) renderConcept(arg);
    else if (view === "drill") renderDrill(arg && byId[arg] ? arg : null);
    else if (view === "sources") renderSources();
    else renderMap();
    updatePill();
    window.scrollTo(0, 0);
  }
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-go]");
    if (t) { location.hash = `#/c/${t.dataset.go}`; }
  });
  window.addEventListener("hashchange", route);
  route();
})();
