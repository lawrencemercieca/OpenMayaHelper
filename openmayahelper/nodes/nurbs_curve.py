"""NURBS curve wrapper."""

from __future__ import annotations

from maya.api import OpenMaya as om

from ..registry import register_node
from .base import Node


class NurbsCurve(Node):
    """Wrapper around nurbsCurve shapes."""

    @property
    def fn_curve(self) -> om.MFnNurbsCurve:
        return self._dag_function_set(om.MFnNurbsCurve)

    def cv_positions(self, space=om.MSpace.kObject) -> om.MPointArray:
        return self.fn_curve.cvPositions(space)

    def set_cv_positions(self, positions, space=om.MSpace.kObject) -> "NurbsCurve":
        points = om.MPointArray()
        for position in positions:
            point = position if isinstance(position, om.MPoint) else om.MPoint(*position)
            points.append(point)
        self.fn_curve.setCVPositions(points, space)
        self.fn_curve.updateCurve()
        return self


register_node(NurbsCurve, om.MFn.kNurbsCurve)
