"""Problem: Gap-Query Substrings.

Approach: Suffix Automaton with end-position spread aggregation.
Time: O(|s| * |Sigma| + |queries| * |states|).
Space: O(|s| * |Sigma|).
"""

from __future__ import annotations

import json
import sys
from typing import Any


def solve(input_data: dict[str, Any]) -> list[int]:
    """For each gap query, count distinct substrings that are g-good."""
    source: str = str(input_data["s"])
    queries: list[int] = [int(g) for g in input_data["queries"]]

    length = len(source)
    if length == 0:
        return [0] * len(queries)

    max_states = 2 * length + 2
    longest = [0] * max_states
    suffix_link = [-1] * max_states
    transitions: list[dict[str, int]] = [dict() for _ in range(max_states)]
    min_end = [10**9] * max_states
    max_end = [-(10**9)] * max_states

    state_count = 1
    last = 0

    for index, char in enumerate(source, start=1):
        current = state_count
        state_count += 1
        longest[current] = longest[last] + 1
        min_end[current] = index
        max_end[current] = index

        parent = last
        while parent != -1 and char not in transitions[parent]:
            transitions[parent][char] = current
            parent = suffix_link[parent]

        if parent == -1:
            suffix_link[current] = 0
        else:
            successor = transitions[parent][char]
            if longest[parent] + 1 == longest[successor]:
                suffix_link[current] = successor
            else:
                clone = state_count
                state_count += 1
                longest[clone] = longest[parent] + 1
                suffix_link[clone] = suffix_link[successor]
                transitions[clone] = transitions[successor].copy()
                min_end[clone] = 10**9
                max_end[clone] = -(10**9)

                while parent != -1 and transitions[parent].get(char) == successor:
                    transitions[parent][char] = clone
                    parent = suffix_link[parent]

                suffix_link[successor] = clone
                suffix_link[current] = clone

        last = current

    # Propagate min and max end positions up the suffix link tree.
    # States ordered descending by longest string length (leaves to root).
    order = sorted(range(state_count), key=lambda state: longest[state], reverse=True)
    for state in order:
        link = suffix_link[state]
        if link != -1:
            if min_end[state] < min_end[link]:
                min_end[link] = min_end[state]
            if max_end[state] > max_end[link]:
                max_end[link] = max_end[state]

    # Pre-extract (min_len, max_len, spread) for all non-root states.
    state_info: list[tuple[int, int, int]] = []
    for state in range(1, state_count):
        min_len = longest[suffix_link[state]] + 1
        max_len = longest[state]
        spread = max_end[state] - min_end[state]
        state_info.append((min_len, max_len, spread))

    answers: list[int] = []
    for gap in queries:
        total = 0
        for min_len, max_len, spread in state_info:
            # Substring length L is g-good iff spread >= L + gap <=> L <= spread - gap
            valid_max = min(max_len, spread - gap)
            if valid_max >= min_len:
                total += valid_max - min_len + 1
        answers.append(total)

    return answers


def main() -> None:
    json.dump(solve(json.load(sys.stdin)), sys.stdout)


if __name__ == "__main__":
    main()
