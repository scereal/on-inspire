// Learn player: one problem, step by step. Each step asks first, then explains, with "Why?" terms
// leading into the concept network. Spec: design/specs/2026-10-05-math-140-explorer-design.md §4.
(function () {
  const root = document.getElementById("learn");
  const id = new URLSearchParams(location.search).get("id");
  const walk = (window.WALKTHROUGHS || []).find((w) => w.id === id);
  const C = window.CURRICULUM || { units: [] };
  const concepts = Object.fromEntries((window.CONCEPTS || []).map((c) => [c.id, c]));
  const titles = {}, subtopics = {};
  for (const u of C.units) for (const o of u.outcomes) {
    titles[o.id] = o.title;
    for (const s of o.subtopics) { titles[s.id] = s.title; subtopics[s.id] = s; }
  }

  const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const h = (tag, props = {}, ...kids) => { const n = Object.assign(document.createElement(tag), props); n.append(...kids); return n; };
  const math = (node) => {
    try {
      if (window.renderMathInElement) {
        window.renderMathInElement(node, { delimiters: [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false }], throwOnError: false });
      }
    } catch {}
    return node;
  };
  // Show options in a fresh random order each time: the data lists the right answer first.
  const shuffled = (items) => {
    const order = items.map((item, index) => ({ item, index }));
    for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
    return order;
  };
  const terms = (text) => text.replace(/\[\[([a-z0-9-]+)(?:\|([^\]]*))?\]\]/g, (m, cid, label) =>
    `<button type="button" class="why-term" data-concept="${cid}">${label || esc(concepts[cid] ? concepts[cid].title : cid)}</button>`);
  const bold = (text) => text.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  const paragraphs = (text) => text.split(/\n\n+/).map((p) => `<p>${bold(terms(p))}</p>`).join("");
  // Phone keyboards may type a typographic minus; type="text" keeps the minus key on iOS.
  const readNumber = (raw) => {
    const t = raw.trim().replace(/[\u2212\u2013]/g, "-").replace(/\s+/g, "");
    const frac = t.match(/^(-?\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)$/);   // exact answers may be typed as fractions, e.g. 3/2
    if (frac) return Number(frac[2]) === 0 ? NaN : Number(frac[1]) / Number(frac[2]);
    return t === "" ? NaN : Number(t);
  };
  // Speak what a reader sees: drop KaTeX's hidden MathML copy so each formula is read once.
  const speakable = (node) => { const c = node.cloneNode(true); c.querySelectorAll(".katex-mathml").forEach((m) => m.remove()); return c.textContent.replace(/\s+/g, " ").trim(); };
  const chip = (target) => {
    if (target.startsWith("foundation:")) {
      const cid = target.slice(11);
      return `<button type="button" class="chip foundation" data-concept="${esc(cid)}">${esc(concepts[cid] ? concepts[cid].title : cid)}</button>`;
    }
    return `<a class="chip" href="../math-140/#${esc(target)}" data-target="${esc(target)}"><span class="chip-id">${esc(target.split(".").slice(0, 3).join("."))}</span> ${esc(titles[target] || target)}</a>`;
  };
  const chips = (list) => (list && list.length ? `<div class="builds-on"><span>Builds on</span>${list.map(chip).join("")}</div>` : "");

  if (!walk) {
    root.innerHTML = `<h1>Learn</h1><p class="feedback bad">This walkthrough isn't available yet. <a href="../math-140/">Back to the Calculus 1 map</a>.</p>`;
    return;
  }

  // Speech is optional: some browsers don't have it, and accessing it can throw
  let synth = null;
  try { synth = window.speechSynthesis || null; } catch { synth = null; }

  const sub = subtopics[walk.subtopic] || {};
  const practice = walk.practice || sub.practice;
  document.title = `${walk.title}: Learn`;
  root.innerHTML = `
    <header class="learn-head">
      <p class="learn-sub"><a href="../math-140/#${esc(walk.subtopic)}">${esc(walk.subtopic)} ${esc(titles[walk.subtopic] || "")}</a></p>
      <h1>${esc(walk.title)}</h1>
      <div class="learn-problem">${paragraphs(walk.problem)}</div>
      ${chips(sub.builds_on)}
    </header>
    <div class="steps" id="rail" role="list" aria-label="Steps"></div>
    <section class="learn-step" id="step" data-why-host aria-live="off"></section>`;
  math(root.querySelector(".learn-head"));

  root.addEventListener("click", (e) => {
    const c = e.target.closest("[data-concept]");
    if (c && window.Why) { Why.open(c.dataset.concept, {}, c); }
  });

  let current = 0;
  const rail = () => {
    root.querySelector("#rail").replaceChildren(...walk.steps.map((_, i) => {
      const b = h("button", { type: "button", textContent: i + 1, disabled: i > current });
      b.setAttribute("role", "listitem");
      b.setAttribute("aria-label", `Step ${i + 1}`);
      if (i === current) b.setAttribute("aria-current", "step");
      if (i < current) b.classList.add("done");
      b.addEventListener("click", () => go(i));
      return b;
    }));
  };

  const go = (i) => {
    current = i;
    rail();
    const step = walk.steps[i];
    const box = root.querySelector("#step");
    const fb = h("div", { className: "feedback", role: "status" });
    const narration = h("div", { className: "learn-narration", hidden: true });
    narration.innerHTML = paragraphs(step.narration) + (step.math || []).map((m) => `<div class="why-math">$$${m}$$</div>`).join("");
    const widget = h("div", { className: "why-widget", hidden: true });
    const tagRow = h("div", { hidden: true });
    tagRow.innerHTML = chips(step.builds_on);
    const next = h("div", { className: "row", hidden: true });
    const last = i === walk.steps.length - 1;
    const nextBtn = h("button", { type: "button", className: last ? "primary" : "", textContent: last ? "Finish" : "Next step" });
    nextBtn.addEventListener("click", () => (last ? finish() : go(i + 1)));
    next.append(nextBtn);
    const reveal = () => {
      narration.hidden = false;
      tagRow.hidden = false;
      next.hidden = false;
      if (step.widget && window.Widgets) { widget.hidden = false; try { Widgets.render(step.widget.type, widget, step.widget); } catch { widget.hidden = true; } }
      math(narration);
      read.hidden = !synth;
      nextBtn.focus();
    };
    const ask = step.ask;
    const prompt = math(h("p", { className: "prompt", innerHTML: terms(ask.prompt) }));
    let input;
    if (ask.format === "choice") {
      input = h("div", { className: "choices" });
      for (const { item: o, index } of shuffled(ask.options)) {
        const b = math(h("button", { type: "button", innerHTML: o.label }));
        b.dataset.index = index;
        b.addEventListener("click", () => {
          if (o.correct) {
            b.classList.add("right");
            input.querySelectorAll("button").forEach((x) => (x.disabled = true));
            fb.className = "feedback good";
            fb.textContent = "Right.";
            reveal();
          } else {
            b.classList.add("wrong");
            fb.className = "feedback bad";
            fb.innerHTML = terms(o.feedback || "Not quite. Try another.");
            math(fb);
          }
        });
        input.append(b);
      }
    } else {
      const field = h("input", { type: "text", inputMode: "text", autocomplete: "off", spellcheck: false, id: "answer" });
      const check = h("button", { type: "submit", className: "primary", textContent: "Check" });
      input = h("form", { className: "row" }, h("label", { htmlFor: "answer", className: "sr-only", textContent: "Your answer" }), field, check);
      input.addEventListener("submit", (e) => {
        e.preventDefault();
        const v = readNumber(field.value);
        if (Number.isNaN(v)) { fb.className = "feedback bad"; fb.textContent = "Type a number first."; return; }
        if (Math.abs(v - ask.answer) <= (ask.tolerance || 0)) {
          field.disabled = check.disabled = true;
          fb.className = "feedback good";
          fb.textContent = "Right.";
          reveal();
        } else {
          fb.className = "feedback bad";
          fb.textContent = ask.hint || `${v > ask.answer ? "Too big" : "Too small"}. Work through it one step at a time.`;
          math(fb);
        }
      });
    }
    const read = h("button", { type: "button", className: "read-aloud", textContent: "🔊 Read aloud", hidden: true });
    read.addEventListener("click", () => {
      try {
        synth.cancel();
        synth.speak(new SpeechSynthesisUtterance(speakable(narration)));
      } catch { read.hidden = true; }
    });
    box.replaceChildren(h("h2", { textContent: `Step ${i + 1} of ${walk.steps.length}` }), prompt, input, fb, read, narration, widget, tagRow, next);
  };

  const finish = () => {
    current = walk.steps.length;
    rail();
    const box = root.querySelector("#step");
    box.innerHTML = `
      <h2>What you just did</h2>
      <div class="learn-summary">${paragraphs(walk.summary)}</div>
      <div class="row">
        ${practice ? `<a class="button primary practice-this" href="../../math/practice/?f=${encodeURIComponent(practice.framework)}&level=${practice.level}">Practice this</a>` : ""}
        <a class="button" href="../math-140/#${esc(walk.subtopic)}">Back to the Calculus 1 map</a>
      </div>`;
    math(box);
  };

  go(0);
})();
