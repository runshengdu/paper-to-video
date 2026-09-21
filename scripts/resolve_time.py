#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline_lib import load_timeline, parse_clock, resolve_time


def main():
    parser = argparse.ArgumentParser(
        description="Resolve a clock time to a timeline clip and beat"
    )
    parser.add_argument("--timeline", type=Path, required=True)
    parser.add_argument("time", help="Clock time such as 1:23 or seconds")
    args = parser.parse_args()
    data = load_timeline(args.timeline)
    hit = resolve_time(data, parse_clock(args.time))
    print(json.dumps(hit, indent=2, ensure_ascii=False))
    return 0 if hit.get("clip") else 2


if __name__ == "__main__":
    raise SystemExit(main())
