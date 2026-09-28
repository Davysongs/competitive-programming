"""Problem: Hidden Tree Matching Oracle.

Approach: Deterministic bipartite forest coloring templates with binary-search edge isolation.
Time: O(N log N) oracle queries and O(N^2) local computation.
Space: O(N) for adjacency list, component colorings, and binary codes.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations
import json
import sys
from typing import Any, Callable


def reconstruct_tree(
    node_count: int,
    query_oracle: Callable[[list[int]], int],
) -> list[list[int]]:
    """Reconstruct all N - 1 tree edges using matching oracle queries."""
    if node_count == 2:
        return [[1, 2]]

    code_rows = 16

    def generate_codes(limit: int) -> list[list[int]]:
        codes: list[list[int]] = []
        for extra_ones in combinations(range(1, code_rows), 7):
            bits = [0] * code_rows
            bits[0] = 1
            for idx in extra_ones:
                bits[idx] = 1
            codes.append(bits)
            if len(codes) == limit:
                break
        return codes

    component_codes = generate_codes(node_count)
    discovered_edges: list[list[int]] = []
    adj: dict[int, list[int]] = {i: [] for i in range(1, node_count + 1)}

    def get_bipartite_components() -> list[tuple[list[int], list[int]]]:
        visited: dict[int, int] = {}
        components: list[tuple[list[int], list[int]]] = []

        for start in range(1, node_count + 1):
            if start in visited:
                continue
            black: list[int] = []
            white: list[int] = []
            queue = deque([start])
            visited[start] = 0
            while queue:
                u = queue.popleft()
                if visited[u] == 0:
                    black.append(u)
                else:
                    white.append(u)
                for v in adj[u]:
                    if v not in visited:
                        visited[v] = 1 - visited[u]
                        queue.append(v)
            components.append((black, white))

        return components

    def find_single_edge(subset: list[int]) -> tuple[int, int]:
        mid = len(subset) // 2
        left = subset[:mid]
        right = subset[mid:]

        if query_oracle(left) > 0:
            return find_single_edge(left)
        if query_oracle(right) > 0:
            return find_single_edge(right)

        curr_left = left
        while len(curr_left) > 1:
            split_idx = len(curr_left) // 2
            left_half = curr_left[:split_idx]
            right_half = curr_left[split_idx:]
            if query_oracle(left_half + right) > 0:
                curr_left = left_half
            else:
                curr_left = right_half
        u = curr_left[0]

        curr_right = right
        while len(curr_right) > 1:
            split_idx = len(curr_right) // 2
            left_half = curr_right[:split_idx]
            right_half = curr_right[split_idx:]
            if query_oracle([u] + left_half) > 0:
                curr_right = left_half
            else:
                curr_right = right_half
        v = curr_right[0]

        return (u, v)

    while len(discovered_edges) < node_count - 1:
        components = get_bipartite_components()
        found_edge = False

        for row in range(code_rows):
            query_set: list[int] = []
            for comp_idx, (black, white) in enumerate(components):
                if component_codes[comp_idx][row] == 0:
                    query_set.extend(black)
                else:
                    query_set.extend(white)

            if len(query_set) >= 2 and query_oracle(query_set) > 0:
                u, v = find_single_edge(query_set)
                canonical_edge = [min(u, v), max(u, v)]
                discovered_edges.append(canonical_edge)
                adj[u].append(v)
                adj[v].append(u)
                found_edge = True
                break

        if not found_edge:
            raise RuntimeError("Failed to expose tree edge across components")

    discovered_edges.sort()
    return discovered_edges


def solve(input_data: dict[str, Any]) -> list[list[int]]:
    """Solve the hidden tree reconstruction problem."""
    node_count = int(input_data.get("N", input_data.get("n", 2)))

    if "oracle" in input_data and callable(input_data["oracle"]):
        return reconstruct_tree(node_count, input_data["oracle"])

    def stdio_oracle(subset: list[int]) -> int:
        if len(subset) <= 1:
            return 0
        sys.stdout.write(json.dumps({"type": "query", "S": subset}) + "\n")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            raise EOFError("Unexpected EOF while reading matching oracle response")
        return int(json.loads(line)["matching_size"])

    return reconstruct_tree(node_count, stdio_oracle)


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
