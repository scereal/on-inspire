"""Build a verified problem bank.

    .venv/bin/python -m generator.build_bank ibp --count 400 --seed 1
    .venv/bin/python -m generator.build_bank all
"""
import argparse
import sys

from generator.core import bank
from generator.frameworks import available, get


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("framework", help="framework id, or 'all'")
    p.add_argument("--count", type=int, help="problems to bank (default: the framework's own targets)")
    p.add_argument("--seed", type=int, default=1)
    args = p.parse_args()
    frameworks = available() if args.framework == "all" else {args.framework: get(args.framework)}
    for fw in frameworks.values():
        try:
            problems, report = bank.build(fw, args.count, args.seed, rejected_ids=bank.rejected_ids())
        except bank.BuildError as e:
            sys.exit(str(e))
        bank.write(fw, problems, report)
        per_level = ", ".join(f"L{lvl}: {r['accepted']}/{r['tried']}" for lvl, r in report["levels"].items())
        print(f"{fw.id}: {report['accepted']} problems ({report['acceptance_rate']:.0%} accepted) [{per_level}]")


if __name__ == "__main__":
    main()
