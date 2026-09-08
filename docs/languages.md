# Language Strategy

Language coverage is evidence-based rather than quota-based. A problem lists a
language only when the corresponding source exists and passes the same shared tests.

## Python

Python is the historical and primary algorithm-development language. It has the
broadest current coverage and favors direct, typed-enough implementations with a
small JSON adapter around `solve`.

## C++

C++ is supported for classic competitive programming and performance-sensitive
implementations. New solutions should use modern standard C++, clear ownership,
STL facilities, and explicit handling of the repository's JSON boundary. There are
currently no migrated C++ solutions, so the repository does not claim C++ coverage
for its existing problems.

## Go

Go is a growth language for algorithms, data structures, CLI-adjacent work, and
straightforward performance-conscious implementations. Goroutines should appear
only when concurrency belongs to the problem. There are currently no verified Go
problem implementations.

## Rust

Rust is selective: it is most useful here when ownership, borrowing, memory-aware
data structures, iterators, or safe parallelism add genuine engineering value.
Safe Rust and the standard library are preferred. There are currently no verified
Rust problem implementations.

The templates establish basic language conventions, but templates are not counted
as solution coverage.
