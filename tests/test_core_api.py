"""Broader PyMEL-style API tests for openmayahelper.core."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class CoreApiTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_node_helpers_expose_basic_identity_methods(self):
        node = self.core.createNode("transform", name="identityNode")
        self.assertEqual(str(node), "identityNode")
        self.assertEqual(node.nodeName(), "identityNode")
        self.assertEqual(node.namespace(), "")
        self.assertEqual(node.type_name, "transform")

    def test_attr_wrapper_exposes_basic_metadata_and_values(self):
        node = self.core.createNode("transform", name="attrMetaNode")
        attr = self.core.addAttr(node, longName="weight", attributeType="double")
        attr.set(5.25)
        self.assertEqual(attr.node(), node)
        self.assertEqual(attr.nodeName(), "attrMetaNode")
        self.assertEqual(attr.longName(), "weight")
        self.assertEqual(attr.name(), "attrMetaNode.weight")
        self.assertEqual(attr.get(), 5.25)

    def test_general_namespace_proxies_maya_cmds(self):
        node = self.core.createNode("transform", name="proxyNode")
        self.assertTrue(self.core.general.objExists("proxyNode"))
        self.assertEqual(self.core.general.nodeType(node.name), "transform")

    def test_batch_set_and_undo(self):
        node = self.core.createNode("transform", name="batchNode")
        batch = self.core.my.batch()
        batch.set(node.translateX, 3.0)
        batch.do_it()
        self.assertEqual(node.translateX.get(), 3.0)
        batch.undo_it()
        self.assertEqual(node.translateX.get(), 0.0)

    def test_attribute_connections_expose_source_and_destinations(self):
        source = self.core.createNode("transform", name="srcNode")
        target = self.core.createNode("transform", name="dstNode")
        source.translateX.connect(target.translateX)
        self.assertEqual(str(target.translateX.source()), "srcNode.translateX")
        self.assertEqual([str(item) for item in source.translateX.destinations()], ["dstNode.translateX"])
