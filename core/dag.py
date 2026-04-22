"""DAG helpers."""

from maya.api import OpenMaya as om


def dag_path_from_name(name):
    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDagPath(0)


def full_path_name(dag_path):
    return dag_path.fullPathName()
