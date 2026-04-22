"""Dependency graph helpers."""

from maya.api import OpenMaya as om

from .objects import get_mobject


def dependency_node_from_name(name):
    return om.MFnDependencyNode(get_mobject(name))


def dependency_type_name(node_or_object):
    if isinstance(node_or_object, om.MObject):
        return om.MFnDependencyNode(node_or_object).typeName
    return dependency_node_from_name(node_or_object).typeName
