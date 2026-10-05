"""Browser test for the practice page (spec section 7, item 6).

Plays one problem per framework and level at phone and desktop sizes: on every choice step it
clicks a wrong option first (feedback must appear), then the right one; sliders and numbers get a
wrong value then the right one; mixing steps replay a shortest pour sequence from the solver.

Needs Playwright with Chromium plus the generator's dependencies:
    python tests/e2e_practice.py
"""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fractions import Fraction  # noqa: E402

from generator.frameworks.mixing import reachable  # noqa: E402

DOCS = ROOT / "docs"
BANK = DOCS / "math" / "bank"


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(DOCS))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/math/practice/"


def play(page, base, fw, level, failures):
    page.goto(f"{base}?f={fw}&level={level}")
    page.wait_for_selector("#stage[data-problem]", timeout=10000)
    pid = page.get_attribute("#stage", "data-problem")
    data = json.loads((BANK / f"{fw}-{level}.json").read_text())
    problem = next(p for p in data["problems"] if p["id"] == pid)
    for i, step in enumerate(problem["steps"]):
        where = f"{fw}-{level} step {i + 1}"
        fmt = step["format"]
        if fmt == "choice":
            buttons = page.locator(".choices button")
            wrong = next((j for j, o in enumerate(step["options"]) if not o["correct"]), None)
            right = next(j for j, o in enumerate(step["options"]) if o["correct"])
            if wrong is not None:
                buttons.nth(wrong).click()
                if "bad" not in (page.get_attribute(".task .feedback", "class") or ""):
                    failures.append(f"{where}: no feedback after a wrong choice")
            buttons.nth(right).click()
        elif fmt == "number":
            page.fill("#answer", str(step["answer"] * 3 + 1))
            page.click("form.row button[type=submit]")
            if "bad" not in (page.get_attribute(".task .feedback", "class") or ""):
                failures.append(f"{where}: no feedback after a wrong number")
            frac = Fraction(step["answer"]).limit_denominator(100)
            exact = abs(float(frac) - step["answer"]) < 1e-9 and frac.denominator not in (1, 10, 100)
            page.fill("#answer", f"{frac.numerator}/{frac.denominator}" if exact else str(step["answer"]))
            page.click("form.row button[type=submit]")
        elif fmt == "slider":
            set_value = "(e, v) => { e.value = v; e.dispatchEvent(new Event('input')); }"
            page.eval_on_selector("#slider", set_value, str(step["slider"]["min"] + step["slider"]["step"]))
            page.click("button:has-text('Launch')")
            page.eval_on_selector("#slider", set_value, str(step["answer"]))
            page.click("button:has-text('Launch')")
        elif fmt == "mix":
            _, path = reachable(*problem["scene"]["cups"])[Fraction(step["answer"])]
            labels = {"concentrate": "Add concentrate", "water": "Add water", "empty": "Empty"}
            for action, cup in path:
                cell = page.locator(".cup").nth(cup)
                name = labels.get(action) or ("Pour into B" if cup == 0 else "Pour into A")
                cell.get_by_role("button", name=name).click()
        if "good" not in (page.get_attribute(".task .feedback", "class") or ""):
            failures.append(f"{where} ({fmt}): correct answer not accepted")
            return
        page.locator(".task .row button").last.click()
    if "Solved" not in page.inner_text("#task"):
        failures.append(f"{fw}-{level}: finish screen missing")


def main():
    base = serve()
    index = json.loads((BANK / "index.json").read_text())
    failures, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, viewport in [("phone", {"width": 390, "height": 844}), ("desktop", {"width": 1280, "height": 900})]:
            page = browser.new_page(viewport=viewport)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(base)
            page.wait_for_selector(".topics li")
            for fw, info in index.items():
                for level in info["levels"]:
                    play(page, base, fw, int(level), failures)
            page.goto(f"{base}?f=ibp&level=9")
            page.wait_for_selector("text=isn't available yet")
            width = page.evaluate("document.documentElement.scrollWidth")
            if width > viewport["width"]:
                failures.append(f"{name}: page scrolls sideways ({width}px)")
            page.close()
        browser.close()
    for line in failures + [f"page error: {e}" for e in errors]:
        print("FAIL", line)
    print(f"{'ok' if not (failures or errors) else 'FAILED'}: practice page, {sum(len(i['levels']) for i in index.values())} levels x 2 sizes")
    sys.exit(1 if failures or errors else 0)


if __name__ == "__main__":
    main()
