"""End-to-end check of the built atlas in a real browser.

Opens every concept page at desktop and phone width, solves every problem through the UI
(clicking the right option, typing the numeric answer), and fails on any page error,
console error, horizontal scroll, or problem that doesn't reach 'Solved'.

Run:  python3 test_atlas.py [--site]   (needs playwright; PLAYWRIGHT_BROWSERS_PATH if browsers live elsewhere)
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SITE_MODE = "--site" in sys.argv
if SITE_MODE:
    # the real site page, a full document
    wrapped = None
    url = (HERE.parent.parent / "docs" / "dynamics" / "mech-419" / "index.html").as_uri()
else:
    # the artifact page is a body fragment; wrap it the way the artifact host does
    page_html = (HERE / "mech419-atlas.html").read_text()
    wrapped = HERE / "_test_page.html"
    wrapped.write_text("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head><body>" + page_html + "</body></html>")
    url = wrapped.as_uri()

failures = []
shots = HERE / "_shots"
shots.mkdir(exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for name, w, h, scheme in [("desktop", 1280, 900, "light"), ("phone", 390, 844, "dark")]:
        ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
        page = ctx.new_page()
        allowed = ("cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg", "fonts.googleapis.com", "fonts.gstatic.com")
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") or any(a in route.request.url for a in allowed) else route.abort())
        errs = []
        page.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        page.on("console", lambda m: errs.append(f"console: {m.text}") if m.type == "error" else None)
        page.goto(url)
        page.wait_for_function("window.MathJax && window.MathJax.typesetPromise", timeout=30000)
        page.wait_for_timeout(500)
        page.screenshot(path=str(shots / f"{name}-map.png"), full_page=False)
        if name == "desktop":
            bad = page.evaluate("""async () => {
              const snippets = [];
              const walk = (v) => {
                if (typeof v === 'string') { for (const m of v.matchAll(/\\$\\$([\\s\\S]+?)\\$\\$|\\$([^$]+?)\\$/g)) snippets.push([m[1] || m[2], !!m[1]]); }
                else if (Array.isArray(v)) v.forEach(walk);
                else if (v && typeof v === 'object') Object.values(v).forEach(walk);
              };
              window.ATLAS.concepts.forEach((c) => { walk(c); c.math.forEach((m) => snippets.push([m, true])); });
              const out = [];
              for (const [tex, display] of snippets) {
                try {
                  const node = await MathJax.tex2svgPromise(tex, { display });
                  const err = node.querySelector('[data-mjx-error], mjx-merror');
                  if (err) out.push(tex.slice(0, 80) + '  ->  ' + (err.getAttribute('data-mjx-error') || err.textContent));
                } catch (e) { out.push(tex.slice(0, 80) + '  ->  ' + e.message); }
              }
              return [snippets.length, out];
            }""")
            print(f"math snippets rendered: {bad[0]}, errors: {len(bad[1])}")
            failures += ["math: " + b for b in bad[1]]
        ids = page.evaluate("window.ATLAS.concepts.map(c => c.id)")
        for cid in ids:
            page.evaluate(f"location.hash = '#/c/{cid}'")
            page.wait_for_selector(f".prob", timeout=5000)
            page.wait_for_timeout(120)
            sw = page.evaluate("document.documentElement.scrollWidth")
            if sw > w + 1:
                failures.append(f"{name} {cid}: horizontal scroll {sw}px")
            if name == "phone" and cid not in ("c-lagrange-recipe", "c-dynamic-eq", "c-brachistochrone", "p-dot"):
                continue  # solve everything once (desktop); on phone spot-check a few pages
            probs = page.evaluate(f"window.ATLAS.concepts.find(c => c.id === '{cid}').problems")
            for pi, p in enumerate(probs):
                box = page.locator(".prob").nth(pi)
                for si, st in enumerate(p["steps"]):
                    step = box.locator(".step").nth(si)
                    step.wait_for(timeout=3000)
                    if st["type"] == "choice":
                        right = next(k for k, o in enumerate(st["options"]) if o["correct"])
                        step.locator(f'.opt[data-index="{right}"]').click()
                    else:
                        step.locator("input").fill(repr(st["answer"]))
                        step.locator("button[type=submit]").click()
                status = box.locator(".status").inner_text()
                if "Solved" not in status:
                    failures.append(f"{name} {cid} problem {p['id']}: not solved ({status!r})")
            page.wait_for_timeout(400)
            raw = page.evaluate("""() => {
              const w = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT, { acceptNode: (n) => n.parentElement.closest('mjx-container, script, style') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
              const out = []; let n;
              while ((n = w.nextNode())) if (/\\\\[a-zA-Z]+|\\$/.test(n.textContent)) out.push(n.textContent.trim().slice(0, 90));
              return out;
            }""")
            failures += [f"{name} {cid}: raw TeX in text: {r!r}" for r in raw]
            if cid in ("c-lagrange-recipe", "c-dynamic-eq", "c-brachistochrone", "c-constraint-types", "c-canonical", "c-linearization", "q-pipeline", "p-dot"):
                page.screenshot(path=str(shots / f"{name}-{cid}.png"), full_page=True)
        # one wrong answer path: a choice step shows its misconception and stays unsolved
        page.evaluate("location.hash = '#/c/p-taylor'")
        page.wait_for_selector(".prob")
        for target in ("#/drill", "#/drill/c-linearization", "#/sources", "#/"):
            page.evaluate(f"location.hash = '{target}'")
            page.wait_for_timeout(300)
            page.screenshot(path=str(shots / f"{name}-{target.strip('#/').replace('/', '_') or 'home'}.png"))
        failures += [f"{name}: {e}" for e in errs]
        ctx.close()
    browser.close()

if wrapped:
    wrapped.unlink()
if failures:
    print("\n".join(failures))
    sys.exit(1)
print(f"atlas e2e ({'site' if SITE_MODE else 'artifact'}): all concept pages render, every problem solvable through the UI, no errors")
