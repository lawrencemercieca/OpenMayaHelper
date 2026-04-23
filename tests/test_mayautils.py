"""OpenMayaHelper port of PyMEL's test_mayautils module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class MayaUtilsTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.mayautils = import_module("openmayahelper.mayautils")

    def test_get_maya_version_matches_cmds_about_api(self):
        self.assertEqual(self.mayautils.getMayaVersion(), self.cmds.about(api=True))
