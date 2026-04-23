"""Testing helpers for compatibility assertions."""

from __future__ import annotations

from collections import Counter
import unittest


class TestCaseExtended(unittest.TestCase):
    def assertIteration(self, actual, expected, orderMatters=True, onlyMembershipMatters=False):
        actual_list = list(actual)
        expected_list = list(expected)
        if onlyMembershipMatters:
            self.assertEqual(set(actual_list), set(expected_list))
            return
        if orderMatters:
            self.assertEqual(actual_list, expected_list)
            return
        self.assertEqual(Counter(actual_list), Counter(expected_list))
