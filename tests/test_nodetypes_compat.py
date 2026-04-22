"""PyMEL-derived nodetype expectations for mymaya.core.nt."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class NodeTypesCompatibilityTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.pm = import_module("mymaya.core")

    def test_nt_transform_and_joint_are_callable(self):
        transform_cls = self.pm.nt.Transform
        joint_cls = self.pm.nt.Joint
        self.assertTrue(callable(transform_cls), "pm.nt.Transform must be callable like PyMEL nodetypes.")
        self.assertTrue(callable(joint_cls), "pm.nt.Joint must be callable like PyMEL nodetypes.")

    def test_nt_transform_constructor_creates_scene_node(self):
        transform = self.pm.nt.Transform(name="ctorTransform")
        self.assertEqual(str(transform), "ctorTransform")
        self.assertEqual(self.cmds.nodeType("ctorTransform"), "transform")

    def test_transform_supports_translation_get_set_methods(self):
        transform = self.pm.createNode("transform", name="moveMe")
        transform.setTranslation((1.0, 2.0, 3.0))
        translation = transform.getTranslation()
        self.assertEqual(tuple(translation), (1.0, 2.0, 3.0))

    def test_joint_orientation_is_exposed(self):
        joint = self.pm.createNode("joint", name="jointA")
        orientation = joint.orientation
        self.assertEqual(tuple(orientation), (0.0, 0.0, 0.0, 1.0))


if __name__ == "__main__":
    import unittest

    unittest.main()
