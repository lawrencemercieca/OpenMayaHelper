"""OpenMayaHelper port of PyMEL's test_testingutils module."""

from __future__ import annotations

from openmayahelper.testingutils import TestCaseExtended


class TestingUtilsTests(TestCaseExtended):
    def test_exact_iteration_match(self):
        self.assertIteration("foo", ["f", "o", "o"])

    def test_only_membership_match(self):
        self.assertIteration("foo", ["o", "f"], onlyMembershipMatters=True)

    def test_unordered_counter_match(self):
        self.assertIteration("foo", ["o", "f", "o"], orderMatters=False)
