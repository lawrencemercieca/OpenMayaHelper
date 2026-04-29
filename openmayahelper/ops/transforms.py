"""Transform operations."""

from maya.api import OpenMaya as om

from ..nodes.transform import Transform


def _coerce_transform(node):
    if isinstance(node, Transform):
        return node
    if hasattr(node, "dag_path") and node.dag_path is not None:
        return node
    return Transform.from_name(str(node))


def _as_vector(value):
    if isinstance(value, om.MVector):
        return value
    if isinstance(value, om.MPoint):
        return om.MVector(value)
    return om.MVector(*value)


def get_translation(node, space=om.MSpace.kTransform):
    return _coerce_transform(node).getTranslation(space=space)


def set_translation(node, value, space=om.MSpace.kTransform):
    return _coerce_transform(node).setTranslation(_as_vector(value), space=space)


def match_translation(source, target, space=om.MSpace.kTransform):
    source = _coerce_transform(source)
    target = _coerce_transform(target)
    om.MFnTransform(target.dag_path).setTranslation(source.getTranslation(space=space), space)
    return target


def get_matrix(node, world=True):
    node = _coerce_transform(node)
    return node.dag_path.inclusiveMatrix() if world else node.dag_path.exclusiveMatrix()


def get_world_matrix(node):
    return get_matrix(node, world=True)


def match_matrix(source, target, world=True):
    source = _coerce_transform(source)
    target = _coerce_transform(target)
    matrix = source.dag_path.inclusiveMatrix() if world else source.dag_path.exclusiveMatrix()
    transform = om.MTransformationMatrix(matrix)
    om.MFnTransform(target.dag_path).setTransformation(transform)
    return target


# PyMEL-style aliases.
getTranslation = get_translation
setTranslation = set_translation
matchTranslation = match_translation
getMatrix = get_matrix
getWorldMatrix = get_world_matrix
matchMatrix = match_matrix
