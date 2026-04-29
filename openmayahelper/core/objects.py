"""MObject utility helpers.

These helpers intentionally accept PyMEL-style inputs as well as OpenMaya
objects so migration code can be written in a drop-in style.

Supported inputs include:
    - node names / full paths / plug strings
    - PyMEL PyNode-like objects
    - project wrapper objects exposing ``mobject`` or ``dag_path``
    - OpenMaya ``MObject``, ``MDagPath``, ``MPlug``
    - function sets exposing ``object()``
"""

from maya.api import OpenMaya as om


_STRING_TYPES = (str,)


def _call_or_value(value):
    """Return ``value()`` when value is a zero-arg callable property proxy."""
    if callable(value):
        try:
            return value()
        except TypeError:
            return value
    return value


def as_name(obj):
    """Return a Maya node/plug name for common PyMEL/OpenMaya wrapper inputs."""
    if isinstance(obj, _STRING_TYPES):
        return obj

    if isinstance(obj, om.MDagPath):
        return obj.fullPathName()

    if isinstance(obj, om.MPlug):
        return obj.name()

    if isinstance(obj, om.MObject):
        return get_node_name(obj)

    for attr_name in ("name", "nodeName", "longName", "fullPath"):
        if hasattr(obj, attr_name):
            try:
                value = _call_or_value(getattr(obj, attr_name))
                if value:
                    return str(value)
            except Exception:
                pass

    return str(obj)


def _get_from_api_method(obj, method_name):
    method = getattr(obj, method_name, None)
    if method is None:
        return None
    try:
        return method()
    except Exception:
        return None


def get_mobject(node):
    """Return an ``MObject`` from a node name, PyMEL node, wrapper, path, plug, or fn.

    This is deliberately permissive to make PyMEL migration easier.
    """
    if isinstance(node, om.MObject):
        return node

    if isinstance(node, om.MDagPath):
        return node.node()

    if isinstance(node, om.MPlug):
        return node.node()

    # Project wrapper: wrapper.mobject
    mobject = getattr(node, "mobject", None)
    if isinstance(mobject, om.MObject):
        return mobject

    # Project wrapper: wrapper.dag_path
    dag_path = getattr(node, "dag_path", None)
    if isinstance(dag_path, om.MDagPath):
        return dag_path.node()

    # PyMEL has API accessors on many objects. Keep these optional so the module
    # works without importing pymel.
    for method_name in ("__apimobject__", "__apiobject__"):
        value = _get_from_api_method(node, method_name)
        if isinstance(value, om.MObject):
            return value
        if isinstance(value, om.MDagPath):
            return value.node()

    # Function sets expose object().
    obj_method = getattr(node, "object", None)
    if callable(obj_method):
        try:
            value = obj_method()
            if isinstance(value, om.MObject):
                return value
        except Exception:
            pass

    name = as_name(node)
    if "." in name:
        # Plug strings are accepted, but this function returns the owning node.
        name = name.split(".", 1)[0]

    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDependNode(0)


def get_node_name(node, full_path=False):
    """Return the node name for an ``MObject``/``MDagPath``/PyMEL/wrapper input."""
    if isinstance(node, om.MDagPath):
        return node.fullPathName() if full_path else node.partialPathName()

    mobject = get_mobject(node)

    if full_path and mobject.hasFn(om.MFn.kDagNode):
        return om.MDagPath.getAPathTo(mobject).fullPathName()

    return om.MFnDependencyNode(mobject).name()


def exists(node):
    """Return True if the node can be resolved to an ``MObject``."""
    try:
        mobject = get_mobject(node)
        return not mobject.isNull()
    except Exception:
        return False


def is_dag_node(node):
    """Return True if the input resolves to a DAG node."""
    try:
        return get_mobject(node).hasFn(om.MFn.kDagNode)
    except Exception:
        return False
