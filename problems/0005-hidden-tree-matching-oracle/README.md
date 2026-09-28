# Hidden Tree Matching Oracle

**Difficulty:** Expert
**Category:** Algorithmic Paradigms, Graph Theory
**Tags:** `interactive`, `binary-search`, `tree`

## Problem

This is an **interactive problem**.

You are tasked with discovering the topology of a hidden communications network. The network consists of $N$ nodes labelled from $1$ to $N$. The network topology is guaranteed to be a **tree** (a connected acyclic undirected graph with exactly $N - 1$ edges).

You do not know the edges of the tree initially. To uncover them, you can query an oracle with subsets of nodes.

A **maximum matching** in an undirected graph is a largest set of pairwise non-adjacent edges (no two edges share an endpoint).

In a single query, you choose a non-empty subset of nodes $S \subseteq \{1, 2, \dots, N\}$. The oracle returns the **size of the maximum matching** in the induced subgraph $G[S]$. The induced subgraph $G[S]$ consists of the nodes in $S$ and all edges of the hidden tree whose both endpoints lie in $S$.

Your goal is to determine all $N - 1$ edges of the hidden tree using at most $12{,}000$ queries.

## Input Format

The interaction begins with the judge sending a single JSON object via standard input:

```text
{"N": 3}
```

- `N` (integer): number of nodes in the hidden tree, where $2 <= N <= 200$.

## Output Format

During the interaction, write query objects to standard output:

```text
{"type": "query", "S": [1, 2, 3]}
```

- `type` (string): must be `"query"`.
- `S` (array of integers): a non-empty list of distinct node labels from $1$ to $N$.

The judge responds with one JSON object on standard input:

```text
{"matching_size": 1}
```

- `matching_size` (integer): the size of a maximum matching in the induced subgraph $G[S]$.

When all $N - 1$ edges are determined, submit the final answer:

```text
{"type": "answer", "value": [[1, 2], [2, 3]]}
```

- `type` (string): must be `"answer"`.
- `value` (array of pairs): exactly $N - 1$ edges of the hidden tree.
- Each edge must be `[u, v]` with $u < v$.
- Edges must be sorted in ascending lexicographic order.

Submitting the answer terminates the interaction. Standard output must be flushed after every message.

## Constraints

- $2 <= N <= 200$
- $S$ must be a non-empty list of distinct integers in $[1, N]$
- Maximum number of queries: $12000$
- Time limit: 20000ms
- Memory limit: 256MB

## Examples

### Example 1

**Input**

```json
{
  "n": 3,
  "edges": [
    [
      1,
      2
    ],
    [
      2,
      3
    ]
  ]
}
```

**Output**

```json
[
  [
    1,
    2
  ],
  [
    2,
    3
  ]
]
```

**Explanation**

The hidden tree is a path $1 - 2 - 3$ on $N = 3$ nodes.

Interaction trace:
1. Judge sends initial state: `{"N": 3}`.
2. Solution queries $S = [1, 2, 3]$: `{"type": "query", "S": [1, 2, 3]}`.
3. Judge responds: `{"matching_size": 1}`. Both $(1, 2)$ and $(2, 3)$ share node 2, so maximum matching size is 1. This confirms at least one edge exists among $\{1, 2, 3\}$.
4. Solution queries $S = [1, 3]$: `{"type": "query", "S": [1, 3]}`.
5. Judge responds: `{"matching_size": 0}`. Nodes 1 and 3 are not adjacent.
6. Solution queries $S = [1, 2]$: `{"type": "query", "S": [1, 2]}`.
7. Judge responds: `{"matching_size": 1}`. Edge $(1, 2)$ is confirmed.
8. Solution queries $S = [2, 3]$: `{"type": "query", "S": [2, 3]}`.
9. Judge responds: `{"matching_size": 1}`. Edge $(2, 3)$ is confirmed.
10. Solution outputs the answer: `{"type": "answer", "value": [[1, 2], [2, 3]]}`.

### Example 2

**Input**

```json
{
  "n": 4,
  "edges": [
    [
      1,
      2
    ],
    [
      1,
      3
    ],
    [
      1,
      4
    ]
  ]
}
```

**Output**

```json
[
  [
    1,
    2
  ],
  [
    1,
    3
  ],
  [
    1,
    4
  ]
]
```

**Explanation**

The hidden tree is a star on $N = 4$ nodes with center node 1 and leaf nodes 2, 3, 4.

Interaction trace:
1. Judge sends: `{"N": 4}`.
2. Any query containing center node 1 and at least one leaf returns `matching_size: 1`, while any subset of leaves $\{2, 3, 4\}$ returns `matching_size: 0`.
3. Binary search isolates edges $(1, 2)$, $(1, 3)$, and $(1, 4)$.
4. Solution outputs: `{"type": "answer", "value": [[1, 2], [1, 3], [1, 4]]}`.

## Approach

1. **Known Forest and Bipartite Colorings**:
   At any point during the reconstruction, the set of currently discovered edges forms a spanning forest on the $N$ nodes. Because every tree and forest is bipartite, each connected component can be 2-colored into two independent sets, say black and white. If a query set $S$ contains at most one color class from each component, no already known edge can appear in $G[S]$.

2. **Deterministic Component Exposure Codes**:
   To discover an unknown edge between two different components, we need a query set $S$ that includes both endpoints of that edge.
   Assign each component an index $i$ and a binary code $C_i$ of length 16 with exactly 8 ones, where bit 0 is always 1 and the other 7 ones are chosen from positions 1 to 15 in lexicographic order.
   For any two distinct component codes $C_A$ and $C_B$, their intersection size $I$ satisfies $1 <= I <= 7$. Because both have weight 8, all four bit pairs $(0,0)$, $(0,1)$, $(1,0)$, and $(1,1)$ appear at least once across the 16 positions.
   Therefore, across the 16 template queries, every combination of color classes between any two components is queried. If any edge exists between two components, at least one of the 16 templates will produce `matching_size > 0`.

3. **Binary Search Edge Isolation**:
   When `query(S) > 0`, $G[S]$ contains at least one unknown edge. We isolate one edge $(u, v)$ using divide-and-conquer:
   - Split $S$ into two halves $L$ and $R$.
   - If `query(L) > 0`, recurse on $L$.
   - If `query(R) > 0`, recurse on $R$.
   - Otherwise, the edge must cross between $L$ and $R$.
   - Binary search in $L$ to find node $u \in L$ that has a neighbor in $R$ (by testing `query(L_half + R) > 0`).
   - Binary search in $R$ to find node $v \in R$ adjacent to $u$ (by testing `query([u] + R_half) > 0`).
   Each edge isolation requires $O(\log |S|)$ queries.

4. **Iterative Forest Assembly**:
   Add the isolated edge $(u, v)$ to the discovered forest. Repeat this process until all $N - 1$ edges are found.
   Sort the discovered edges canonically and output the final answer.

## Complexity

Let $N$ be the number of nodes in the hidden tree ($N <= 200$).

- **Query Complexity:** Each of the $N - 1$ edges is exposed in at most 16 template queries and isolated in $O(\log N)$ binary search queries. Total queries are at most $16(N - 1) + 2(N - 1)\lceil\log_2 N\rceil <= 6368$, well within the 12,000 query budget.
- **Time Complexity:** $O(N^2)$ local computation from BFS recoloring and component maintenance, taking less than 100ms.
- **Space Complexity:** $O(N)$ to store adjacency lists, component assignments, and binary codes.

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
