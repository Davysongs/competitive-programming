"""Deterministic runtime generators for compact stress-test specifications.

Generators return a value for one input field. They never compute expected output;
expectations remain independent test data in ``tests.json``.
"""

from __future__ import annotations

import decimal
import math
import random
import string
from collections.abc import Callable, Mapping
from typing import Any


class GeneratorError(ValueError):
    """Raised when a generator specification is invalid."""


Generator = Callable[[random.Random, Mapping[str, Any]], Any]
Validator = Callable[[Mapping[str, Any]], None]


CHARSETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "digits": string.digits,
    "binary": "01",
    "alphanumeric": string.ascii_letters + string.digits,
}


def _integer(
    config: Mapping[str, Any],
    name: str,
    *,
    minimum: int | None = None,
    default: int | None = None,
) -> int:
    value = config.get(name, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise GeneratorError(f"{name!r} must be an integer")
    if minimum is not None and value < minimum:
        raise GeneratorError(f"{name!r} must be at least {minimum}")
    return value


def _number(config: Mapping[str, Any], name: str, default: float) -> float:
    value = config.get(name, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise GeneratorError(f"{name!r} must be numeric")
    return float(value)


def _boolean(config: Mapping[str, Any], name: str, default: bool = False) -> bool:
    value = config.get(name, default)
    if not isinstance(value, bool):
        raise GeneratorError(f"{name!r} must be a boolean")
    return value


def _characters(config: Mapping[str, Any]) -> str:
    charset = config.get("charset", "lowercase")
    if not isinstance(charset, str) or not charset:
        raise GeneratorError("'charset' must be a non-empty string")
    return CHARSETS.get(charset, charset)


def _validate_repeat_string(config: Mapping[str, Any]) -> None:
    value = config.get("value")
    if not isinstance(value, str) or len(value) != 1:
        raise GeneratorError("'value' must contain exactly one character")
    _integer(config, "length", minimum=0)


def _generate_repeat_string(
    _rng: random.Random, config: Mapping[str, Any]
) -> str:
    return str(config["value"]) * int(config["length"])


def _validate_repeat_pattern(config: Mapping[str, Any]) -> None:
    pattern = config.get("pattern")
    if not isinstance(pattern, str) or not pattern:
        raise GeneratorError("'pattern' must be a non-empty string")
    has_length = "length" in config
    has_repetitions = "repetitions" in config
    if has_length == has_repetitions:
        raise GeneratorError("provide exactly one of 'length' or 'repetitions'")
    _integer(
        config,
        "length" if has_length else "repetitions",
        minimum=0,
    )


def _generate_repeat_pattern(
    _rng: random.Random, config: Mapping[str, Any]
) -> str:
    pattern = str(config["pattern"])
    if "repetitions" in config:
        return pattern * int(config["repetitions"])
    length = int(config["length"])
    if length == 0:
        return ""
    repeats = (length + len(pattern) - 1) // len(pattern)
    return (pattern * repeats)[:length]


def _validate_random_string(config: Mapping[str, Any]) -> None:
    _integer(config, "length", minimum=0)
    _characters(config)


def _generate_random_string(
    rng: random.Random, config: Mapping[str, Any]
) -> str:
    characters = _characters(config)
    return "".join(rng.choice(characters) for _ in range(int(config["length"])))


def _validate_random_string_array(config: Mapping[str, Any]) -> None:
    _integer(config, "n", minimum=0)
    _characters(config)
    if "length" in config:
        _integer(config, "length", minimum=0)
        if "min_length" in config or "max_length" in config:
            raise GeneratorError(
                "'length' cannot be combined with 'min_length' or 'max_length'"
            )
        return
    minimum = _integer(config, "min_length", minimum=0, default=1)
    maximum = _integer(config, "max_length", minimum=0, default=10)
    if minimum > maximum:
        raise GeneratorError("'min_length' cannot exceed 'max_length'")


def _generate_random_string_array(
    rng: random.Random, config: Mapping[str, Any]
) -> list[str]:
    characters = _characters(config)
    fixed_length = config.get("length")
    minimum = int(config.get("min_length", 1))
    maximum = int(config.get("max_length", 10))
    result: list[str] = []
    for _ in range(int(config["n"])):
        length = (
            int(fixed_length)
            if fixed_length is not None
            else rng.randint(minimum, maximum)
        )
        result.append("".join(rng.choice(characters) for _ in range(length)))
    return result


def _validate_random_array(config: Mapping[str, Any]) -> None:
    size = _integer(config, "n", minimum=0)
    minimum = _integer(config, "min", default=0)
    maximum = _integer(config, "max", default=1_000_000_000)
    unique = _boolean(config, "unique")
    _boolean(config, "sorted")
    if minimum > maximum:
        raise GeneratorError("'min' cannot exceed 'max'")
    if unique and maximum - minimum + 1 < size:
        raise GeneratorError("the requested range cannot provide enough unique values")


def _generate_random_array(
    rng: random.Random, config: Mapping[str, Any]
) -> list[int]:
    size = int(config["n"])
    minimum = int(config.get("min", 0))
    maximum = int(config.get("max", 1_000_000_000))
    if config.get("unique", False):
        result = rng.sample(range(minimum, maximum + 1), size)
    else:
        result = [rng.randint(minimum, maximum) for _ in range(size)]
    if config.get("sorted", False):
        result.sort()
    return result


def _validate_random_permutation(config: Mapping[str, Any]) -> None:
    _integer(config, "n", minimum=0)
    _boolean(config, "zero_indexed")


def _generate_random_permutation(
    rng: random.Random, config: Mapping[str, Any]
) -> list[int]:
    start = 0 if config.get("zero_indexed", False) else 1
    result = list(range(start, start + int(config["n"])))
    rng.shuffle(result)
    return result


def _validate_random_matrix(config: Mapping[str, Any]) -> None:
    _integer(config, "rows", minimum=0)
    _integer(config, "cols", minimum=0)
    minimum = _integer(config, "min", default=0)
    maximum = _integer(config, "max", default=1_000_000_000)
    if minimum > maximum:
        raise GeneratorError("'min' cannot exceed 'max'")


def _generate_random_matrix(
    rng: random.Random, config: Mapping[str, Any]
) -> list[list[int]]:
    minimum = int(config.get("min", 0))
    maximum = int(config.get("max", 1_000_000_000))
    return [
        [rng.randint(minimum, maximum) for _ in range(int(config["cols"]))]
        for _ in range(int(config["rows"]))
    ]


def _validate_random_tree(config: Mapping[str, Any]) -> None:
    _integer(config, "n", minimum=0)
    weighted = _boolean(config, "weighted")
    _boolean(config, "one_indexed", True)
    if weighted:
        minimum = _integer(config, "weight_min", default=1)
        maximum = _integer(config, "weight_max", default=1_000_000)
        if minimum > maximum:
            raise GeneratorError("'weight_min' cannot exceed 'weight_max'")


def _generate_random_tree(
    rng: random.Random, config: Mapping[str, Any]
) -> list[list[int]]:
    size = int(config["n"])
    offset = 1 if config.get("one_indexed", True) else 0
    weighted = bool(config.get("weighted", False))
    edges: list[list[int]] = []
    for node in range(1, size):
        parent = rng.randrange(node)
        edge = [parent + offset, node + offset]
        if weighted:
            edge.append(
                rng.randint(
                    int(config.get("weight_min", 1)),
                    int(config.get("weight_max", 1_000_000)),
                )
            )
        edges.append(edge)
    rng.shuffle(edges)
    return edges


def _validate_random_intervals(config: Mapping[str, Any]) -> None:
    size = _integer(config, "n", minimum=0)
    minimum = _integer(config, "min", default=0)
    maximum = _integer(config, "max", default=1_000_000_000)
    strict = _boolean(config, "strict")
    non_overlapping = _boolean(config, "non_overlapping")
    _boolean(config, "sorted")
    if minimum > maximum:
        raise GeneratorError("'min' cannot exceed 'max'")
    if strict and size and minimum == maximum:
        raise GeneratorError("strict intervals require at least two coordinates")
    if strict and non_overlapping and maximum - minimum + 1 < 2 * size:
        raise GeneratorError(
            "strict non-overlapping intervals require at least 2*n coordinates"
        )


def _generate_random_intervals(
    rng: random.Random, config: Mapping[str, Any]
) -> list[list[int]]:
    size = int(config["n"])
    minimum = int(config.get("min", 0))
    maximum = int(config.get("max", 1_000_000_000))
    strict = bool(config.get("strict", False))
    non_overlapping = bool(config.get("non_overlapping", False))
    intervals: list[list[int]] = []

    if non_overlapping:
        coordinates = (
            sorted(rng.sample(range(minimum, maximum + 1), 2 * size))
            if strict
            else sorted(rng.randint(minimum, maximum) for _ in range(2 * size))
        )
        intervals = [coordinates[index : index + 2] for index in range(0, 2 * size, 2)]
    else:
        for _ in range(size):
            if strict:
                left = rng.randint(minimum, maximum - 1)
                right = rng.randint(left + 1, maximum)
            else:
                first = rng.randint(minimum, maximum)
                second = rng.randint(minimum, maximum)
                left, right = sorted((first, second))
            intervals.append([left, right])

    if config.get("sorted", False):
        intervals.sort()
    return intervals


def _packet_probability_bounds(
    config: Mapping[str, Any],
) -> tuple[float, float, int]:
    minimum_probability = _number(config, "q_min", 0.1)
    maximum_probability = _number(config, "q_max", 0.99)
    decimals = _integer(config, "q_decimals", minimum=0, default=3)
    if not 0 < minimum_probability <= maximum_probability <= 1:
        raise GeneratorError("probabilities must satisfy 0 < q_min <= q_max <= 1")
    scale = 10**decimals
    dec_min = decimal.Decimal(str(minimum_probability))
    dec_max = decimal.Decimal(str(maximum_probability))
    k_min = math.ceil(dec_min * scale)
    k_max = math.floor(dec_max * scale)
    if k_min > k_max:
        raise GeneratorError(
            "no representable decimal-grid value exists in range [q_min, q_max]"
        )
    return k_min / scale, k_max / scale, decimals


def _validate_random_packets(config: Mapping[str, Any]) -> None:
    _integer(config, "n", minimum=0)
    minimum_duration = _integer(config, "s_min", minimum=1, default=1)
    maximum_duration = _integer(
        config, "s_max", minimum=1, default=1_000_000_000
    )
    if minimum_duration > maximum_duration:
        raise GeneratorError("'s_min' cannot exceed 's_max'")
    _packet_probability_bounds(config)


def _generate_random_packets(
    rng: random.Random, config: Mapping[str, Any]
) -> list[list[int | float]]:
    minimum_duration = int(config.get("s_min", 1))
    maximum_duration = int(config.get("s_max", 1_000_000_000))
    minimum_grid, maximum_grid, decimals = _packet_probability_bounds(config)
    return [
        [
            rng.randint(minimum_duration, maximum_duration),
            round(
                rng.uniform(minimum_grid, maximum_grid),
                decimals,
            ),
        ]
        for _ in range(int(config["n"]))
    ]


GENERATORS: dict[str, tuple[Validator, Generator, bool]] = {
    "repeat_string": (_validate_repeat_string, _generate_repeat_string, False),
    "repeat_pattern": (_validate_repeat_pattern, _generate_repeat_pattern, False),
    "random_string": (_validate_random_string, _generate_random_string, True),
    "random_string_array": (
        _validate_random_string_array,
        _generate_random_string_array,
        True,
    ),
    "random_array": (_validate_random_array, _generate_random_array, True),
    "random_permutation": (
        _validate_random_permutation,
        _generate_random_permutation,
        True,
    ),
    "random_matrix": (_validate_random_matrix, _generate_random_matrix, True),
    "random_tree": (_validate_random_tree, _generate_random_tree, True),
    "random_intervals": (
        _validate_random_intervals,
        _generate_random_intervals,
        True,
    ),
    "random_packets": (_validate_random_packets, _generate_random_packets, True),
}

GENERATOR_TYPES = tuple(GENERATORS)
RANDOM_GENERATOR_TYPES = frozenset(
    name for name, (_, _, uses_randomness) in GENERATORS.items() if uses_randomness
)


def validate_generator_config(config: Mapping[str, Any]) -> None:
    """Validate a generator without allocating its potentially large result."""
    if not isinstance(config, Mapping):
        raise GeneratorError("generator specification must be an object")
    generator_type = config.get("type")
    if not isinstance(generator_type, str) or not generator_type:
        raise GeneratorError("generator specification requires a non-empty 'type'")
    definition = GENERATORS.get(generator_type)
    if definition is None:
        available = ", ".join(GENERATOR_TYPES)
        raise GeneratorError(
            f"unknown generator type {generator_type!r}; available: {available}"
        )
    if "seed" in config and (
        not isinstance(config["seed"], int) or isinstance(config["seed"], bool)
    ):
        raise GeneratorError("'seed' must be an integer")
    definition[0](config)


def generate_test_input(config: Mapping[str, Any]) -> Any:
    """Materialize one deterministic value from a compact specification."""
    validate_generator_config(config)
    generator_type = str(config["type"])
    _, generator, _ = GENERATORS[generator_type]
    return generator(random.Random(config.get("seed", 42)), config)
