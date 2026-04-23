"""OpenMayaHelper port of PyMEL's test_plugins module."""

from __future__ import annotations

import inspect
import os

from maya_testlib import MayaTestCase, import_module


THIS_FILE = os.path.normpath(os.path.abspath(inspect.getsourcefile(lambda: None)))
THIS_DIR = os.path.dirname(THIS_FILE)
PLUGIN_NAME = "dynamicNodes.py"
PLUGIN_PATH = os.path.join(THIS_DIR, "plugins", PLUGIN_NAME)


class PluginTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def tearDown(self):
        if self.cmds.pluginInfo(PLUGIN_NAME, query=True, loaded=True):
            self.cmds.file(new=True, force=True)
            self.core.unloadPlugin(PLUGIN_NAME, force=True)

    def test_dynamic_node_types_can_be_accessed_after_plugin_load(self):
        all_nodes = set(self.core.allNodeTypes())
        self.assertNotIn("initialNode", all_nodes)
        self.core.loadPlugin(PLUGIN_PATH)
        all_nodes = set(self.core.allNodeTypes())
        self.assertIn("initialNode", all_nodes)
        node = self.core.nt.InitialNode()
        node.attr("aFloat").set(5.0)
        self.assertEqual(self.core.getAttr(f"{node}.aFloat"), 5.0)
