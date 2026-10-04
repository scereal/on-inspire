"""Registry of problem frameworks, keyed by id."""
import importlib

NAMES = ["ibp", "projectile", "mixing", "bounce"]


def get(framework_id):
    module = importlib.import_module(f"generator.frameworks.{framework_id}")
    return module.FRAMEWORK


def available():
    out = {}
    for name in NAMES:
        try:
            out[name] = get(name)
        except ModuleNotFoundError:
            pass
    return out
