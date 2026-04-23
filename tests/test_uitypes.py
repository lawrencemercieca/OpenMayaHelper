"""OpenMayaHelper port of PyMEL's test_uitypes module."""

from __future__ import annotations

import unittest

from openmayahelper import uitypes as ui


class UiTypesTests(unittest.TestCase):
    def test_nested_layout_contexts(self):
        with ui.ColumnLayout() as column:
            self.assertEqual(ui.currentParent(), column)
            with ui.RowLayout() as row:
                self.assertEqual(ui.currentParent(), row)
            self.assertEqual(ui.currentParent(), column)
        self.assertIsNone(ui.currentParent())

    def test_menu_context_is_tracked_separately(self):
        with ui.ColumnLayout() as column:
            self.assertEqual(ui.currentParent(), column)
            with ui.Menu() as menu:
                self.assertEqual(ui.currentMenuParent(), menu)
                self.assertEqual(ui.currentParent(), column)
                with ui.MenuItem(subMenu=True) as submenu:
                    self.assertEqual(ui.currentMenuParent(), submenu)
