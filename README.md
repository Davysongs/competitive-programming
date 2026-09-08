# Competitive Programming

A multi-language collection of algorithmic problems, data structures,
competitive-programming solutions, and verification tooling.

## About

This repository is a problem-centric algorithmic workspace: each problem owns one
language-independent statement, metadata record, and shared test specification.
Verified implementations live beneath that problem, so adding another language
does not duplicate or weaken the contract.

It is both a competitive-programming archive and an engineering portfolio focused
on reasoning, readable implementations, reproducible verification, developer
tooling, and automation. Contest code is not presented as production application
architecture; its portfolio value is the algorithmic and language foundation it
demonstrates.

## Problem Statistics

<!-- statistics:start -->
Problems: 2 · Python: 2 · C++: 0 · Go: 0 · Rust: 0
<!-- statistics:end -->

Statistics and the [problem index](docs/problem-index.md) are generated from the
problem metadata with `python scripts/generate_index.py`.

## Languages

- **Python** has the broadest solution coverage and is the primary algorithm-development language.
- **C++** is supported for performance-oriented and classic contest implementations.
- **Go** is a deliberate growth area for clear, performance-conscious solutions and tooling.
- **Rust** is reserved for problems that meaningfully demonstrate safety, ownership, or memory-aware design.

Coverage is intentionally uneven. A language appears in a problem only after its
implementation is reviewed, compiled, and tested. See [language strategy](docs/languages.md).

## Problem Categories

The current collection covers strings, greedy algorithms, and dynamic programming,
including suffix automata, exchange arguments, and sequence partitioning. The
generated index is the source of truth as coverage grows.

## Repository Layout

```text
problems/<id>-<slug>/
├── README.md
├── metadata.json
├── tests.json
└── solutions/<language>/solution.<ext>

algorithms/   reusable study implementations
templates/    minimal language starters
docs/         methodology, language strategy, roadmap, and generated index
scripts/      validation, execution, generation, and indexing tools
```

## Testing

Python 3.10 or newer is required for the repository tools. No third-party Python
packages are needed.

```bash
python scripts/validate_problem.py
python scripts/run_problem.py 0001
python scripts/run_problem.py 0001 --language python
python scripts/run_all.py
python -m unittest discover -s tests -v
python scripts/generate_index.py --check
```

The runner reads each problem's shared `tests.json`, materializes deterministic
fixtures, invokes every available implementation through JSON standard input and
output, and compares the parsed result. Native build artifacts are created only in
the operating system's temporary directory.

## Adding a Problem

Start a bundle with:

```bash
python scripts/generate_problem.py "Problem Title" --difficulty Medium --category Arrays --tag two-pointers
```

Complete the statement and tests before adding an implementation, then follow
[CONTRIBUTING.md](CONTRIBUTING.md). The [methodology](docs/methodology.md) describes
the shared contract and validation rules.

## Engineering Practices

- Problem definitions and tests are language-independent.
- Expected outputs are authoritative and never rewritten merely to satisfy code.
- Solution headers state the algorithm and complexity without duplicating statements.
- Generated fixtures are seeded and reproducible.
- CI validates structure, generated documentation, reusable algorithm tests, and every implemented language.
- Build artifacts, credentials, and machine-specific files stay outside version control.

## License

Licensed under the [Apache License 2.0](LICENSE).
