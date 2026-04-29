"""Dependency graph helpers with PyMEL-compatible inputs."""

from maya.api import OpenMaya as om

from .objects import get_mobject, get_node_name
from .plugs import find_plug


def dependency_node_from_name(node):
    """Return ``MFnDependencyNode`` from a node name/PyMEL/wrapper/MObject input."""
    if isinstance(node, om.MFnDependencyNode):
        return node
    return om.MFnDependencyNode(get_mobject(node))


# PyMEL-friendly alias.
as_dependency_node = dependency_node_from_name


def dependency_type_name(node_or_object):
    """Return the dependency node type name."""
    return dependency_node_from_name(node_or_object).typeName


def node_name(node_or_object, full_path=False):
    """Return a node name from common Maya object inputs."""
    return get_node_name(node_or_object, full_path=full_path)


def has_attr(node_or_object, attr_name):
    """Return True if the node has the requested attribute."""
    try:
        dependency_node_from_name(node_or_object).findPlug(attr_name, True)
        return True
    except Exception:
        return False


# PyMEL-style alias.
hasAttr = has_attr


def is_type(node_or_object, type_name):
    """Return True if the node's dependency type name matches ``type_name``."""
    return dependency_type_name(node_or_object) == type_name


def connected_plugs(node_or_plug, attr_name=None, source=True, destination=True):
    """Return connected MPlugs for a node.attr or plug-like input."""
    plug = find_plug(node_or_plug, attr_name) if attr_name else find_plug(node_or_plug)
    return list(plug.connectedTo(source, destination))
