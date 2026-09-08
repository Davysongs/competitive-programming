"""Problem: Data Stream Transmission.

Approach: exchange-argument ordering followed by sequence partition DP.
Time: O(n log n + k * n^2).
Space: O(n).
"""

from __future__ import annotations

import json
import sys
from typing import Any


Packet = tuple[int, float]


def solve(input_data: dict[str, Any]) -> float:
    """Return the minimum expected transmission time, rounded to six places."""
    packet_count = int(input_data["n"])
    checkpoint_count = int(input_data["k"])
    packets: list[Packet] = [
        (int(duration), float(success_probability))
        for duration, success_probability in input_data["packets"]
    ]

    def ordering_key(packet: Packet) -> float:
        duration, success_probability = packet
        failure_probability = 1.0 - success_probability
        return (
            duration / failure_probability
            if failure_probability > 0.0
            else float("inf")
        )

    packets.sort(key=ordering_key)

    success_prefix = [1.0] * (packet_count + 1)
    weighted_duration_prefix = [0.0] * (packet_count + 1)
    for index, (duration, success_probability) in enumerate(packets):
        success_prefix[index + 1] = success_prefix[index] * success_probability
        weighted_duration_prefix[index + 1] = (
            weighted_duration_prefix[index] + duration * success_prefix[index]
        )

    def segment_cost(start: int, end: int) -> float:
        return (
            weighted_duration_prefix[end + 1] - weighted_duration_prefix[start]
        ) / success_prefix[end + 1]

    costs = [segment_cost(0, end) for end in range(packet_count)]
    answer = costs[-1]

    maximum_segments = min(checkpoint_count + 1, packet_count)
    for segment_count in range(2, maximum_segments + 1):
        next_costs = [float("inf")] * packet_count
        for end in range(segment_count - 1, packet_count):
            inverse_success = 1.0 / success_prefix[end + 1]
            next_costs[end] = min(
                costs[split]
                + (
                    weighted_duration_prefix[end + 1]
                    - weighted_duration_prefix[split + 1]
                )
                * inverse_success
                for split in range(segment_count - 2, end)
            )
        costs = next_costs
        answer = min(answer, costs[-1])

    return round(answer, 6)


def main() -> None:
    json.dump(solve(json.load(sys.stdin)), sys.stdout)


if __name__ == "__main__":
    main()
