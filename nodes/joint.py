"""Joint node wrapper."""

from maya.api import OpenMaya as om

from ..registry import register_node
from .transform import Transform


class Joint(Transform):
    """Wrapper around joint nodes."""

    @property
    def orientation(self):
        if self.dag_path is None:
            raise TypeError(f"{self.name} is not a DAG joint")
        return om.MFnIkJoint(self.dag_path).orientation()


register_node(Joint, om.MFn.kJoint)
