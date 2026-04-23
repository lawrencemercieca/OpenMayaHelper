"""Small UI wrapper types with context-manager support."""

from __future__ import annotations

import itertools


_id_counter = itertools.count(1)
_parent_stack = []
_menu_stack = []
_children = {}


def currentParent():
    return _parent_stack[-1] if _parent_stack else None


def currentMenuParent():
    return _menu_stack[-1] if _menu_stack else None


class PyUI:
    kind = "ui"

    def __init__(self, name=None, create=False, parent=None, **kwargs):
        del create, kwargs
        self._name = name or f"{self.kind}{next(_id_counter)}"
        self._parent = parent if parent is not None else currentParent()
        _children.setdefault(self._name, [])
        if self._parent is not None:
            _children.setdefault(str(self._parent), []).append(self)

    def __enter__(self):
        if isinstance(self, (Menu, MenuItem)):
            _menu_stack.append(self)
        else:
            _parent_stack.append(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        if isinstance(self, (Menu, MenuItem)):
            _menu_stack.pop()
        else:
            _parent_stack.pop()

    def name(self):
        return self._name

    def shortName(self):
        return self._name

    def child_count(self):
        return len(_children.get(self._name, ()))

    def __str__(self):
        return self._name


class FormLayout(PyUI):
    kind = "formLayout"


class RowLayout(PyUI):
    kind = "rowLayout"


class ColumnLayout(PyUI):
    kind = "columnLayout"


class OptionMenu(PyUI):
    kind = "optionMenu"


class Menu(PyUI):
    kind = "menu"


class MenuItem(PyUI):
    kind = "menuItem"

    def __init__(self, subMenu=False, **kwargs):
        super().__init__(**kwargs)
        self.subMenu = subMenu
