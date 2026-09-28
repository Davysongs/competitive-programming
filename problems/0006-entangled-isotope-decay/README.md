# Entangled Isotope Decay

**Difficulty:** Very Hard
**Category:** Data Structures, Graph Theory, Greedy
**Tags:** `exchange-argument`, `priority-queue`, `priority-queue-greedy`, `tree`

## Problem

You are managing the stabilization process of a volatile radioactive core modeled as a rooted tree structure. The core consists of $N$ isotopes, labeled from $1$ to $N$, with isotope $1$ being the root. The parent-child relationships in the tree represent physical dependencies: a child isotope can only be removed after its parent has been removed.

Each isotope $i$ is characterized by two properties:

1. **Alpha Emission ($\text{alpha}_i$)**: The amount of radiation released into the environment when this isotope is removed.
2. **Beta Sensitivity ($\text{beta}_i$)**: A coefficient representing how much the isotope destabilizes due to the background radiation accumulated before its removal.

The process occurs in $N$ sequential steps. In each step, you select one available isotope (one whose parent has already been removed, or the root) and remove it.

Let the sequence of removal be $s_1, s_2, \ldots, s_N$.

The **Instability Cost** for removing the isotope at step $i$ (which is isotope $s_i$) is calculated as:

$$Cost_i = \text{beta}_{s_i} \times \left( \sum_{j < i} \text{alpha}_{s_j} \right)$$

Your objective is to determine a valid removal sequence that **minimizes** the Total Instability Cost, defined as:

$$\text{Total Cost} = \sum_{i=1}^{N} Cost_i$$

## Input Format

The input is a JSON object with the following fields:

- `N` (integer): The number of isotopes.
- `alpha` (array of integers): Array of length $N$ where `alpha[i]` is the alpha emission of isotope $i+1$ (0-indexed, so `alpha[0]` is for isotope 1, `alpha[1]` for isotope 2, etc.).
- `beta` (array of integers): Array of length $N$ where `beta[i]` is the beta sensitivity of isotope $i+1$ (0-indexed, matching `alpha`).
- `edges` (array of arrays): Array of $N-1$ pairs `[u, v]` where $u$ is the parent of $v$ ($1 \le u, v \le N$).

Example input:
```json
{
  "N": 3,
  "alpha": [10, 10, 10],
  "beta": [1, 100, 100],
  "edges": [
    [1, 2],
    [1, 3]
  ]
}
```

## Output Format

A JSON integer value representing the minimum total instability cost.

Example output:
```json
3000
```

## Constraints

- $1 \le N \le 200{,}000$
- $1 \le \text{alpha}_i \le 10^9$ for all $i$
- $1 \le \text{beta}_i \le 10^9$ for all $i$
- The edges form a valid rooted tree with node 1 as root ($u$ is the parent of $v$).
- The answer can be very large (up to approximately $2 \times 10^{28}$). Solutions must use big-integer arithmetic.
- Time limit: 30000ms
- Memory limit: 256MB

## Examples

### Example 1

Input:
```json
{
  "N": 3,
  "alpha": [10, 10, 10],
  "beta": [1, 100, 100],
  "edges": [
    [1, 2],
    [1, 3]
  ]
}
```

Output:
```json
3000
```

Explanation:

Isotope 1 is the root and must be removed first.
- Step 1: Remove isotope 1. Accumulated radiation before removal is 0. Cost = $1 \times 0 = 0$. Accumulated radiation becomes 10.
- Step 2: Both isotopes 2 and 3 are now available. Removing isotope 2 costs $100 \times 10 = 1000$. Accumulated radiation becomes 20.
- Step 3: Removing isotope 3 costs $100 \times 20 = 2000$.

Total cost = $0 + 1000 + 2000 = 3000$.

### Example 2

Input:
```json
{
  "N": 3,
  "alpha": [100, 1, 1],
  "beta": [1, 100, 100],
  "edges": [
    [1, 2],
    [2, 3]
  ]
}
```

Output:
```json
20100
```

Explanation:

The tree is a directed chain $1 \to 2 \to 3$. Precedence forces the sequence $[1, 2, 3]$.
- Step 1: Remove isotope 1. Cost = $1 \times 0 = 0$. Accumulated alpha is 100.
- Step 2: Remove isotope 2. Cost = $100 \times 100 = 10000$. Accumulated alpha is 101.
- Step 3: Remove isotope 3. Cost = $100 \times 101 = 10100$.

Total cost = $0 + 10000 + 10100 = 20100$.

### Example 3

Input:
```json
{
  "N": 4,
  "alpha": [10, 20, 20, 20],
  "beta": [1, 100, 100, 1],
  "edges": [
    [1, 2],
    [1, 3],
    [3, 4]
  ]
}
```

Output:
```json
4050
```

Explanation:

Isotope 1 is the root. Isotopes 2 and 3 are children of 1, and 4 is a child of 3.
Comparing isotopes 2 and 3: both have beta/alpha ratio $100 / 20 = 5$. Removing isotope 2 before 3 yields:
- Isotope 1: cost 0 (alpha = 10)
- Isotope 2: cost $100 \times 10 = 1000$ (alpha = 30)
- Isotope 3: cost $100 \times 30 = 3000$ (alpha = 50)
- Isotope 4: cost $1 \times 50 = 50$ (alpha = 70)

Total cost = $0 + 1000 + 3000 + 50 = 4050$.

## Approach

### 1. Exchange Argument

Consider two adjacent contiguous blocks of elements $A$ and $B$ in the removal order, with aggregate alpha emissions $\alpha(A), \alpha(B)$ and beta sensitivities $\beta(A), \beta(B)$.

- If $A$ is scheduled before $B$, the interaction cost between them is $\alpha(A) \times \beta(B)$.
- If $B$ is scheduled before $A$, the interaction cost between them is $\alpha(B) \times \beta(A)$.

Scheduling $A$ before $B$ is strictly optimal if:
$$\alpha(A) \times \beta(B) < \alpha(B) \times \beta(A) \iff \frac{\beta(A)}{\alpha(A)} > \frac{\beta(B)}{\alpha(B)}$$

Hence, nodes or compound blocks with a higher ratio $\beta / \alpha$ must be executed earlier whenever precedence constraints allow.

### 2. Tree Contraction Property

Let $u \neq 1$ be a non-root node with the globally maximum ratio $\beta_u / \alpha_u$.
Because its ratio is maximal, as soon as its parent $p$ is removed, no other node in the tree can yield a better cost reduction than $u$. Thus, $u$ must be removed immediately after $p$.

We can contract $u$ into $p$, forming a combined super-node $(p \circ u)$ with:
$$\alpha(p \circ u) = \alpha(p) + \alpha(u)$$
$$\beta(p \circ u) = \beta(p) + \beta(u)$$

The merge incurs an immediate cross cost of $\alpha(p) \times \beta(u)$ added to the running total.

### 3. Algorithm with Priority Queue and DSU

1. Maintain compound nodes using a Disjoint Set Union (DSU) data structure with iterative path compression.
2. Initialize a max-priority queue containing all non-root nodes $2, \ldots, N$, ordered by the ratio $\beta / \alpha$.
3. To eliminate floating-point precision issues, order entries using integer cross-multiplication:
   $$\beta_1 \times \alpha_2 > \beta_2 \times \alpha_1$$
4. Repeatedly pop the highest-ratio node $u$ from the heap:
   - If the heap entry is stale (superseded by a later update or already merged), discard it.
   - Find the DSU representative $u_{\text{rep}}$ of $u$.
   - Find the parent $p$ of $u_{\text{rep}}$ in the contraction tree and its DSU representative $p_{\text{rep}}$.
   - Accumulate cross cost $\alpha(p_{\text{rep}}) \times \beta(u_{\text{rep}})$.
   - Merge $u_{\text{rep}}$ into $p_{\text{rep}}$ by updating cumulative alpha, beta, and DSU parent pointers.
   - If $p_{\text{rep}}$ is not the root node 1, increment its version counter and push it back into the priority queue with its new aggregate ratio.
5. Once all $N-1$ non-root nodes have been merged into the root, return the accumulated total cost.

## Complexity

- **Time Complexity:** $O(N \log N)$. Each contraction reduces the number of active super-nodes by 1, performing at most $N-1$ merges. Each merge executes $O(1)$ DSU operations and at most one priority queue push. The priority queue size is at most $2N$.
- **Space Complexity:** $O(N)$ auxiliary space for DSU arrays, parent pointers, alpha/beta sums, version tables, and heap entries.

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
