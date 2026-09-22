"""Problem: XOR Oracle: Reconstruct the Hidden Set.

Approach: binary Trie prefix-probing DFS with bitwise complement masking.
Time: O(N * B) oracle queries and operations, where B = 30.
Space: O(N * B) for the Trie and discovered elements.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Callable


def reconstruct_hidden_set(
    target_count: int,
    query_oracle: Callable[[int], int],
) -> list[int]:
    """Reconstruct all target_count elements of the hidden set using oracle queries."""
    known_elements: set[int] = set()
    discovered_order: list[int] = []
    trie_root: dict[int, Any] = {}

    def insert_element(value: int) -> None:
        if value in known_elements:
            return
        known_elements.add(value)
        discovered_order.append(value)

        current_node = trie_root
        for bit_index in range(29, -1, -1):
            bit = (value >> bit_index) & 1
            if bit not in current_node:
                current_node[bit] = {}
            current_node = current_node[bit]

    def prefix_exists_in_trie(prefix: int, depth: int) -> bool:
        current_node = trie_root
        for bit_index in range(29, depth - 1, -1):
            bit = (prefix >> bit_index) & 1
            if bit not in current_node:
                return False
            current_node = current_node[bit]
        return True

    # Bootstrap: Q(0) = max(A) because y ^ 0 = y
    initial_element = query_oracle(0)
    insert_element(initial_element)

    def search_subtrie(depth: int, current_prefix: int) -> None:
        if depth < 0 or len(known_elements) == target_count:
            return

        for bit_val in (0, 1):
            if len(known_elements) == target_count:
                return

            candidate_prefix = current_prefix | (bit_val << depth)
            if prefix_exists_in_trie(candidate_prefix, depth):
                search_subtrie(depth - 1, candidate_prefix)
            else:
                prefix_mask = ((1 << (30 - depth)) - 1) << depth
                probe_value = (~candidate_prefix) & prefix_mask
                response = query_oracle(probe_value)

                if (response & prefix_mask) == prefix_mask:
                    recovered_element = response ^ probe_value
                    insert_element(recovered_element)
                    search_subtrie(depth - 1, candidate_prefix)

    search_subtrie(29, 0)
    return discovered_order


def solve(input_data: dict[str, Any]) -> list[int]:
    """Expose problem solution accepting dictionary input with optional internal oracle."""
    if "oracle" in input_data and callable(input_data["oracle"]):
        return reconstruct_hidden_set(int(input_data["n"]), input_data["oracle"])

    if "a" in input_data and isinstance(input_data["a"], list):
        hidden_elements = input_data["a"]
        count = int(input_data.get("n", len(hidden_elements)))
        return reconstruct_hidden_set(
            count,
            lambda x: max(y ^ x for y in hidden_elements),
        )

    target_count = int(input_data["n"])

    def stdio_oracle(x: int) -> int:
        sys.stdout.write(json.dumps({"type": "query", "x": x}) + "\n")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            raise EOFError("Unexpected EOF while reading oracle response")
        return int(json.loads(line)["res"])

    return reconstruct_hidden_set(target_count, stdio_oracle)


def main() -> None:
    line = sys.stdin.readline()
    if not line:
        return
    initial_message = json.loads(line)
    result = solve(initial_message)
    sys.stdout.write(json.dumps({"type": "answer", "value": result}) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()

