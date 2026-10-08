"""End-to-end check of the built MECH 430 atlas in a real browser.

- src/gas.js (what the simulators compute with) matches content/gas.py at every point in code/gas_checks.json.
- Every concept page renders; every problem is solved through the UI with every step type: choice, num,
  expr, blank, spot, order, dial (slider set to the verified answer) and code (the reference solution is
  typed into the editor and run in Skulpt, Python in the browser). A wrong solution is confirmed to fail.
- Every simulator renders a readout without errors; the flow lab, code track, drills and sources render.
- No page errors, console errors, MathJax errors, raw TeX/markdown left in the text, or horizontal
  scroll at desktop or phone width.

Run:  python3 test_atlas.py [--site]   (needs playwright and network access to cdnjs and jsdelivr)
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SITE_MODE = "--site" in sys.argv
if SITE_MODE:
    wrapped = None  # the real site page, a full document
    url = (HERE.parent.parent / "docs" / "fluids" / "mech-430" / "index.html").as_uri()
else:
    page_html = (HERE / "mech430-atlas.html").read_text()
    wrapped = HERE / "_test_page.html"
    wrapped.write_text("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head><body>" + page_html + "</body></html>")
    url = wrapped.as_uri()
checks = json.loads((HERE / "code" / "gas_checks.json").read_text())
failures = []
shots = HERE / "_shots"
shots.mkdir(exist_ok=True)
PHONE_PAGES = {"c-back-pressure-regimes", "c-area-ratio", "c-theta-beta-mach", "c-moc-unit-processes", "q-whole-nozzle", "p-root-finding"}
SHOOT = {"c-back-pressure-regimes", "c-shock-formation", "c-mach-cone", "c-area-velocity", "c-choking", "c-normal-shock-relations",
         "c-rocket-thrust", "c-supersonic-inlet", "c-shinkansen", "c-fanno-effects", "c-rayleigh-effects", "c-theta-beta-mach",
         "c-mach-reflection", "c-prandtl-meyer", "c-moc-unit-processes", "c-compressibility", "c-sound-derivation", "c-moving-shocks",
         "c-area-ratio", "c-over-under-expanded"}
RAW_TEXT = """(sel) => {
  const out = [];
  document.querySelectorAll(sel).forEach((root) => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => n.parentElement.closest('mjx-container, script, style, pre, code, textarea, input, .checks') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    let n;
    while ((n = w.nextNode())) if (/\\\\[a-zA-Z]+|\\$|\\[\\[|\\*\\*/.test(n.textContent)) out.push(n.textContent.trim().slice(0, 90));
  });
  return out;
}"""
JS_EVAL = """(checks) => {
  const bad = [];
  for (const [fn, args, want] of checks) {
    let got;
    if (fn === 'nozzle.As') got = Gas.nozzle(args[0], args[1]).As;
    else if (fn === 'nozzle.pd') got = Gas.nozzle(args[0], args[1]).pd;
    else if (fn === 'ob_max') got = Gas.ob_max(...args)[0];
    else got = Gas[fn](...args);
    if (!(Math.abs(got - want) <= 1e-6 * Math.max(1, Math.abs(want)))) bad.push(fn + '(' + args.join(', ') + ') = ' + got + ', python gives ' + want);
  }
  return bad;
}"""


def solve_problem(page, box, p, label, phone=False):
    for si, st in enumerate(p["steps"]):
        step = box.locator(".step").nth(si)
        step.wait_for(timeout=4000)
        t = st["type"]
        if t == "choice":
            right = next(k for k, o in enumerate(st["options"]) if o["correct"])
            step.locator(f'.opt[data-index="{right}"]').click()
        elif t == "spot":
            step.locator(f'.spot-line[data-index="{next(k for k, ln in enumerate(st["lines"]) if ln["wrong"])}"]').click()
        elif t == "order":
            for k in range(len(st["items"])):
                step.locator(f'.order-item[data-index="{k}"]').click()
        elif t == "dial":
            step.locator("input[type=range]").evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", st["answer"])
            step.locator("[data-lock]").click()
        elif t == "code":
            ta = step.locator("textarea")
            ta.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", st["solution"])
            step.locator("[data-run]").click()
            step.locator(".fb").first.wait_for(timeout=60000)
            if step.locator(".fb.ok").count() == 0:
                failures.append(f"{label} {p['id']} code: reference solution failed in Skulpt: {step.locator('.code-out').inner_text()[:400]}")
                return
        else:
            ans = repr(st["answer"]) if t == "num" else st["ref"] if t == "expr" else st["answers"][0]
            step.locator("input").fill(ans)
            step.locator("button[type=submit]").click()
    status = box.locator(".status").inner_text()
    if "Solved" not in status:
        failures.append(f"{label} problem {p['id']}: not solved ({status!r})")


def check_page(page, name, w, label, tex=True):
    sw = page.evaluate("document.documentElement.scrollWidth")
    if sw > w + 1:
        failures.append(f"{name} {label}: horizontal scroll {sw}px")
    if tex:
        page.wait_for_timeout(250)
        failures.extend(f"{name} {label}: raw markup in text: {r!r}" for r in page.evaluate(RAW_TEXT, "main"))


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for name, w, h, scheme in [("desktop", 1280, 900, "light"), ("phone", 390, 844, "dark")]:
        ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
        page = ctx.new_page()
        allowed = ("cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg", "fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net/npm/skulpt@1.2.0/")
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") or any(a in route.request.url for a in allowed) else route.abort())
        errs = []
        page.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        page.on("console", lambda m: errs.append(f"console: {m.text}") if m.type == "error" else None)
        page.goto(url)
        page.wait_for_function("window.MathJax && window.MathJax.typesetPromise", timeout=30000)
        page.wait_for_timeout(800)
        page.screenshot(path=str(shots / f"{name}-map.png"), full_page=name == "desktop")
        check_page(page, name, w, "map")
        A = page.evaluate("window.ATLAS")
        if name == "desktop":
            bad = page.evaluate(JS_EVAL, checks)
            print(f"gas.js vs gas.py: {len(checks)} points, {len(bad)} mismatches")
            failures.extend("gas.js: " + b for b in bad)
            mj = page.evaluate("""async () => {
              const snippets = [];
              const walk = (v) => {
                if (typeof v === 'string') { for (const m of v.replace(/```[\\s\\S]*?```|`[^`]*`/g, '').matchAll(/\\$\\$([\\s\\S]+?)\\$\\$|\\$([^$]+?)\\$/g)) snippets.push([m[1] || m[2], !!m[1]]); }
                else if (Array.isArray(v)) v.forEach(walk);
                else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => { if (!['starter', 'solution', 'tests', 'wrong', 'harness', 'report', 'ref'].includes(k)) walk(x); });
              };
              window.ATLAS.concepts.forEach((c) => { walk(c); c.math.forEach((m) => snippets.push([m, true])); });
              const out = [];
              for (const [tex, display] of snippets) {
                try { const node = await MathJax.tex2svgPromise(tex, { display }); const err = node.querySelector('[data-mjx-error], mjx-merror'); if (err) out.push(tex.slice(0, 80) + '  ->  ' + (err.getAttribute('data-mjx-error') || err.textContent)); }
                catch (e) { out.push(tex.slice(0, 80) + '  ->  ' + e.message); }
              }
              return [snippets.length, out];
            }""")
            print(f"math snippets rendered: {mj[0]}, errors: {len(mj[1])}")
            failures += ["math: " + b for b in mj[1]]
        for c in A["concepts"]:
            cid = c["id"]
            if name == "phone" and cid not in PHONE_PAGES:
                continue
            page.evaluate(f"location.hash = '#/c/{cid}'")
            page.wait_for_selector(".prob", timeout=5000)
            page.wait_for_timeout(150)
            if c["widget"]:
                if page.locator("#widget-host .widget").count() == 0 or not page.locator("#widget-host .w-read, #widget-host .table-out").first.inner_text().strip():
                    failures.append(f"{name} {cid}: widget {c['widget']['type']} has no readout")
            for p in c["problems"]:
                solve_problem(page, page.locator(f'.prob[data-pid="{p["id"]}"]'), p, f"{name} {cid}")
            check_page(page, name, w, cid)
            if cid in SHOOT and (name == "desktop" or cid in PHONE_PAGES):
                page.screenshot(path=str(shots / f"{name}-{cid}.png"), full_page=True)
        # a wrong solution must fail
        if name == "desktop":
            page.evaluate("localStorage.clear(); location.hash = '#/c/c-area-ratio'")
            page.wait_for_selector(".prob")
            cs = next(s for s in next(p for p in next(c for c in A["concepts"] if c["id"] == "c-area-ratio")["problems"] if p["id"] == "c-ar-2")["steps"] if s["type"] == "code")
            step = page.locator('.prob[data-pid="c-ar-2"] .step').first
            step.locator("textarea").evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", cs["wrong"][0])
            step.locator("[data-run]").click()
            step.locator(".fb").first.wait_for(timeout=60000)
            if step.locator(".fb.no").count() == 0:
                failures.append("a wrong solution was accepted for c-ar-2")
            page.screenshot(path=str(shots / "desktop-code-wrong.png"), full_page=False)
            # a wrong number gives feedback
            page.evaluate("location.hash = '#/c/c-normal-shock-relations'")
            page.wait_for_selector(".prob")
            first = page.locator(".prob").first
            first.locator(".step input").first.fill("12345")
            first.locator("button[type=submit]").first.click()
            if first.locator(".fb.no").count() == 0:
                failures.append("a wrong answer gave no feedback")
        # the flow lab: every simulator
        page.evaluate("location.hash = '#/lab'")
        page.wait_for_selector(".simcard")
        n_sims = page.locator(".simcard").count()
        for k in range(n_sims):
            page.locator(".simcard").nth(k).click()
            page.wait_for_timeout(250)
            txt = page.locator("#sim-host .w-read").first.inner_text().strip() if page.locator("#sim-host .w-read").count() else ""
            if not txt:
                failures.append(f"{name} lab simulator {k}: no readout")
            if name == "desktop":
                page.locator("#sim-host").screenshot(path=str(shots / f"sim-{k:02d}.png"))
        check_page(page, name, w, "lab")
        page.screenshot(path=str(shots / f"{name}-lab.png"), full_page=name == "desktop")
        # tables: an inverse lookup
        page.locator(".tables-widget select").nth(1).select_option("AR_sup")
        page.locator(".tables-widget input[type=text]").first.fill("2")
        page.wait_for_timeout(100)
        if "2.19" not in page.locator(".tables-widget .table-out").inner_text():
            failures.append(f"{name}: tables inverse A/A*=2 did not give M=2.197")
        for target in ("#/code", "#/drill", "#/drill/missed", "#/drill/code", "#/sources", "#/"):
            page.evaluate(f"location.hash = '{target}'")
            page.wait_for_timeout(350)
            check_page(page, name, w, target, tex=target not in ("#/drill", "#/drill/code", "#/drill/missed"))
            page.screenshot(path=str(shots / f"{name}-{target.strip('#/').replace('/', '_') or 'home'}.png"))
        page.fill("#search", "shock")
        page.wait_for_timeout(150)
        if page.locator("#search-results a").count() == 0:
            failures.append(f"{name}: search found nothing for 'shock'")
        failures += [f"{name}: {e}" for e in errs]
        ctx.close()
    browser.close()

if wrapped:
    wrapped.unlink()
if failures:
    print("\n".join(failures[:80]))
    print(f"... {len(failures)} failure(s)")
    sys.exit(1)
print(f"atlas e2e ({'site' if SITE_MODE else 'artifact'}): gas.js matches gas.py; every concept, simulator and page renders; every problem (including Python exercises) is solved through the UI; no errors")
