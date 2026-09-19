"""Unit tests for deterministic runtime input generators."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.test_generators import (  # noqa: E402
    GENERATOR_TYPES,
    GeneratorError,
    generate_test_input,
    validate_generator_config,
)


class GeneratorTests(unittest.TestCase):
    def test_every_registered_generator_is_deterministic(self) -> None:
        configurations = {
            "repeat_string": {"value": "x", "length": 8},
            "repeat_pattern": {"pattern": "abc", "length": 8},
            "random_string": {"seed": 1, "length": 8, "charset": "abc"},
            "random_string_array": {
                "seed": 2,
                "n": 4,
                "min_length": 1,
                "max_length": 3,
                "charset": "ab",
            },
            "random_array": {"seed": 3, "n": 6, "min": -2, "max": 2},
            "random_permutation": {"seed": 4, "n": 6},
            "random_matrix": {
                "seed": 5,
                "rows": 2,
                "cols": 3,
                "min": 1,
                "max": 9,
            },
            "random_tree": {"seed": 6, "n": 6, "weighted": True},
            "random_intervals": {
                "seed": 7,
                "n": 3,
                "min": 0,
                "max": 20,
                "strict": True,
            },
            "random_packets": {
                "seed": 8,
                "n": 4,
                "s_min": 1,
                "s_max": 10,
                "q_min": 0.5,
                "q_max": 0.9,
                "q_decimals": 2,
            },
        }
        self.assertEqual(set(configurations), set(GENERATOR_TYPES))
        for generator_type, parameters in configurations.items():
            with self.subTest(generator_type=generator_type):
                config = {"type": generator_type, **parameters}
                self.assertEqual(
                    generate_test_input(config), generate_test_input(config)
                )

    def test_repeat_pattern_supports_length_and_repetitions(self) -> None:
        self.assertEqual(
            generate_test_input(
                {"type": "repeat_pattern", "pattern": "abc", "length": 8}
            ),
            "abcabcab",
        )
        self.assertEqual(
            generate_test_input(
                {"type": "repeat_pattern", "pattern": "ab", "repetitions": 3}
            ),
            "ababab",
        )

    def test_random_array_options(self) -> None:
        result = generate_test_input(
            {
                "type": "random_array",
                "seed": 9,
                "n": 5,
                "min": 1,
                "max": 10,
                "unique": True,
                "sorted": True,
            }
        )
        self.assertEqual(result, sorted(result))
        self.assertEqual(len(result), len(set(result)))

    def test_tree_has_valid_tree_shape(self) -> None:
        edges = generate_test_input(
            {"type": "random_tree", "seed": 10, "n": 100}
        )
        self.assertEqual(len(edges), 99)
        self.assertTrue(all(1 <= left <= 100 and 1 <= right <= 100 for left, right in edges))

    def test_non_overlapping_intervals_are_ordered(self) -> None:
        intervals = generate_test_input(
            {
                "type": "random_intervals",
                "seed": 11,
                "n": 20,
                "min": 0,
                "max": 100,
                "strict": True,
                "non_overlapping": True,
            }
        )
        self.assertTrue(all(left < right for left, right in intervals))
        self.assertTrue(
            all(intervals[index][1] <= intervals[index + 1][0] for index in range(19))
        )

    def test_invalid_specs_fail_before_generation(self) -> None:
        invalid = (
            {},
            {"type": "unknown"},
            {
                "type": "repeat_pattern",
                "pattern": "ab",
                "length": 2,
                "repetitions": 1,
            },
            {"type": "random_array", "n": 3, "min": 2, "max": 1},
            {"type": "random_packets", "n": 1, "q_min": 0, "q_max": 1},
            {
                "type": "random_packets",
                "n": 1,
                "q_min": 0.11,
                "q_max": 0.14,
                "q_decimals": 1,
            },
            {
                "type": "random_intervals",
                "n": 3,
                "min": 0,
                "max": 4,
                "strict": True,
                "non_overlapping": True,
            },
        )
        for config in invalid:
            with self.subTest(config=config), self.assertRaises(GeneratorError):
                validate_generator_config(config)

    def test_random_packets_grid_bounds(self) -> None:
        packets = generate_test_input(
            {
                "type": "random_packets",
                "seed": 99,
                "n": 20,
                "q_min": 0.15,
                "q_max": 0.24,
                "q_decimals": 1,
            }
        )
        self.assertEqual(len(packets), 20)
        for _, q in packets:
            self.assertEqual(q, 0.2)
            self.assertIsInstance(q, float)


if __name__ == "__main__":
    unittest.main()
