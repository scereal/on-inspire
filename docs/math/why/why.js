// The "Why?" panel: a browsable network of first-principles explanations.
// Spec: design/specs/2026-10-04-why-network-design.md §5. Concepts come from window.CONCEPTS (concepts.js).
(function () {
  const MAP_LIMIT = 8;
  let byId = null, usedByMap = null;
  let panel = null, history = [], vars = {}, opener = null;

  const store = {
    visited() { try { return new Set(JSON.parse(localStorage.getItem("why:visited") || "[]")); } catch { return new Set(); } },
    mark(id) { try { const v = store.visited(); v.add(id); localStorage.setItem("why:visited", JSON.stringify([...v])); } catch {} },
  };

  function index() {
    if (byId) return;
    byId = {};
    usedByMap = {};
    for (const c of window.CONCEPTS || []) {
      byId[c.id] = c;
      usedByMap[c.id] = usedByMap[c.id] || [];
    }
    for (const c of window.CONCEPTS || []) {
      for (const d of c.deeper || []) (usedByMap[d] = usedByMap[d] || []).push(c.id);
    }
  }

  const usedBy = (id) => { index(); return [...(usedByMap[id] || [])]; };
  const label = (id) => (byId[id] ? byId[id].title : id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));

  function bodyHtml(c) {
    let text = c.body || "";
    if (c.entry) text = text.replace(/\{\{([A-Za-z_]\w*)\}\}/g, (m, k) => (k in vars ? esc(vars[k]) : m));
    text = text.replace(/\[\[([a-z0-9-]+)(?:\|([^\]]*))?\]\]/g, (m, id, shown) =>
      `<button type="button" class="why-term" data-concept="${id}">${shown || esc(label(id))}</button>`);
    return text.split(/\n\n+/).map((p) => `<p>${p}</p>`).join("");
  }

  function linkButtons(ids, visited) {
    return ids.map((id) => `<button type="button" data-concept="${id}" class="${visited.has(id) ? "visited" : ""}">${esc(label(id))}</button>`).join("");
  }

  function mapHtml(c, visited) {
    const groups = { deeper: [...(c.deeper || [])], related: [...(c.related || [])], usedby: usedBy(c.id) };
    const shown = { deeper: [], related: [], usedby: [] };
    const overflow = [];
    let room = MAP_LIMIT;
    for (const kind of ["deeper", "related", "usedby"]) {
      for (const id of groups[kind]) {
        if (room > 0) { shown[kind].push(id); room--; } else overflow.push(id);
      }
    }
    const nodes = (ids) => ids.map((id) => `<button type="button" class="why-node ${visited.has(id) ? "visited" : ""}" data-concept="${id}">${esc(label(id))}</button>`).join("");
    const half = Math.ceil(shown.related.length / 2);
    return {
      map: `<div class="why-map" aria-label="Concept map">
        <div class="why-map-row up">${nodes(shown.usedby)}</div>
        <div class="why-map-row mid"><div class="side">${nodes(shown.related.slice(0, half))}</div>
          <span class="why-node centre" aria-current="true">${esc(c.title)}</span>
          <div class="side">${nodes(shown.related.slice(half))}</div></div>
        <div class="why-map-row down">${nodes(shown.deeper)}</div>
        ${overflow.length ? `<p class="why-more-note">+${overflow.length} more, listed below</p>` : ""}
      </div>`,
      more: overflow.length ? `<div class="why-more"><span>More connections:</span> ${linkButtons(overflow, visited)}</div>` : "",
    };
  }

  function ensurePanel() {
    if (panel) return panel;
    panel = document.createElement("section");
    panel.className = "why-panel";
    panel.hidden = true;
    panel.setAttribute("aria-label", "Why is this the case?");
    panel.addEventListener("click", (e) => {
      const t = e.target.closest("button");
      if (!t) return;
      if (t.dataset.concept) go(t.dataset.concept);
      else if (t.dataset.crumb !== undefined) jump(Number(t.dataset.crumb));
      else if (t.classList.contains("why-back")) back();
      else if (t.classList.contains("why-close")) close();
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && panel && !panel.hidden) close(); });
    return panel;
  }

  function render() {
    index();
    const id = history[history.length - 1];
    const c = byId[id];
    if (!c) return;
    store.mark(id);
    const visited = store.visited();
    const { map, more } = mapHtml(c, visited);
    const trail = history.map((h, i) => (i === history.length - 1
      ? `<span aria-current="page">${esc(label(h))}</span>`
      : `<button type="button" data-crumb="${i}">${esc(label(h))}</button>`)).join(' <span class="sep">›</span> ');
    const math = (c.math || []).map((m) => `<div class="why-math">$$${m}$$</div>`).join("");
    const group = (kind, heading, ids) => (ids.length
      ? `<div class="why-group why-group-${kind}"><span class="why-group-label">${heading}</span>${linkButtons(ids, visited)}</div>` : "");
    panel.innerHTML = `
      <div class="why-top"><button type="button" class="why-back" ${history.length < 2 ? "disabled" : ""}>← Back</button>
        <nav class="why-trail" aria-label="Your route">${trail}</nav></div>
      <h3 class="why-title" tabindex="-1">${esc(c.title)}</h3>
      ${c.foundation ? '<p class="why-kind"><span class="why-badge">Starting point: this rests on nothing deeper</span></p>' : ""}
      <div class="why-body">${bodyHtml(c)}</div>${math}
      <div class="why-widget"></div>
      ${group("deeper", "Why? Go deeper", c.deeper || [])}
      ${group("related", "Related ideas", c.related || [])}
      ${group("usedby", "Where else this is used", usedBy(c.id))}
      ${map}${more}
      <div class="why-bottom"><button type="button" class="why-close">Back to the problem</button></div>`;
    const slot = panel.querySelector(".why-widget");
    if (c.widget && window.Widgets && typeof window.Widgets.render === "function") {
      try { window.Widgets.render(c.widget.type, slot, c.widget); } catch (err) { slot.textContent = "This interactive couldn't load."; }
    } else {
      slot.innerHTML = `<p class="why-placeholder">Interactive: ${esc(c.widget ? c.widget.type : "none")}</p>`;
    }
    try {
      if (window.renderMathInElement) {
        window.renderMathInElement(panel, { delimiters: [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false }], throwOnError: false });
      }
    } catch {}
    panel.querySelector(".why-title").focus();
  }

  function go(id) { index(); if (!byId[id]) return; history.push(id); render(); }
  function back() { if (history.length > 1) { history.pop(); render(); } }
  function jump(i) { history = history.slice(0, i + 1); render(); }

  function open(entryId, entryVars = {}, from = null) {
    index();
    ensurePanel();
    opener = from;
    vars = entryVars || {};
    history = [entryId];
    const host = (from && (from.closest("[data-why-host]") || from.parentElement)) || document.querySelector("main") || document.body;
    if (panel.previousElementSibling !== host) host.after(panel);
    panel.hidden = false;
    render();
    panel.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }

  function close() {
    if (!panel) return;
    panel.hidden = true;
    if (opener && document.contains(opener)) opener.focus();
  }

  function attach(container, entryId, entryVars = {}) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "why-open";
    btn.textContent = "Why is this the case?";
    btn.addEventListener("click", () => open(entryId, entryVars, btn));
    container.append(btn);
    return btn;
  }

  window.Why = { attach, open, close, usedBy };
})();
