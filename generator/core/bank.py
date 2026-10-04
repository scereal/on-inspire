"""Build, write and re-check problem banks (spec sections 3.3 and 6)."""
import hashlib
import json
import random
from pathlib import Path

from .themes import summary
from .validators import validate

ROOT = Path(__file__).resolve().parents[2]
BANK_DIR = ROOT / "docs" / "math" / "bank"
MIN_ACCEPT = 0.05
TRIES_PER_PROBLEM = 60


class BuildError(Exception):
    pass


def problem_id(fw, level, canonical):
    return f"{fw.id}-{level}-{hashlib.sha1(canonical.encode()).hexdigest()[:8]}"


def candidate(fw, level, seed):
    """Everything about one candidate is derived from its seed, so it can be rebuilt exactly."""
    rng = random.Random(f"{fw.id}:{level}:{seed}")
    themes = fw.themes_for(level)
    theme = rng.choice(themes) if themes else None
    params = fw.sample(rng, level, theme)
    ok, reason, solution, report = validate(fw, params, level, theme)
    if not ok:
        return None, reason
    canonical = fw.canonical(params, level)
    return {
        "id": problem_id(fw, level, canonical),
        "framework": fw.id,
        "level": level,
        "seed": seed,
        "theme": summary(theme),
        "params": params,
        "story": solution.story,
        "scene": solution.scene,
        "steps": [s.to_dict() for s in solution.steps],
        "validation": report,
        "generator_version": fw.version,
        "_canonical": canonical,
    }, None


def level_targets(fw, count):
    total = sum(fw.targets.values())
    return {lvl: max(1, round(count * t / total)) for lvl, t in sorted(fw.targets.items())}


def build(fw, count=None, seed=1, rejected_ids=frozenset(), min_accept=MIN_ACCEPT):
    master = random.Random(f"bank:{fw.id}:{seed}")
    targets = level_targets(fw, count or sum(fw.targets.values()))
    problems, report = {}, {"framework": fw.id, "seed": seed, "levels": {}}
    tried_total = accepted_total = 0
    for level, target in targets.items():
        accepted, seen, rejected, tries = [], set(), {}, 0
        while len(accepted) < target and tries < target * TRIES_PER_PROBLEM:
            tries += 1
            record, reason = candidate(fw, level, master.randrange(2**31))
            if record and record["_canonical"] in seen:
                record, reason = None, "duplicate"
            if record and record["id"] in rejected_ids:
                record, reason = None, "rejected-in-review"
            if not record:
                key = reason.split(":")[0]
                rejected[key] = rejected.get(key, 0) + 1
                continue
            seen.add(record.pop("_canonical"))
            accepted.append(record)
        problems[level] = accepted
        report["levels"][str(level)] = {"target": target, "tried": tries, "accepted": len(accepted), "rejected": rejected}
        tried_total += tries
        accepted_total += len(accepted)
    report["tried"], report["accepted"] = tried_total, accepted_total
    report["acceptance_rate"] = round(accepted_total / tried_total, 4) if tried_total else 0
    if report["acceptance_rate"] < min_accept:
        raise BuildError(f"{fw.id}: only {report['acceptance_rate']:.1%} of candidates passed; tighten the sampler")
    return problems, report


def rebuild_problem(fw, record):
    rebuilt, reason = candidate(fw, record["level"], record["seed"])
    if rebuilt:
        rebuilt.pop("_canonical")
    return rebuilt if rebuilt else {"rebuild_failed": reason}


def dumps(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def write(fw, problems, report, bank_dir=BANK_DIR):
    bank_dir.mkdir(parents=True, exist_ok=True)
    for old in bank_dir.glob(f"{fw.id}-*.json"):
        old.unlink()
    for level, items in problems.items():
        meta = {"framework": fw.id, "title": fw.title, "outcome": fw.outcome, "level": level,
                "level_name": fw.levels[level].name, "misconceptions": fw.misconceptions, "problems": items}
        (bank_dir / f"{fw.id}-{level}.json").write_text(dumps(meta), encoding="utf-8")
    report_path = bank_dir / "report.json"
    combined = json.loads(report_path.read_text()) if report_path.exists() else {}
    combined[fw.id] = report
    report_path.write_text(json.dumps(combined, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    write_index(bank_dir)


def write_index(bank_dir=BANK_DIR):
    """index.json: which frameworks and levels exist, for the practice page's picker."""
    index = {}
    for path in sorted(bank_dir.glob("*-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "problems" not in data:
            continue
        entry = index.setdefault(data["framework"], {"title": data["title"], "outcome": data["outcome"], "levels": {}})
        entry["levels"][str(data["level"])] = {"name": data["level_name"], "count": len(data["problems"])}
    (bank_dir / "index.json").write_text(json.dumps(index, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    return index


def rejected_ids(bank_dir=BANK_DIR):
    path = bank_dir / "review.json"
    if not path.exists():
        return set()
    return {r["id"] for r in json.loads(path.read_text()).get("rejected", [])}
