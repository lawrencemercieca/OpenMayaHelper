"""Focused behavioral tests for openmayahelper.core."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class GeneralCompatibilityTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_create_node_returns_wrapped_transform(self):
        node = self.core.createNode("transform", name="compatNode")
        self.assertEqual(str(node), "compatNode")
        self.assertTrue(hasattr(node, "translate"))

    def test_pynode_resolves_nodes_and_attributes(self):
        transform = self.core.createNode("transform", name="driver")
        plug = self.core.PyNode("driver.translateX")
        self.assertEqual(str(transform), "driver")
        self.assertEqual(str(plug), "driver.translateX")

    def test_add_get_set_delete_attr(self):
        node = self.core.createNode("transform", name="attrNode")
        attr = self.core.addAttr(node, longName="weight", attributeType="double")
        self.assertEqual(str(attr), "attrNode.weight")
        self.assertTrue(self.core.hasAttr(node, "weight"))
        self.core.setAttr(attr, 3.5)
        self.assertEqual(self.core.getAttr(attr), 3.5)
        self.core.deleteAttr(attr)
        self.assertFalse(self.core.hasAttr(node, "weight"))

    def test_connect_and_list_connections(self):
        source = self.core.createNode("transform", name="driverSource")
        destination = self.core.createNode("transform", name="driverDestination")
        self.core.connectAttr(source.translateX, destination.translateX)

        source_nodes = self.core.listConnections(destination.translateX, source=True, destination=False)
        source_plugs = self.core.listConnections(destination.translateX, source=True, destination=False, plugs=True)

        self.assertIn(source, source_nodes)
        self.assertEqual([str(plug) for plug in source_plugs], ["driverSource.translateX"])

    def test_ls_and_select_round_trip_wrapped_nodes(self):
        first = self.core.createNode("transform", name="selA")
        second = self.core.createNode("transform", name="selB")

        listed = self.core.ls("sel*")
        self.assertIn(first, listed)
        self.assertIn(second, listed)

        self.core.select([first, second], replace=True)
        selected = self.core.ls(selection=True)
        self.assertEqual({str(node) for node in selected}, {"selA", "selB"})

    def test_rename_and_delete(self):
        node = self.core.createNode("transform", name="renameMe")
        renamed = self.core.rename(node, "renamedNode")
        self.assertEqual(str(renamed), "renamedNode")

        self.core.delete(renamed)
        self.assertEqual(self.cmds.objExists("renamedNode"), 0)


if __name__ == "__main__":
    import unittest

    unittest.main()
