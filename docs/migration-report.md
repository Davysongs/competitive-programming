# Migration Report

## Scope

The repository root initially contained only a short README, an Apache 2.0 license,
and a Go-oriented `.gitignore`. The first two task bundles from `.tmp` were migrated
into the problem-centric layout. Original bundle identifiers remain in metadata as
`legacy_id` values.

| Legacy ID | Repository ID | Result |
| --- | --- | --- |
| `rec0se4dv5obqvcuu` | `0001` | Migrated and verified |
| `rec4joxvhmy3txfnn` | `0002` | Migrated and verified |

The statements, examples, constraints, and resource limits were preserved. Python
references were cleaned without changing their algorithms or JSON stdin/stdout
behavior. Tutorial material was distilled into the problem README approach and
complexity sections.

## Audit Findings

- The repository initially contained no problem code, scripts, tests, build files,
  package files, or language implementations beyond the two staged Python bundles.
- Neither bundle contained a C++ reference. No unverified C++, Go, or Rust solution
  was manufactured during migration.
- IDs and slugs were unique after mapping. Test names were unique and both JSON
  specifications parsed successfully.
- A generated `__pycache__/reference.cpython-310.pyc` existed in the second staging
  bundle. It was not migrated and `.gitignore` now excludes such artifacts.
- `0001` test `max_q_count` omitted `expected_output` and described using the
  reference implementation as a runtime oracle. Its seeded input was retained and
  the oracle was replaced with a compact 26-value `$map_input` expectation. This
  preserves the 200,000-query boundary case without committing a huge repeated
  output array or testing the solution against itself.
- Existing generated expectations were reproduced using their declared seeds before
  migration. Data Stream Transmission passed all 44 expectations unchanged.

## Corrected Source Fixtures

Lexicographic Rank Sum Queries contained eight statement/fixture mismatches in
addition to the missing `max_q_count` expectation:

- Four repeated-string stress tests had placeholder or truncated source strings. A
  deterministic `repeat_string` generator now materializes the documented lengths
  of 300, 45,000, or 60,000 characters while retaining their intended outputs.
- `multiple_chars_same_prefix` excluded substring `c` from query `c`; its result was
  corrected from `[8, 36]` to `[9, 45]`.
- `deterministic_modulo_test`, `deterministic_modulo_reduction`, and
  `deterministic_modulo_wrap` described different strings than their stored inputs
  and had incompatible expected results. Their descriptions and expectations now
  match the stored inputs.

The corrections were checked with brute-force substring sorting for feasible cases
and periodic-string counting formulas for larger cases. Every expected rank pair
now satisfies the definition's invariant
`sum = count * (count + 1) / 2 mod 1,000,000,007`.

The source bundle also contains three names for the same `abba` fixture
(`palindrome_string`, `palindrome_string_fixed_desc`, and `palindrome_fixed`). They
remain to preserve the supplied test set, although they add no new coverage.

## Verification Boundary

Python is the only solution toolchain installed in the migration environment.
C++/Go/Rust adapters and CI conventions are present, but the index reports zero
implementations for those languages until real solutions can be compiled and pass
the shared suites.
