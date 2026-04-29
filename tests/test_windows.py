"""OpenMayaHelper port of PyMEL's test_windows module."""

from __future__ import annotations

import unittest

from openmayahelper import pmcmds as pm
from openmayahelper import windows
from openmayahelper.uitypes import Menu, MenuItem, OptionMenu


class WindowsTests(unittest.TestCase):
    def setUp(self):
        self.win = pm.window("windowMenuTest")

    def tearDown(self):
        pm.deleteUI(self.win, window=True)

    def test_option_menu_can_be_queried_as_menu(self):
        pm.formLayout()
        option_menu = OptionMenu("someOptionMenu", create=True)
        MenuItem(parent=option_menu)
        self.assertEqual(windows.menu(option_menu, q=True, numberOfItems=True), 1)
        self.assertEqual(windows.menu(option_menu.name(), q=True, numberOfItems=True), 1)
        self.assertEqual(windows.menu(option_menu.shortName(), q=True, numberOfItems=True), 1)
        self.assertIsInstance(windows.menu(option_menu), Menu)
        self.assertIsInstance(windows.menu(option_menu.name()), Menu)
