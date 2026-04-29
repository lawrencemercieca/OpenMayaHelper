"""Small UI wrapper types with PyMEL-style context-manager support."""

from __future__ import annotations

import itertools


_id_counter = itertools.count(1)
_registry = {}
_children = {}
_current_parent = None
_current_menu_parent = None
_parent_context_stack = []
_menu_context_stack = []


def currentParent():
    return _current_parent


def currentMenuParent():
    return _current_menu_parent


def get_ui(name):
    if isinstance(name, PyUI):
        return name
    return _registry.get(str(name))


def deleteUI(target, **kwargs):
    del kwargs
    ui = get_ui(target)
    if ui is None:
        return
    _unregister(ui)


class PyUI:
    kind = "ui"
    acts_as_parent = True
    acts_as_menu_parent = False

    def __new__(cls, name=None, *args, **kwargs):
        existing = get_ui(name)
        if existing is not None and isinstance(existing, cls):
            return existing
        return super().__new__(cls)

    def __init__(self, name=None, create=False, parent=None, **kwargs):
        del create, kwargs
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._name = name or f"{self.kind}{next(_id_counter)}"
        self._children = []
        self._previous_parent = currentParent()
        self._previous_menu_parent = currentMenuParent()
        self._parent = _resolve_parent(self, parent)
        self._register()
        if self._parent is not None:
            _attach_child(self._parent, self)
        if self.acts_as_parent:
            _set_current_parent(self)
        if self.acts_as_menu_parent:
            _set_current_menu_parent(self)

    def _register(self):
        _registry[self._name] = self
        _children.setdefault(self._name, [])

    def __enter__(self):
        if self.acts_as_parent:
            _parent_context_stack.append(self._parent if _current_parent == self else _current_parent)
            _set_current_parent(self)
        if self.acts_as_menu_parent:
            _menu_context_stack.append(self._previous_menu_parent if _current_menu_parent == self else _current_menu_parent)
            _set_current_menu_parent(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        if self.acts_as_menu_parent:
            _set_current_menu_parent(_menu_context_stack.pop())
        if self.acts_as_parent:
            _set_current_parent(_parent_context_stack.pop())

    def name(self):
        return self._name

    def shortName(self):
        return self._name.rsplit("|", 1)[-1]

    def child_count(self):
        return len(_children.get(self._name, ()))

    def children(self):
        return list(_children.get(self._name, ()))

    def __str__(self):
        return self._name

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self._name)


class Window(PyUI):
    kind = "window"

    def __init__(self, name=None, create=False, parent=None, **kwargs):
        super().__init__(name=name, create=create, parent=None, **kwargs)
        self._top_level_layout = None
        _set_current_parent(self)
        _set_current_menu_parent(None)


class Layout(PyUI):
    kind = "layout"


class FormLayout(Layout):
    kind = "formLayout"


class RowLayout(Layout):
    kind = "rowLayout"


class ColumnLayout(Layout):
    kind = "columnLayout"


class Menu(PyUI):
    kind = "menu"
    acts_as_parent = False
    acts_as_menu_parent = True


class MenuItem(PyUI):
    kind = "menuItem"
    acts_as_parent = False

    def __init__(self, subMenu=False, name=None, create=False, parent=None, **kwargs):
        self.subMenu = subMenu
        self.acts_as_menu_parent = bool(subMenu)
        super().__init__(name=name, create=create, parent=parent if parent is not None else currentMenuParent(), **kwargs)


class OptionMenu(Menu):
    kind = "optionMenu"


class OptionMenuGrp(PyUI):
    kind = "optionMenuGrp"

    def __init__(self, name=None, create=False, parent=None, **kwargs):
        super().__init__(name=name, create=create, parent=parent, **kwargs)
        self._menu = OptionMenu(name=f"{self._name}|OptionMenu", parent=self)

    def menu(self):
        return self._menu

    def __enter__(self):
        _parent_context_stack.append(self._parent if _current_parent == self else _current_parent)
        _menu_context_stack.append(self._previous_menu_parent if _current_menu_parent == self._menu else _current_menu_parent)
        _set_current_parent(self)
        _set_current_menu_parent(self._menu)
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        _set_current_menu_parent(_menu_context_stack.pop())
        _set_current_parent(_parent_context_stack.pop())


class TextFieldButtonGrp(PyUI):
    kind = "textFieldButtonGrp"


class TextScrollList(PyUI):
    kind = "textScrollList"
    acts_as_parent = False

    def __init__(self, name=None, create=False, parent=None, **kwargs):
        super().__init__(name=name, create=create, parent=parent, **kwargs)
        self._items = []
        self._selected = []

    def extend(self, values):
        self._items.extend(values)

    def getSelectItem(self):
        return list(self._selected)


def _resolve_parent(ui, explicit_parent):
    if explicit_parent is not None:
        return get_ui(explicit_parent) or explicit_parent
    parent = currentParent()
    if isinstance(parent, Window) and isinstance(ui, Layout):
        if parent._top_level_layout is None:
            parent._top_level_layout = ui
            return parent
        return parent._top_level_layout
    return parent


def _attach_child(parent, child):
    parent = get_ui(parent) or parent
    if isinstance(parent, PyUI):
        parent._children.append(child)
        _children.setdefault(parent.name(), []).append(child)


def _set_current_parent(value):
    global _current_parent
    _current_parent = value


def _set_current_menu_parent(value):
    global _current_menu_parent
    _current_menu_parent = value


def _unregister(ui):
    for child in list(ui.children()):
        _unregister(child)
    _registry.pop(ui.name(), None)
    _children.pop(ui.name(), None)
    if isinstance(ui._parent, PyUI):
        _children[ui._parent.name()] = [child for child in _children.get(ui._parent.name(), []) if child != ui]
        ui._parent._children = [child for child in ui._parent._children if child != ui]
    global _current_parent, _current_menu_parent
    if _current_parent == ui:
        _current_parent = ui._parent if isinstance(ui._parent, PyUI) else None
    if _current_menu_parent == ui:
        _current_menu_parent = None
