# Data Stream Transmission

**Difficulty:** Expert  
**Category:** Greedy, Dynamic Programming  
**Tags:** `exchange-argument`, `sequence-dp`

## Problem

You are given $N$ data packets that must all be transmitted in some order. Each packet
$i$ has a transmission time $S_i$ (a positive integer) and a success probability $Q_i$
(a float in the range $(0, 1]$).

Packets are grouped into contiguous segments. When a packet in a segment fails
(which happens with probability $1 - Q_i$), the entire segment restarts from its
first packet. A segment completes only when every packet in it succeeds in the
same uninterrupted run.

You may place at most $K$ checkpoints between consecutive packets. Each checkpoint
marks the boundary between two segments. Failures after a checkpoint only restart
the segment that contains the failed packet.

Your two decisions are:

1. The order in which to transmit all $N$ packets.
2. The placement of at most $K$ checkpoints to partition the ordered sequence into
   segments.

Minimize the total expected transmission time across all segments, and return it
rounded to 6 decimal places using Python's built-in `round()` function.

**Expected time for one segment** containing packets $p_1, p_2, \ldots, p_m$
(in their order within the segment):

Define the **per-attempt cost** $C$ as the expected transmission time of a single
attempt on the segment. Because each packet is tried only if all preceding packets
in that attempt succeeded:
$$C = S_{p_1} + Q_{p_1} \cdot S_{p_2} + Q_{p_1} \cdot Q_{p_2} \cdot S_{p_3}
+ \cdots + \left(\prod_{t=1}^{m-1} Q_{p_t}\right) \cdot S_{p_m}$$

Define the **segment success probability** $R$ as the probability that the entire
segment finishes without any failure:
$$R = Q_{p_1} \cdot Q_{p_2} \cdots Q_{p_m}$$

Because the segment keeps restarting until it succeeds, its expected time follows a
geometric distribution:
$$E[\text{segment}] = \frac{C}{R}$$

The total expected time is the sum of $E[\text{segment}]$ over all segments.

## Input Format

Input is a JSON object with the following fields:

- `n` (integer): Number of packets.
- `k` (integer): Maximum number of checkpoints that can be placed.
- `packets` (array of arrays): List of n pairs [s_i, q_i] where s_i (integer)
  is the transmission time of packet i and q_i (float) is its success probability.

Example input:
```json
{
  "n": 2,
  "k": 0,
  "packets": [[10, 0.5], [10, 0.5]]
}
```

## Output Format

Output is a JSON number (float): the minimum total expected transmission time,
rounded to 6 decimal places.

Example output:
```json
60.0
```

## Constraints

- 1 <= n <= 200
- 0 <= k (k may exceed n - 1; at most n - 1 checkpoints can be physically placed, so any k >= n - 1 is equivalent to k = n - 1)
- 1 <= s_i <= 10^9
- 0.0 < q_i <= 1.0 for all i
- The product $Q_{p_1} \cdot Q_{p_2} \cdots Q_{p_m}$ for any segment will not
  underflow IEEE 754 double precision floating point.
- Time limit: 2000ms
- Memory limit: 256MB

## Examples

### Example 1

**Input:**
```json
{
  "n": 2,
  "k": 0,
  "packets": [[10, 0.5], [10, 0.5]]
}
```

**Output:**
```json
60.0
```

**Explanation:**
With no checkpoints ($k=0$), both packets form a single segment.
Both packets have the same greedy key $S_i / (1 - Q_i) = 10 / 0.5 = 20$, so
order does not matter.
- Per-attempt cost: $C = S_1 + Q_1 \cdot S_2 = 10 + 0.5 \times 10 = 15$
- Segment success probability: $R = Q_1 \cdot Q_2 = 0.5 \times 0.5 = 0.25$
- Expected time: $E = C / R = 15 / 0.25 = 60.0$

### Example 2

**Input:**
```json
{
  "n": 2,
  "k": 1,
  "packets": [[10, 0.5], [10, 0.5]]
}
```

**Output:**
```json
40.0
```

**Explanation:**
With $k=1$, one checkpoint is placed between the two packets.
Each packet becomes its own single-packet segment.
- Segment 1: $E_1 = S_1 / Q_1 = 10 / 0.5 = 20.0$
- Segment 2: $E_2 = S_2 / Q_2 = 10 / 0.5 = 20.0$
- Total: $E = 20.0 + 20.0 = 40.0$

### Example 3

**Input:**
```json
{
  "n": 2,
  "k": 0,
  "packets": [[5, 0.1], [20, 0.8]]
}
```

**Output:**
```json
87.5
```

**Explanation:**
Greedy keys $S_i / (1 - Q_i)$:
- Packet A (5, 0.1): $5 / (1 - 0.1) = 5 / 0.9 \approx 5.56$
- Packet B (20, 0.8): $20 / (1 - 0.8) = 20 / 0.2 = 100$

Since key(A) < key(B), the optimal order is A then B.
- Per-attempt cost: $C = S_A + Q_A \cdot S_B = 5 + 0.1 \times 20 = 7$
- Segment success probability: $R = Q_A \cdot Q_B = 0.1 \times 0.8 = 0.08$
- Expected time: $E = C / R = 7 / 0.08 = 87.5$

If instead the order were B then A:
- $C = 20 + 0.8 \times 5 = 24$, $R = 0.08$, $E = 24 / 0.08 = 300$ (much worse).

### Example 4

**Input:**
```json
{
  "n": 3,
  "k": 1,
  "packets": [[2, 0.5], [4, 0.5], [6, 0.5]]
}
```

**Output:**
```json
28.0
```

**Explanation (DP trace):**

**Step 1 – Sort by $S_i / (1 - Q_i)$.**
Keys: $2/0.5=4$, $4/0.5=8$, $6/0.5=12$. Sorted order: $(2,0.5),\,(4,0.5),\,(6,0.5)$.

**Step 2 – Prefix arrays.**

| $i$ | $S[i]$ | $Q[i]$ | $P[i]$  | $ws[i]$ |
|-----|--------|--------|---------|---------|
| 0   | 2      | 0.5    | 1.0     | 0.0     |
| 1   | 4      | 0.5    | 0.5     | 2.0     |
| 2   | 6      | 0.5    | 0.25    | 4.0     |
| 3   | –      | –      | 0.125   | 5.5     |

**Step 3 – DP initialisation (1 segment, 0 checkpoints).**

$$dp[i] = \frac{ws[i+1] - ws[0]}{P[i+1]}$$

| $i$ | $dp[i]$                          |
|-----|----------------------------------|
| 0   | $2.0 / 0.5 = 4.0$                |
| 1   | $4.0 / 0.25 = 16.0$              |
| 2   | $5.5 / 0.125 = 44.0$             |

Answer so far (no checkpoint): $44.0$.

**Step 4 – DP round 2 (2 segments, 1 checkpoint).**

For each endpoint $i$, try every split point $j$ and keep the minimum
$dp[j] + (ws[i+1] - ws[j+1]) / P[i+1]$:

| $i$ | $j$ | $dp[j]$ | $(ws[i+1]-ws[j+1])/P[i+1]$ | Total |
|-----|-----|---------|-----------------------------|-------|
| 1   | 0   | 4.0     | $(4.0-2.0)/0.25 = 8.0$      | **12.0** |
| 2   | 0   | 4.0     | $(5.5-2.0)/0.125 = 28.0$    | 32.0  |
| 2   | 1   | 16.0    | $(5.5-4.0)/0.125 = 12.0$    | **28.0** |

New $dp['new'][1]=12.0$, $dp['new'][2]=28.0$.

Answer updated: $\min(44.0,\,28.0) = \mathbf{28.0}$.

The optimal split is placing the checkpoint after the second packet, giving
segments $[(2,0.5),(4,0.5)]$ and $[(6,0.5)]$ with expected times $16.0$ and $12.0$ respectively.

## Approach

An adjacent-swap exchange argument shows that packets should be ordered by
$S_i/(1-Q_i)$ in ascending order; packets with $Q_i=1$ have an infinite key and
come last. This order is optimal independently of checkpoint placement.

After sorting, precompute prefix products of success probabilities and prefix sums
of probability-weighted durations. They make the expected cost of any contiguous
segment available in $O(1)$. A rolling dynamic program then tries every final
segment boundary for each permitted segment count. The number of segments is
capped at $n$, so values of $k$ greater than $n-1$ are handled naturally. All
rounding is deferred until the final result.

## Complexity

**Time:** $O(n \log n + k'n^2)$, where $k'=\min(k,n-1)$  
**Space:** $O(n)$

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
