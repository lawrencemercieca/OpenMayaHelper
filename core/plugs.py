"""MPlug utility helpers."""

from maya.api import OpenMaya as om

from .objects import get_mobject


def find_plug(node_or_name, attr_name, want_networked_plug=True):
    mobject = node_or_name if isinstance(node_or_name, om.MObject) else get_mobject(node_or_name)
    return om.MFnDependencyNode(mobject).findPlug(attr_name, want_networked_plug)


def split_plug_name(plug_name):
    node_name, attr_name = plug_name.split('.', 1)
    return node_name, attr_name
