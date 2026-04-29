"""Mesh node wrapper."""

from __future__ import annotations

from maya.api import OpenMaya as om

from ..registry import register_node
from .base import Node


class Mesh(Node):
    """Wrapper around mesh shape nodes."""

    @property
    def fn_mesh(self) -> om.MFnMesh:
        return self._dag_function_set(om.MFnMesh)

    def num_vertices(self) -> int:
        return self.fn_mesh.numVertices

    def points(self, space=om.MSpace.kObject) -> om.MPointArray:
        return self.fn_mesh.getPoints(space)

    def set_points(self, points, space=om.MSpace.kObject) -> "Mesh":
        point_array = points if isinstance(points, om.MPointArray) else om.MPointArray(points)
        self.fn_mesh.setPoints(point_array, space)
        return self


register_node(Mesh, om.MFn.kMesh)
