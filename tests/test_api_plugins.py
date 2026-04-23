"""OpenMayaHelper port of PyMEL's test_api_plugins module."""

from __future__ import annotations

import os
import re

from maya_testlib import MayaTestCase, import_module


class ApiPluginsTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.api_plugins = import_module("openmayahelper.api_plugins")

    def test_maya_plugins_discovers_plugin_path_and_filters(self):
        plugin_path = os.environ.get("MAYA_PLUG_IN_PATH")
        self.assertTrue(plugin_path)

        all_plugins = self.api_plugins.mayaPlugins()
        self.assertTrue(all_plugins)

        plugin_name = os.path.splitext(all_plugins[0])[0]
        filtered = self.api_plugins.mayaPlugins(filters=[plugin_name])
        self.assertNotIn(plugin_name, [os.path.splitext(item)[0] for item in filtered])

        regex_filtered = self.api_plugins.mayaPlugins(filters=[re.compile(rf"^{re.escape(plugin_name)}$")])
        self.assertEqual(filtered, regex_filtered)

        callable_filtered = self.api_plugins.mayaPlugins(filters=[lambda item: os.path.splitext(item)[0] == plugin_name])
        self.assertEqual(filtered, callable_filtered)
