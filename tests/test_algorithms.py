"""Focused tests for reusable algorithm reference modules."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "algorithms" / "strings" / "suffix_automaton.py"
SPEC = importlib.util.spec_from_file_location("suffix_automaton", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
SuffixAutomaton = MODULE.SuffixAutomaton


class SuffixAutomatonTests(unittest.TestCase):
    def test_membership(self) -> None:
        automaton = SuffixAutomaton.from_text("banana")
        self.assertTrue(automaton.contains("ana"))
        self.assertTrue(automaton.contains("banana"))
        self.assertTrue(automaton.contains(""))
        self.assertFalse(automaton.contains("apple"))

    def test_distinct_substring_count(self) -> None:
        self.assertEqual(SuffixAutomaton.from_text("banana").distinct_substring_count(), 15)
        self.assertEqual(SuffixAutomaton.from_text("aaaa").distinct_substring_count(), 4)

    def test_extend_requires_one_character(self) -> None:
        automaton = SuffixAutomaton()
        with self.assertRaises(ValueError):
            automaton.extend("ab")


if __name__ == "__main__":
    unittest.main()
