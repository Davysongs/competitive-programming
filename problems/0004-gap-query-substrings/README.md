# Gap-Query Substrings

**Difficulty:** Easy
**Category:** String, Algorithmic Paradigms
**Tags:** `suffix-structures`, `sorting`

## Problem

Given a string $s$ of length $n$ over lowercase English letters and a list of non-negative integers called `queries`, answer each query independently.

For a query value $g$, a substring of $s$ is called **$g$-good** if there exist two occurrences $[l_1, r_1]$ and $[l_2, r_2]$ (1-based indices with $r_1 \le r_2$) such that $l_2 \ge r_1 + 1 + g$. That is, there are at least $g$ characters strictly between the end of the first occurrence and the start of the second occurrence.

When $g = 0$, this corresponds to the standard non-overlapping condition where the two occurrences share no positions. For $g \ge 1$, the two occurrences must be separated by at least $g$ unused characters.

For each query $g$, determine the number of distinct $g$-good substrings of $s$.

All queries are answered against the same string $s$.

## Input Format

The input is a JSON object with two fields:

- `s` (string): the input string of length $n$.
- `queries` (array of integers): the list of gap values to answer.

Example input:
```json
{
  "s": "aaaa",
  "queries": [0, 1, 2, 3]
}
```

## Output Format

A JSON array of integers, one count per query in the same order as `queries`.

Example output:
```json
[2, 1, 1, 0]
```

## Constraints

- $1 \le |s| \le 200{,}000$
- $1 \le |\text{queries}| \le 10$
- $0 \le \text{queries}[i] < |s|$ for all $i$
- $s$ consists only of lowercase English letters
- Time limit: 5000ms
- Memory limit: 256MB

## Examples

### Example 1

Input:
```json
{
  "s": "aaaa",
  "queries": [0, 1, 2, 3]
}
```

Output:
```json
[2, 1, 1, 0]
```

Explanation:

The string `"aaaa"` has 4 distinct substrings: `"a"`, `"aa"`, `"aaa"`, `"aaaa"`.

For a substring of length $L$ with two occurrences ending at 1-based positions $r_1$ and $r_2$ (with $r_2 > r_1$), the second occurrence starts at $l_2 = r_2 - L + 1$. The $g$-good condition $l_2 \ge r_1 + 1 + g$ simplifies to $r_2 - r_1 \ge L + g$.
Therefore, a substring satisfies the condition if and only if the spread between its maximum and minimum end positions, $d = \max(\text{end positions}) - \min(\text{end positions})$, satisfies $d \ge L + g$.

- Substring `"a"` ($L = 1$): end positions are 1, 2, 3, 4. Spread $d = 4 - 1 = 3$.
  - $g = 0$: $3 \ge 1 + 0 \implies$ yes.
  - $g = 1$: $3 \ge 1 + 1 \implies$ yes.
  - $g = 2$: $3 \ge 1 + 2 \implies$ yes.
  - $g = 3$: $3 \ge 1 + 3 \implies$ no.
- Substring `"aa"` ($L = 2$): end positions are 2, 3, 4. Spread $d = 4 - 2 = 2$.
  - $g = 0$: $2 \ge 2 + 0 \implies$ yes.
  - $g = 1$: $2 \ge 2 + 1 \implies$ no.
  - $g = 2$: $2 \ge 2 + 2 \implies$ no.
  - $g = 3$: $2 \ge 2 + 3 \implies$ no.
- Substring `"aaa"` ($L = 3$): end positions are 3, 4. Spread $d = 4 - 3 = 1$.
  - $g = 0$: $1 \ge 3 + 0 \implies$ no.
- Substring `"aaaa"` ($L = 4$): only one occurrence, never $g$-good.

Summary counts: $g=0 \to 2$, $g=1 \to 1$, $g=2 \to 1$, $g=3 \to 0$.

### Example 2

Input:
```json
{
  "s": "abcabc",
  "queries": [0, 1, 2, 3]
}
```

Output:
```json
[6, 5, 3, 0]
```

Explanation:

The repeated substrings in `"abcabc"` are `"a"`, `"b"`, `"c"`, `"ab"`, `"bc"`, `"abc"`, all having end-position spread $d = 3$.
- $g = 0$ ($d \ge L$): `"a"` ($3 \ge 1$), `"b"` ($3 \ge 1$), `"c"` ($3 \ge 1$), `"ab"` ($3 \ge 2$), `"bc"` ($3 \ge 2$), `"abc"` ($3 \ge 3$) all qualify (total: 6).
- $g = 1$ ($d \ge L + 1$): all except `"abc"` qualify (total: 5).
- $g = 2$ ($d \ge L + 2$): only `"a"`, `"b"`, `"c"` qualify (total: 3).
- $g = 3$ ($d \ge L + 3$): none qualify (total: 0).

### Example 3

Input:
```json
{
  "s": "abab",
  "queries": [0, 1, 2]
}
```

Output:
```json
[3, 2, 0]
```

Explanation:

Repeated substrings are `"a"` ($L=1, d=2$), `"b"` ($L=1, d=2$), `"ab"` ($L=2, d=2$).
- $g = 0$: all 3 qualify ($d \ge L$).
- $g = 1$: `"a"` and `"b"` qualify ($2 \ge 2$), but `"ab"` fails ($2 < 3$).
- $g = 2$: none qualify ($2 < 1 + 2$).

## Approach

1. **Equivalence Classes and Suffix Automaton**:
   Every distinct substring of $s$ corresponds to a unique state in the Suffix Automaton (SAM) of $s$. A SAM state $v$ represents an equivalence class of substrings that share identical end-position sets (`endpos`).
   The lengths of substrings in state $v$ form a contiguous interval $[\text{len}(\text{link}(v)) + 1, \text{len}(v)]$.

2. **End-Position Spread**:
   For any substring with occurrences ending at $r_1 < r_2 < \dots < r_k$, the existence of two occurrences separated by at least $g$ characters ($l_2 \ge r_1 + 1 + g$) is maximized by picking the earliest occurrence $r_{\min}$ and the latest occurrence $r_{\max}$.
   The condition simplifies to:
   $$r_{\max} - r_{\min} \ge L + g \iff L \le (r_{\max} - r_{\min}) - g$$
   Since all substrings in state $v$ share the exact same set of end positions, they all share the exact same spread $d(v) = \max(\text{endpos}(v)) - \min(\text{endpos}(v))$.

3. **Bottom-Up Propagation on the Link Tree**:
   - Direct occurrences of prefixes are marked during SAM construction: state $v$ corresponding to prefix $s[1..i]$ starts with $\min(v) = \max(v) = i$. Cloned states start with no direct occurrences.
   - States are sorted descending by length (topological order from leaves to root in the suffix link tree).
   - For each state $v$ with suffix link $p = \text{link}(v)$, update:
     $$\min(p) = \min(\min(p), \min(v))$$
     $$\max(p) = \max(\max(p), \max(v))$$

4. **Answering Queries**:
   For a state $v$ with length range $[\text{lo}, \text{hi}]$ and spread $d$, a length $L \in [\text{lo}, \text{hi}]$ is $g$-good if and only if $L \le d - g$.
   The number of qualifying substrings from state $v$ is:
   $$\max(0, \min(\text{hi}, d - g) - \text{lo} + 1)$$
   Summing this quantity over all states $v \neq 0$ answers query $g$ in $O(|\text{states}|)$ time.

## Complexity

Let $n = |s|$ and $Q = |\text{queries}|$. The alphabet size is $|\Sigma| = 26$.

- **Time Complexity:**
  - Suffix Automaton construction: $O(n \cdot |\Sigma|)$.
  - End-position propagation: O(n log n) because states are ordered with comparison sorting.
  - Query processing: O(Q \cdot n) since there are at most 2n - 1 states in the automaton.
  - Total Time: O(n log n + Q \cdot n). With n \le 200{,}000 and Q \le 10, this finishes well within the 5000ms time limit.

- **Space Complexity:**
  - $O(n \cdot |\Sigma|)$ to store the suffix automaton transitions, links, and length intervals.

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
