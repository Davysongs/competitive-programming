#!/usr/bin/env python3
"""Run one problem's implementations against its shared JSON test suite."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from repository import (
    LANGUAGE_FILES,
    find_problem,
    implemented_languages,
    load_json,
    materialize_test,
    test_cases,
    values_equal,
)


def command_for(
    language: str, source: Path, build_directory: Path
) -> tuple[list[str] | None, list[str]]:
    if language == "python":
        return None, [sys.executable, str(source)]
    if language == "go":
        executable = build_directory / "solution-go"
        return ["go", "build", "-o", str(executable), str(source)], [str(executable)]
    if language == "cpp":
        executable = build_directory / "solution-cpp"
        return [
            "g++",
            "-std=c++20",
            "-O2",
            "-Wall",
            "-Wextra",
            "-pedantic",
            str(source),
            "-o",
            str(executable),
        ], [str(executable)]
    if language == "rust":
        executable = build_directory / "solution-rust"
        return [
            "rustc",
            "--edition=2021",
            "-O",
            str(source),
            "-o",
            str(executable),
        ], [str(executable)]
    raise ValueError(f"unsupported language: {language}")


def comparison_tolerance(specification: dict[str, Any], test: dict[str, Any]) -> float | None:
    comparison = test.get("comparison_override", specification.get("comparison", "exact"))
    if comparison in ("exact", "unordered"):
        return None
    if comparison == "float_tolerance":
        return float(test.get("float_tolerance", specification.get("float_tolerance", 0)))
    raise ValueError(f"unsupported comparison strategy: {comparison!r}")


def concise(value: Any, limit: int = 500) -> str:
    representation = repr(value)
    if len(representation) <= limit:
        return representation
    return representation[:limit] + f"... <{len(representation) - limit} characters omitted>"


def _run_interactive_test(
    run_command: list[str],
    input_data: dict[str, Any],
    expected: Any,
    specification: dict[str, Any],
    test: dict[str, Any],
    timeout_seconds: float,
) -> tuple[bool, str]:
    hidden = input_data.get("a")
    if hidden is None and isinstance(input_data.get("hidden_state"), dict):
        hidden = input_data["hidden_state"].get("a")
    if not isinstance(hidden, list):
        return False, "interactive test requires hidden list 'a'"

    n = input_data.get("n", len(hidden))
    max_queries = test.get("max_queries", 13000)

    try:
        process = subprocess.Popen(
            run_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as error:
        return False, f"failed to execute command: {error}"

    try:
        if process.stdin is None or process.stdout is None:
            return False, "failed to attach standard I/O streams"

        process.stdin.write(json.dumps({"n": n}) + "\n")
        process.stdin.flush()

        query_count = 0
        actual: Any = None

        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError as error:
                process.kill()
                return False, f"invalid JSON from solution: {error}"

            msg_type = message.get("type")
            if msg_type == "query":
                query_count += 1
                if query_count > max_queries:
                    process.kill()
                    return False, f"query limit exceeded: {query_count} > {max_queries}"
                x = message.get("x")
                if not isinstance(x, int) or isinstance(x, bool) or not (0 <= x < (1 << 30)):
                    process.kill()
                    return False, f"invalid query parameter x: {x!r}"
                response_val = max(y ^ x for y in hidden)
                process.stdin.write(json.dumps({"res": response_val}) + "\n")
                process.stdin.flush()
            elif msg_type == "answer":
                actual = message.get("value")
                break
            else:
                process.kill()
                return False, f"unknown message type: {msg_type!r}"

        stdout, stderr = process.communicate(timeout=timeout_seconds)
        if process.returncode != 0:
            detail = stderr.strip() or f"exit code {process.returncode}"
            return False, f"solution exited with error: {detail}"

        if actual is None:
            return False, "solution terminated without answer"

        tolerance = comparison_tolerance(specification, test)
        comparison = test.get("comparison_override") or specification.get("comparison", "exact")
        is_unordered = comparison == "unordered"
        if not values_equal(actual, expected, tolerance, unordered=is_unordered):
            return False, f"expected {concise(expected)}, received {concise(actual)}"

        return True, ""
    except subprocess.TimeoutExpired:
        process.kill()
        return False, f"timed out after {timeout_seconds}s"
    except Exception as error:
        process.kill()
        return False, f"interactive error: {error}"


def run_language(
    problem: Path,
    language: str,
    specification: dict[str, Any],
    timeout_seconds: float,
) -> tuple[int, int, list[str]]:
    source = problem / "solutions" / language / LANGUAGE_FILES[language]
    failures: list[str] = []
    cases = list(test_cases(specification))

    with tempfile.TemporaryDirectory(prefix="cp-runner-") as temporary_directory:
        build_directory = Path(temporary_directory)
        build_command, run_command = command_for(language, source, build_directory)
        required_command = build_command[0] if build_command else run_command[0]
        if shutil.which(required_command) is None:
            return 0, len(cases), [f"required command not found: {required_command}"]
        if build_command:
            environment = os.environ.copy()
            if language == "go":
                environment["GOCACHE"] = str(build_directory / "go-cache")
            build = subprocess.run(
                build_command,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
                env=environment,
            )
            if build.returncode != 0:
                detail = (build.stderr or build.stdout).strip()
                return 0, len(cases), [f"build failed: {detail}"]

        is_interactive = specification.get("io_mode") == "interactive"
        passed = 0
        for test in cases:
            name = str(test.get("name", "unnamed"))
            try:
                input_data, expected = materialize_test(test)
                if is_interactive:
                    success, error_detail = _run_interactive_test(
                        run_command,
                        input_data,
                        expected,
                        specification,
                        test,
                        timeout_seconds,
                    )
                    if not success:
                        failures.append(f"{name}: {error_detail}")
                        continue
                    passed += 1
                else:
                    execution = subprocess.run(
                        run_command,
                        input=json.dumps(input_data, separators=(",", ":")),
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=timeout_seconds,
                    )
                    if execution.returncode != 0:
                        detail = execution.stderr.strip() or f"exit code {execution.returncode}"
                        failures.append(f"{name}: execution failed: {detail}")
                        continue
                    try:
                        actual: Any = json.loads(execution.stdout)
                    except json.JSONDecodeError as error:
                        failures.append(f"{name}: invalid JSON output: {error}")
                        continue
                    tolerance = comparison_tolerance(specification, test)
                    comparison = test.get("comparison_override") or specification.get("comparison", "exact")
                    is_unordered = comparison == "unordered"
                    if not values_equal(actual, expected, tolerance, unordered=is_unordered):
                        failures.append(
                            f"{name}: expected {concise(expected)}, received {concise(actual)}"
                        )
                        continue
                    passed += 1
            except (KeyError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
                failures.append(f"{name}: {error}")
    return passed, len(cases), failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", help="numeric ID or full problem directory name")
    parser.add_argument("--language", choices=sorted(LANGUAGE_FILES))
    parser.add_argument("--timeout", type=float, help="per-test timeout in seconds")
    parser.add_argument(
        "--test",
        action="append",
        default=[],
        metavar="GLOB",
        help="run test names matching this glob; may be repeated",
    )
    parser.add_argument(
        "--generated-only",
        action="store_true",
        help="run only cases that materialize generated input fields",
    )
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="list matching tests without executing implementations",
    )
    parser.add_argument("--quiet", action="store_true")
    arguments = parser.parse_args()

    try:
        problem = find_problem(arguments.problem)
        metadata = load_json(problem / "metadata.json")
        specification = load_json(problem / "tests.json")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    languages = implemented_languages(problem)
    if arguments.language:
        if arguments.language not in languages:
            print(
                f"ERROR: {problem.name} has no {arguments.language} implementation",
                file=sys.stderr,
            )
            return 2
        languages = [arguments.language]
    if not languages:
        print(f"ERROR: {problem.name} has no implementations", file=sys.stderr)
        return 2

    selected_tests = list(
        test_cases(specification, arguments.test, arguments.generated_only)
    )
    if not selected_tests:
        print("ERROR: no tests matched the requested selection", file=sys.stderr)
        return 2
    if arguments.list_tests:
        for test in selected_tests:
            kind = (
                "generated"
                if test.get("generators") or test.get("generate")
                else "inline"
            )
            print(f"{test['name']}\t{kind}")
        return 0
    specification = {**specification, "tests": selected_tests}

    timeout_seconds = arguments.timeout or max(
        5.0, float(metadata["resource_limits"]["time_ms"]) / 1000 * 3
    )
    if not arguments.quiet:
        print(f"Problem: {problem.name}\n")

    successful = True
    for language in languages:
        passed, total, failures = run_language(
            problem, language, specification, timeout_seconds
        )
        status = "PASS" if passed == total else "FAIL"
        print(f"{language.capitalize():<10} {passed}/{total} {status}")
        for failure in failures:
            print(f"  - {failure}")
        successful = successful and passed == total

    if not arguments.quiet:
        print("\nAll implemented languages passed." if successful else "\nFailures detected.")
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
