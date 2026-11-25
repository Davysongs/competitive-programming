# Cumulative Power Grid

**Difficulty:** Expert
**Category:** Greedy
**Tags:** `exchange-argument`, `priority-queue-greedy`

## Problem

You are given a sequential power grid of $N$ nodes (1-indexed). You must inject non-negative energy $x_i \ge 0$ into each node $i$ ($1 \le i \le N$) such that:

1. **Prefix requirements:** For each $1 \le i \le N$, the cumulative energy satisfies $\sum_{j=1}^{i} x_j \ge D_i$, where $D_i$ is the $i$-th prefix lower bound.
2. **Exact total:** $\sum_{i=1}^{N} x_i = D_N$.

The **total cost** of the injection strategy is:

$$C = \sum_{i=1}^{N} x_i^2 + 2 \sum_{i=1}^{N} P_i \cdot x_i - D_N^2$$

Find the minimum possible value of $C$.

The minimum is always a rational number $\frac{a}{b}$ with $\gcd(a, b) = 1$. Output $a \cdot b^{-1} \pmod{998244353}$, where $b^{-1}$ denotes the modular multiplicative inverse of $b$.

## Input Format

Input is a JSON object with the following fields:

- `n` (integer): Number of nodes ($N$).
- `d` (array of integers, length `n`): Non-decreasing prefix lower-bound array. `d[i]` (0-indexed) equals $D_{i+1}$, the minimum cumulative energy for the first $i+1$ nodes.
- `p` (array of integers, length `n`): Per-unit cost array. `p[i]` (0-indexed) equals $P_{i+1}$, the linear cost coefficient for node $i+1$.

Example input:
```json
{
  "n": 2,
  "d": [10, 20],
  "p": [5, 1]
}
```

## Output Format

Output is a JSON integer: the minimum cost modulo $998244353$.

Example output:
```json
998244273
```

## Constraints

- $1 \le N \le 10^5$
- $D$ is non-decreasing with $0 \le D_1 \le D_2 \le \cdots \le D_N \le 10^{14}$
- $1 \le P_i \le 10^9$ for all $1 \le i \le N$
- Time limit: 5000ms
- Memory limit: 256MB

## Examples

### Example 1

**Input**

```json
{
  "n": 2,
  "d": [10, 20],
  "p": [5, 1]
}
```

**Output**

```json
998244273
```

**Explanation**

With $N = 2$, $D = [10, 20]$, and $P = [5, 1]$, the constraints are $x_1 \ge 10$, $x_1 + x_2 \ge 20$, and $x_1 + x_2 = 20$.
This forces $x_2 = 20 - x_1$ and $x_1 \ge 10$.
At the minimum feasible choice $x_1 = 10$, $x_2 = 10$ (notice $x_1 = 8$ violates $x_1 \ge 10$):

$$C = 10^2 + 10^2 + 2(5)(10) + 2(1)(10) - 20^2 = 100 + 100 + 100 + 20 - 400 = -80$$

Modulo $998244353$, $-80 \equiv 998244353 - 80 = 998244273$.

### Example 2

**Input**

```json
{
  "n": 2,
  "d": [0, 20],
  "p": [5, 1]
}
```

**Output**

```json
998244265
```

**Explanation**

With $N = 2$, $D = [0, 20]$, and $P = [5, 1]$, node 1 has requirement $x_1 \ge 0$ and the exact total is $x_1 + x_2 = 20$, so $x_2 = 20 - x_1$.
Substituting into the objective gives:

$$C = x_1^2 + (20 - x_1)^2 + 2(5)x_1 + 2(1)(20 - x_1) - 400 = 2x_1^2 - 32x_1 + 40$$

Setting $\frac{dC}{dx_1} = 4x_1 - 32 = 0$ yields $x_1 = 8$ and $x_2 = 12$, which satisfies all constraints ($x_1 = 8 \ge 0$, $x_1 + x_2 = 20 \ge 20$).
The minimum cost is $C = 2(8)^2 - 32(8) + 40 = -88$, and $-88 \equiv 998244265 \pmod{998244353}$.

### Example 3

**Input**

```json
{
  "n": 2,
  "d": [0, 20],
  "p": [30, 1]
}
```

**Output**

```json
40
```

**Explanation**

With $N = 2$, $D = [0, 20]$, and $P = [30, 1]$, substituting $x_2 = 20 - x_1$ gives:

$$C = x_1^2 + (20 - x_1)^2 + 2(30)x_1 + 2(1)(20 - x_1) - 400 = 2x_1^2 + 18x_1 + 40$$

The unconstrained minimum is at $x_1 = -4.5$, which is infeasible due to $x_1 \ge 0$.
Thus the optimal feasible point is at the boundary $x_1 = 0$, $x_2 = 20$, giving $C = 40$.

## Approach

### 1. Convex Reformulation and KKT Conditions

Since $D_N^2$ and $\sum_{i=1}^N P_i^2$ are constants, minimizing $C = \sum_{i=1}^N x_i^2 + 2\sum_{i=1}^N P_i x_i - D_N^2$ is equivalent to minimizing the strictly convex objective:

$$g(x) = \sum_{i=1}^N (x_i + P_i)^2$$

Let incremental requirements be $\text{req}_1 = D_1$ and $\text{req}_i = \max(0, D_i - D_{i-1})$ for $i \ge 2$. Prefix constraints allow energy required at an earlier step to be front-loaded only or satisfied across contiguous pooled prefixes. By KKT optimality conditions, optimal allocations partition the grid left-to-right into contiguous blocks, where every block $b$ has a single Lagrange multiplier $\nu_b$:

- **Active nodes** ($P_i < \nu_b$): $x_i = \nu_b - P_i > 0$.
- **Inactive nodes** ($P_i \ge \nu_b$): $x_i = 0$.

If block $b$ has total requirement $W_b$ and $\text{cnt}_b > 0$ active nodes with sum $\text{active\_sum}_b = \sum_{\text{active}} P_i$, then $\sum_{\text{active}} (\nu_b - P_i) = W_b$ yields:

$$\nu_b = \frac{W_b + \text{active\_sum}_b}{\text{cnt}_b}$$

If $\text{cnt}_b = 0$ (possible only when $W_b = 0$), all nodes are inactive and the block's effective threshold for future merges is $\nu_b = \min_{\text{inactive}} P_i$.

### 2. Pool Adjacent Violators Algorithm (PAVA) with Dual Heaps

Process nodes from left to right as single-node blocks maintained on a stack with non-increasing multipliers $\nu$:

1. Create a block for node $i$ with $W = \text{req}_i$ and $P_i$ initially active, then rebalance its active/inactive sets.
2. While the stack top block has $\nu_{\text{top}} < \nu_{\text{curr}}$ (strict inequality preserves non-increasing monotonicity without redundant equal merges), pop and merge the two blocks.
3. Each block maintains:
   - A max-heap of active $P_i$ values (to demote the largest active $P_i \ge \nu$ to inactive).
   - A min-heap of inactive $P_i$ values (to promote the smallest inactive $P_i < \nu$ to active, or force-activate one node when $\text{cnt} = 0$ and $W > 0$).
   - Running sums $W$, $\text{active\_sum}$, $\text{active\_sq}$, and $\text{cnt}$.
4. Merge heaps using small-to-large transfers before restoring KKT invariants.

### 3. Modular Arithmetic and Numerical Precision

- **Exact fraction comparisons:** Intermediate numerators $W_b + \text{active\_sum}_b$ can reach $10^{14} + 10^{14}$, exceeding exact 53-bit IEEE-754 float precision. Compare $\nu_1 < \nu_2$ via exact integer cross-multiplication $\text{num}_1 \cdot \text{den}_2 < \text{num}_2 \cdot \text{den}_1$.
- **Modular reduction before squaring:** For each block with $\text{cnt}_b > 0$, its contribution to $\sum (x_i^2 + 2 P_i x_i)$ is $\nu_b^2 \cdot \text{cnt}_b - \sum_{\text{active}} P_i^2 = \frac{(W_b + \text{active\_sum}_b)^2}{\text{cnt}_b} - \text{active\_sq}_b$. Reduce $(W_b + \text{active\_sum}_b)$ modulo $998244353$ before squaring, multiply by $\text{cnt}_b^{-1} \pmod{998244353}$, subtract $\text{active\_sq}_b$, and finally subtract $D_N^2 \pmod{998244353}$.
- **Edge cases:** $W = 0$ across all nodes leaves every node inactive with cost $0$; binding $N = 1$ with huge $P_1$ uses forced activation when $W > 0$ so $\text{cnt}$ never divides by zero.

## Complexity

**Time:** O(N log^2 N) amortized (each node transfers across heaps $O(\log N)$ times via small-to-large merging, each push taking $O(\log N)$).
**Space:** O(N) for the PAVA stack and dual heaps containing $N$ elements in total.

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
