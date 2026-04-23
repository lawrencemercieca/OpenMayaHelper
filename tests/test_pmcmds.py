"""OpenMayaHelper port of PyMEL's test_pmcmds module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class PmCmdsTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.pmcmds = import_module("openmayahelper.pmcmds")

    def test_create_node_returns_wrapped_transform(self):
        node = self.pmcmds.createNode("transform", name="pmcmdsNode")
        self.assertEqual(str(node), "pmcmdsNode")

    def test_set_and_get_attr_accept_wrapped_attr(self):
        node = self.pmcmds.createNode("transform", name="pmcmdsAttrNode")
        self.pmcmds.setAttr(node.translateX, 5.0)
        self.assertEqual(self.pmcmds.getAttr(node.translateX), 5.0)

    def test_connect_attr_accepts_wrapped_attrs(self):
        source = self.pmcmds.createNode("transform", name="pmcmdsSource")
        target = self.pmcmds.createNode("transform", name="pmcmdsTarget")
        self.pmcmds.connectAttr(source.translateX, target.translateX)
        results = self.pmcmds.listConnections(target.translateX, source=True, destination=False, plugs=True)
        self.assertEqual([str(result) for result in results], ["pmcmdsSource.translateX"])

    def test_select_and_ls_accept_wrapped_nodes(self):
        first = self.pmcmds.createNode("transform", name="pmcmdsSelA")
        second = self.pmcmds.createNode("transform", name="pmcmdsSelB")
        self.pmcmds.select([first, second], replace=True)
        listed = self.pmcmds.ls(selection=True)
        self.assertEqual({str(node) for node in listed}, {"pmcmdsSelA", "pmcmdsSelB"})
