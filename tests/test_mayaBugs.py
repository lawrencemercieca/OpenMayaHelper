"""OpenMayaHelper port of PyMEL's test_mayaBugs module."""

from __future__ import annotations

import unittest

from openmayahelper.maya_bugs import known_issue_ids


class MayaBugsTests(unittest.TestCase):
    def test_known_issue_ids_are_stable(self):
        self.assertEqual(
            known_issue_ids(),
            ("constraint_offset_query", "empty_nurbs_curve", "surface_range_domain"),
        )
