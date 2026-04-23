"""Transform node wrapper."""

from maya.api import OpenMaya as om

from ..registry import register_node
from .base import Node


class Transform(Node):
    """Wrapper around transform nodes."""

    @property
    def translation(self):
        if self.dag_path is None:
            raise TypeError(f"{self.name} is not a DAG transform")
        return om.MFnTransform(self.dag_path).translation(om.MSpace.kTransform)

    def set_translation(self, value, space=om.MSpace.kTransform):
        if self.dag_path is None:
            raise TypeError(f"{self.name} is not a DAG transform")
        vector = value if isinstance(value, om.MVector) else om.MVector(*value)
        om.MFnTransform(self.dag_path).setTranslation(vector, space)
        return self

    def getTranslation(self, space=om.MSpace.kTransform):
        if self.dag_path is None:
            raise TypeError(f"{self.name} is not a DAG transform")
        return om.MFnTransform(self.dag_path).translation(space)

    def setTranslation(self, value, space=om.MSpace.kTransform):
        return self.set_translation(value, space=space)


register_node(Transform, om.MFn.kTransform)
