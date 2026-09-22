# XOR Oracle: Reconstruct the Hidden Set

**Difficulty:** Easy  
**Category:** Algorithmic Paradigms, String  
**Tags:** interactive, bitmasking, trie

## Problem

A hidden set $A$ contains $N$ distinct non-negative integers, where each element satisfies $0 <= A_i < 2^{30}$. Your task is to determine every element of $A$ by interacting with an oracle.

In each query, you choose an integer $X$ ($0 <= X < 2^{30}$). The oracle computes the bitwise XOR of $X$ with every element of $A$ and returns the maximum result:

$$Q(X) = \max_{y \in A} (y \oplus X)$$

You must recover all $N$ elements of $A$ using at most 13000 queries.

## Input Format

The interaction begins with the oracle sending a single JSON object via standard input:

```json
{"n": 3}
```

- `n` (integer): the number of elements in the hidden set $A$, with $1 <= n <= 400$.

## Output Format

During the interaction, write query objects to standard output:

```json
{"type": "query", "x": 7}
```

- `type` (string): must be `"query"`.
- `x` (integer): chosen query value satisfying $0 <= x < 2^{30}$.

The oracle replies with one JSON object on standard input:

```json
{"res": 7}
```

- `res` (integer): the oracle response $Q(x) = \max_{y \in A} (y \oplus x)$.

Once all $N$ elements are determined, submit them as:

```json
{"type": "answer", "value": [7, 0, 2]}
```

- `type` (string): must be `"answer"`.
- `value` (array of integers): exactly $N$ distinct integers in any order representing every element of $A$.

Submitting the answer terminates the interaction. Standard output must be flushed after every message.

## Constraints

- $1 <= N <= 400$
- $0 <= A_i < 2^{30}$ for all $i$; all elements are distinct
- $0 <= X < 2^{30}$ for all queries
- At most 13000 total queries (the final answer submission does not count towards the query limit)
- Time limit: 5000 ms
- Memory limit: 256 MB

## Examples

### Example 1

**Input**

```json
{
  "n": 2,
  "a": [1, 2]
}
```

**Output**

```json
[1, 2]
```

**Explanation**

Hidden set: $A = \{1, 2\}$.

Interaction trace:
1. Oracle -> Solver: `{"n": 2}`
2. Solver -> Oracle: `{"type": "query", "x": 0}`
3. Oracle -> Solver: `{"res": 2}`. Query $X = 0$ yields $Q(0) = \max(1 \oplus 0, 2 \oplus 0) = 2$. Recover element $y = 2 \oplus 0 = 2$.
4. Solver -> Oracle: `{"type": "query", "x": 2}`
5. Oracle -> Solver: `{"res": 3}`. Query $X = 2$ yields $Q(2) = \max(1 \oplus 2, 2 \oplus 2) = \max(3, 0) = 3$. Recover element $y = 3 \oplus 2 = 1$.
6. Solver -> Oracle: `{"type": "answer", "value": [1, 2]}`. Both elements are recovered within 2 queries.

### Example 2

**Input**

```json
{
  "n": 1,
  "a": [13]
}
```

**Output**

```json
[13]
```

**Explanation**

Hidden set: $A = \{13\}$.

Interaction trace:
1. Oracle -> Solver: `{"n": 1}`
2. Solver -> Oracle: `{"type": "query", "x": 0}` (or any $X$)
3. Oracle -> Solver: `{"res": 13}`. For $N = 1$, any query $X$ directly reveals the single element as $y = Q(X) \oplus X$.
4. Solver -> Oracle: `{"type": "answer", "value": [13]}`. Finished in 1 query.

### Example 3

**Input**

```json
{
  "n": 3,
  "a": [0, 2, 7]
}
```

**Output**

```json
[0, 2, 7]
```

**Explanation**

Hidden set: $A = \{0, 2, 7\}$.

Interaction trace:
1. Oracle -> Solver: `{"n": 3}`
2. Query $X = 0$ -> response $Q(0) = 7$. Recover $y = 7 \oplus 0 = 7$. Known: $\{7\}$.
3. Query $X = 7$ -> response $Q(7) = 7$. Recover $y = 7 \oplus 7 = 0$. Known: $\{7, 0\}$.
4. Query $X = 4$ -> response $Q(4) = 6$. Recover $y = 6 \oplus 4 = 2$. Known: $\{7, 0, 2\}$.
5. All 3 elements are known; submit `{"type": "answer", "value": [0, 2, 7]}`.

## Approach

1. **Bootstrap with $X = 0$**:  
   Because $y \oplus 0 = y$ for every integer $y$, querying $X = 0$ returns $Q(0) = \max_{y \in A} y$. This reveals the largest element of $A$ in a single query. We insert this element into our set of known elements and into a binary Trie.

2. **Element Recovery Invariant**:  
   For any query $X$, the response is $R = Q(X) = y^* \oplus X$, where $y^* \in A$ is the element achieving the maximum XOR sum. Thus, the maximizing element can be recovered as $y^* = R \oplus X$.

3. **Bit-Complement Mask Probing**:  
   To test whether any element of $A$ has a specific prefix $p$ from bit 29 down to bit depth $d$:
   - Construct a mask covering bits 29 down to $d$:
     $$\text{mask} = ((1 \ll (30 - d)) - 1) \ll d$$
   - Invert prefix $p$ over the masked bits:
     $$X = (\sim p) \ \& \ \text{mask}$$
   - For any candidate $y$, $(y \oplus X) \ \& \ \text{mask} == \text{mask}$ if and only if $y$ matches prefix $p$ at all bits from 29 down to $d$.
   - If any such element exists in $A$, $Q(X) \ \& \ \text{mask} == \text{mask}$. Furthermore, the element $y^* = Q(X) \oplus X$ is an element of $A$ that belongs to this prefix branch.

4. **Trie-Guided DFS**:  
   Maintain a binary Trie containing all currently known elements. Traverse prefix branches from depth 29 down to 0:
   - For each child bit $b \in \{0, 1\}$, form the candidate prefix.
   - If the candidate prefix is already present in the Trie, recurse directly without issuing a query.
   - If the candidate prefix is not in the Trie, issue a probe with $X = (\sim \text{prefix}) \ \& \ \text{mask}$.
     - If the prefix is confirmed, insert the recovered element $y^* = Q(X) \oplus X$ into the Trie and recurse.
     - Otherwise, no element in $A$ has this prefix, so prune the entire branch.
   - If at any point the number of discovered elements equals $N$, terminate the search immediately.

5. **Query Efficiency**:  
   Each internal node in the Trie branches at most once into an unexplored path. With $N <= 400$ elements and 30 bit levels, the Trie contains at most $N \cdot 30 = 12000$ edges. Thus, at most 12000 probe queries plus 1 bootstrap query ($<= 12001$ total) are performed, staying well within the 13000 query budget.

## Complexity

**Time:** $O(N \cdot B)$ where $N <= 400$ and $B = 30$ bits.  
**Space:** $O(N \cdot B)$ for storing the binary Trie and discovered elements.

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py)
