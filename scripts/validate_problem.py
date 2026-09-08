#!/usr/bin/env python3
"""Validate problem bundles and their language-independent contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from repository import (
    LANGUAGE_FILES,
    find_problem,
    implemented_languages,
    load_json,
    problem_directories,
)


DIRECTORY_PATTERN = re.compile(r"^(?P<id>\d{4})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$")
REQUIRED_HEADINGS = (
    "## Problem",
    "## Input Format",
    "## Output Format",
    "## Constraints",
    "## Examples",
    "## Approach",
    "## Complexity",
    "## Implementations",
)
SUPPORTED_COMPARISONS = {"exact", "float_tolerance"}
SUPPORTED_GENERATORS = {
    "random_string",
    "random_string_array",
    "random_packets",
    "repeat_string",
}


def _example_json(readme: str) -> list[Any]:
    examples = readme.split("## Examples", maxsplit=1)
    if len(examples) != 2:
        return []
    before_approach = examples[1].split("## Approach", maxsplit=1)[0]
    blocks = re.findall(r"```json\s*(.*?)\s*```", before_approach, flags=re.DOTALL)
    parsed: list[Any] = []
    for block in blocks:
        parsed.append(json.loads(block))
    return parsed


def _validate_generator(generator: Any, location: str, errors: list[str]) -> None:
    if not isinstance(generator, dict):
        errors.append(f"{location} must be an object")
        return
    if generator.get("type") not in SUPPORTED_GENERATORS:
        errors.append(f"{location} has unsupported type {generator.get('type')!r}")
    if not isinstance(generator.get("field"), str):
        errors.append(f"{location} requires a string field")
    if generator.get("type") != "repeat_string" and not isinstance(
        generator.get("seed"), int
    ):
        errors.append(f"{location} requires an integer seed")
    if generator.get("type") == "repeat_string":
        if not isinstance(generator.get("value"), str) or len(generator["value"]) != 1:
            errors.append(f"{location} requires a one-character value")
        if not isinstance(generator.get("length"), int) or generator["length"] < 0:
            errors.append(f"{location} requires a non-negative integer length")


def validate_bundle(problem: Path) -> list[str]:
    errors: list[str] = []
    match = DIRECTORY_PATTERN.fullmatch(problem.name)
    if not match:
        errors.append("directory name must match NNNN-url-safe-slug")

    required_files = ("README.md", "metadata.json", "tests.json")
    for filename in required_files:
        if not (problem / filename).is_file():
            errors.append(f"missing {filename}")
    if errors and any(not (problem / name).is_file() for name in required_files):
        return errors

    try:
        metadata = load_json(problem / "metadata.json")
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid metadata.json: {error}")
        return errors
    try:
        tests = load_json(problem / "tests.json")
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid tests.json: {error}")
        return errors

    if not isinstance(metadata, dict):
        return [*errors, "metadata.json root must be an object"]
    if match:
        if metadata.get("id") != match.group("id"):
            errors.append("metadata id does not match the directory ID")
        if metadata.get("slug") != match.group("slug"):
            errors.append("metadata slug does not match the directory slug")
    for field in ("title", "difficulty", "cognitive_focus", "io_mode", "status"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            errors.append(f"metadata field {field!r} must be a non-empty string")
    for field in ("category", "tags", "available_languages"):
        value = metadata.get(field)
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value
        ):
            errors.append(f"metadata field {field!r} must be a string array")

    limits = metadata.get("resource_limits")
    if not isinstance(limits, dict):
        errors.append("resource_limits must be an object")
    else:
        for field in ("time_ms", "memory_mb"):
            if not isinstance(limits.get(field), int) or limits[field] <= 0:
                errors.append(f"resource_limits.{field} must be a positive integer")

    actual_languages = implemented_languages(problem)
    declared_languages = metadata.get("available_languages", [])
    unsupported = sorted(set(declared_languages) - set(LANGUAGE_FILES))
    if unsupported:
        errors.append(f"unsupported language names: {', '.join(unsupported)}")
    if declared_languages != actual_languages:
        errors.append(
            "available_languages does not match implementations on disk "
            f"(declared={declared_languages}, actual={actual_languages})"
        )

    if not isinstance(tests, dict):
        return [*errors, "tests.json root must be an object"]
    if tests.get("io_mode") != metadata.get("io_mode"):
        errors.append("tests io_mode does not match metadata io_mode")
    if tests.get("comparison") not in SUPPORTED_COMPARISONS:
        errors.append(f"unsupported comparison strategy: {tests.get('comparison')!r}")
    if not isinstance(tests.get("float_tolerance"), (int, float)):
        errors.append("float_tolerance must be numeric")
    cases = tests.get("tests")
    if not isinstance(cases, list) or not cases:
        errors.append("tests must be a non-empty array")
        cases = []

    names: set[str] = set()
    for index, test in enumerate(cases):
        location = f"tests[{index}]"
        if not isinstance(test, dict):
            errors.append(f"{location} must be an object")
            continue
        name = test.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{location} requires a non-empty name")
        elif name in names:
            errors.append(f"duplicate test name: {name}")
        else:
            names.add(name)
        if not isinstance(test.get("input"), dict):
            errors.append(f"{location} requires an input object")
        if "expected_output" not in test:
            errors.append(f"{location} is missing expected_output")
        expected = test.get("expected_output")
        if isinstance(expected, dict) and "$map_input" in expected:
            mapping = expected["$map_input"]
            if not isinstance(mapping, dict):
                errors.append(f"{location} $map_input must be an object")
            elif not isinstance(mapping.get("field"), str) or not isinstance(
                mapping.get("values"), dict
            ):
                errors.append(f"{location} $map_input requires field and values")
        override = test.get("comparison_override")
        if override is not None and override not in SUPPORTED_COMPARISONS:
            errors.append(f"{location} has unsupported comparison_override {override!r}")
        generators = test.get("generators", [])
        if generators and not isinstance(generators, list):
            errors.append(f"{location}.generators must be an array")
        elif isinstance(generators, list):
            for generator_index, generator in enumerate(generators):
                _validate_generator(
                    generator, f"{location}.generators[{generator_index}]", errors
                )
        if "generate" in test:
            _validate_generator(test["generate"], f"{location}.generate", errors)

    try:
        readme = (problem / "README.md").read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            if heading not in readme:
                errors.append(f"README.md is missing heading {heading!r}")
        for language in actual_languages:
            expected_link = f"solutions/{language}/{LANGUAGE_FILES[language]}"
            if expected_link not in readme:
                errors.append(f"README.md does not link to {expected_link}")

        blocks = _example_json(readme)
        example_cases = [test for test in cases if re.fullmatch(r"example\d+", test.get("name", ""))]
        if len(blocks) != 2 * len(example_cases):
            errors.append(
                "README example JSON block count does not match numbered example tests"
            )
        else:
            for index, test in enumerate(example_cases):
                if blocks[index * 2] != test.get("input"):
                    errors.append(f"README input for {test['name']} differs from tests.json")
                if blocks[index * 2 + 1] != test.get("expected_output"):
                    errors.append(f"README output for {test['name']} differs from tests.json")
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"README example validation failed: {error}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", nargs="?", help="optional ID or directory name")
    arguments = parser.parse_args()
    try:
        problems = [find_problem(arguments.problem)] if arguments.problem else problem_directories()
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    all_errors: dict[Path, list[str]] = {}
    seen_ids: dict[str, Path] = {}
    seen_slugs: dict[str, Path] = {}
    for problem in problems:
        errors = validate_bundle(problem)
        try:
            metadata = load_json(problem / "metadata.json")
        except (OSError, json.JSONDecodeError):
            metadata = {}
        for field, seen in (("id", seen_ids), ("slug", seen_slugs)):
            value = metadata.get(field)
            if isinstance(value, str) and value in seen:
                errors.append(f"duplicate {field} also used by {seen[value].name}")
            elif isinstance(value, str):
                seen[value] = problem
        if errors:
            all_errors[problem] = errors

    if all_errors:
        for problem, errors in all_errors.items():
            print(f"ERROR {problem.relative_to(problem.parents[1])}")
            for error in errors:
                print(f"  - {error}")
        return 1
    print(f"Validated {len(problems)} problem bundle(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
