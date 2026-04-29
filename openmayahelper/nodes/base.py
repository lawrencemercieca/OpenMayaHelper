"""Base node wrapper.

This is intentionally PyMEL-like at the public API level, but OpenMaya-first internally.
It keeps compatibility helpers such as ``node.name()`` and ``node.tx`` while caching
function sets and attribute wrappers so repeated operations avoid unnecessary lookups.
"""

from __future__ import annotations

from typing import Any

from maya import cmds
from maya.api import OpenMaya as om

from ..attrs.attr import Attr


class _CallableString(str):
    """String subclass that can also be called to return itself.

    This keeps PyMEL-style compatibility for code that does either ``node.name``
    or ``node.name()``. You can remove this later if you want a stricter API.
    """

    def __call__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    __hash__ = str.__hash__


class Node:
    """Thin wrapper around a Maya dependency node."""

    def __init__(self, mobject: om.MObject, dag_path: om.MDagPath | None = None):
        self._mobject = mobject
        self._dag_path = om.MDagPath(dag_path) if dag_path is not None else None
        self._fn_cache: dict[type, Any] = {}
        self._attr_cache: dict[str, Attr] = {}

    @classmethod
    def from_name(cls, name: str) -> "Node":
        from ..registry import wrap_node

        return wrap_node(name)

    @property
    def mobject(self) -> om.MObject:
        return self._mobject

    @property
    def dag_path(self) -> om.MDagPath | None:
        return self._dag_path

    def _function_set(self, fn_type: type) -> Any:
        """Return a cached function set for this node."""
        fn = self._fn_cache.get(fn_type)
        if fn is None:
            fn = fn_type(self.mobject)
            self._fn_cache[fn_type] = fn
        return fn

    def _dag_function_set(self, fn_type: type) -> Any:
        """Return a cached DAG function set for this node."""
        if self.dag_path is None:
            raise TypeError(f"{self.name} is not a DAG node")
        fn = self._fn_cache.get(fn_type)
        if fn is None:
            fn = fn_type(self.dag_path)
            self._fn_cache[fn_type] = fn
        return fn

    @property
    def fn(self) -> om.MFnDependencyNode:
        return self._function_set(om.MFnDependencyNode)

    @property
    def fn_dag(self) -> om.MFnDagNode:
        return self._dag_function_set(om.MFnDagNode)

    @property
    def name(self) -> _CallableString:
        return _CallableString(self.fn.name())

    @property
    def type_name(self) -> str:
        return self.fn.typeName

    @property
    def is_dag(self) -> bool:
        return self.dag_path is not None

    def attr(self, name: str | Attr) -> Attr:
        """Return a cached Attr wrapper.

        This caches the Attr object. If your Attr class also caches the MPlug,
        repeated get/set/connect calls become much cheaper than repeated string lookups.
        """
        if isinstance(name, Attr):
            return name

        attr_name = str(name)
        attr = self._attr_cache.get(attr_name)
        if attr is None:
            attr = Attr(self, attr_name)
            self._attr_cache[attr_name] = attr
        return attr

    def clear_attr_cache(self) -> None:
        self._attr_cache.clear()

    def has_attr(self, name: str) -> bool:
        try:
            self.fn.findPlug(str(name), False)
            return True
        except RuntimeError:
            return False

    def hasAttr(self, name: str) -> bool:
        return self.has_attr(name)

    def addAttr(self, name: str | None = None, **kwargs) -> Attr:
        """Add an attribute and return the wrapped attribute.

        This currently uses cmds for broad compatibility with Maya's many addAttr flags.
        It clears the attr cache because the node schema changed.
        """
        attr_name = kwargs.pop("longName", name)
        if not attr_name:
            raise ValueError("Attribute name is required")

        attr_type = kwargs.pop("type", None)
        if attr_type == "string":
            kwargs["dataType"] = "string"
        elif attr_type:
            kwargs["attributeType"] = attr_type

        cmds.addAttr(str(self.name), longName=attr_name, **kwargs)
        self.clear_attr_cache()
        return self.attr(attr_name)

    def deleteAttr(self, name: str | Attr, **kwargs) -> None:
        attr_name = name.longName() if isinstance(name, Attr) else str(name)
        cmds.deleteAttr(f"{self.name}.{attr_name}", **kwargs)
        self.clear_attr_cache()

    def setAttr(self, name: str, value: Any) -> "Node":
        self.attr(name).set(value)
        return self

    def getAttr(self, name: str) -> Any:
        return self.attr(name).get()

    def rename(self, new_name: str) -> "Node":
        """Rename the node and return a freshly wrapped node.

        Returning a new wrapper keeps the cached DAG path/name/function sets clean.
        """
        cmds.rename(str(self.name), new_name)
        return self.from_name(new_name)

    def exists(self) -> bool:
        try:
            return not self.mobject.isNull()
        except RuntimeError:
            return bool(cmds.objExists(str(self.name)))

    def nodeName(self) -> _CallableString:
        return self.name

    def namespace(self) -> str:
        short_name = str(self.name).split("|")[-1]
        if ":" not in short_name:
            return ""
        return short_name.rsplit(":", 1)[0] + ":"

    def fullPath(self) -> _CallableString:
        if self.dag_path is None:
            return self.name
        return _CallableString(self.dag_path.fullPathName())

    def longName(self) -> _CallableString:
        return self.fullPath()

    def getParent(self, generations: int = 1) -> "Node | None":
        if self.dag_path is None:
            return None
        if generations == 0:
            return self

        if generations > 0:
            current = om.MDagPath(self.dag_path)
            for _ in range(generations):
                if current.length() <= 1:
                    return None
                current.pop()
            return self.from_name(current.fullPathName())

        chain: list[Node] = [self]
        walker = om.MDagPath(self.dag_path)
        while walker.length() > 1:
            walker.pop()
            chain.append(self.from_name(walker.fullPathName()))

        index = abs(generations)
        return chain[index] if index < len(chain) else None

    def getChildren(self, type: str | None = None) -> list["Node"]:
        """Return child DAG nodes using OpenMaya traversal instead of cmds.listRelatives."""
        if self.dag_path is None:
            return []

        children: list[Node] = []
        for index in range(self.dag_path.childCount()):
            child_obj = self.dag_path.child(index)
            child_path = om.MDagPath(self.dag_path)
            child_path.push(child_obj)

            child = self.from_name(child_path.fullPathName())
            if type is None or child.type_name == type:
                children.append(child)

        return children

    def childAtIndex(self, index: int) -> "Node":
        return self.getChildren()[index]

    def getShape(self) -> "Node | None":
        for child in self.getChildren():
            if child.type_name != "transform":
                return child
        return None

    def hasParent(self, other: object) -> bool:
        if self.dag_path is None:
            return False

        target = str(other.fullPath()) if hasattr(other, "fullPath") else str(other)
        target_short = target.split("|")[-1]

        walker = om.MDagPath(self.dag_path)
        while walker.length() > 1:
            walker.pop()
            parent_full = walker.fullPathName()
            if parent_full == target or parent_full.split("|")[-1] == target_short:
                return True
        return False

    def hasChild(self, other: object) -> bool:
        if self.dag_path is None:
            return False

        target = str(other.fullPath()) if hasattr(other, "fullPath") else str(other)
        target_short = target.split("|")[-1]

        for child in self.getChildren():
            child_full = str(child.fullPath())
            if child_full == target or child_full.split("|")[-1] == target_short:
                return True
        return False

    def isParentOf(self, other: object) -> bool:
        if hasattr(other, "hasParent"):
            return other.hasParent(self)
        return False

    def isChildOf(self, other: object) -> bool:
        return self.hasParent(other)

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def __getattr__(self, item: str) -> Attr:
        if item.startswith("_"):
            raise AttributeError(item)
        if self.has_attr(item):
            return self.attr(item)
        raise AttributeError(f"{self.__class__.__name__} has no attribute {item!r}")

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.name)!r})"
