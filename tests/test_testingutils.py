"""OpenMayaHelper port of PyMEL's test_testingutils module."""

from __future__ import annotations

from openmayahelper.testingutils import TestCaseExtended, permutations


class TestingUtilsTests(TestCaseExtended):
    def test_exact_iteration_match(self):
        self.assertIteration("foo", ["f", "o", "o"])

    def test_only_membership_match(self):
        self.assertIteration("foo", ["o", "f"], onlyMembershipMatters=True)

    def test_unordered_counter_match(self):
        self.assertIteration("foo", ["o", "f", "o"], orderMatters=False)

    def test_defaults_fail_for_wrong_order_and_multiplicity(self):
        with self.assertRaises(self.failureException):
            self.assertIteration("foo", ["o", "f", "o"])
        with self.assertRaises(self.failureException):
            self.assertIteration("foo", ["f", "o"])

    def test_only_membership_ignores_order_and_duplicates(self):
        self.assertIteration("foo", ["f", "o", "f"], onlyMembershipMatters=True)
        self.assertIteration("foo", ["o", "f"], orderMatters=False, onlyMembershipMatters=True)
        with self.assertRaises(self.failureException):
            self.assertIteration("foo", ["o", "x"], onlyMembershipMatters=True)

    def test_unordered_exact_match_respects_multiplicity(self):
        self.assertIteration("foo", ["o", "f", "o"], orderMatters=False)
        with self.assertRaises(self.failureException):
            self.assertIteration("foo", ["f", "o", "f"], orderMatters=False)

    def test_permutations(self):
        self.assertIteration(permutations([1, 2]), [[1, 2], [2, 1]], orderMatters=False)
        self.assertEqual(permutations("", None), [[]])
        self.assertIteration(
            permutations("bar", 2),
            [["b", "a"], ["b", "r"], ["a", "b"], ["a", "r"], ["r", "b"], ["r", "a"]],
            orderMatters=False,
        )
