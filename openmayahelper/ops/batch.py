"""Batched DG edits using MDGModifier.

This module provides a small PyMEL-friendly batching layer while keeping the
actual edit operations OpenMaya-based where possible.
"""

import json

from maya.api import OpenMaya as om

from ..attrs.attr import Attr, _coerce_attr


def _as_attr(value):
    return value if isinstance(value, Attr) else _coerce_attr(value)


def _plug(value):
    return value if isinstance(value, om.MPlug) else _as_attr(value).plug


class DGModifierBatch:
    """Queue DG edits and commit them with one modifier.

    Example:
        with DGModifierBatch() as batch:
            batch.set("node.tx", 10)
            batch.connect("a.out", "b.in", force=True)
    """

    def __init__(self):
        self.modifier = om.MDGModifier()
        self._committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return False
        self.do_it()
        return False

    @property
    def committed(self):
        return self._committed

    def set(self, attr, value):
        plug = _plug(attr)
        if plug.isCompound and isinstance(value, (tuple, list)):
            for index, child_value in enumerate(value):
                self._queue_simple_set(plug.child(index), child_value)
            return self
        self._queue_simple_set(plug, value)
        return self

    # PyMEL/cmds-style alias.
    setAttr = set

    def connect(self, source, destination, force=True):
        source_plug = _plug(source)
        destination_plug = _plug(destination)
        if force:
            existing = destination_plug.source()
            if not existing.isNull:
                self.modifier.disconnect(existing, destination_plug)
        self.modifier.connect(source_plug, destination_plug)
        return self

    # PyMEL/cmds-style alias.
    connectAttr = connect

    def disconnect(self, source, destination):
        self.modifier.disconnect(_plug(source), _plug(destination))
        return self

    # PyMEL/cmds-style alias.
    disconnectAttr = disconnect

    def do_it(self):
        if not self._committed:
            self.modifier.doIt()
            self._committed = True
        return self

    # Maya API style alias.
    doIt = do_it

    def undo_it(self):
        if self._committed:
            self.modifier.undoIt()
            self._committed = False
        return self

    # Maya API style alias.
    undoIt = undo_it

    def _queue_simple_set(self, plug, value):
        if isinstance(value, bool):
            self.modifier.newPlugValueBool(plug, value)
            return
        if isinstance(value, int) and not isinstance(value, bool):
            self.modifier.newPlugValueInt(plug, value)
            return
        if isinstance(value, float):
            self.modifier.newPlugValueDouble(plug, value)
            return
        if isinstance(value, str):
            self.modifier.newPlugValueString(plug, value)
            return
        if isinstance(value, om.MObject):
            self.modifier.newPlugValue(plug, value)
            return
        if isinstance(value, (tuple, list)):
            self._queue_cmds_set_attr(plug, "*" + repr(list(value)))
            return
        self._queue_cmds_set_attr(plug, repr(value))

    def _queue_cmds_set_attr(self, plug, value_expression):
        # Keep this fallback for data types that MDGModifier cannot set directly.
        command = (
            "python("
            + json.dumps(
                f"from maya import cmds; cmds.setAttr({plug.name()!r}, {value_expression})"
            )
            + ")"
        )
        self.modifier.commandToExecute(command)


# Small convenience constructor.
def batch():
    return DGModifierBatch()
