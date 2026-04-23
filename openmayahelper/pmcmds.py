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
]


def __getattr__(name):
    command = getattr(cmds, name, None)
    if command is None:
        raise AttributeError(name)
    return command
