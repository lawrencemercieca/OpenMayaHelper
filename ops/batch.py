"""Batched DG edits using MDGModifier."""

import json

from maya.api import OpenMaya as om

from ..attrs.attr import Attr, _coerce_attr


class DGModifierBatch:
    """Queue attribute edits and commit them with one modifier."""

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

    def set(self, attr, value):
        attr = _coerce_attr(attr) if not isinstance(attr, Attr) else attr
        plug = attr.plug
        if plug.isCompound and isinstance(value, (tuple, list)):
            for index, child_value in enumerate(value):
                self._queue_simple_set(plug.child(index), child_value)
            return self
        self._queue_simple_set(plug, value)
        return self

    def connect(self, source, destination):
        source_attr = _coerce_attr(source) if not isinstance(source, Attr) else source
        destination_attr = _coerce_attr(destination) if not isinstance(destination, Attr) else destination
        self.modifier.connect(source_attr.plug, destination_attr.plug)
        return self

    def disconnect(self, source, destination):
        source_attr = _coerce_attr(source) if not isinstance(source, Attr) else source
        destination_attr = _coerce_attr(destination) if not isinstance(destination, Attr) else destination
        self.modifier.disconnect(source_attr.plug, destination_attr.plug)
        return self

    def do_it(self):
        if not self._committed:
            self.modifier.doIt()
            self._committed = True
        return self

    def undo_it(self):
        if self._committed:
            self.modifier.undoIt()
            self._committed = False
        return self

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
        if isinstance(value, (tuple, list)):
            command = (
                'python('
                + json.dumps(
                    f"from maya import cmds; cmds.setAttr({plug.name()!r}, *{list(value)!r})"
                )
                + ')'
            )
            self.modifier.commandToExecute(command)
            return
        command = (
            'python('
            + json.dumps(
                f"from maya import cmds; cmds.setAttr({plug.name()!r}, {value!r})"
            )
            + ')'
        )
        self.modifier.commandToExecute(command)
