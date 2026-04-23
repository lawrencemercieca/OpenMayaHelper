"""Registry and automatic node wrapping."""

from maya.api import OpenMaya as om


_REGISTRY = []


def register_node(node_cls, *fn_types):
    """Register a node class against one or more MFn type ids."""
    _REGISTRY.append((node_cls, fn_types))


def get_selection_list(name):
    selection = om.MSelectionList()
    selection.add(name)
    return selection


def get_mobject(name):
    return get_selection_list(name).getDependNode(0)


def get_dag_path(name):
    selection = get_selection_list(name)
    try:
        return selection.getDagPath(0)
    except (RuntimeError, TypeError):
        return None


def wrap_mobject(mobject, dag_path=None):
    from .nodes.base import Node

    if dag_path is None and mobject.hasFn(om.MFn.kDagNode):
        dag_path = om.MFnDagNode(mobject).getPath()
    for node_cls, fn_types in reversed(_REGISTRY):
        if any(mobject.hasFn(fn_type) for fn_type in fn_types):
            return node_cls(mobject, dag_path=dag_path)
    return Node(mobject, dag_path=dag_path)


def wrap_node(name):
    mobject = get_mobject(name)
    dag_path = get_dag_path(name)
    return wrap_mobject(mobject, dag_path=dag_path)
