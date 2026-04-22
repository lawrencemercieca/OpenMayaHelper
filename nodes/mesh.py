"""Mesh node wrapper."""

from maya.api import OpenMaya as om

from ..registry import register_node
from .base import Node


class Mesh(Node):
    """Wrapper around mesh shape nodes."""

    @property
    def fn_mesh(self):
        dag_path = self.dag_path
        if dag_path is None:
            raise TypeError(f"{self.name} is not a DAG mesh")
        return om.MFnMesh(dag_path)

    def num_vertices(self):
        return self.fn_mesh.numVertices


register_node(Mesh, om.MFn.kMesh)
