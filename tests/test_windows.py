"""OpenMayaHelper port of PyMEL's test_windows module."""

from __future__ import annotations

import unittest

from openmayahelper import windows
from openmayahelper.uitypes import MenuItem, OptionMenu


class WindowsTests(unittest.TestCase):
    def test_option_menu_can_be_queried_as_menu(self):
        option_menu = OptionMenu("someOptionMenu")
        MenuItem(parent=option_menu)
        self.assertEqual(windows.menu(option_menu, q=True, numberOfItems=True), 1)
        self.assertEqual(windows.menu(option_menu.name(), q=True, numberOfItems=True), 1)
