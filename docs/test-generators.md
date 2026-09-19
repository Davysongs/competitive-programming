# Runtime Test Generators

Runtime generators keep large stress inputs out of `tests.json`. A test stores a
small base input, one or more field generators, and an independent expected output.
The runner materializes the full input in memory immediately before invoking a
solution; generated data is never written into the repository.

## Test Shape

```json
{
  "name": "stress_gen_n200_k10",
  "input": {
    "n": 200,
    "k": 10
  },
  "expected_output": 354659.898367,
  "generators": [
    {
      "type": "random_packets",
      "field": "packets",
      "seed": 7,
      "n": 200,
      "s_min": 1,
      "s_max": 1000,
      "q_min": 0.5,
      "q_max": 0.99,
      "q_decimals": 3
    }
  ]
}
```

`field` names the top-level input property to create. Do not include that property
in `input`; the validator rejects duplicated placeholder data. Multiple generators
may populate different fields, and every random generator must declare its own
integer seed. Independent seeds prevent adding or reordering another generator from
changing an existing fixture.

Expected output must remain independent from the solution under test. Never call a
reference solution at runtime to manufacture the expectation.

## Supported Generators

| Type | Required parameters | Useful options |
| --- | --- | --- |
| `repeat_string` | `value`, `length` | Repeats one character |
| `repeat_pattern` | `pattern`, exactly one of `length` or `repetitions` | Truncates to an exact length when requested |
| `random_string` | `seed`, `length` | `charset` |
| `random_string_array` | `seed`, `n` | Fixed `length`, or `min_length` and `max_length`; `charset` |
| `random_array` | `seed`, `n` | `min`, `max`, `unique`, `sorted` |
| `random_permutation` | `seed`, `n` | `zero_indexed` |
| `random_matrix` | `seed`, `rows`, `cols` | `min`, `max` |
| `random_tree` | `seed`, `n` | `weighted`, weight bounds, `one_indexed` |
| `random_intervals` | `seed`, `n` | Bounds, `strict`, `non_overlapping`, `sorted` |
| `random_packets` | `seed`, `n` | Duration/probability bounds and `q_decimals` |

Named character sets are `lowercase`, `uppercase`, `digits`, `binary`, and
`alphanumeric`. Any other non-empty string is treated as a custom character set.

## Repeated and Periodic Boundaries

Deterministic generators need no seed:

```json
{
  "type": "repeat_pattern",
  "field": "s",
  "pattern": "abcdefghijklmnopqrstuvwxyz",
  "length": 200000
}
```

This form is useful for worst-case repeated prefixes, periodic strings, sorted
patterns, and other adversarial inputs whose expanded representation would be
needlessly large.

## Compact Element-Wise Expectations

If a generated input array contains many repetitions of a small value set,
`$map_input` can compact the expected output as well:

```json
{
  "$map_input": {
    "field": "queries",
    "values": {
      "a": [1, 1],
      "b": [25264, 319147480]
    }
  }
}
```

The runner expands each input element through this lookup. Every possible generated
value must have an entry.

## Running Stress Cases

```bash
# List generated cases without executing them
python scripts/run_problem.py 0001 --generated-only --list-tests

# Run every generated case in every implemented language
python scripts/run_problem.py 0001 --generated-only

# Run named cases or shell-style name patterns
python scripts/run_problem.py 0001 --test stress_n200000_seed13
python scripts/run_problem.py 0001 --test "stress_*"

# Combine selection with one language
python scripts/run_problem.py 0002 --generated-only --language go
```

The same per-test timeout rules and comparison strategies used for inline tests
apply to generated tests.

## Validation Rules

`python scripts/validate_problem.py` checks generator names and parameters without
allocating large results. It also enforces:

- explicit seeds for randomized generators;
- one generator per target field;
- omission of generated fields from the inline base input;
- a 4 KiB limit for inline test inputs;
- presence of expected outputs required by the normal test schema.

Generator implementations and invariants are covered by the repository unit suite.
