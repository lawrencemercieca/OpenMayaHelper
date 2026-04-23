"""Surface consistency tests for openmayahelper.core."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


CRITICAL_CORE_SYMBOLS = {
    "Attribute",
    "PyNode",
    "about",
    "addAttr",
    "connectAttr",
    "createNode",
    "delete",
    "deleteAttr",
    "general",
    "getAttr",
    "hasAttr",
    "keyframe",
    "listConnections",
    "ls",
    "mel",
    "nodetypes",
    "nt",
    "rename",
    "select",
    "setAttr",
    "setKeyframe",
    "system",
}


class SurfaceComparisonTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_critical_surface_symbols_exist(self):
        missing = sorted(name for name in CRITICAL_CORE_SYMBOLS if not hasattr(self.core, name))
        self.assertEqual([], missing, "openmayahelper.core is missing critical surface symbols.")

    def test_basic_scene_ops_are_self_consistent(self):
        node = self.core.createNode("transform", name="sharedNode")
        self.core.addAttr(node, longName="speed", attributeType="double")
        self.core.setAttr("sharedNode.speed", 7.25)
        listed = [str(item) for item in self.core.ls("sharedNode")]
        attr = self.core.PyNode("sharedNode.speed")

        self.assertEqual(str(node), "sharedNode")
        self.assertEqual(listed, ["sharedNode"])
        self.assertEqual(str(attr), "sharedNode.speed")
        self.assertEqual(self.core.getAttr(attr), 7.25)


if __name__ == "__main__":
    import unittest

    unittest.main()
