"""Problem: Entangled Isotope Decay.

Approach: Tree contraction via greedy priority queue and Disjoint Set Union (DSU).
Time: O(N log N).
Space: O(N).
"""

from __future__ import annotations

import heapq
import json
import sys
from typing import Any


class RatioEntry:
    """Priority queue entry comparing beta/alpha ratio via cross-multiplication.

    Higher beta/alpha ratio means higher priority (processed earlier).
    Cross-multiplication prevents precision loss from floating-point division.
    """

    __slots__ = ("beta", "alpha", "node", "version")

    def __init__(self, beta: int, alpha: int, node: int, version: int) -> None:
        self.beta = beta
        self.alpha = alpha
        self.node = node
        self.version = version

    def __lt__(self, other: RatioEntry) -> bool:
        return self.beta * other.alpha > other.beta * self.alpha

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RatioEntry):
            return NotImplemented
        return self.beta * other.alpha == other.beta * self.alpha


def solve(input_data: dict[str, Any]) -> int:
    """Compute the minimum total instability cost for isotope removal."""
    n = int(input_data["N"])
    if n <= 1:
        return 0

    alpha = input_data["alpha"]
    beta = input_data["beta"]
    edges = input_data["edges"]

    alpha_arr = [0] + [int(x) for x in alpha]
    beta_arr = [0] + [int(x) for x in beta]

    parent = [0] * (n + 1)
    for u, v in edges:
        parent[int(v)] = int(u)

    dsu_parent = list(range(n + 1))

    def find(x: int) -> int:
        root = x
        while dsu_parent[root] != root:
            root = dsu_parent[root]
        curr = x
        while dsu_parent[curr] != root:
            nxt = dsu_parent[curr]
            dsu_parent[curr] = root
            curr = nxt
        return root

    version = [0] * (n + 1)
    merged = [False] * (n + 1)

    pq: list[RatioEntry] = []
    for i in range(2, n + 1):
        heapq.heappush(pq, RatioEntry(beta_arr[i], alpha_arr[i], i, 0))

    total_cost = 0

    while pq:
        entry = heapq.heappop(pq)
        u = entry.node

        if entry.version != version[u] or merged[u]:
            continue

        merged[u] = True
        u_rep = find(u)
        p = parent[u_rep]
        p_rep = find(p)

        total_cost += alpha_arr[p_rep] * beta_arr[u_rep]
        alpha_arr[p_rep] += alpha_arr[u_rep]
        beta_arr[p_rep] += beta_arr[u_rep]
        dsu_parent[u_rep] = p_rep

        if p_rep != 1:
            version[p_rep] += 1
            heapq.heappush(
                pq,
                RatioEntry(beta_arr[p_rep], alpha_arr[p_rep], p_rep, version[p_rep]),
            )

    return total_cost


def main() -> None:
    json.dump(solve(json.load(sys.stdin)), sys.stdout)


if __name__ == "__main__":
    main()
