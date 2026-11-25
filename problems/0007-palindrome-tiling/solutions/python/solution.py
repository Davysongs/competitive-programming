"""Problem: Palindrome Tiling.

Approach: Two-level interval dynamic programming over collapsible values and palindromic tiling blocks.
Time: O(N^3 log N).
Space: O(N^2 log N).
"""

from __future__ import annotations

import json
import sys
from typing import Any


def solve(input_data: dict[str, Any]) -> int:
    """Compute the maximum number of blocks in a palindromic tiling of array a."""
    n: int = int(input_data["n"])
    a: list[int] = [int(x) for x in input_data["a"]]

    if n == 0:
        return 0

    # vals[i][j]: set of values that subarray a[i..j] can collapse into.
    # left_values[i][j]: union of vals[i][k] for k < j where a[k+1..j] is collapsible.
    vals: list[list[set[int]]] = [[set() for _ in range(n)] for _ in range(n)]
    left_values: list[list[set[int]]] = [[set() for _ in range(n)] for _ in range(n)]

    for i in range(n):
        vals[i][i].add(a[i])

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            current_values: set[int] = set()

            # Type-1 merge: identical collapsible value on left and right halves.
            for k in range(i, j):
                for val in vals[i][k]:
                    if val in vals[k + 1][j]:
                        current_values.add(val + 1)

            # Type-2 merge: matching endpoint value with collapsible middle.
            for m in range(i + 1, j):
                for val in vals[m + 1][j]:
                    if val in left_values[i][m]:
                        current_values.add(val + 1)

            vals[i][j] = current_values

            prefix_values: set[int] = set()
            for k in range(i, j):
                if vals[k + 1][j]:
                    prefix_values.update(vals[i][k])
            left_values[i][j] = prefix_values

    # max_blocks[i][j]: maximum block count for a palindromic tiling of a[i..j].
    # left_inner[i][j][val]: maximum inner block count for left block with collapsed value val.
    max_blocks: list[list[int]] = [[0] * n for _ in range(n)]
    left_inner: list[list[dict[int, int]]] = [
        [dict() for _ in range(n)] for _ in range(n)
    ]

    for i in range(n):
        max_blocks[i][i] = 1
        left_inner[i][i][a[i]] = 0

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1

            # Baseline: single collapsed block (K = 1).
            if vals[i][j]:
                max_blocks[i][j] = 1

            # K >= 2: match outer left block and outer right block on equal value.
            for k2 in range(i, j):
                left_map = left_inner[i][k2]
                for val in vals[k2 + 1][j]:
                    if val in left_map:
                        candidate = 2 + left_map[val]
                        if candidate > max_blocks[i][j]:
                            max_blocks[i][j] = candidate

            current_map = left_inner[i][j]

            # Case k1 = j: empty interior contributes 0 inner blocks.
            for val in vals[i][j]:
                if current_map.get(val, -1) < 0:
                    current_map[val] = 0

            # Case k1 < j: non-empty interior must itself admit a palindromic tiling.
            for k1 in range(i, j):
                inner_count = max_blocks[k1 + 1][j]
                if inner_count > 0:
                    for val in vals[i][k1]:
                        if current_map.get(val, -1) < inner_count:
                            current_map[val] = inner_count

    return max_blocks[0][n - 1]


def main() -> None:
    input_data = json.load(sys.stdin)
    result = solve(input_data)
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
