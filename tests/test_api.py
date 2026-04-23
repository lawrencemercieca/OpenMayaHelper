"""OpenMayaHelper port of PyMEL's test_api module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class ApiTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.api = import_module("openmayahelper.api")
        self.core = import_module("openmayahelper.core")

    def test_maya_api_get_returns_wrapped_node(self):
        self.core.createNode("transform", name="apiNode")
        node = self.api.MayaAPI().get("apiNode")
        self.assertEqual(str(node), "apiNode")

    def test_maya_api_attr_returns_wrapped_attr(self):
        self.core.createNode("transform", name="apiAttrNode")
        attr = self.api.MayaAPI().attr("apiAttrNode.translateX")
        self.assertEqual(str(attr), "apiAttrNode.translateX")

    def test_maya_api_selected_wraps_selection(self):
        node = self.core.createNode("transform", name="selectedNode")
        self.core.select(node, replace=True)
        selected = self.api.MayaAPI().selected
        self.assertEqual([str(item) for item in selected], ["selectedNode"])

