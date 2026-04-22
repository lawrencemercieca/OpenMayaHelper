"""Core Maya wrappers and helpers.

This package is imported throughout the codebase as a PyMEL-style facade:

    import mymaya.core as pm

Historically this module only exposed a few low-level helpers, but the
surrounding code expects common ``pymel.core`` symbols such as ``about``,
``playbackOptions``, ``Attribute``, ``general`` and ``nodetypes`` to be
available directly from ``mymaya.core``. Re-export those explicit symbols and
fall back to PyMEL for anything else we do not implement locally.
"""

import pymel.core as _pm

from .dag import dag_path_from_name
from .dg import dependency_node_from_name
from .objects import get_mobject, get_node_name
from .plugs import find_plug
from ..nodes import AnimCurve as _WrappedAnimCurve
from ..nodes import Joint as _WrappedJoint
from ..nodes import Mesh as _WrappedMesh
from ..nodes import NurbsCurve as _WrappedNurbsCurve
from ..nodes import Transform as _WrappedTransform
from ..registry import wrap_node

# Frequently referenced PyMEL namespaces/types.
Attribute = _pm.Attribute
general = _pm.general
mel = _pm.mel
system = _pm.system


class _NodeTypes:
    Transform = (_WrappedTransform, _pm.nodetypes.Transform)
    Joint = (_WrappedJoint, _pm.nodetypes.Joint)
    Mesh = (_WrappedMesh, _pm.nodetypes.Mesh)
    NurbsCurve = (_WrappedNurbsCurve, _pm.nodetypes.NurbsCurve)
    AnimCurve = (_WrappedAnimCurve, _pm.nodetypes.AnimCurve)

    def __getattr__(self, name):
        if name.startswith('AnimCurve'):
            return (_WrappedAnimCurve, getattr(_pm.nodetypes, name))
        return getattr(_pm.nodetypes, name)


nodetypes = _NodeTypes()
nt = nodetypes


def createNode(node_type, *args, **kwargs):
    """Create wrapped scene nodes."""
    node = _pm.createNode(node_type, *args, **kwargs)
    return wrap_node(str(node))


def PyNode(name):
    text = str(name)
    node = _pm.PyNode(text)
    if '.' in text or isinstance(node, _pm.Attribute):
        return node
    return wrap_node(text)


def hasAttr(node, name):
    return _pm.attributeQuery(name, node=str(node), exists=True)


def ls(*args, **kwargs):
    results = _pm.ls(*args, **kwargs) or []
    wrapped = []
    for result in results:
        if isinstance(result, (_pm.nodetypes.Transform, _pm.nodetypes.Joint, _pm.nodetypes.Mesh, _pm.nodetypes.NurbsCurve, _pm.nodetypes.AnimCurve)):
            wrapped.append(wrap_node(str(result)))
        else:
            wrapped.append(result)
    return wrapped


def listConnections(target, **kwargs):
    results = _pm.listConnections(target, **kwargs) or []
    wrapped = []
    for result in results:
        if isinstance(result, (_pm.nodetypes.Transform, _pm.nodetypes.Joint, _pm.nodetypes.Mesh, _pm.nodetypes.NurbsCurve, _pm.nodetypes.AnimCurve)):
            wrapped.append(wrap_node(str(result)))
        else:
            wrapped.append(result)
    return wrapped


def __getattr__(name):
    """Delegate unresolved symbols to ``pymel.core``."""
    return getattr(_pm, name)


def __dir__():
    return sorted(set(globals()) | set(dir(_pm)))


__all__ = [
    'Attribute',
    'PyNode',
    'dag_path_from_name',
    'dependency_node_from_name',
    'find_plug',
    'general',
    'get_mobject',
    'get_node_name',
    'mel',
    'nodetypes',
    'nt',
    'system',
]
