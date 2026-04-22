"""MObject utility helpers."""

from maya.api import OpenMaya as om


def get_mobject(name):
    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDependNode(0)


def get_node_name(mobject):
    return om.MFnDependencyNode(mobject).name()
