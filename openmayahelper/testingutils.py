"""Testing helpers for compatibility assertions."""

from __future__ import annotations

import itertools
import unittest


class TestCaseExtended(unittest.TestCase):
    def assertIteration(self, actual, expected, orderMatters=True, onlyMembershipMatters=False):
        actual_list = list(actual)
        expected_list = list(expected)
        if onlyMembershipMatters:
            self.assertTrue(_same_membership(actual_list, expected_list))
            return
        if orderMatters:
            self.assertEqual(actual_list, expected_list)
            return
        self.assertTrue(_same_multiset(actual_list, expected_list))

    def assertNoError(self, func, *args, **kwargs):
        func(*args, **kwargs)


def permutations(sequence, length=None):
    values = list(sequence)
    if length is None:
        length = len(values)
    return [list(items) for items in itertools.permutations(values, length)]


def _same_membership(left, right):
    return _consume_matches(_dedupe(left), _dedupe(right))


def _same_multiset(left, right):
    return _consume_matches(list(left), list(right))


def _dedupe(values):
    result = []
    for value in values:
        if not any(existing == value for existing in result):
            result.append(value)
    return result


def _consume_matches(left, right):
    remaining = list(right)
    for item in left:
        for index, candidate in enumerate(remaining):
            if candidate == item:
                remaining.pop(index)
                break
        else:
            return False
    return not remaining
