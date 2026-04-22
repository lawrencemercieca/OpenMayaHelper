"""Focused PyMEL-style behavioral tests for mymaya.core."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class GeneralCompatibilityTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.pm = import_module("mymaya.core")

    def test_create_node_returns_wrapped_transform(self):
        node = self.pm.createNode("transform", name="compatNode")
        self.assertEqual(str(node), "compatNode")
        self.assertTrue(hasattr(node, "translate"))

    def test_pynode_resolves_nodes_and_attributes(self):
        transform = self.pm.createNode("transform", name="driver")
        plug = self.pm.PyNode("driver.translateX")
        self.assertEqual(str(transform), "driver")
        self.assertEqual(str(plug), "driver.translateX")

    def test_add_get_set_delete_attr(self):
        node = self.pm.createNode("transform", name="attrNode")
        attr = self.pm.addAttr(node, longName="weight", attributeType="double")
        self.assertEqual(str(attr), "attrNode.weight")
        self.assertTrue(self.pm.hasAttr(node, "weight"))
        self.pm.setAttr(attr, 3.5)
        self.assertEqual(self.pm.getAttr(attr), 3.5)
        self.pm.deleteAttr(attr)
        self.assertFalse(self.pm.hasAttr(node, "weight"))

    def test_connect_and_list_connections(self):
        source = self.pm.createNode("transform", name="source")
        destination = self.pm.createNode("transform", name="destination")
        self.pm.connectAttr(source.translateX, destination.translateX)

        source_nodes = self.pm.listConnections(destination.translateX, source=True, destination=False)
        source_plugs = self.pm.listConnections(destination.translateX, source=True, destination=False, plugs=True)

        self.assertIn(source, source_nodes)
        self.assertEqual([str(plug) for plug in source_plugs], ["source.translateX"])

    def test_ls_and_select_round_trip_wrapped_nodes(self):
        first = self.pm.createNode("transform", name="selA")
        second = self.pm.createNode("transform", name="selB")

        listed = self.pm.ls("sel*")
        self.assertIn(first, listed)
        self.assertIn(second, listed)

        self.pm.select([first, second], replace=True)
        selected = self.pm.ls(selection=True)
        self.assertEqual({str(node) for node in selected}, {"selA", "selB"})

    def test_rename_and_delete(self):
        node = self.pm.createNode("transform", name="renameMe")
        renamed = self.pm.rename(node, "renamedNode")
        self.assertEqual(str(renamed), "renamedNode")

        self.pm.delete(renamed)
        self.assertEqual(self.cmds.objExists("renamedNode"), 0)


if __name__ == "__main__":
    import unittest

    unittest.main()
