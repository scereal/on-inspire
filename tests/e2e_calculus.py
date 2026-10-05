"""Browser tests for the calculus explorer (Playwright).

    python tests/e2e_calculus.py
"""
import functools
import http.server
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


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


def is_open(page, oid):
    return page.get_attribute(f"[data-outcome='{oid}'] > button", "aria-expanded") == "true"


def map_tests(page, base, c, label):
    page.goto(f"{base}/calculus/math-140/")
    page.wait_for_selector("[data-outcome]")
    c.ok("Review of functions and graphs. Limits, continuity, derivative." in page.inner_text(".official"), f"{label}: official description quoted")
    c.ok(page.locator("[data-unit]").count() == 6, f"{label}: all six units shown")
    page.click("[data-outcome='140.3.1'] > button")
    c.ok(is_open(page, "140.3.1"), f"{label}: an outcome opens")
    c.ok(page.locator("[data-outcome='140.3.1'] [data-subtopic]").count() == 3, f"{label}: 140.3.1 lists its 3 subtopics")
    page.click("[data-subtopic='140.3.1.rate'] a[data-target='140.2.1']")
    c.ok(is_open(page, "140.2.1"), f"{label}: a chip to an unbuilt outcome opens it")
    c.ok("coming soon" in page.inner_text("[data-outcome='140.2.1']").lower(), f"{label}: unbuilt outcome says coming soon")
    page.click("[data-outcome='140.3.1'] > button")
    c.ok(not is_open(page, "140.3.1"), f"{label}: an outcome closes again")
    page.goto(f"{base}/calculus/math-140/#140.3.2")
    page.wait_for_selector("[data-outcome]")
    page.wait_for_timeout(200)
    c.ok(is_open(page, "140.3.2"), f"{label}: #140.3.2 opens on load")
    page.goto("about:blank")  # a fresh load, not a hash change on the open page
    page.goto(f"{base}/calculus/math-140/#140.9.9")
    page.wait_for_selector("[data-outcome]")
    c.ok(page.locator("[data-outcome] > button[aria-expanded='true']").count() == 0, f"{label}: an unknown hash opens nothing")
    width = page.evaluate("document.documentElement.scrollWidth")
    c.ok(width <= page.viewport_size["width"], f"{label}: no sideways scroll ({width}px)")


def entrance_tests(page, base, c, label):
    page.goto(f"{base}/math/")
    c.ok(page.locator("a[href='../calculus/math-140/']").count() >= 1, f"{label}: gallery links to the MATH 140 map")
    c.ok(page.locator("a[href='why/atlas.html']").count() >= 1, f"{label}: gallery links to the concept atlas")
    page.goto(f"{base}/#math")
    page.wait_for_timeout(600)
    leaf = page.locator("[aria-label='Calculus 1 (MATH 140)']")
    c.ok(leaf.count() == 1, f"{label}: homepage math node has a Calculus 1 leaf")
    if leaf.count():
        leaf.click()
        page.wait_for_selector("[data-outcome]")
        c.ok(page.url.endswith("/calculus/math-140/"), f"{label}: homepage leaf opens the map")


def main():
    base = serve()
    c, errors = Checker(), []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, vp in [("phone", {"width": 390, "height": 844}), ("desktop", {"width": 1280, "height": 900})]:
            page = browser.new_page(viewport=vp)
            page.on("pageerror", lambda e: errors.append(str(e)))
            map_tests(page, base, c, name)
            entrance_tests(page, base, c, name)
            page.close()
        browser.close()
    for line in c.failures + [f"page error: {e}" for e in errors]:
        print("FAIL", line)
    print("ok: calculus explorer" if not (c.failures or errors) else f"FAILED: {len(c.failures) + len(errors)} problem(s)")
    sys.exit(1 if c.failures or errors else 0)


if __name__ == "__main__":
    main()
