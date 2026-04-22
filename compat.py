"""Compatibility helpers for scene and attribute operations."""

from maya import cmds, mel as maya_mel
import pymel.core as pm

from .api import MayaAPI
from .attrs.attr import Attr, _coerce_attr
from .nodes import AnimCurve, Joint, Mesh, Node, NurbsCurve, Transform
from .registry import wrap_node

my = MayaAPI()
Attribute = Attr


class _MelCompat:
    @staticmethod
    def currentTimeUnitToFPS():
        return maya_mel.eval('currentTimeUnitToFPS()')


class _NodeTypes:
    Transform = (Transform, pm.nodetypes.Transform)
    Joint = (Joint, pm.nodetypes.Joint)
    Mesh = (Mesh, pm.nodetypes.Mesh)
    NurbsCurve = (NurbsCurve, pm.nodetypes.NurbsCurve)
    AnimCurve = (AnimCurve, pm.nodetypes.AnimCurve)


mel = _MelCompat()
general = pm.general
nt = _NodeTypes()
nodetypes = _NodeTypes()
system = pm.system
MayaAttributeError = AttributeError


def _coerce_node_name(value):
    if isinstance(value, Node):
        return value.name
    if isinstance(value, Attr):
        return value.full_name
    if hasattr(value, 'name'):
        name_attr = getattr(value, 'name')
        return name_attr() if callable(name_attr) else name_attr
    return str(value)


def ls(*args, **kwargs):
    return my.ls(*args, **kwargs)


def PyNode(name):
    text = str(name)
    if '.' in text:
        return my.attr(text)
    return my.get(text)


def hasAttr(node, name):
    if isinstance(node, Node):
        return node.has_attr(name)
    return cmds.attributeQuery(name, node=_coerce_node_name(node), exists=True)


def getAttr(plug):
    if isinstance(plug, Attr):
        return plug.get()
    return pm.getAttr(str(plug))


def setAttr(plug, value):
    if isinstance(plug, Attr):
        return plug.set(value)
    return pm.setAttr(str(plug), value)


def addAttr(node, **kwargs):
    if isinstance(node, Node):
        return node.addAttr(**kwargs)
    cmds.addAttr(_coerce_node_name(node), **kwargs)
    attr_name = kwargs.get('longName') or kwargs.get('ln')
    if attr_name:
        return _coerce_attr(f"{_coerce_node_name(node)}.{attr_name}")
    return None


def deleteAttr(target):
    if isinstance(target, Attr):
        target.node().deleteAttr(target)
        return
    text = str(target)
    if '.' not in text:
        raise ValueError('deleteAttr requires an attribute path')
    pm.deleteAttr(text)


def createNode(node_type, name=None):
    created = cmds.createNode(node_type, name=name) if name else cmds.createNode(node_type)
    return wrap_node(created)


def rename(node, new_name):
    if isinstance(node, Node):
        return node.rename(new_name)
    return wrap_node(pm.rename(node, new_name))


def delete(target):
    if isinstance(target, (list, tuple, set)):
        names = [_coerce_node_name(item) for item in target]
    else:
        names = [_coerce_node_name(target)]
    if names:
        cmds.delete(names)


def listConnections(target, **kwargs):
    results = cmds.listConnections(_coerce_node_name(target), **kwargs) or []
    if kwargs.get('plugs'):
        return [_coerce_attr(result) for result in results]
    return [wrap_node(result) for result in results]


def keyframe(target, **kwargs):
    if isinstance(kwargs.get('index'), int):
        kwargs['index'] = (kwargs['index'],)
    return cmds.keyframe(_coerce_node_name(target), **kwargs)


def setKeyframe(target, **kwargs):
    return cmds.setKeyframe(_coerce_node_name(target), **kwargs)


def connectAttr(source, destination, force=True):
    return _coerce_attr(source).connect(_coerce_attr(destination), force=force)


def channelBox(*args, **kwargs):
    return cmds.channelBox(*args, **kwargs)


def select(targets=None, **kwargs):
    if targets is None:
        return cmds.select(**kwargs)
    if isinstance(targets, (list, tuple, set)):
        names = [_coerce_node_name(item) for item in targets]
    else:
        names = [_coerce_node_name(targets)]
    return cmds.select(names, **kwargs)
