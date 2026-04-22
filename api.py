"""Top-level API surface for the mymaya package."""

from maya import cmds
from maya.api import OpenMaya as om

from .nodes.base import Node
from .ops.batch import DGModifierBatch
from .registry import wrap_node


class MayaAPI:
    """Small convenience facade around Maya scene access."""

    @property
    def selected(self):
        """Return wrapped selected nodes."""
        names = cmds.ls(selection=True, long=True) or []
        return [wrap_node(name) for name in names]

    def ls(self, *args, **kwargs):
        """List scene nodes and wrap them into typed node objects."""
        names = cmds.ls(*args, long=True, **kwargs) or []
        return [wrap_node(name) for name in names]

    def get(self, name):
        """Return a wrapped node by name."""
        return wrap_node(name)

    def batch(self):
        """Create a DG modifier based batch context."""
        return DGModifierBatch()

    def attr(self, plug):
        """Resolve an arbitrary plug string into an Attr."""
        return Node.from_name(str(plug).split('.', 1)[0]).attr(str(plug).split('.', 1)[1])
