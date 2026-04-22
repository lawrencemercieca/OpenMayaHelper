"""Animation curve node wrapper."""

from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

from ..registry import register_node
from .base import Node


class AnimCurve(Node):
    """Wrapper around animCurve nodes."""

    @property
    def _fn_anim_curve(self):
        return oma.MFnAnimCurve(self.mobject)

    def numKeys(self):
        return self._fn_anim_curve.numKeys

    def getTime(self, index):
        return self._fn_anim_curve.input(index).value


register_node(AnimCurve, om.MFn.kAnimCurve)
