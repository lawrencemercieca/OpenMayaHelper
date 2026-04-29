"""Top-level API surface for the openmayahelper package."""

from maya import cmds
from maya.api import OpenMaya as om

from . import omutils
from .nodes.base import Node
from .ops.batch import DGModifierBatch
from .registry import wrap_node


class MayaAPI:
    """Small convenience facade around Maya scene access."""

    @property
    def selected(self):
        """Return wrapped selected nodes using OpenMaya's active selection list."""
        selection = om.MGlobal.getActiveSelectionList()
        wrapped = []
        for index in range(selection.length()):
            try:
                path = selection.getDagPath(index)
                wrapped.append(wrap_node(path.fullPathName()))
            except RuntimeError:
                obj = selection.getDependNode(index)
                wrapped.append(wrap_node(om.MFnDependencyNode(obj).absoluteName()))
        return wrapped

    def ls(self, *args, **kwargs):
        """List scene nodes and wrap them into typed node objects."""
        names = cmds.ls(*args, long=True, **kwargs) or []
        return [wrap_node(name) for name in names]

    def get(self, name):
        """Return a wrapped node by name, MObject, MDagPath, or wrapper."""
        return wrap_node(omutils.name_of(name))

    def mobject(self, node):
        """Return an OpenMaya MObject for a node-like value."""
        return omutils.mobject(node)

    def dag_path(self, node):
        """Return an OpenMaya MDagPath for a DAG node-like value."""
        return omutils.dag_path(node)

    def plug(self, attr):
        """Return an OpenMaya MPlug for a plug-like value."""
        return omutils.plug(attr)

    def batch(self):
        """Create a DG modifier based batch context."""
        return DGModifierBatch()

    def attr(self, plug):
        """Resolve an arbitrary plug string/MPlug into an Attr wrapper."""
        text = omutils.name_of(plug)
        return Node.from_name(text.split('.', 1)[0]).attr(text.split('.', 1)[1])
