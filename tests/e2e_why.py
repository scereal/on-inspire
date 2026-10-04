"""Browser tests for the "Why?" panel (Playwright).

Task 2 tests the panel on the atlas page with a fixture network served in place of concepts.js.
    python tests/e2e_why.py
"""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def node(id, deeper=(), related=(), foundation=False, body=None, entry=False):
    n = {"id": id, "title": f"Title {id}", "body": body or f"About {id}.", "deeper": list(deeper),
         "related": list(related), "foundation": foundation, "widget": {"type": "secant"}}
    if entry:
        n["entry"] = True
    return n


FIXTURE = [
    node("e1", deeper=["a"], entry=True, body="Value is {{V}}, because of [[a|idea A]] and $x^2$."),
    node("e2", deeper=["b"], entry=True),
    node("a", deeper=["f1"], related=["b"], body="A rests on [[f1]]; compare [[b]]."),
    node("b", deeper=["f1"]),
    node("hub", deeper=["f1"], related=[f"n{i}" for i in range(1, 10)]),
    node("f1", foundation=True),
    *[node(f"n{i}", foundation=True) for i in range(1, 10)],
]


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(DOCS)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}"


class Checker:
    def __init__(self):
        self.failures = []

    def ok(self, cond, msg):
        if not cond:
            self.failures.append(msg)


def title(page):
    return page.inner_text(".why-panel .why-title")


def panel_tests(page, base, c, label):
    page.route("**/why/concepts.js", lambda r: r.fulfill(content_type="text/javascript",
                                                          body="window.CONCEPTS = " + json.dumps(FIXTURE) + ";"))
    page.goto(f"{base}/math/why/atlas.html")
    page.wait_for_selector("[data-open='e1']")
    opener = page.locator("[data-open='e1']")
    page.evaluate("() => Why.open('e1', {V: 7}, document.querySelector(\"[data-open='e1']\"))")
    page.wait_for_selector(".why-panel:not([hidden])")
    c.ok(title(page) == "Title e1", f"{label}: entry title shown")
    c.ok("Value is 7" in page.inner_text(".why-panel .why-body"), f"{label}: entry variables filled in")
    c.ok(page.is_disabled(".why-back"), f"{label}: Back disabled at the first concept")
    c.ok(page.evaluate("document.activeElement.classList.contains('why-title')"), f"{label}: focus on the title")
    c.ok(page.evaluate("""() => { let n = document.querySelector('.why-panel');
        for (; n; n = n.parentElement) { const v = n.getAttribute('aria-live'); if (v) return v === 'off'; } return true; }"""),
         f"{label}: the panel isn't announced as a live region")

    page.click(".why-body [data-concept='a']")                      # a term in the text
    c.ok(title(page) == "Title a", f"{label}: term opens its concept")
    page.click(".why-group-deeper [data-concept='f1']")              # Go deeper
    c.ok(title(page) == "Title f1", f"{label}: deeper link")
    c.ok(page.locator(".why-group-usedby [data-concept]").count() >= 2, f"{label}: used-by computed (a, b, hub use f1)")
    page.click(".why-back")
    page.click(".why-back")
    c.ok(title(page) == "Title e1", f"{label}: Back twice returns to the entry")
    c.ok(page.is_disabled(".why-back"), f"{label}: Back disabled again at the start")

    page.click(".why-body [data-concept='a']")
    page.click(".why-group-related [data-concept='b']")              # Related
    c.ok(title(page) == "Title b", f"{label}: related link")
    page.click(".why-map [data-concept='f1']")                       # map node
    c.ok(title(page) == "Title f1", f"{label}: map node")
    c.ok(page.locator(".why-trail [data-crumb]").count() == 3 and page.inner_text(".why-trail [aria-current]") == "Title f1",
         f"{label}: trail shows the route (3 clickable crumbs e1 › a › b, then the current f1)")
    page.click(".why-trail [data-crumb='0']")                        # crumb jump
    c.ok(title(page) == "Title e1" and page.is_disabled(".why-back"), f"{label}: crumb jumps back and truncates history")

    page.evaluate("() => Why.open('hub', {}, document.querySelector(\"[data-open='hub']\"))")
    c.ok(page.locator(".why-map [data-concept]").count() <= 9, f"{label}: map shows at most 8 neighbours + centre")
    c.ok("more" in page.inner_text(".why-map"), f"{label}: map lists the overflow as '+N more'")

    page.evaluate("() => Why.open('e1', {V: 1}, document.querySelector(\"[data-open='e1']\"))")
    page.click(".why-body [data-concept='a']")
    page.evaluate("() => Why.open('e2', {}, document.querySelector(\"[data-open='e2']\"))")
    c.ok(title(page) == "Title e2" and page.is_disabled(".why-back"), f"{label}: a new entry resets the history")

    page.evaluate("() => Why.open('e1', {V: 1}, document.querySelector(\"[data-open='e1']\"))")
    page.keyboard.press("Escape")
    c.ok(page.is_hidden(".why-panel"), f"{label}: Escape closes the panel")
    c.ok(page.evaluate("document.activeElement === document.querySelector(\"[data-open='e1']\")"), f"{label}: focus returns to the opener")
    page.evaluate("() => Why.open('e1', {V: 1}, document.querySelector(\"[data-open='e1']\"))")
    page.click(".why-close")
    c.ok(page.is_hidden(".why-panel"), f"{label}: Back to the problem closes the panel")

    width = page.evaluate("document.documentElement.scrollWidth")
    c.ok(width <= page.viewport_size["width"], f"{label}: no sideways scroll ({width}px)")


TWO_CUPS = [  # (answer to the opening question, moves as (button text, cup index))
    (None, [("Add tea", 0), ("Add water", 0)]),
    ("1/4", [("Add tea", 0), ("Add water", 0), ("Add water", 0), ("Add water", 0)]),
    ("Yes, somehow", [("Add tea", 0), ("Add water", 0), ("Add water", 0), ("Add water", 0), ("Pour into B", 0), ("Add water", 1)]),
    ("3/8", [("Add tea", 0), ("Add water", 0), ("Pour into B", 0), ("Add water", 1), ("Pour into A", 1)]),
]
TWO_CUPS_ENTRIES = ["tc-half", "tc-one-to-three", "tc-one-eighth", "tc-three-eighths"]


def two_cups(page, base, c, label):
    page.goto(f"{base}/math/two-cups/")
    page.wait_for_selector(".cup")
    for level, (answer, moves) in enumerate(TWO_CUPS):
        if answer:
            page.click(f".task .choices button:text-is('{answer}')")
        for text, cup in moves:
            page.locator(".cup").nth(cup).get_by_role("button", name=text).click()
        c.ok("Done in" in page.inner_text(".task"), f"{label}: two cups level {level + 1} solved")
        why = page.locator(".task .why-open")
        c.ok(why.count() == 1, f"{label}: two cups level {level + 1} offers Why?")
        if why.count():
            why.click()
            c.ok(page.is_visible(".why-panel"), f"{label}: two cups level {level + 1} opens the panel")
            entry = page.evaluate("() => (window.CONCEPTS || []).find(x => x.id === %r)?.title" % TWO_CUPS_ENTRIES[level])
            c.ok(entry and page.inner_text(".why-title") == entry, f"{label}: level {level + 1} shows entry {TWO_CUPS_ENTRIES[level]}")
            page.click(".why-body .why-term >> nth=0")
            c.ok(page.is_enabled(".why-back"), f"{label}: level {level + 1} entry links deeper")
            page.click(".why-close")
        if level < 3:
            page.click(".task .row button:text-is('Next step')")


IBP_ENTRIES = ["ibp-pick-u", "ibp-sign", "ibp-v", "ibp-blank", "ibp-chain", "ibp-minus", "ibp-check"]


def ibp(page, base, c, label):
    page.goto(f"{base}/math/integration-by-parts/")
    page.wait_for_selector(".task")
    items = page.evaluate("() => window.IBP_ITEMS")
    for i, item in enumerate(items):
        if item["type"] == "error":
            page.locator(".work button").nth(item["wrong"]).click()
        else:
            right = next(j for j, o in enumerate(item["options"]) if o.get("right"))
            page.locator(".choices button").nth(right).click()
        why = page.locator(".task .why-open")
        c.ok(why.count() == 1, f"{label}: IBP problem {i + 1} offers Why?")
        if why.count():
            why.click()
            c.ok(page.evaluate("""() => { let n = document.querySelector('.why-panel');
                for (; n; n = n.parentElement) { const v = n.getAttribute('aria-live'); if (v) return v === 'off'; } return true; }"""),
                 f"{label}: IBP problem {i + 1} panel isn't announced as a live region")
            entry = page.evaluate("() => (window.CONCEPTS || []).find(x => x.id === %r)?.title" % IBP_ENTRIES[i])
            c.ok(entry and page.inner_text(".why-title") == entry, f"{label}: IBP problem {i + 1} shows {IBP_ENTRIES[i]}")
            page.click(".why-body .why-term >> nth=0")
            c.ok(page.is_enabled(".why-back"), f"{label}: IBP problem {i + 1} entry links deeper")
            page.click(".why-close")
        if i < len(items) - 1:
            page.click(".task .row button:text-is('Next problem')")


SW_ENTRIES = ["sw-best-height", "sw-why-sin3t", "sw-pattern", "sw-gibbs"]


def square_wave(page, base, c, label):
    page.goto(f"{base}/math/square-wave/")
    page.wait_for_selector("#task")
    set_range = "(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }"
    page.locator("input[type=range]").evaluate(set_range, "1.27")
    page.click("text=Check my fit")
    c.ok(page.is_disabled("#task button:text-is('Check my fit')"), f"{label}: square wave Check is disabled after success")
    for i in range(4):
        if i == 1:
            page.click("text=sin 3t")
            page.locator("input[type=range]").evaluate(set_range, "0.42")
            page.click("text=Check my fit")
        elif i == 2:
            page.click(".choices button:text-is('0.25')")
        elif i == 3:
            page.click(".choices button:has-text('narrower')")
        why = page.locator("#task .why-open")
        c.ok(why.count() == 1, f"{label}: square wave step {i + 1} offers Why?")
        if why.count():
            why.click()
            entry = page.evaluate("() => (window.CONCEPTS || []).find(x => x.id === %r)?.title" % SW_ENTRIES[i])
            c.ok(entry and page.inner_text(".why-title") == entry, f"{label}: square wave step {i + 1} shows {SW_ENTRIES[i]}")
            body = page.inner_text(".why-body")
            c.ok("{{" not in body, f"{label}: square wave step {i + 1} fills its numbers")
            if i == 0:
                c.ok("1.27" in body, f"{label}: step 1 entry shows the page's 1.27")
            page.click(".why-body .why-term >> nth=0")
            c.ok(page.is_enabled(".why-back"), f"{label}: square wave step {i + 1} entry links deeper")
            page.click(".why-close")
        if i < 3:
            page.click("#task button:text-is('Next step')")


def atlas(page, base, c, label):
    page.goto(f"{base}/math/why/atlas.html")
    page.wait_for_selector(".atlas-map [data-node]")
    concepts = page.evaluate("() => window.CONCEPTS")
    edges = sum(len(x["deeper"]) for x in concepts)
    c.ok(page.locator(".atlas-map [data-node]").count() == len(concepts), f"{label}: atlas map shows every concept")
    c.ok(page.locator(".atlas-map line.atlas-edge").count() == edges, f"{label}: atlas map draws every deeper link ({edges})")
    page.click(".atlas-map [data-node='limit']")
    c.ok(page.is_visible(".why-panel") and page.inner_text(".why-title") == next(x["title"] for x in concepts if x["id"] == "limit"),
         f"{label}: clicking a map node opens it")
    page.click(".why-close")
    page.click(".atlas-map [data-node='sw-best-height']")
    c.ok("{{" not in page.inner_text(".why-body"), f"{label}: atlas entries show example numbers, not {{{{A1}}}}")
    page.click(".why-close")
    if label != "desktop":
        wide = []
        for concept in concepts:
            page.evaluate("(id) => Why.open(id)", concept["id"])
            if page.evaluate("document.documentElement.scrollWidth") > page.viewport_size["width"]:
                wide.append(concept["id"])
        c.ok(not wide, f"{label}: every widget fits without sideways scroll (overflowing: {wide})")
        return
    for concept in concepts:  # every widget renders and responds once
        page.evaluate("(id) => Why.open(id)", concept["id"])
        w = page.locator(".why-widget")
        ok = w.locator("svg").count() == 1 and w.locator(".w-readout").count() == 1
        snapshot = lambda: (w.locator(".w-readout").inner_text(), w.locator("svg").inner_html()) if ok else ("", "")
        before = snapshot()
        rng = w.locator("input[type=range]")
        if rng.count():  # move to whichever end of the range differs from the current value
            rng.first.evaluate("(el) => { el.value = Number(el.value) >= Number(el.max) ? el.min : el.max; el.dispatchEvent(new Event('input')); }")
        else:
            w.locator(".w-controls button").first.click()
        after = snapshot()
        c.ok(ok and after[0] and after != before, f"widget for '{concept['id']}' ({concept['widget']['type']}) renders and responds")


def main():
    base = serve()
    c, errors = Checker(), []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, vp in [("phone", {"width": 390, "height": 844}), ("desktop", {"width": 1280, "height": 900})]:
            page = browser.new_page(viewport=vp)
            page.on("pageerror", lambda e: errors.append(str(e)))
            panel_tests(page, base, c, name)
            page.unroute("**/why/concepts.js")
            two_cups(page, base, c, name)
            ibp(page, base, c, name)
            square_wave(page, base, c, name)
            atlas(page, base, c, name)
            page.close()

        # Hostile environments: no localStorage, no KaTeX
        ctx = browser.new_context()
        ctx.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } });")
        ctx.route("**/cdnjs.cloudflare.com/**", lambda r: r.abort())
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(f"hostile: {e}"))
        panel_tests(page, base, c, "no-storage-no-katex")
        c.ok("$x^2$" in page.evaluate("() => { Why.open('e1', {V: 2}); return document.querySelector('.why-body').textContent; }"),
             "no-katex: raw math stays readable")
        ctx.close()
        browser.close()
    for line in c.failures + [f"page error: {e}" for e in errors]:
        print("FAIL", line)
    print("ok: why panel" if not (c.failures or errors) else f"FAILED: {len(c.failures) + len(errors)} problem(s)")
    sys.exit(1 if c.failures or errors else 0)


if __name__ == "__main__":
    main()
