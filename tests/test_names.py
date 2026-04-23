"""OpenMayaHelper port of PyMEL's test_names module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class NameTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_namespace_is_empty_for_plain_nodes(self):
        node = self.core.createNode("transform", name="plainNode")
        self.assertEqual(node.namespace(), "")

    def test_namespace_is_detected_for_namespaced_nodes(self):
        self.cmds.namespace(add="foo")
        node = self.core.createNode("transform", name="foo:bar")
        self.assertEqual(node.namespace(), "foo:")

