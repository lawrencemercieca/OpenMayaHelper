"""NURBS curve wrapper."""

from maya.api import OpenMaya as om

from ..registry import register_node
from .base import Node


class NurbsCurve(Node):
    """Wrapper around nurbsCurve shapes."""

    @property
    def fn_curve(self):
        dag_path = self.dag_path
        if dag_path is None:
            raise TypeError(f"{self.name} is not a DAG curve")
        return om.MFnNurbsCurve(dag_path)

    def cv_positions(self, space=om.MSpace.kObject):
        return self.fn_curve.cvPositions(space)

    def set_cv_positions(self, positions, space=om.MSpace.kObject):
        points = om.MPointArray()
        for position in positions:
            point = position if isinstance(position, om.MPoint) else om.MPoint(*position)
            points.append(point)
        self.fn_curve.setCVPositions(points, space)
        self.fn_curve.updateCurve()
        return self


register_node(NurbsCurve, om.MFn.kNurbsCurve)
