"""Compatibility helpers for PyMEL-like scene and attribute operations.

This module keeps the public PyMEL-style API small and familiar while routing
node, plug, connection, rename, selection, and scalar attr operations through
Maya Python API 2.0 where it is practical.  Complex Maya commands intentionally
fall back to ``maya.cmds`` so the surface remains a drop-in replacement for
existing PyMEL-heavy tools.
"""

from __future__ import annotations

from maya import cmds, mel as maya_mel
from maya.api import OpenMaya as om

from . import omutils
from .api import MayaAPI
from .attrs.attr import Attr, _coerce_attr
from .nodes import AnimCurve, Joint, Mesh, Node, NurbsCurve, Transform
from .registry import wrap_node

my = MayaAPI()
Attribute = Attr
MayaAttributeError = AttributeError


class _MelCompat:
    @staticmethod
    def currentTimeUnitToFPS():
        return maya_mel.eval("currentTimeUnitToFPS()")


class _CmdNamespace:
    """Expose selected maya.cmds commands as namespace-style attributes."""

    def __getattr__(self, name):
        command = getattr(cmds, name, None)
        if command is None:
            raise AttributeError(name)
        return command


class _NodeTypeFactory:
    """Callable factory for the public nodetype constructor surface."""

    def __init__(self, wrapper_cls, node_type):
        self._wrapper_cls = wrapper_cls
        self._node_type = node_type

    def __call__(self, *args, **kwargs):
        if args:
            return wrap_node(omutils.name_of(args[0]))
        name = kwargs.pop("name", kwargs.pop("n", None))
        created = createNode(self._node_type, name=name, *args, **kwargs)
        return created

    @property
    def __name__(self):
        return self._wrapper_cls.__name__

    def __repr__(self):
        return f"<NodeTypeFactory {self._wrapper_cls.__name__}({self._node_type})>"


class _NodeTypes:
    Transform = _NodeTypeFactory(Transform, "transform")
    Joint = _NodeTypeFactory(Joint, "joint")
    Mesh = _NodeTypeFactory(Mesh, "mesh")
    NurbsCurve = _NodeTypeFactory(NurbsCurve, "nurbsCurve")
    AnimCurve = _NodeTypeFactory(AnimCurve, "animCurveTL")

    def __getattr__(self, name):
        if name.startswith("AnimCurve"):
            return _NodeTypeFactory(AnimCurve, name[0].lower() + name[1:])
        node_type = name[0].lower() + name[1:]
        if node_type in set(cmds.allNodeTypes()):
            return _NodeTypeFactory(Node, node_type)
        raise AttributeError(name)


mel = _MelCompat()
general = _CmdNamespace()
system = _CmdNamespace()
nt = _NodeTypes()
nodetypes = nt


def _coerce_node_name(value):
    return omutils.name_of(value)


def _wrap_mobject(obj):
    return wrap_node(om.MFnDependencyNode(obj).absoluteName())


def about(**kwargs):
    return cmds.about(**kwargs)


def playbackOptions(**kwargs):
    return cmds.playbackOptions(**kwargs)


def allNodeTypes():
    return cmds.allNodeTypes()


def ls(*args, **kwargs):
    return my.ls(*args, **kwargs)


def PyNode(name):
    if isinstance(name, om.MPlug):
        return my.attr(name)
    text = omutils.name_of(name)
    if "." in text:
        return my.attr(text)
    return my.get(text)


def hasAttr(node, name):
    try:
        obj = omutils.mobject(node)
        dep = om.MFnDependencyNode(obj)
        return dep.hasAttribute(name)
    except Exception:
        return cmds.attributeQuery(name, node=_coerce_node_name(node), exists=True)


def getAttr(plug):
    if isinstance(plug, Attr):
        return plug.get()
    try:
        return omutils.mplug_value(omutils.plug(plug))
    except Exception:
        return cmds.getAttr(omutils.name_of(plug))


def setAttr(plug, value, *args, **kwargs):
    if isinstance(plug, Attr):
        return plug.set(value)
    if args or kwargs or isinstance(value, (tuple, list)):
        return cmds.setAttr(omutils.name_of(plug), *(value if isinstance(value, (tuple, list)) else (value,)), *args, **kwargs)
    try:
        return omutils.set_mplug_value(omutils.plug(plug), value)
    except Exception:
        return cmds.setAttr(omutils.name_of(plug), value)


def addAttr(node, **kwargs):
    # Attribute creation has many Maya command flags; cmds keeps PyMEL parity.
    cmds.addAttr(_coerce_node_name(node), **kwargs)
    attr_name = kwargs.get("longName") or kwargs.get("ln")
    if attr_name:
        return _coerce_attr(f"{_coerce_node_name(node)}.{attr_name}")
    return None


def deleteAttr(target):
    if isinstance(target, Attr):
        target.node().deleteAttr(target)
        return
    text = omutils.name_of(target)
    if "." not in text:
        raise ValueError("deleteAttr requires an attribute path")
    cmds.deleteAttr(text)


def createNode(node_type, name=None, *args, **kwargs):
    # DAG creation is still safest through cmds because parent/shape behavior is command-specific.
    if kwargs or node_type in {"transform", "joint", "mesh", "nurbsCurve"}:
        created = cmds.createNode(node_type, name=name, *args, **kwargs) if name else cmds.createNode(node_type, *args, **kwargs)
        return wrap_node(created)
    mod = om.MDGModifier()
    obj = mod.createNode(node_type)
    mod.doIt()
    if name:
        rename(_wrap_mobject(obj), name)
        return wrap_node(name)
    return _wrap_mobject(obj)


def rename(node, new_name):
    try:
        obj = omutils.mobject(node)
        mod = om.MDGModifier()
        mod.renameNode(obj, new_name)
        mod.doIt()
        return _wrap_mobject(obj)
    except Exception:
        return wrap_node(cmds.rename(_coerce_node_name(node), new_name))


def delete(target):
    targets = target if isinstance(target, (list, tuple, set)) else [target]
    fallback = []
    for item in targets:
        try:
            mod = om.MDGModifier()
            mod.deleteNode(omutils.mobject(item))
            mod.doIt()
        except Exception:
            fallback.append(_coerce_node_name(item))
    if fallback:
        cmds.delete(fallback)


def listConnections(target, **kwargs):
    plugs_requested = kwargs.get("plugs") or kwargs.get("p")
    try:
        mplug = omutils.plug(target)
        as_source = kwargs.get("source", kwargs.get("s", True))
        as_dest = kwargs.get("destination", kwargs.get("d", True))
        connected = mplug.connectedTo(as_dest, as_source)
        if plugs_requested:
            return [_coerce_attr(item.name()) for item in connected]
        return [wrap_node(om.MFnDependencyNode(item.node()).absoluteName()) for item in connected]
    except Exception:
        results = cmds.listConnections(_coerce_node_name(target), **kwargs) or []
        if plugs_requested:
            return [_coerce_attr(result) for result in results]
        return [wrap_node(result) for result in results]


def keyframe(target, **kwargs):
    if isinstance(kwargs.get("index"), int):
        kwargs["index"] = (kwargs["index"],)
    return cmds.keyframe(_coerce_node_name(target), **kwargs)


def setKeyframe(target, **kwargs):
    return cmds.setKeyframe(_coerce_node_name(target), **kwargs)


def connectAttr(source, destination, force=True):
    try:
        src = omutils.plug(source)
        dst = omutils.plug(destination)
        mod = om.MDGModifier()
        if force and dst.isConnected:
            for connected in dst.connectedTo(True, False):
                mod.disconnect(connected, dst)
        mod.connect(src, dst)
        mod.doIt()
        return None
    except Exception:
        return cmds.connectAttr(omutils.name_of(source), omutils.name_of(destination), force=force)


def channelBox(*args, **kwargs):
    return cmds.channelBox(*args, **kwargs)


def loadPlugin(*args, **kwargs):
    return cmds.loadPlugin(*args, **kwargs)


def unloadPlugin(*args, **kwargs):
    return cmds.unloadPlugin(*args, **kwargs)


def addDynamicNode(*args, **kwargs):
    command = getattr(cmds, "addDynamicNode", None)
    if command is None:
        raise AttributeError("addDynamicNode")
    return command(*args, **kwargs)


def select(targets=None, **kwargs):
    if targets is None:
        return cmds.select(**kwargs)
    if kwargs:
        return cmds.select([_coerce_node_name(item) for item in targets] if isinstance(targets, (list, tuple, set)) else [_coerce_node_name(targets)], **kwargs)
    sel = om.MSelectionList()
    for item in (targets if isinstance(targets, (list, tuple, set)) else [targets]):
        sel.add(_coerce_node_name(item))
    om.MGlobal.setActiveSelectionList(sel)
    return None


__all__ = [
    "Attribute",
    "MayaAttributeError",
    "PyNode",
    "about",
    "addDynamicNode",
    "addAttr",
    "allNodeTypes",
    "channelBox",
    "connectAttr",
    "createNode",
    "delete",
    "deleteAttr",
    "general",
    "getAttr",
    "hasAttr",
    "keyframe",
    "listConnections",
    "ls",
    "mel",
    "my",
    "nodetypes",
    "nt",
    "playbackOptions",
    "rename",
    "select",
    "setAttr",
    "setKeyframe",
    "system",
    "loadPlugin",
    "unloadPlugin",
]
