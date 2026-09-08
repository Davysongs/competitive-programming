"""A reusable suffix automaton for substring queries.

Construction takes O(n * alpha) expected time with hash-map transitions and O(n)
space. Membership checks take O(m) expected time for a pattern of length m.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class _State:
    longest: int = 0
    link: int = -1
    transitions: dict[str, int] = field(default_factory=dict)


class SuffixAutomaton:
    """Minimal DFA recognizing every substring of an incrementally added text."""

    def __init__(self) -> None:
        self._states = [_State()]
        self._last = 0

    @classmethod
    def from_text(cls, text: str) -> "SuffixAutomaton":
        automaton = cls()
        for character in text:
            automaton.extend(character)
        return automaton

    def extend(self, character: str) -> None:
        """Append one character to the represented text."""
        if len(character) != 1:
            raise ValueError("extend expects exactly one character")

        current = len(self._states)
        self._states.append(_State(longest=self._states[self._last].longest + 1))
        parent = self._last

        while parent != -1 and character not in self._states[parent].transitions:
            self._states[parent].transitions[character] = current
            parent = self._states[parent].link

        if parent == -1:
            self._states[current].link = 0
        else:
            successor = self._states[parent].transitions[character]
            if self._states[parent].longest + 1 == self._states[successor].longest:
                self._states[current].link = successor
            else:
                clone = len(self._states)
                self._states.append(
                    _State(
                        longest=self._states[parent].longest + 1,
                        link=self._states[successor].link,
                        transitions=self._states[successor].transitions.copy(),
                    )
                )
                while (
                    parent != -1
                    and self._states[parent].transitions.get(character) == successor
                ):
                    self._states[parent].transitions[character] = clone
                    parent = self._states[parent].link
                self._states[successor].link = clone
                self._states[current].link = clone
        self._last = current

    def contains(self, pattern: str) -> bool:
        """Return whether pattern is a substring of the represented text."""
        state = 0
        for character in pattern:
            next_state = self._states[state].transitions.get(character)
            if next_state is None:
                return False
            state = next_state
        return True

    def distinct_substring_count(self) -> int:
        """Count distinct non-empty substrings represented by this automaton."""
        return sum(
            state.longest - self._states[state.link].longest
            for state in self._states[1:]
        )
