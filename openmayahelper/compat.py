"""Compatibility helpers for scene and attribute operations."""

from maya import cmds, mel as maya_mel

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
            return wrap_node(str(args[0]))
        name = kwargs.pop("name", kwargs.pop("n", None))
        created = cmds.createNode(self._node_type, name=name) if name else cmds.createNode(self._node_type)
        return wrap_node(created)

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
    if isinstance(value, Node):
        return value.name
    if isinstance(value, Attr):
        return value.full_name
    if hasattr(value, "name"):
        name_attr = getattr(value, "name")
        return name_attr() if callable(name_attr) else name_attr
    return str(value)


def about(**kwargs):
    return cmds.about(**kwargs)


def playbackOptions(**kwargs):
    return cmds.playbackOptions(**kwargs)


def allNodeTypes():
    return cmds.allNodeTypes()


def ls(*args, **kwargs):
    return my.ls(*args, **kwargs)


def PyNode(name):
    text = str(name)
    if "." in text:
        return my.attr(text)
    return my.get(text)


def hasAttr(node, name):
    if isinstance(node, Node):
        return node.has_attr(name)
    return cmds.attributeQuery(name, node=_coerce_node_name(node), exists=True)


def getAttr(plug):
    if isinstance(plug, Attr):
        return plug.get()
    return cmds.getAttr(str(plug))


def setAttr(plug, value):
    if isinstance(plug, Attr):
        return plug.set(value)
    if isinstance(value, (tuple, list)):
        cmds.setAttr(str(plug), *value)
    else:
        cmds.setAttr(str(plug), value)
    return None


def addAttr(node, **kwargs):
    if isinstance(node, Node):
        return node.addAttr(**kwargs)
    cmds.addAttr(_coerce_node_name(node), **kwargs)
    attr_name = kwargs.get("longName") or kwargs.get("ln")
    if attr_name:
        return _coerce_attr(f"{_coerce_node_name(node)}.{attr_name}")
    return None


def deleteAttr(target):
    if isinstance(target, Attr):
        target.node().deleteAttr(target)
        return
    text = str(target)
    if "." not in text:
        raise ValueError("deleteAttr requires an attribute path")
    cmds.deleteAttr(text)


def createNode(node_type, name=None, *args, **kwargs):
    created = cmds.createNode(node_type, name=name, *args, **kwargs) if name else cmds.createNode(node_type, *args, **kwargs)
    return wrap_node(created)


def rename(node, new_name):
    return wrap_node(cmds.rename(_coerce_node_name(node), new_name))


def delete(target):
    if isinstance(target, (list, tuple, set)):
        names = [_coerce_node_name(item) for item in target]
    else:
        names = [_coerce_node_name(target)]
    if names:
        cmds.delete(names)


def listConnections(target, **kwargs):
    results = cmds.listConnections(_coerce_node_name(target), **kwargs) or []
    if kwargs.get("plugs"):
        return [_coerce_attr(result) for result in results]
    return [wrap_node(result) for result in results]


def keyframe(target, **kwargs):
    if isinstance(kwargs.get("index"), int):
        kwargs["index"] = (kwargs["index"],)
    return cmds.keyframe(_coerce_node_name(target), **kwargs)


def setKeyframe(target, **kwargs):
    return cmds.setKeyframe(_coerce_node_name(target), **kwargs)


def connectAttr(source, destination, force=True):
    return _coerce_attr(source).connect(_coerce_attr(destination), force=force)


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
    if isinstance(targets, (list, tuple, set)):
        names = [_coerce_node_name(item) for item in targets]
    else:
        names = [_coerce_node_name(targets)]
    return cmds.select(names, **kwargs)


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
