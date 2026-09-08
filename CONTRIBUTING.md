# Contributing

Contributions should strengthen correctness, clarity, or genuinely useful language
coverage. A new implementation is portfolio evidence only when it is idiomatic,
understandable, and passes the problem's existing shared tests.

## Problem Bundles

Use `python scripts/generate_problem.py "Title"` to create the language-independent
files. Complete the statement, constraints, examples, metadata, and tests before
adding solution code. Do not invent missing constraints or source attribution.

Directory names use `NNNN-url-safe-slug`. IDs and slugs are permanent once public.
Each implementation must be placed at
`problems/<id>-<slug>/solutions/<language>/solution.<ext>` and added to both
`available_languages` and the problem README.

## Solution Standard

Start each source file with a concise problem, approach, time, and space summary.
Keep the JSON stdin/stdout boundary separate from the inspectable `solve` logic.
Prefer standard-library dependencies and do not add concurrency or abstraction
without an algorithmic reason.

## Verification

Before opening a pull request, run:

```bash
python scripts/validate_problem.py
python scripts/run_all.py
python -m unittest discover -s tests -v
python scripts/generate_index.py
python scripts/generate_index.py --check
```

Never change expected output solely to make a solution pass. If the statement,
examples, and tests disagree, document the discrepancy and resolve the contract
before migrating or implementing that problem.
