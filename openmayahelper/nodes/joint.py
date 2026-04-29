"""Joint node wrapper."""

from __future__ import annotations

from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

from ..registry import register_node
from .transform import Transform


class Joint(Transform):
    """Wrapper around joint nodes."""

    @property
    def fn_joint(self) -> oma.MFnIkJoint:
        return self._dag_function_set(oma.MFnIkJoint)

    @property
    def orientation(self) -> om.MQuaternion:
        return self.fn_joint.orientation().asQuaternion()


register_node(Joint, om.MFn.kJoint)
