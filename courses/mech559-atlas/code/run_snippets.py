"""Execute the atlas's code snippets and record what really happens.

Called by build.py with a Python that has numpy/scipy/scikit-learn/pandas:
    python run_snippets.py tasks.json results.json
Each task is one of:
    {"kind": "example", "id", "code"}                          -> must run; stdout captured
    {"kind": "bug", "id", "bad", "good", "verify", "good_check", "show"}
    {"kind": "workflow", "id", "steps": [code, ...]}           -> run in one namespace; stdout per step
"""
import contextlib
import io
import json
import sys
import traceback
import warnings


def run(code, ns):
    """Run code in namespace ns; return (stdout, exception or None, [warnings])."""
    buf = io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<snippet>", "exec"), ns)
            exc = None
        except Exception as e:  # noqa: BLE001 - we want every failure recorded
            exc = e
    return buf.getvalue(), exc, [(w.category.__name__, str(w.message)) for w in caught]


def one_line(msg, limit=260):
    msg = " ".join(str(msg).split())
    return msg if len(msg) <= limit else msg[: limit - 1] + "…"


def main(tasks_path, out_path):
    tasks = json.load(open(tasks_path))
    results, failures = {}, []
    for t in tasks:
        tid = t["id"]
        if t["kind"] == "example":
            out, exc, warns = run(t["code"], {})
            if exc:
                failures.append(f"{tid}: example raised {type(exc).__name__}: {exc}")
            results[tid] = {"output": out.rstrip()}
        elif t["kind"] == "workflow":
            ns, outs = {}, []
            for i, code in enumerate(t["steps"]):
                out, exc, _ = run(code, ns)
                if exc:
                    failures.append(f"{tid} step {i + 1}: raised {type(exc).__name__}: {exc}\n{traceback.format_exception_only(type(exc), exc)}")
                outs.append(out.rstrip())
            results[tid] = {"outputs": outs}
        elif t["kind"] == "bug":
            mode = t["verify"][0]
            ns_bad = {}
            out, exc, warns = run(t["bad"], ns_bad)
            symptom = None
            if mode == "raises":
                _, name, sub = t["verify"]
                if exc is None:
                    failures.append(f"{tid}: bad snippet should raise {name} but ran")
                elif type(exc).__name__ != name or sub not in str(exc):
                    failures.append(f"{tid}: expected {name} containing {sub!r}, got {type(exc).__name__}: {exc}")
                else:
                    symptom = f"{type(exc).__name__}: {one_line(exc)}"
            elif mode == "warns":
                _, name, sub = t["verify"]
                hit = [w for w in warns if w[0] == name and sub in w[1]]
                if exc is not None:
                    failures.append(f"{tid}: bad snippet raised {type(exc).__name__}: {exc}")
                elif not hit:
                    failures.append(f"{tid}: expected a {name} containing {sub!r}; got {warns}")
                else:
                    symptom = f"{hit[0][0]}: {one_line(hit[0][1])}"
            else:  # silent
                if exc is not None:
                    failures.append(f"{tid}: bad snippet raised {type(exc).__name__}: {exc}")
                else:
                    try:
                        ok = eval(t["verify"][1], ns_bad)
                    except Exception as e:  # noqa: BLE001
                        ok = False
                        failures.append(f"{tid}: silent check errored: {e}")
                    if not ok:
                        failures.append(f"{tid}: silent check {t['verify'][1]!r} was False: the bug doesn't reproduce")
            bad_show = None
            if exc is None and t.get("show"):
                try:
                    bad_show = str(eval(t["show"], ns_bad))
                except Exception as e:  # noqa: BLE001
                    failures.append(f"{tid}: show (bad) errored: {e}")
            ns_good = {}
            out, exc, warns_good = run(t["good"], ns_good)
            good_show = None
            if exc is not None:
                failures.append(f"{tid}: good snippet raised {type(exc).__name__}: {exc}")
            else:
                try:
                    if not eval(t["good_check"], ns_good):
                        failures.append(f"{tid}: good_check {t['good_check']!r} was False")
                    good_show = str(eval(t["show"], ns_good)) if t.get("show") else None
                except Exception as e:  # noqa: BLE001
                    failures.append(f"{tid}: good check errored: {e}")
            results[tid] = {"symptom": symptom, "bad_show": bad_show, "good_show": good_show}
    import numpy, scipy, sklearn, pandas  # noqa: E401
    results["_versions"] = {"python": sys.version.split()[0], "numpy": numpy.__version__, "scipy": scipy.__version__,
                            "scikit-learn": sklearn.__version__, "pandas": pandas.__version__}
    json.dump({"results": results, "failures": failures}, open(out_path, "w"), indent=1)
    print(f"ran {len(tasks)} code tasks, {len(failures)} failure(s)")
    for f in failures:
        print("FAIL", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
