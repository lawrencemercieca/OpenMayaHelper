"""DAG helpers with PyMEL-compatible inputs."""

from maya.api import OpenMaya as om

from .objects import as_name, get_mobject


def dag_path_from_name(node):
    """Return an ``MDagPath`` from a name, PyMEL node, wrapper, or MObject."""
    if isinstance(node, om.MDagPath):
        return om.MDagPath(node)

    dag_path = getattr(node, "dag_path", None)
    if isinstance(dag_path, om.MDagPath):
        return om.MDagPath(dag_path)

    # PyMEL DAG nodes commonly expose __apimdagpath__.
    api_dag_method = getattr(node, "__apimdagpath__", None)
    if callable(api_dag_method):
        try:
            value = api_dag_method()
            if isinstance(value, om.MDagPath):
                return om.MDagPath(value)
        except Exception:
            pass

    if isinstance(node, om.MObject):
        if not node.hasFn(om.MFn.kDagNode):
            raise TypeError("MObject is not a DAG node")
        return om.MDagPath.getAPathTo(node)

    name = as_name(node)
    if "." in name:
        name = name.split(".", 1)[0]

    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDagPath(0)


# PyMEL-friendly alias.
as_dag_path = dag_path_from_name


def full_path_name(node):
    """Return the full DAG path name for a DAG node-like input."""
    return dag_path_from_name(node).fullPathName()


def partial_path_name(node):
    """Return the shortest unique DAG path name for a DAG node-like input."""
    return dag_path_from_name(node).partialPathName()


def child_paths(node, type_filter=None):
    """Return child ``MDagPath`` objects without going through ``cmds.listRelatives``.

    ``type_filter`` may be an ``MFn`` enum, such as ``om.MFn.kMesh``.
    """
    dag_path = dag_path_from_name(node)
    result = []

    for index in range(dag_path.childCount()):
        child_obj = dag_path.child(index)
        if type_filter is not None and not child_obj.hasFn(type_filter):
            continue
        child_path = om.MDagPath(dag_path)
        child_path.push(child_obj)
        result.append(child_path)

    return result


def parent_path(node, generations=1):
    """Return an ancestor ``MDagPath`` or ``None``.

    ``generations=1`` matches the usual PyMEL ``getParent()`` behaviour.
    """
    if generations < 1:
        return dag_path_from_name(node)

    dag_path = dag_path_from_name(node)
    for _ in range(generations):
        if dag_path.length() <= 1:
            return None
        dag_path.pop()
    return dag_path


def shape_paths(node, intermediate=False):
    """Return shape paths below a transform-like input."""
    dag_path = dag_path_from_name(node)
    mobj = dag_path.node()

    if mobj.hasFn(om.MFn.kShape):
        return [dag_path]

    shapes = []
    for child_path in child_paths(dag_path):
        child_obj = child_path.node()
        if not child_obj.hasFn(om.MFn.kShape):
            continue
        if not intermediate:
            fn = om.MFnDagNode(child_path)
            try:
                if fn.isIntermediateObject:
                    continue
            except Exception:
                pass
        shapes.append(child_path)
    return shapes


def first_shape_path(node, intermediate=False):
    """Return the first shape path below a transform-like input or ``None``."""
    shapes = shape_paths(node, intermediate=intermediate)
    return shapes[0] if shapes else None


def all_paths_to(node):
    """Return all DAG paths to a DAG node, useful for instanced shapes."""
    mobject = get_mobject(node)
    if not mobject.hasFn(om.MFn.kDagNode):
        return []
    return list(om.MDagPath.getAllPathsTo(mobject))
