"""OpenMayaHelper port of PyMEL's test_uitypes module."""

from __future__ import annotations

import unittest

from openmayahelper import pmcmds as pm
from openmayahelper import uitypes as ui


class UiTypesTests(unittest.TestCase):
    def setUp(self):
        self.win = pm.window("testWindow")

    def tearDown(self):
        pm.deleteUI(self.win, window=True)

    def test_class_init_tracks_top_level_layout_parent(self):
        with ui.FormLayout() as form:
            self.assertEqual(pm.currentParent(), form)
        self.assertEqual(pm.currentParent(), self.win)
        with ui.RowLayout() as row:
            self.assertEqual(pm.currentParent(), row)
        self.assertEqual(pm.currentParent(), form)
        with ui.ColumnLayout() as column:
            self.assertEqual(pm.currentParent(), column)
        self.assertEqual(pm.currentParent(), form)

    def test_cmd_init_and_parent_jump(self):
        layout = ui.ColumnLayout()
        ui.RowLayout()
        with pm.rowLayout(parent=layout) as row:
            self.assertEqual(pm.currentParent(), row)
        self.assertEqual(pm.currentParent(), layout)

    def test_nested_layout_contexts(self):
        with ui.ColumnLayout() as column:
            self.assertEqual(ui.currentParent(), column)
            with pm.rowLayout() as row:
                self.assertEqual(pm.currentParent(), row)
            self.assertEqual(ui.currentParent(), column)
        self.assertEqual(pm.currentParent(), self.win)

    def test_menu_context_is_tracked_separately(self):
        with ui.ColumnLayout() as column:
            self.assertEqual(pm.currentParent(), column)
            with pm.popupMenu() as menu:
                self.assertEqual(pm.currentMenuParent(), menu)
                self.assertEqual(pm.currentParent(), column)
                with ui.MenuItem(subMenu=True) as submenu:
                    self.assertEqual(pm.currentMenuParent(), submenu)
                self.assertEqual(pm.currentMenuParent(), menu)

    def test_option_menu_group_and_window_exit(self):
        with ui.ColumnLayout() as column:
            with ui.OptionMenuGrp() as menu_group:
                self.assertEqual(pm.currentParent(), menu_group)
                self.assertEqual(pm.currentMenuParent(), menu_group.menu())
            self.assertEqual(pm.currentParent(), column)
        new_window = ui.Window("otherWindow")
        try:
            with new_window:
                self.assertEqual(pm.currentParent(), new_window)
                with pm.formLayout() as form:
                    self.assertEqual(pm.currentParent(), form)
                self.assertEqual(pm.currentParent(), new_window)
            self.assertTrue(pm.currentParent() in (self.win, None, new_window))
        finally:
            pm.deleteUI(new_window, window=True)

    def test_text_scroll_list_empty_selection(self):
        with ui.Window("scrollWindow"):
            with pm.formLayout():
                scroll_list = pm.textScrollList()
                scroll_list.extend(["a", "b", "c"])
        self.assertEqual(scroll_list.getSelectItem(), [])
        pm.deleteUI("scrollWindow", window=True)
