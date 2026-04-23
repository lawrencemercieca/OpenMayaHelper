"""Transform operations."""

from maya.api import OpenMaya as om

from ..nodes.transform import Transform


def _coerce_transform(node):
    return node if isinstance(node, Transform) else Transform.from_name(node)


def match_translation(source, target, space=om.MSpace.kTransform):
    source = _coerce_transform(source)
    target = _coerce_transform(target)
    om.MFnTransform(target.dag_path).setTranslation(source.translation, space)
    return target
