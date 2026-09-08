# Lexicographic Rank Sum Queries

**Difficulty:** Easy  
**Category:** Strings  
**Tags:** `suffix-automaton`, `lexicographic-order`

## Problem

Given a string $s$ of length $n$ over lowercase English letters, the **lexicographic order** of all distinct non-empty substrings of $s$ induces a ranking: the lexicographically smallest substring receives rank $1$, the second-smallest receives rank $2$, and so on.

Formally, for each distinct non-empty substring $x$ of $s$, define:

$$\text{rank}(x) = 1 + |\{y : y \text{ is a distinct non-empty substring of } s,\ y < x \text{ lexicographically}\}|$$

Given $q$ query strings $t_1, t_2, \ldots, t_q$, answer each query independently. For query string $t_i$, compute:

- $\text{count}_i$ = the number of distinct non-empty substrings of $s$ that are lexicographically $\leq t_i$
- $\text{sum}_i$ = the sum of $\text{rank}(x)$ over all distinct non-empty substrings $x$ of $s$ with $x \leq t_i$, modulo $10^9 + 7$

Note: the query string $t_i$ need not itself be a substring of $s$.

Output the pair $[\text{count}_i,\ \text{sum}_i]$ for each query $i$.

## Input Format

The input is a JSON object with two fields:

- `s` (string): the main string of length $n$
- `queries` (array of strings): $q$ query strings

Example input:
```json
{
  "s": "abc",
  "queries": ["b"]
}
```

## Output Format

A JSON array of $q$ pairs. The $i$-th pair is $[\text{count}_i,\ \text{sum}_i \bmod (10^9+7)]$.

Example output:
```json
[[4, 10]]
```

## Constraints

- $1 \leq |s| \leq 200{,}000$
- $1 \leq q \leq 200{,}000$
- $1 \leq |t_i| \leq 200{,}000$ for each query
- Sum of all $|t_i| \leq 200{,}000$
- All strings consist of lowercase English letters only
- Time limit: 4000ms
- Memory limit: 256MB

## Examples

### Example 1

**Input:**
```json
{
  "s": "abc",
  "queries": ["b"]
}
```

**Output:**
```json
[[4, 10]]
```

**Explanation:**

The distinct non-empty substrings of `"abc"` in sorted order are:

| Rank | Substring |
|------|-----------|
| 1    | `a`       |
| 2    | `ab`      |
| 3    | `abc`     |
| 4    | `b`       |
| 5    | `bc`      |
| 6    | `c`       |

For query `"b"`, we need all distinct substrings lexicographically $\leq$ `"b"`.

Step 1: Substrings starting with characters less than `b`. Only character `a` qualifies. Substrings starting with `a`: `a` (rank 1), `ab` (rank 2), `abc` (rank 3). Count so far: 3. Rank sum so far: $1 + 2 + 3 = 6$.

Step 2: Substrings starting with `b` that are $\leq$ `"b"`. The substring `b` itself (rank 4) equals the query, so it qualifies. The substring `bc` (rank 5) does not qualify since `"bc" > "b"`.

Step 3: Characters beyond `b` are all lexicographically greater, so no more substrings qualify.

Final result: $\text{count} = 3 + 1 = 4$, $\text{sum} = 6 + 4 = 10$.

### Example 2

**Input:**
```json
{
  "s": "aab",
  "queries": ["ab", "b", "a"]
}
```

**Output:**
```json
[[4, 10], [5, 15], [1, 1]]
```

**Explanation:**

The distinct non-empty substrings of `"aab"` in sorted order are:

| Rank | Substring |
|------|-----------|
| 1    | `a`       |
| 2    | `aa`      |
| 3    | `aab`     |
| 4    | `ab`      |
| 5    | `b`       |

**Query `"ab"`:**

Step 1: No characters come before `a`, so no entire character groups are skipped.

Step 2: The prefix `"a"` matches a substring of `s`. It has rank 1. Count so far: 1, sum so far: 1.

Step 3: Among substrings of `s` that start with `"a"`, consider the second character. Substrings `"aa"` (rank 2) and `"aab"` (rank 3) both have second character `a`, and since `a < b`, all substrings in this group are $\leq$ `"ab"`. That adds 2 substrings. Count so far: $1 + 2 = 3$, sum so far: $1 + 2 + 3 = 6$.

Step 4: The prefix `"ab"` matches a substring of `s`. It has rank 4. Count: $3 + 1 = 4$, sum: $6 + 4 = 10$.

Final result: $[\text{count}, \text{sum}] = [4, 10]$.

**Query `"b"`:**

Step 1: Substrings starting with characters less than `b`. Character `a` qualifies. The substrings starting with `a` are: `a` (rank 1), `aa` (rank 2), `aab` (rank 3), `ab` (rank 4). That gives 4 substrings with rank sum $1 + 2 + 3 + 4 = 10$. Count so far: 4, sum so far: 10.

Step 2: The prefix `"b"` matches a substring of `s`. It has rank 5. Count: $4 + 1 = 5$, sum: $10 + 5 = 15$.

Final result: $[\text{count}, \text{sum}] = [5, 15]$.

**Query `"a"`:**

Step 1: No characters come before `a`, so no character groups are skipped.

Step 2: The prefix `"a"` matches a substring of `s`. It has rank 1. The query string is now exhausted. Count: 1, sum: 1.

Final result: $[\text{count}, \text{sum}] = [1, 1]$.

### Example 3

**Input:**
```json
{
  "s": "banana",
  "queries": ["nana"]
}
```

**Output:**
```json
[[15, 120]]
```

**Explanation:**

The string `"banana"` has 15 distinct non-empty substrings. In sorted order:

| Rank | Substring |
|------|-----------|
| 1    | `a`       |
| 2    | `an`      |
| 3    | `ana`     |
| 4    | `anan`    |
| 5    | `anana`   |
| 6    | `b`       |
| 7    | `ba`      |
| 8    | `ban`     |
| 9    | `bana`    |
| 10   | `banan`   |
| 11   | `banana`  |
| 12   | `n`       |
| 13   | `na`      |
| 14   | `nan`     |
| 15   | `nana`    |

All 15 substrings are lexicographically $\leq$ `"nana"`:

Step 1: Substrings starting with `a` (ranks 1 through 5) are all less than `"nana"` since `a < n`. Count so far: 5, sum so far: $1+2+3+4+5 = 15$.

Step 2: Substrings starting with `b` (ranks 6 through 11) are all less than `"nana"` since `b < n`. Count so far: 11, sum so far: $15 + 6+7+8+9+10+11 = 66$.

Step 3: Substrings starting with `n`: `n` $\leq$ `"nana"` (since `"n"` is a prefix of `"nana"`), `na` $\leq$ `"nana"` (prefix), `nan` $\leq$ `"nana"` (prefix), `nana` $=$ `"nana"`. All 4 qualify.

Final: $\text{count} = 11 + 4 = 15$ and $\text{sum} = 66 + 12+13+14+15 = 120$.

## Approach

Build a suffix automaton for `s`. Every path from its initial state represents one
distinct substring. Process states from longest to shortest to count how many
non-empty paths are reachable through each transition.

For a query, walk its characters from left to right. At each state, every outgoing
transition whose character is smaller than the next query character contributes a
whole contiguous block of lexicographically ranked substrings. Add the size of each
block and its arithmetic-series rank sum, then follow the matching transition. If
there is no matching transition, no longer prefix can qualify and the walk stops.

This also handles queries that are not substrings, queries shorter or longer than
`s`, repeated characters, and rank sums that wrap modulo $10^9+7$.

## Complexity

Let $n=|s|$ and let $L$ be the total length of all queries. The alphabet has 26
characters.

**Time:** $O((n + L) \cdot 26)$  
**Space:** $O(n)$

## Implementations

| Language | Implementation |
| --- | --- |
| Python | [`solution.py`](solutions/python/solution.py) |
