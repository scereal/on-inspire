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
            learn_tests(page, base, c, name)
            page.close()
        no_speech_test(browser, base, c)
        browser.close()
    for line in c.failures + [f"page error: {e}" for e in errors]:
        print("FAIL", line)
    print("ok: calculus explorer" if not (c.failures or errors) else f"FAILED: {len(c.failures) + len(errors)} problem(s)")
    sys.exit(1 if c.failures or errors else 0)



# --- Learn player (Task 2), with a fixture walkthrough -----------------------------------
import json as _json

FIXTURE_WALK = [{
    "id": "learn-fixture", "subtopic": "140.3.1.rate", "title": "Fixture walkthrough",
    "problem": "A ball falls. How fast at $t = 2$?",
    "steps": [
        {"ask": {"prompt": "First question?", "format": "choice", "answer": "Right",
                 "options": [{"label": "Right", "correct": True}, {"label": "Wrong", "misconception": "m", "feedback": "Not that one."}]},
         "narration": "Because of the [[limit]].", "builds_on": ["140.2.1"]},
        {"ask": {"prompt": "Type 4", "format": "number", "answer": 4, "tolerance": 0.01}, "narration": "Four it is."},
    ],
    "summary": "Done.", "practice": {"framework": "ibp", "level": 1},
}]


def learn_tests(page, base, c, label):
    page.route("**/learn/walkthroughs.js", lambda r: r.fulfill(
        content_type="text/javascript", body="window.WALKTHROUGHS = " + _json.dumps(FIXTURE_WALK) + ";"))
    page.goto(f"{base}/calculus/learn/?id=learn-fixture")
    page.wait_for_selector(".learn-problem")
    c.ok("ball falls" in page.inner_text(".learn-problem"), f"{label}: learn shows the problem")
    c.ok(page.locator(".learn-head a[data-target], .learn-head .chip").count() >= 1, f"{label}: learn shows Builds-on chips")
    c.ok(page.is_visible(".read-aloud"), f"{label}: Read aloud shown when speech exists")
    c.ok(page.is_hidden(".learn-narration"), f"{label}: narration hidden before answering")
    page.click(".learn-step .choices button:text-is('Wrong')")
    c.ok("Not that one" in page.inner_text(".learn-step .feedback"), f"{label}: wrong answer gets its feedback")
    page.click(".learn-step .choices button:text-is('Right')")
    c.ok(page.is_visible(".learn-narration"), f"{label}: narration revealed after the right answer")
    page.click(".learn-narration .why-term")
    c.ok(page.is_visible(".why-panel"), f"{label}: a term opens the Why? panel")
    page.click(".why-close")
    page.click("button:text-is('Next step')")
    page.fill(".learn-step input[type=number]", "5")
    page.click(".learn-step button:text-is('Check')")
    c.ok("bad" in (page.get_attribute(".learn-step .feedback", "class") or ""), f"{label}: wrong number gets feedback")
    page.fill(".learn-step input[type=number]", "4")
    page.click(".learn-step button:text-is('Check')")
    page.click("button:text-is('Finish')")
    href = page.get_attribute("a.practice-this", "href") or ""
    c.ok("f=ibp" in href and "level=1" in href, f"{label}: finish links to practice ({href})")
    page.unroute("**/learn/walkthroughs.js")
    page.goto(f"{base}/calculus/learn/?id=learn-ghost")
    page.wait_for_selector("text=isn't available yet")
    c.ok(page.locator("a[href='../math-140/']").count() >= 1, f"{label}: unknown walkthrough links back to the map")
    width = page.evaluate("document.documentElement.scrollWidth")
    c.ok(width <= page.viewport_size["width"], f"{label}: learn page has no sideways scroll")


def no_speech_test(browser, base, c):
    ctx = browser.new_context()
    ctx.add_init_script("Object.defineProperty(window, 'speechSynthesis', { get() { throw new Error('no speech'); } });")
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("**/learn/walkthroughs.js", lambda r: r.fulfill(
        content_type="text/javascript", body="window.WALKTHROUGHS = " + _json.dumps(FIXTURE_WALK) + ";"))
    page.goto(f"{base}/calculus/learn/?id=learn-fixture")
    page.wait_for_selector(".learn-problem")
    c.ok(page.locator(".read-aloud:visible").count() == 0, "no-speech: Read aloud is hidden")
    page.click(".learn-step .choices button:text-is('Right')")
    c.ok(page.is_visible(".learn-narration") and not errors, f"no-speech: walkthrough still works ({errors})")
    ctx.close()


if __name__ == "__main__":
    main()
