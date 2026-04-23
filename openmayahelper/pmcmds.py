"""Thin command-style facade over the compatibility layer."""

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
