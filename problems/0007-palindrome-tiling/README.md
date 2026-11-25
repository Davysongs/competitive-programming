# Palindrome Tiling

**Difficulty:** Very Hard
**Category:** Dynamic Programming
**Tags:** `interval-dp`

## Problem

You are given an array $A$ of $N$ positive integers, using 0-based indexing: $A[0], A[1], \ldots, A[N-1]$.

A contiguous subarray is **collapsible** if it can be reduced to a single integer by repeatedly applying the following operation zero or more times:

1. Choose a contiguous palindromic subarray $A[l..r]$ with length at least 2 ($r - l \ge 1$).
2. Replace the chosen subarray $A[l..r]$ with a single integer equal to $A[l] + 1$.

Each operation shortens the length of the array by $r - l$. A single element $A[i]$ is trivially collapsible to $A[i]$ using zero operations.

A **palindromic tiling** of length $K$ is a partition of the entire array $A$ into $K$ contiguous non-empty blocks $B_1, B_2, \ldots, B_K$ such that:

1. Every block $B_i$ is collapsible to a single value $v_i$.
2. The sequence of collapsed values $[v_1, v_2, \ldots, v_K]$ forms a palindrome (that is, $v_i = v_{K + 1 - i}$ for all $1 \le i \le K$).

Your task is to compute the maximum possible number of blocks $K$ in any valid palindromic tiling of $A$. If no valid palindromic tiling exists, return 0.

## Input Format

The input is a JSON object with the following fields:

- `n` (integer): The number of elements in the array ($1 \le N \le 100$).
- `a` (array of integers): An array of length `n` containing positive integers ($1 \le A[i] \le 10^9$).

Example input:
```json
{
  "n": 6,
  "a": [1, 2, 1, 1, 2, 1]
}
```

## Output Format

A JSON integer representing the maximum tiling length $K$, or 0 if no valid palindromic tiling exists.

Example output:
```json
6
```

## Constraints

- $1 \le N \le 100$
- $1 \le A[i] \le 10^9$ for all $0 \le i < N$
- Time limit: 5000ms
- Memory limit: 256MB

## Examples

### Example 1

**Input**

```json
{
  "n": 6,
  "a": [1, 2, 1, 1, 2, 1]
}
```

**Output**

```json
6
```

**Explanation**

Partition $A$ into 6 single-element blocks:
$[1], [2], [1], [1], [2], [1]$.
Each block $[A[i]]$ trivially collapses to $A[i]$.
The resulting sequence of collapsed values is $[1, 2, 1, 1, 2, 1]$, which is already a palindrome.
Thus, $K = 6$ is valid, which is the maximum possible since $N = 6$.

### Example 2

**Input**

```json
{
  "n": 11,
  "a": [1, 2, 1, 5, 1, 2, 1, 3, 1, 2, 1]
}
```

**Output**

```json
7
```

**Explanation**

Partition $A$ into 7 blocks:
$[1], [2], [1, 5, 1], [2], [1, 3, 1], [2], [1]$.

- Subarray $[1, 5, 1]$ is a palindrome of length 3, collapsing to $1 + 1 = 2$.
- Subarray $[1, 3, 1]$ is a palindrome of length 3, collapsing to $1 + 1 = 2$.
- Singletons collapse to their own values.

The resulting collapsed sequence is $[1, 2, 2, 2, 2, 2, 1]$, which is a palindrome of length $K = 7$.

### Example 3

**Input**

```json
{
  "n": 3,
  "a": [1, 2, 3]
}
```

**Output**

```json
0
```

**Explanation**

- For $K = 3$: the only partition into 3 non-empty blocks is $[1], [2], [3]$, yielding collapsed values $[1, 2, 3]$, which is not a palindrome.
- For $K = 2$: the partitions are $[1] \mid [2, 3]$ and $[1, 2] \mid [3]$. Neither $[2, 3]$ nor $[1, 2]$ is a palindrome, so neither can collapse to a single value.
- For $K = 1$: the entire array $[1, 2, 3]$ is not palindromic and contains no palindromic subarrays of length at least 2, so it cannot collapse to a single value.

Therefore, no valid palindromic tiling exists, and the answer is 0.

## Approach

The problem requires determining the maximum block count $K$ in a partition of $A[0..N-1]$ into collapsible blocks whose collapsed values form a palindrome. This is solved using a two-level interval dynamic programming approach.

### 1. Inner Interval DP: Reachable Collapsible Values

First, compute $\text{vals}[i][j]$, the set of all integers that subarray $A[i..j]$ can collapse into.
- Base cases: $\text{vals}[i][i] = \{A[i]\}$ for all $0 \le i < N$.
- Transitions for length $L = j - i + 1 \ge 2$:
  1. **Type-1 Merge (two equal halves):** If there exists a split point $k \in [i, j-1]$ such that both $A[i..k]$ and $A[k+1..j]$ can collapse to the same value $v$, then the concatenated collapsed values $[v, v]$ form a palindrome of length 2, which collapses to $v + 1$.
  2. **Type-2 Merge (matching endpoints with collapsible interior):** If there exists an interior range $[k_1, k_2]$ with $i < k_1 \le k_2 < j$ such that $A[i..k_1-1]$ collapses to $v$, $A[k_1..k_2]$ collapses to some value $w$, and $A[k_2+1..j]$ collapses to $v$, then the sequence of collapsed values $[v, w, v]$ forms an odd-length palindrome, which collapses to $v + 1$.

To optimize the Type-2 check from $O(N^4)$ to $O(N^3)$, maintain prefix reachability table $\text{left\_values}[i][m]$ containing all values $v \in \text{vals}[i][k]$ for $k < m$ such that $\text{vals}[k+1][m]$ is non-empty. Then for any $v \in \text{vals}[m+1][j]$, if $v \in \text{left\_values}[i][m]$, $v + 1$ is added to $\text{vals}[i][j]$.

### 2. Outer Interval DP: Maximum Palindromic Tiling

Next, compute $\text{max\_blocks}[i][j]$, the maximum number of blocks in any palindromic tiling of $A[i..j]$.
- Base cases: $\text{max\_blocks}[i][i] = 1$ for all $0 \le i < N$.
- If $\text{vals}[i][j]$ is non-empty, the entire subarray can collapse to 1 block ($K = 1$ baseline), so $\text{max\_blocks}[i][j] \ge 1$.
- For $K \ge 2$, a palindromic tiling must have its outermost left block $A[i..k_1]$ and outermost right block $A[k_2+1..j]$ collapse to the same value $v$.
  - If $k_1 = k_2$ (no interior elements), the two blocks adjacent to each other yield $K = 2$.
  - If $k_1 < k_2$, the interior subarray $A[k_1+1..k_2]$ must itself admit a valid palindromic tiling of length $I = \text{max\_blocks}[k_1+1][k_2] > 0$, contributing $2 + I$ blocks.
- To compute this efficiently in $O(N^3)$, maintain $\text{left\_inner}[i][k_2][v]$, storing the maximum inner block count among all valid left blocks $A[i..k_1]$ collapsing to $v$ (with $0$ if $k_1 = k_2$, and $\text{max\_blocks}[k_1+1][k_2]$ if $k_1 < k_2$).
- Then for each right block $A[k_2+1..j]$ collapsing to $v$, update $\text{max\_blocks}[i][j] = \max(\text{max\_blocks}[i][j], 2 + \text{left\_inner}[i][k_2][v])$.

The final answer is $\text{max\_blocks}[0][N-1]$.

## Complexity

- **Time Complexity:** $O(N^3 \log N)$. There are $O(N^2)$ intervals. For each interval, iterating over split points takes $O(N)$ operations with small set operations. Given $N \le 100$, the total number of operations is well within the 5000ms time limit.
- **Space Complexity:** $O(N^2 \log N)$ to store the DP tables `vals`, `left_values`, `max_blocks`, and `left_inner`.

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
