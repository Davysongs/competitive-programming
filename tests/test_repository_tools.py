"""Unit tests for shared test materialization and comparison behavior."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from repository import materialize_test, values_equal  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
