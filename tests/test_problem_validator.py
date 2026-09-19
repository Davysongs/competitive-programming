"""Tests for structural validation of compact problem fixtures."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_problem import validate_bundle  # noqa: E402


README = """# Test

## Problem
Test.
## Input Format
JSON.
## Output Format
JSON.
## Constraints
None.
## Examples
### Example 1
```json
{}
```
```json
null
```
## Approach
Test.
## Complexity
Constant.
## Implementations
None.
"""


class ProblemValidatorTests(unittest.TestCase):
    def validate_test(self, test: dict[str, Any]) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            problem = Path(temporary_directory) / "0001-test"
            problem.mkdir()
            metadata = {
                "id": "0001",
                "slug": "test",
                "title": "Test",
                "difficulty": "Easy",
                "category": ["Testing"],
                "tags": ["fixtures"],
                "cognitive_focus": "Validation",
                "resource_limits": {"time_ms": 1000, "memory_mb": 64},
                "io_mode": "json-stdio",
                "available_languages": [],
                "status": "draft",
            }
            specification = {
                "io_mode": "json-stdio",
                "comparison": "exact",
                "float_tolerance": 0,
                "tests": [test],
            }
            (problem / "README.md").write_text(README, encoding="utf-8")
            (problem / "metadata.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            (problem / "tests.json").write_text(
                json.dumps(specification), encoding="utf-8"
            )
            return validate_bundle(problem)

    def test_large_inline_input_is_rejected(self) -> None:
        errors = self.validate_test(
            {
                "name": "example1",
                "input": {"values": list(range(2_000))},
                "expected_output": None,
            }
        )
        self.assertTrue(any("inline bytes" in error for error in errors))

    def test_generated_field_must_not_be_duplicated_inline(self) -> None:
        errors = self.validate_test(
            {
                "name": "example1",
                "input": {"s": "placeholder"},
                "expected_output": None,
                "generators": [
                    {
                        "type": "repeat_string",
                        "field": "s",
                        "value": "a",
                        "length": 100,
                    }
                ],
            }
        )
        self.assertTrue(
            any("keeps generated fields inline" in error for error in errors)
        )

    def test_random_generator_requires_explicit_seed(self) -> None:
        errors = self.validate_test(
            {
                "name": "example1",
                "input": {},
                "expected_output": None,
                "generators": [
                    {
                        "type": "random_string",
                        "field": "s",
                        "length": 100,
                    }
                ],
            }
        )
        self.assertTrue(any("explicit seed" in error for error in errors))

    def test_unhashable_generator_type_is_rejected_without_crashing(self) -> None:
        errors = self.validate_test(
            {
                "name": "example1",
                "input": {},
                "expected_output": None,
                "generators": [
                    {
                        "type": [],
                        "field": "s",
                    }
                ],
            }
        )
        self.assertTrue(any("requires a non-empty 'type'" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
