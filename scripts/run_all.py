#!/usr/bin/env python3
"""Run every implemented solution against its problem's shared tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from repository import problem_directories


def main() -> int:
    failures = 0
    runner = Path(__file__).with_name("run_problem.py")
    for problem in problem_directories():
        result = subprocess.run(
            [sys.executable, "-B", str(runner), problem.name],
            check=False,
        )
        failures += result.returncode != 0
        print()
    if failures:
        print(f"{failures} problem(s) failed.")
        return 1
    print("All problems passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
