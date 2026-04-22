"""Surface comparison tests against PyMEL when both runtimes are available."""

from __future__ import annotations

from maya_testlib import MayaPyMELCompareTestCase, import_module


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


class SurfaceComparisonTests(MayaPyMELCompareTestCase):
    def setUp(self):
        super().setUp()
        self.mm = import_module("mymaya.core")
        self.pm = import_module("pymel.core")

    def test_critical_surface_symbols_exist(self):
        missing = sorted(name for name in CRITICAL_CORE_SYMBOLS if not hasattr(self.mm, name))
        self.assertEqual([], missing, "mymaya.core is missing critical pymel.core symbols.")

    def test_basic_scene_ops_match_pymel(self):
        mm_node = self.mm.createNode("transform", name="sharedNode")
        self.mm.addAttr(mm_node, longName="speed", attributeType="double")
        self.mm.setAttr("sharedNode.speed", 7.25)
        mm_list = [str(node) for node in self.mm.ls("sharedNode")]
        mm_attr = self.mm.PyNode("sharedNode.speed")

        pm_node = self.pm.PyNode("sharedNode")
        pm_list = [str(node) for node in self.pm.ls("sharedNode")]
        pm_attr = self.pm.PyNode("sharedNode.speed")

        self.assertEqual(str(mm_node), str(pm_node))
        self.assertEqual(mm_list, pm_list)
        self.assertEqual(str(mm_attr), str(pm_attr))
        self.assertEqual(self.mm.getAttr(mm_attr), self.pm.getAttr(pm_attr))


if __name__ == "__main__":
    import unittest

    unittest.main()
