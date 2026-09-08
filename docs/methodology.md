# Methodology

## Problem-Centric Contract

A directory beneath `problems/` is the unit of ownership. Its README defines the
human contract, `metadata.json` defines searchable attributes and implementation
availability, and `tests.json` defines one shared executable contract. Language
solutions must not reinterpret that contract.

Every solution reads one JSON value from standard input and writes one JSON value
to standard output. Diagnostic output belongs on standard error. Implementations
should expose a small `solve` function where the language permits it.

## Test Specification

Each test has a unique name, an input, and an independent expected output. The
default comparison is exact. A test may opt into `float_tolerance` when equivalent
floating-point implementations can differ at insignificant digits.

Large inputs may use deterministic generators. Supported generators currently
cover repeated strings, seeded random strings, arrays of strings, and packet
records; random generators own their own seed so output is stable. The `$map_input` expected-output encoding compactly stores a
lookup for large generated arrays whose output is element-wise. It avoids checking
in megabytes of repeated values and, unlike a runtime reference oracle, remains an
independent expectation.

## Validation

`validate_problem.py` checks naming, required files, metadata types, resource
limits, unique IDs/slugs/test names, language declarations, generator schemas,
README sections, implementation links, and agreement between numbered README
examples and numbered example tests.

`run_problem.py` materializes each fixture, builds an implementation when needed,
runs it in isolation, parses its JSON, and reports failures by test name. Temporary
build output is never written into the repository.

## Competitive Programming and Engineering

The solutions intentionally optimize for contest constraints and algorithmic
clarity. Repository organization, repeatable tests, validation, documentation, and
CI demonstrate engineering discipline around that code; they do not turn contest
solutions into production services.
