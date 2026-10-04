"""Re-check every banked problem: it must rebuild identically from its seed (which re-runs
every validator), carry a passing validation report, be unique, and not be rejected in review.

    .venv/bin/python -m generator.audit_bank
"""
import json
import sys

from generator.core import bank
from generator.frameworks import available


def audit(bank_dir=bank.BANK_DIR):
    problems_found, checked = [], 0
    banned = bank.rejected_ids(bank_dir)
    frameworks = available()
    for path in sorted(bank_dir.glob("*-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        fw = frameworks.get(data.get("framework"))
        if not fw:
            continue
        ids = set()
        for record in data["problems"]:
            checked += 1
            where = f"{path.name}:{record['id']}"
            if record["id"] in ids:
                problems_found.append(f"{where} duplicate id")
            ids.add(record["id"])
            if record["id"] in banned:
                problems_found.append(f"{where} was rejected in review")
            if not all(record["validation"].values()):
                problems_found.append(f"{where} has a failing validation report")
            if bank.rebuild_problem(fw, record) != record:
                problems_found.append(f"{where} does not rebuild identically from its seed")
    return checked, problems_found


def main():
    checked, found = audit()
    for line in found:
        print("FAIL", line)
    print(f"audited {checked} problems, {len(found)} issue(s)")
    sys.exit(1 if found or not checked else 0)


if __name__ == "__main__":
    main()
