"""Transform node wrapper."""

from __future__ import annotations

from maya.api import OpenMaya as om

from ..registry import register_node
from .base import Node


class Transform(Node):
    """Wrapper around transform nodes."""

    @property
    def fn_transform(self) -> om.MFnTransform:
        return self._dag_function_set(om.MFnTransform)

    @property
    def translation(self) -> om.MVector:
        return self.getTranslation()

    def set_translation(self, value, space=om.MSpace.kTransform) -> "Transform":
        vector = value if isinstance(value, om.MVector) else om.MVector(*value)
        self.fn_transform.setTranslation(vector, space)
        return self

    def getTranslation(self, space=om.MSpace.kTransform) -> om.MVector:
        return self.fn_transform.translation(space)

    def setTranslation(self, value, space=om.MSpace.kTransform) -> "Transform":
        return self.set_translation(value, space=space)


register_node(Transform, om.MFn.kTransform)
