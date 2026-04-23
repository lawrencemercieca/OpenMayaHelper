"""OpenMayaHelper port of PyMEL's test_trees module."""

from __future__ import annotations

import unittest

from openmayahelper.trees import Tree


class TreesTests(unittest.TestCase):
    def setUp(self):
        self.tree = Tree("dependNode", ("FurAttractors", ("FurCurveAttractors", "FurDescription"), "abstractBaseCreate"))

    def test_parent_method(self):
        fur_attractors = self.tree.child(0)
        self.assertEqual(fur_attractors.parent().value, "dependNode")
        self.assertEqual(fur_attractors.child(0).parent().value, "FurAttractors")

    def test_contains_walks_children(self):
        self.assertIn("FurDescription", self.tree)
        self.assertNotIn("MissingNode", self.tree)
