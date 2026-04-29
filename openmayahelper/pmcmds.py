"""Thin command-style facade over the compatibility layer."""

from maya import cmds

from .compat import (
    PyNode,
    addAttr,
    connectAttr,
    createNode,
    delete,
    deleteAttr,
    getAttr,
    hasAttr,
    listConnections,
    ls,
    rename,
    select,
    setAttr,
)
from . import uitypes

__all__ = [
    "PyNode",
    "addAttr",
    "connectAttr",
    "createNode",
    "delete",
    "deleteAttr",
    "getAttr",
    "hasAttr",
    "listConnections",
    "ls",
    "rename",
    "select",
    "setAttr",
    "columnLayout",
    "currentMenuParent",
    "currentParent",
    "deleteUI",
    "formLayout",
    "menuItem",
    "optionMenuGrp",
    "popupMenu",
    "rowLayout",
    "textFieldButtonGrp",
    "textScrollList",
    "window",
]


def window(name=None, **kwargs):
    del kwargs
    return uitypes.Window(name)


def formLayout(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.FormLayout(name=name, parent=parent)


def rowLayout(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.RowLayout(name=name, parent=parent)


def columnLayout(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.ColumnLayout(name=name, parent=parent)


def popupMenu(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.Menu(name=name, parent=parent if parent is not None else uitypes.currentParent())


def menuItem(name=None, parent=None, subMenu=False, **kwargs):
    del kwargs
    return uitypes.MenuItem(name=name, parent=parent, subMenu=subMenu)


def textFieldButtonGrp(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.TextFieldButtonGrp(name=name, parent=parent)


def optionMenuGrp(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.OptionMenuGrp(name=name, parent=parent)


def textScrollList(name=None, parent=None, **kwargs):
    del kwargs
    return uitypes.TextScrollList(name=name, parent=parent)


def currentParent():
    return uitypes.currentParent()


def currentMenuParent():
    return uitypes.currentMenuParent()


def deleteUI(target, **kwargs):
    return uitypes.deleteUI(target, **kwargs)


def __getattr__(name):
    command = getattr(cmds, name, None)
    if command is None:
        raise AttributeError(name)
    return command
