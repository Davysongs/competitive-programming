"""Problem: Cumulative Power Grid.

Approach: Pool Adjacent Violators Algorithm (PAVA) with dual active/inactive heaps and small-to-large merging.
Time: O(N log^2 N).
Space: O(N).
"""

from __future__ import annotations

import heapq
import json
import sys
from typing import Any


MOD = 998_244_353
NEG_INF_SENTINEL = -(10**18)


def _rebalance_block(block: dict[str, Any]) -> None:
    """Restore KKT active/inactive partition invariants via exact integer cross-multiplication."""
    active_max_heap: list[int] = block["active_max_heap"]
    inactive_min_heap: list[int] = block["inactive_min_heap"]

    while True:
        changed = False
        active_count: int = block["active_count"]
        if active_count > 0:
            numerator = block["requirement"] + block["active_sum"]
            # Move largest active cost to inactive if P_i >= nu.
            if active_max_heap and -active_max_heap[0] * active_count >= numerator:
                cost = -heapq.heappop(active_max_heap)
                block["active_sum"] -= cost
                block["active_sq_sum"] -= cost * cost
                block["active_count"] -= 1
                heapq.heappush(inactive_min_heap, cost)
                changed = True
            # Move smallest inactive cost to active if P_i < nu.
            elif inactive_min_heap and inactive_min_heap[0] * active_count < numerator:
                cost = heapq.heappop(inactive_min_heap)
                block["active_sum"] += cost
                block["active_sq_sum"] += cost * cost
                block["active_count"] += 1
                heapq.heappush(active_max_heap, -cost)
                changed = True
        elif block["requirement"] > 0 and inactive_min_heap:
            # Forced activation: a block with positive requirement needs at least one active node.
            cost = heapq.heappop(inactive_min_heap)
            block["active_sum"] += cost
            block["active_sq_sum"] += cost * cost
            block["active_count"] += 1
            heapq.heappush(active_max_heap, -cost)
            changed = True

        if not changed:
            break

    if block["active_count"] > 0:
        block["nu_num"] = block["requirement"] + block["active_sum"]
        block["nu_den"] = block["active_count"]
    else:
        # An all-inactive block uses its minimum inactive cost as its effective threshold.
        block["nu_num"] = inactive_min_heap[0] if inactive_min_heap else NEG_INF_SENTINEL
        block["nu_den"] = 1


def _make_block(requirement: int, linear_cost: int) -> dict[str, Any]:
    """Create a single-node PAVA block and initialize its KKT partition."""
    block: dict[str, Any] = {
        "requirement": requirement,
        "active_sum": linear_cost,
        "active_sq_sum": linear_cost * linear_cost,
        "active_count": 1,
        "active_max_heap": [-linear_cost],
        "inactive_min_heap": [],
        "nu_num": 0,
        "nu_den": 1,
    }
    _rebalance_block(block)
    return block


def _merge_blocks(left_block: dict[str, Any], right_block: dict[str, Any]) -> None:
    """Merge right_block into left_block using small-to-large heap transfers."""
    left_block["requirement"] += right_block["requirement"]
    left_block["active_sum"] += right_block["active_sum"]
    left_block["active_sq_sum"] += right_block["active_sq_sum"]
    left_block["active_count"] += right_block["active_count"]

    if len(left_block["active_max_heap"]) < len(right_block["active_max_heap"]):
        left_block["active_max_heap"], right_block["active_max_heap"] = (
            right_block["active_max_heap"],
            left_block["active_max_heap"],
        )
    for item in right_block["active_max_heap"]:
        heapq.heappush(left_block["active_max_heap"], item)

    if len(left_block["inactive_min_heap"]) < len(right_block["inactive_min_heap"]):
        left_block["inactive_min_heap"], right_block["inactive_min_heap"] = (
            right_block["inactive_min_heap"],
            left_block["inactive_min_heap"],
        )
    for item in right_block["inactive_min_heap"]:
        heapq.heappush(left_block["inactive_min_heap"], item)

    _rebalance_block(left_block)


def solve(input_data: dict[str, Any]) -> int:
    """Compute the minimum total injection cost modulo 998244353."""
    node_count = int(input_data["n"])
    prefix_bounds = [int(value) for value in input_data["d"]]
    linear_costs = [int(value) for value in input_data["p"]]

    blocks: list[dict[str, Any]] = []
    previous_bound = 0
    for idx in range(node_count):
        bound = prefix_bounds[idx]
        incremental_req = max(0, bound - previous_bound)
        previous_bound = bound

        current_block = _make_block(incremental_req, linear_costs[idx])
        while (
            blocks
            and blocks[-1]["nu_num"] * current_block["nu_den"]
            < current_block["nu_num"] * blocks[-1]["nu_den"]
        ):
            previous_block = blocks.pop()
            _merge_blocks(previous_block, current_block)
            current_block = previous_block
        blocks.append(current_block)

    total_cost = 0
    for block in blocks:
        active_count = block["active_count"]
        if active_count > 0:
            numerator_mod = (block["requirement"] + block["active_sum"]) % MOD
            inv_count = pow(active_count, MOD - 2, MOD)
            block_term = (
                numerator_mod * numerator_mod % MOD * inv_count
                - block["active_sq_sum"]
            ) % MOD
            total_cost = (total_cost + block_term) % MOD

    total_bound_mod = prefix_bounds[-1] % MOD
    total_cost = (total_cost - total_bound_mod * total_bound_mod) % MOD
    return total_cost


def main() -> None:
    json.dump(solve(json.load(sys.stdin)), sys.stdout)


if __name__ == "__main__":
    main()
