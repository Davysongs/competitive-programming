"""Unit tests for shared test materialization and comparison behavior."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from repository import materialize_test, test_cases, values_equal  # noqa: E402


class RepositoryToolTests(unittest.TestCase):
    def test_seeded_string_generation_is_stable(self) -> None:
        test = {
            "input": {"items": []},
            "expected_output": {
                "$map_input": {
                    "field": "items",
                    "values": {"a": 1, "b": 2},
                }
            },
            "generators": [
                {
                    "type": "random_string_array",
                    "field": "items",
                    "seed": 1,
                    "n": 4,
                    "length": 1,
                    "charset": "ab",
                }
            ],
        }
        input_data, expected = materialize_test(test)
        self.assertEqual(input_data["items"], ["a", "a", "b", "a"])
        self.assertEqual(expected, [1, 1, 2, 1])

    def test_recursive_tolerance(self) -> None:
        self.assertTrue(values_equal([1.0, {"x": 2}], [1.00001, {"x": 2}], 0.001))
        self.assertFalse(values_equal([1.0], [1.1], 0.001))
        self.assertTrue(values_equal(1, 1.0, None))
        self.assertFalse(values_equal(True, 1, None))

    def test_repeated_string_generation(self) -> None:
        input_data, expected = materialize_test(
            {
                "input": {"s": "placeholder"},
                "expected_output": 3,
                "generate": {
                    "type": "repeat_string",
                    "field": "s",
                    "value": "x",
                    "length": 3,
                },
            }
        )
        self.assertEqual(input_data, {"s": "xxx"})
        self.assertEqual(expected, 3)

    def test_multiple_generators_do_not_mutate_test_specification(self) -> None:
        test = {
            "input": {"n": 8},
            "expected_output": None,
            "generators": [
                {
                    "type": "repeat_pattern",
                    "field": "s",
                    "pattern": "abc",
                    "length": 8,
                },
                {
                    "type": "random_array",
                    "field": "values",
                    "seed": 12,
                    "n": 8,
                    "min": 0,
                    "max": 1,
                },
            ],
        }
        input_data, _ = materialize_test(test)
        self.assertEqual(input_data["s"], "abcabcab")
        self.assertEqual(len(input_data["values"]), 8)
        self.assertEqual(test["input"], {"n": 8})

    def test_generator_requires_target_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "field"):
            materialize_test(
                {
                    "input": {},
                    "expected_output": None,
                    "generate": {
                        "type": "repeat_string",
                        "value": "a",
                        "length": 3,
                    },
                }
            )

    def test_test_case_selection_supports_globs_and_generated_filter(self) -> None:
        specification = {
            "tests": [
                {"name": "example1", "input": {}, "expected_output": None},
                {
                    "name": "stress_random",
                    "input": {},
                    "expected_output": None,
                    "generators": [{"type": "repeat_string"}],
                },
                {
                    "name": "stress_periodic",
                    "input": {},
                    "expected_output": None,
                    "generate": {"type": "repeat_pattern"},
                },
            ]
        }
        selected = list(test_cases(specification, ["stress_*"], generated_only=True))
        self.assertEqual(
            [test["name"] for test in selected],
            ["stress_random", "stress_periodic"],
        )

    def test_copy_input_materialization(self) -> None:
        test = {
            "input": {"items": [1, 2, 3]},
            "expected_output": {
                "$copy_input": {
                    "field": "items",
                }
            },
        }
        input_data, expected = materialize_test(test)
        self.assertEqual(expected, [1, 2, 3])
        self.assertIsNot(input_data["items"], expected)

    def test_unordered_values_equal(self) -> None:
        self.assertTrue(values_equal([2, 1, 3], [1, 2, 3], None, unordered=True))
        self.assertFalse(values_equal([2, 1, 3], [1, 2, 3], None, unordered=False))
        self.assertFalse(values_equal([1, 2], [1, 2, 3], None, unordered=True))
        self.assertTrue(
            values_equal([{"x": 2}, {"x": 1}], [{"x": 1}, {"x": 2}], None, unordered=True)
        )
        self.assertTrue(
            values_equal([[2, 1], [4, 3]], [[1, 2], [3, 4]], None, unordered=True)
        )
        self.assertFalse(
            values_equal([1, 1, 2], [1, 2, 2], None, unordered=True)
        )
        self.assertTrue(
            values_equal([1.0001, 2.0], [2.0001, 1.0], 0.001, unordered=True)
        )


if __name__ == "__main__":
    unittest.main()

