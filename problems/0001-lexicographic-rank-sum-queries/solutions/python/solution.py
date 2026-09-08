"""Problem: Lexicographic Rank Sum Queries.

Approach: suffix automaton with lexicographic subtree counts.
Time: O((|s| + total query length) * alphabet size).
Space: O(|s|).
"""

from __future__ import annotations

import json
import sys
from typing import Any


MODULUS = 1_000_000_007


def solve(input_data: dict[str, Any]) -> list[list[int]]:
    """Return the number and rank sum of substrings not greater than each query."""
    source = str(input_data["s"])
    queries = [str(query) for query in input_data["queries"]]

    maximum_states = 2 * len(source) + 1
    longest = [0] * maximum_states
    suffix_link = [-1] * maximum_states
    transitions: list[dict[str, int]] = [dict() for _ in range(maximum_states)]
    state_count = 1
    last = 0

    for character in source:
        current = state_count
        state_count += 1
        longest[current] = longest[last] + 1

        parent = last
        while parent != -1 and character not in transitions[parent]:
            transitions[parent][character] = current
            parent = suffix_link[parent]

        if parent == -1:
            suffix_link[current] = 0
        else:
            successor = transitions[parent][character]
            if longest[parent] + 1 == longest[successor]:
                suffix_link[current] = successor
            else:
                clone = state_count
                state_count += 1
                longest[clone] = longest[parent] + 1
                suffix_link[clone] = suffix_link[successor]
                transitions[clone] = transitions[successor].copy()
                while (
                    parent != -1
                    and transitions[parent].get(character) == successor
                ):
                    transitions[parent][character] = clone
                    parent = suffix_link[parent]
                suffix_link[successor] = clone
                suffix_link[current] = clone
        last = current

    order = sorted(range(state_count), key=longest.__getitem__)
    reachable_substrings = [0] * state_count
    for state in reversed(order):
        reachable_substrings[state] = sum(
            1 + reachable_substrings[next_state]
            for next_state in transitions[state].values()
        )

    ordered_transitions = [
        sorted(state_transitions.items())
        for state_transitions in transitions[:state_count]
    ]

    answers: list[list[int]] = []
    for query in queries:
        count = 0
        rank_sum = 0
        rank_offset = 0
        state = 0

        for character in query:
            for edge_character, next_state in ordered_transitions[state]:
                if edge_character >= character:
                    break
                block_size = 1 + reachable_substrings[next_state]
                rank_sum += block_size * rank_offset
                rank_sum += block_size * (block_size + 1) // 2
                rank_sum %= MODULUS
                count += block_size
                rank_offset += block_size

            next_state = transitions[state].get(character)
            if next_state is None:
                break

            state = next_state
            count += 1
            rank_offset += 1
            rank_sum = (rank_sum + rank_offset) % MODULUS

        answers.append([count, rank_sum])

    return answers


def main() -> None:
    json.dump(solve(json.load(sys.stdin)), sys.stdout)


if __name__ == "__main__":
    main()
