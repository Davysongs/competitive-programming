"""Shared repository discovery and test-specification helpers."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterator

from test_generators import generate_test_input


ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_DIR = ROOT / "problems"
LANGUAGE_FILES = {
    "python": "solution.py",
    "cpp": "solution.cpp",
    "go": "solution.go",
    "rust": "solution.rs",
}


def problem_directories() -> list[Path]:
    if not PROBLEMS_DIR.exists():
        return []
    return sorted(path for path in PROBLEMS_DIR.iterdir() if path.is_dir())


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def find_problem(selector: str) -> Path:
    matches = [
        path
        for path in problem_directories()
        if path.name == selector or path.name.startswith(f"{selector}-")
    ]
    if not matches:
        raise ValueError(f"no problem matches {selector!r}")
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise ValueError(f"selector {selector!r} is ambiguous: {names}")
    return matches[0]


def implemented_languages(problem: Path) -> list[str]:
    return [
        language
        for language, filename in LANGUAGE_FILES.items()
        if (problem / "solutions" / language / filename).is_file()
    ]


def _generators_for(test: dict[str, Any]) -> list[dict[str, Any]]:
    generators = list(test.get("generators", []))
    if "generate" in test:
        generators.append(test["generate"])
    return generators


def materialize_test(test: dict[str, Any]) -> tuple[dict[str, Any], Any]:
    input_data = copy.deepcopy(test["input"])
    for generator in _generators_for(test):
        field = generator.get("field")
        if not isinstance(field, str) or not field:
            raise ValueError("generator requires a non-empty 'field'")
        input_data[field] = generate_test_input(generator)

    expected = copy.deepcopy(test["expected_output"])
    if isinstance(expected, dict) and "$map_input" in expected:
        specification = expected["$map_input"]
        values = specification["values"]
        expected = [values[str(item)] for item in input_data[specification["field"]]]
    return input_data, expected


def values_equal(actual: Any, expected: Any, tolerance: float | None) -> bool:
    actual_is_number = isinstance(actual, (int, float)) and not isinstance(actual, bool)
    expected_is_number = isinstance(expected, (int, float)) and not isinstance(
        expected, bool
    )
    if actual_is_number and expected_is_number:
        if tolerance is not None:
            return abs(float(actual) - float(expected)) <= tolerance
        return actual == expected
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            values_equal(left, right, tolerance)
            for left, right in zip(actual, expected)
        )
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            values_equal(actual[key], expected[key], tolerance) for key in actual
        )
    return actual == expected


def test_cases(specification: dict[str, Any]) -> Iterator[dict[str, Any]]:
    yield from specification.get("tests", [])
