"""End-to-end check of the built MECH 559 atlas in a real browser.

Opens every concept page and every Code lab page, solves every problem through the UI (all six step
types: choice, num, expr, blank, spot, order), and fails on any page error, console error, MathJax
error, raw TeX or unresolved [[link]] left in the text, horizontal scroll, empty widget readout, or a
problem that doesn't reach 'Solved'.

Run:  python3 test_atlas.py [--site]   (needs playwright; PLAYWRIGHT_BROWSERS_PATH if browsers live elsewhere)
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SITE_MODE = "--site" in sys.argv
if SITE_MODE:
    wrapped = None  # the real site page, a full document
    url = (HERE.parent.parent / "docs" / "optimization" / "mech-559" / "index.html").as_uri()
else:
    # the artifact page is a body fragment; wrap it the way the artifact host does
    page_html = (HERE / "mech559-atlas.html").read_text()
    wrapped = HERE / "_test_page.html"
    wrapped.write_text("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head><body>" + page_html + "</body></html>")
    url = wrapped.as_uri()
failures = []
shots = HERE / "_shots"
shots.mkdir(exist_ok=True)
PHONE_PAGES = {"c-kkt", "c-negative-null-form", "c-least-squares", "c-trust-region", "q-lp-vertex-nlp", "p-numpy-shapes"}
SHOOT = {"c-kkt", "c-scaling", "c-rbf", "c-kriging", "c-descent", "c-armijo", "c-lp-standard-form", "c-penalty-barrier", "c-pareto", "c-doe",
         "c-model-assessment", "c-feasibility", "c-trust-region", "p-eigen-definiteness", "c-negative-null-form"}

RAW_TEXT = """(sel) => {
  const out = [];
  document.querySelectorAll(sel).forEach((root) => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => n.parentElement.closest('mjx-container, script, style, pre, code, input, .shows') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    let n;
    while ((n = w.nextNode())) if (/\\\\[a-zA-Z]+|\\$|\\[\\[|\\*\\*/.test(n.textContent)) out.push(n.textContent.trim().slice(0, 90));
  });
  return out;
}"""


def solve_problem(page, box, p, label):
    for si, st in enumerate(p["steps"]):
        step = box.locator(".step").nth(si)
        step.wait_for(timeout=3000)
        t = st["type"]
        if t == "choice":
            right = next(k for k, o in enumerate(st["options"]) if o["correct"])
            step.locator(f'.opt[data-index="{right}"]').click()
        elif t == "spot":
            wrong = next(k for k, ln in enumerate(st["lines"]) if ln["wrong"])
            step.locator(f'.spot-line[data-index="{wrong}"]').click()
        elif t == "order":
            for k in range(len(st["items"])):
                step.locator(f'.order-item[data-index="{k}"]').click()
        else:
            ans = repr(st["answer"]) if t == "num" else st["typed"] if t == "expr" else st["answers"][0]
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
        allowed = ("cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg", "fonts.googleapis.com", "fonts.gstatic.com")
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") or any(a in route.request.url for a in allowed) else route.abort())
        errs = []
        page.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        page.on("console", lambda m: errs.append(f"console: {m.text}") if m.type == "error" else None)
        page.goto(url)
        page.wait_for_function("window.MathJax && window.MathJax.typesetPromise", timeout=30000)
        page.wait_for_timeout(600)
        page.screenshot(path=str(shots / f"{name}-map.png"), full_page=name == "desktop")
        check_page(page, name, w, "map")
        A = page.evaluate("window.ATLAS")
        if name == "desktop":
            bad = page.evaluate("""async () => {
              const snippets = [];
              const walk = (v) => {
                if (typeof v === 'string') { for (const m of v.replace(/```[\\s\\S]*?```|`[^`]*`/g, '').matchAll(/\\$\\$([\\s\\S]+?)\\$\\$|\\$([^$]+?)\\$/g)) snippets.push([m[1] || m[2], !!m[1]]); }
                else if (Array.isArray(v)) v.forEach(walk);
                else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => { if (!['code', 'bad', 'good', 'signature', 'js', 'output', 'symptom', 'bad_show', 'good_show', 'outputs'].includes(k)) walk(x); });
              };
              const A = window.ATLAS;
              A.concepts.forEach((c) => { walk(c); c.math.forEach((m) => snippets.push([m, true])); });
              [A.library, A.bugs, A.workflows, A.codeProblems].forEach(walk);
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

        # concept pages
        for c in A["concepts"]:
            cid = c["id"]
            if name == "phone" and cid not in PHONE_PAGES:
                continue
            page.evaluate(f"location.hash = '#/c/{cid}'")
            page.wait_for_selector(".prob", timeout=5000)
            page.wait_for_timeout(120)
            if c["widget"]:
                if page.locator(".widget canvas").count() == 0 or not page.locator(".w-read").first.inner_text().strip():
                    failures.append(f"{name} {cid}: widget {c['widget']['type']} didn't render a readout")
            for pi, p in enumerate(c["problems"]):
                solve_problem(page, page.locator(f'.prob[data-pid="{p["id"]}"]'), p, f"{name} {cid}")
            check_page(page, name, w, cid)
            if cid in SHOOT and (name == "desktop" or cid in PHONE_PAGES):
                page.screenshot(path=str(shots / f"{name}-{cid}.png"), full_page=True)

        # Code lab
        page.evaluate("location.hash = '#/code'")
        page.wait_for_selector("#bug-list")
        check_page(page, name, w, "code home")
        page.screenshot(path=str(shots / f"{name}-code.png"), full_page=name == "desktop")
        page.fill("#bug-search", "args")
        shown = page.locator(".bugcard:not([hidden])").count()
        if not 0 < shown < len(A["bugs"]):
            failures.append(f"{name}: bug search 'args' showed {shown} cards")
        page.fill("#bug-search", "")
        page.click('[data-kind="silent"]')
        silent = sum(b["kind"] == "silent" for b in A["bugs"])
        if page.locator(".bugcard:not([hidden])").count() != silent:
            failures.append(f"{name}: silent filter mismatch")
        libs = A["library"] if name == "desktop" else A["library"][:2]
        for e in libs:
            page.evaluate(f"location.hash = '#/code/lib/{e['id']}'")
            page.wait_for_selector("h1 code")
            if e["code"] and page.locator(".output").count() == 0 and e.get("output"):
                failures.append(f"{name} {e['id']}: output not shown")
            check_page(page, name, w, e["id"])
        if name == "desktop":
            page.evaluate("location.hash = '#/code/lib/lib-minimize'")
            page.wait_for_timeout(300)
            page.screenshot(path=str(shots / "desktop-lib-minimize.png"), full_page=True)
        quiz_for = {p["bug"]: p for p in A["codeProblems"] if p.get("bug")}
        bugs = A["bugs"] if name == "desktop" else A["bugs"][:3]
        for b in bugs:
            page.evaluate(f"location.hash = '#/code/bug/{b['id']}'")
            page.wait_for_selector(".pair")
            if b["id"] in quiz_for:
                p = quiz_for[b["id"]]
                solve_problem(page, page.locator(f'.prob[data-pid="{p["id"]}"]'), p, f"{name} {b['id']}")
            elif name == "desktop":
                failures.append(f"{b['id']}: no practice quiz")
            check_page(page, name, w, b["id"])
        if name == "desktop":
            page.evaluate("location.hash = '#/code/bug/e-ineq-sign'"); page.wait_for_timeout(300)
            page.screenshot(path=str(shots / "desktop-bug-ineq.png"), full_page=True)
        for fl in A["workflows"]:
            page.evaluate(f"location.hash = '#/code/flow/{fl['id']}'")
            page.wait_for_selector(".flow")
            if page.locator(".flow .output").count() < sum(1 for s in fl["steps"] if s["output"]):
                failures.append(f"{name} {fl['id']}: missing outputs")
            check_page(page, name, w, fl["id"])
            page.screenshot(path=str(shots / f"{name}-{fl['id']}.png"), full_page=name == "desktop")
        # the standalone code problems, through the drill
        if name == "desktop":
            byid = {p["id"]: p for p in A["codeProblems"]}
            page.evaluate("location.hash = '#/drill/code'")
            for _ in range(len(byid) + 2):
                page.wait_for_timeout(200)
                box = page.locator("#drill-host .prob")
                if box.count() == 0:
                    break
                pid = box.get_attribute("data-pid")
                solve_problem(page, box, byid[pid], "drill/code")
                page.click("#next")
            left = page.evaluate("window.ATLAS.codeProblems.filter(p => !JSON.parse(localStorage.getItem('mech559-atlas:v1') || '{}')[p.id]).map(p => p.id)")
            if left:
                failures.append(f"code problems left unsolved: {left}")
        # search
        page.fill("#search", "linprog")
        page.wait_for_timeout(150)
        if page.locator("#search-results a").count() == 0:
            failures.append(f"{name}: search found nothing for 'linprog'")
        page.keyboard.press("Escape")
        # a wrong answer shows its misconception and leaves the problem open
        page.evaluate("localStorage.clear(); location.hash = '#/c/c-descent'")
        page.wait_for_timeout(300)
        page.evaluate("location.hash = '#/c/c-fonc'")
        page.wait_for_selector(".prob")
        first = page.locator(".prob").first
        inp = first.locator(".step input")
        if inp.count():
            inp.first.fill("12345")
            first.locator("button[type=submit]").first.click()
            if first.locator(".fb.no").count() == 0:
                failures.append(f"{name}: a wrong answer gave no feedback")
        for target in ("#/drill", "#/drill/c-sqp", "#/sources", "#/"):
            page.evaluate(f"location.hash = '{target}'")
            page.wait_for_timeout(300)
            check_page(page, name, w, target, tex=target != "#/drill" and target != "#/drill/c-sqp")
            page.screenshot(path=str(shots / f"{name}-{target.strip('#/').replace('/', '_') or 'home'}.png"))
        failures += [f"{name}: {e}" for e in errs]
        ctx.close()
    browser.close()

if wrapped:
    wrapped.unlink()
if failures:
    print("\n".join(failures))
    sys.exit(1)
print(f"atlas e2e ({'site' if SITE_MODE else 'artifact'}): every concept and Code lab page renders, every problem is solvable through the UI, no errors")
