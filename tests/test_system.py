"""OpenMayaHelper port of PyMEL's test_system module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class SystemTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_general_namespace_proxies_maya_cmds(self):
        node = self.core.createNode("transform", name="proxyNode")
        self.assertTrue(self.core.general.objExists("proxyNode"))
        self.assertEqual(self.core.general.nodeType(node.name), "transform")

    def test_about_is_forwarded(self):
        version = self.core.about(version=True)
        self.assertTrue(isinstance(version, str))
        self.assertTrue(bool(version))

    def test_playback_options_is_forwarded(self):
        minimum = self.core.playbackOptions(query=True, minTime=True)
        self.assertIsNotNone(minimum)

