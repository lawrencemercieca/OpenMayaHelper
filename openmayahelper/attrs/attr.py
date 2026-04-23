"""Attribute wrapper built on top of MPlug."""

from maya import cmds
from maya.api import OpenMaya as om


class Attr:
    """Wrapper around a specific node attribute."""

    def __init__(self, node, name):
        self._node = node
        self._name = name

    @property
    def plug(self):
        return self._node.fn.findPlug(self._name, True)

    @property
    def full_name(self):
        return f'{self._node.name}.{self._name}'

    def node(self):
        return self._node

    def nodeName(self):
        return self._node.name

    def longName(self):
        return self._name

    def name(self):
        return self.full_name

    def exists(self):
        return bool(cmds.objExists(self.full_name))

    def get(self):
        plug = self.plug
        if plug.isArray:
            return [plug.elementByPhysicalIndex(i).asMObject() for i in range(plug.numElements())]
        if plug.isCompound:
            return tuple(plug.child(i).asDouble() for i in range(plug.numChildren()))
        attr_obj = plug.attribute()
        if attr_obj.hasFn(om.MFn.kTypedAttribute):
            try:
                return cmds.getAttr(self.full_name)
            except RuntimeError:
                return None
        if attr_obj.hasFn(om.MFn.kNumericAttribute):
            numeric_attr = om.MFnNumericAttribute(attr_obj)
            numeric_type = numeric_attr.numericType()
            if numeric_type == om.MFnNumericData.kBoolean:
                return plug.asBool()
            if numeric_type in (om.MFnNumericData.kByte, om.MFnNumericData.kShort, om.MFnNumericData.kInt, om.MFnNumericData.kLong):
                return plug.asInt()
            if numeric_type in (om.MFnNumericData.kFloat, om.MFnNumericData.kDouble, om.MFnNumericData.kAddr):
                return plug.asDouble()
        try:
            return plug.asDouble()
        except RuntimeError:
            try:
                return plug.asString()
            except RuntimeError:
                return cmds.getAttr(self.full_name)

    def set(self, value):
        plug = self.plug
        if plug.isCompound and isinstance(value, (tuple, list)):
            for index, child_value in enumerate(value):
                self._set_simple(plug.child(index), child_value)
            return self
        self._set_simple(plug, value)
        return self

    def _set_simple(self, plug, value):
        if isinstance(value, bool):
            plug.setBool(value)
            return
        if isinstance(value, int) and not isinstance(value, bool):
            plug.setInt(value)
            return
        if isinstance(value, float):
            plug.setDouble(value)
            return
        if isinstance(value, str):
            plug.setString(value)
            return
        cmds.setAttr(plug.name(), *value) if isinstance(value, (tuple, list)) else cmds.setAttr(plug.name(), value)

    def connect(self, other, force=True):
        modifier = om.MDGModifier()
        modifier.connect(self.plug, _coerce_attr(other).plug)
        modifier.doIt()
        return other

    def disconnect(self, other):
        modifier = om.MDGModifier()
        modifier.disconnect(self.plug, _coerce_attr(other).plug)
        modifier.doIt()
        return other

    def listConnections(self, **kwargs):
        from .. import listConnections

        return listConnections(self, **kwargs)

    def source(self):
        source_plug = self.plug.source()
        return None if source_plug.isNull else _attr_from_plug(source_plug)

    def destinations(self):
        return [_attr_from_plug(plug) for plug in self.plug.destinations()]

    def isHidden(self):
        return cmds.addAttr(self.full_name, query=True, hidden=True)

    def isLocked(self):
        return bool(cmds.getAttr(self.full_name, lock=True))

    def lock(self, checkReference=False):
        return self.setLocked(True, checkReference=checkReference)

    def unlock(self, checkReference=False):
        return self.setLocked(False, checkReference=checkReference)

    def setLocked(self, state, checkReference=False):
        if checkReference and cmds.referenceQuery(self.nodeName(), isNodeReferenced=True):
            raise AttributeError(f"{self.full_name} is referenced")
        cmds.setAttr(self.full_name, lock=bool(state))
        return self

    def isSettable(self):
        return bool(cmds.getAttr(self.full_name, settable=True))

    def __rshift__(self, other):
        self.connect(other)
        return other

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"Attr({self.full_name!r})"


def _attr_from_plug(plug):
    from ..registry import wrap_mobject

    node = wrap_mobject(plug.node())
    return Attr(node, plug.partialName(useLongNames=True))


def _coerce_attr(value):
    if isinstance(value, Attr):
        return value
    if hasattr(value, 'node') and callable(getattr(value, 'node')) and hasattr(value, 'attrName'):
        return _coerce_attr(str(value))
    if isinstance(value, str) and '.' in value:
        from ..nodes.base import Node

        node_name, attr_name = value.split('.', 1)
        return Node.from_name(node_name).attr(attr_name)
    raise TypeError(f"Cannot resolve attribute from {value!r}")
