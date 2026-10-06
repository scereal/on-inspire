"""Registry of problem frameworks, keyed by framework id (module names use underscores, ids may use hyphens)."""
import importlib

NAMES = ["ibp", "projectile", "mixing", "bounce", "derivative_definition", "derivative_rules", "limits", "continuity", "elementary_derivatives", "applications", "functions"]


def get(framework_id):
    module = importlib.import_module(f"generator.frameworks.{framework_id.replace('-', '_')}")
    return module.FRAMEWORK


def available():
    out = {}
    for name in NAMES:
        try:
            fw = get(name)
        except ModuleNotFoundError:
            continue
        out[fw.id] = fw
    return out
