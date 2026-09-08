#!/usr/bin/env python3
"""Scaffold a language-independent problem bundle without empty solution folders."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from repository import PROBLEMS_DIR, problem_directories


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def next_id() -> str:
    ids = [int(path.name[:4]) for path in problem_directories() if path.name[:4].isdigit()]
    return f"{max(ids, default=0) + 1:04d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title")
    parser.add_argument("--id", dest="problem_id", default=next_id())
    parser.add_argument("--difficulty", choices=("Easy", "Medium", "Hard", "Expert"), default="Medium")
    parser.add_argument("--category", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    arguments = parser.parse_args()

    if not re.fullmatch(r"\d{4}", arguments.problem_id):
        print("ERROR: --id must contain exactly four digits", file=sys.stderr)
        return 2
    slug = slugify(arguments.title)
    if not slug:
        print("ERROR: title does not produce a valid slug", file=sys.stderr)
        return 2
    problem = PROBLEMS_DIR / f"{arguments.problem_id}-{slug}"
    if problem.exists() or any(
        path.name.startswith(f"{arguments.problem_id}-") for path in problem_directories()
    ):
        print(f"ERROR: problem ID {arguments.problem_id} already exists", file=sys.stderr)
        return 2

    problem.mkdir(parents=True)
    metadata = {
        "id": arguments.problem_id,
        "slug": slug,
        "title": arguments.title,
        "difficulty": arguments.difficulty,
        "category": arguments.category or ["Uncategorized"],
        "tags": arguments.tag,
        "cognitive_focus": "Problem Solving",
        "resource_limits": {"time_ms": 1000, "memory_mb": 256},
        "io_mode": "json-stdio",
        "available_languages": [],
        "status": "draft",
    }
    tests = {
        "io_mode": "json-stdio",
        "comparison": "exact",
        "float_tolerance": 0,
        "tests": [
            {"name": "example1", "input": {}, "expected_output": None}
        ],
    }
    readme = f"""# {arguments.title}

**Difficulty:** {arguments.difficulty}  
**Category:** {', '.join(metadata['category'])}  
**Tags:** {', '.join(arguments.tag) if arguments.tag else 'None yet'}

## Problem

Describe the problem.

## Input Format

Describe the JSON input object.

## Output Format

Describe the JSON output value.

## Constraints

List only known constraints.

## Examples

### Example 1

**Input**

```json
{{}}
```

**Output**

```json
null
```

## Approach

Document the intended approach after solving the problem.

## Complexity

**Time:** TBD  
**Space:** TBD

## Implementations

No verified implementations yet.
"""
    (problem / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (problem / "tests.json").write_text(
        json.dumps(tests, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (problem / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    print(problem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
