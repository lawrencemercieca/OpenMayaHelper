"""Animation curve node wrapper."""

from __future__ import annotations

from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

from ..registry import register_node
from .base import Node


class AnimCurve(Node):
    """Wrapper around animCurve nodes."""

    @property
    def fn_anim_curve(self) -> oma.MFnAnimCurve:
        return self._function_set(oma.MFnAnimCurve)

    @property
    def _fn_anim_curve(self) -> oma.MFnAnimCurve:
        """Backward-compatible alias for existing internal callers."""
        return self.fn_anim_curve

    def numKeys(self) -> int:
        return self.fn_anim_curve.numKeys

    def getTime(self, index: int) -> float:
        return self.fn_anim_curve.input(index).value


register_node(AnimCurve, om.MFn.kAnimCurve)
