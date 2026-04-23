"""OpenMayaHelper port of PyMEL's test_nodetypes module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class NodeTypesTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_nt_transform_and_joint_are_callable(self):
        transform_cls = self.core.nt.Transform
        joint_cls = self.core.nt.Joint
        self.assertTrue(callable(transform_cls))
        self.assertTrue(callable(joint_cls))

    def test_nt_transform_constructor_creates_scene_node(self):
        transform = self.core.nt.Transform(name="ctorTransform")
        self.assertEqual(str(transform), "ctorTransform")
        self.assertEqual(self.cmds.nodeType("ctorTransform"), "transform")

    def test_transform_supports_translation_get_set_methods(self):
        transform = self.core.createNode("transform", name="moveMe")
        transform.setTranslation((1.0, 2.0, 3.0))
        translation = transform.getTranslation()
        self.assertEqual(tuple(translation), (1.0, 2.0, 3.0))

    def test_joint_orientation_is_exposed(self):
        joint = self.core.createNode("joint", name="jointA")
        orientation = joint.orientation
        self.assertEqual(tuple(orientation), (0.0, 0.0, 0.0, 1.0))

    def test_transform_full_path_and_long_name(self):
        parent = self.core.nt.Transform(name="rootNode")
        child = self.core.createNode("transform", name="childNode", parent=str(parent))
        self.assertEqual(str(child.fullPath()), "|rootNode|childNode")
        self.assertEqual(str(child.longName()), "|rootNode|childNode")
