"""PyMEL-compatible attribute wrapper built on top of OpenMaya MPlug.

The goal of this module is to make common PyMEL Attribute call-sites work while
keeping the hot path on cached OpenMaya plugs.
"""

from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya as om


_NUMERIC_INT_TYPES = {
    om.MFnNumericData.kByte,
    om.MFnNumericData.kShort,
    om.MFnNumericData.kInt,
    om.MFnNumericData.kLong,
}

_NUMERIC_FLOAT_TYPES = {
    om.MFnNumericData.kFloat,
    om.MFnNumericData.kDouble,
    om.MFnNumericData.kAddr,
}


class Attr:
    """Thin PyMEL-style wrapper around a Maya ``MPlug``.

    Parameters
    ----------
    node:
        Your node wrapper, PyMEL node, node name, MObject, MDagPath, or None when
        constructing directly from an MPlug.
    name:
        Attribute name, full ``node.attr`` string, PyMEL attribute, or MPlug.
    plug:
        Optional pre-resolved MPlug. Passing this is the fastest path.
    """

    __slots__ = ("_node", "_name", "_plug")

    def __init__(self, node=None, name=None, plug=None):
        if plug is not None:
            self._node = node
            self._plug = _copy_plug(plug)
            self._name = _plug_attr_name(self._plug)
            return

        if isinstance(name, om.MPlug):
            self._node = node
            self._plug = _copy_plug(name)
            self._name = _plug_attr_name(self._plug)
            return

        if isinstance(node, om.MPlug) and name is None:
            self._node = None
            self._plug = _copy_plug(node)
            self._name = _plug_attr_name(self._plug)
            return

        if name is None and isinstance(node, str) and "." in node:
            node, name = node.split(".", 1)

        self._node = _coerce_node(node) if node is not None else None
        self._name = str(name) if name is not None else None
        self._plug = None

    @classmethod
    def from_plug(cls, plug):
        """Create an Attr from an existing MPlug without re-querying by name."""
        return cls(plug=_copy_plug(plug))

    @property
    def plug(self):
        """Cached OpenMaya MPlug."""
        if self._plug is None:
            if self._node is None or not self._name:
                raise ValueError("Attr requires a node and attribute name")
            self._plug = _find_plug(self._node, self._name)
        return self._plug

    @property
    def full_name(self):
        try:
            return self.plug.name()
        except RuntimeError:
            if self._node is None:
                return self._name or ""
            return f"{_node_name(self._node)}.{self._name}"

    def node(self):
        if self._node is not None:
            return self._node
        from ..registry import wrap_mobject

        self._node = wrap_mobject(self.plug.node())
        return self._node

    def nodeName(self):
        return _node_name(self.node())

    def attrName(self, longName=True):
        return self.longName() if longName else self.plug.partialName()

    def longName(self):
        return _plug_attr_name(self.plug)

    def name(self):
        return self.full_name

    def exists(self):
        try:
            return not self.plug.isNull
        except RuntimeError:
            return bool(cmds.objExists(self.full_name))

    def get(self, **kwargs):
        """Return the attribute value using OpenMaya where possible.

        Extra kwargs are accepted for PyMEL compatibility and forwarded to cmds
        only when needed.
        """
        if kwargs:
            return cmds.getAttr(self.full_name, **kwargs)

        plug = self.plug

        if plug.isArray:
            values = []
            for index in range(plug.numElements()):
                values.append(_get_plug_value(plug.elementByPhysicalIndex(index)))
            return values

        if plug.isCompound:
            return tuple(_get_plug_value(plug.child(i)) for i in range(plug.numChildren()))

        return _get_plug_value(plug)

    def set(self, value=None, *values, **kwargs):
        """Set the attribute value.

        Supports common PyMEL/cmds call patterns:
        ``attr.set(1)``, ``attr.set(1, 2, 3)``, ``attr.set(lock=True)``.
        """
        if kwargs:
            cmds.setAttr(self.full_name, **kwargs)
            if value is None and not values:
                return self

        if values:
            value = (value,) + values

        plug = self.plug
        if plug.isCompound and isinstance(value, (tuple, list)):
            for index, child_value in enumerate(value):
                if index >= plug.numChildren():
                    break
                _set_plug_value(plug.child(index), child_value)
            return self

        if plug.isArray and isinstance(value, (tuple, list)) and not _is_numeric_array_attr(plug):
            for index, item in enumerate(value):
                _set_plug_value(plug.elementByLogicalIndex(index), item)
            return self

        _set_plug_value(plug, value)
        return self

    def connect(self, other, force=True, nextAvailable=False, **kwargs):
        destination = _coerce_attr(other)
        if force:
            _disconnect_existing_destination(destination.plug)
        modifier = om.MDGModifier()
        modifier.connect(self.plug, destination.plug)
        modifier.doIt()
        return destination

    def disconnect(self, other=None):
        modifier = om.MDGModifier()
        if other is None:
            source = self.source()
            if source is not None:
                modifier.disconnect(source.plug, self.plug)
            for destination in self.destinations():
                modifier.disconnect(self.plug, destination.plug)
        else:
            modifier.disconnect(self.plug, _coerce_attr(other).plug)
        modifier.doIt()
        return self if other is None else other

    def listConnections(self, **kwargs):
        from .. import listConnections

        return listConnections(self, **kwargs)

    def inputs(self, plugs=False):
        source = self.source()
        if source is None:
            return []
        return [source if plugs else source.node()]

    def outputs(self, plugs=False):
        destinations = self.destinations()
        return destinations if plugs else [destination.node() for destination in destinations]

    def source(self):
        source_plug = self.plug.source()
        return None if source_plug.isNull else _attr_from_plug(source_plug)

    def destinations(self):
        return [_attr_from_plug(plug) for plug in self.plug.destinations()]

    def isConnected(self):
        plug = self.plug
        return bool(plug.isSource or plug.isDestination)

    def isSource(self):
        return bool(self.plug.isSource)

    def isDestination(self):
        return bool(self.plug.isDestination)

    def isHidden(self):
        return bool(cmds.addAttr(self.full_name, query=True, hidden=True))

    def isKeyable(self):
        return bool(cmds.getAttr(self.full_name, keyable=True))

    def setKeyable(self, state):
        cmds.setAttr(self.full_name, keyable=bool(state))
        return self

    def isLocked(self):
        try:
            return bool(self.plug.isLocked)
        except RuntimeError:
            return bool(cmds.getAttr(self.full_name, lock=True))

    def lock(self, checkReference=False):
        return self.setLocked(True, checkReference=checkReference)

    def unlock(self, checkReference=False):
        return self.setLocked(False, checkReference=checkReference)

    def setLocked(self, state, checkReference=False):
        if checkReference and cmds.referenceQuery(self.nodeName(), isNodeReferenced=True):
            raise AttributeError(f"{self.full_name} is referenced")
        self.plug.isLocked = bool(state)
        return self

    def isSettable(self):
        return bool(cmds.getAttr(self.full_name, settable=True))

    def delete(self):
        cmds.deleteAttr(self.full_name)
        return None

    def __rshift__(self, other):
        return self.connect(other)

    def __floordiv__(self, other):
        return self.disconnect(other)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"Attr({self.full_name!r})"

    def __eq__(self, other):
        try:
            return self.full_name == _coerce_attr(other).full_name
        except Exception:
            return False

    def __hash__(self):
        return hash(self.full_name)


def _copy_plug(plug):
    return om.MPlug(plug)


def _attr_from_plug(plug):
    return Attr.from_plug(plug)


def _coerce_attr(value):
    if isinstance(value, Attr):
        return value
    if isinstance(value, om.MPlug):
        return Attr.from_plug(value)
    if isinstance(value, str) and "." in value:
        node_name, attr_name = value.split(".", 1)
        return Attr(node_name, attr_name)
    if hasattr(value, "plug"):
        plug = value.plug
        if isinstance(plug, om.MPlug):
            return Attr.from_plug(plug)
    if hasattr(value, "node") and callable(getattr(value, "node")):
        try:
            return _coerce_attr(str(value))
        except Exception:
            pass
    raise TypeError(f"Cannot resolve attribute from {value!r}")


def _coerce_node(value):
    if value is None:
        return None
    if hasattr(value, "mobject"):
        return value
    if isinstance(value, (om.MObject, om.MDagPath, str)):
        from ..registry import wrap_mobject, wrap_node

        if isinstance(value, om.MDagPath):
            return wrap_mobject(value.node(), value)
        if isinstance(value, om.MObject):
            return wrap_mobject(value)
        return wrap_node(value)
    if hasattr(value, "__apimobject__"):
        from ..registry import wrap_mobject

        api_obj = value.__apimobject__()
        if isinstance(api_obj, om.MObject):
            return wrap_mobject(api_obj)
    return value


def _find_plug(node, attr_name):
    if hasattr(node, "attr") and not hasattr(node, "fn"):
        maybe_attr = node.attr(attr_name)
        if hasattr(maybe_attr, "plug") and isinstance(maybe_attr.plug, om.MPlug):
            return om.MPlug(maybe_attr.plug)
    if hasattr(node, "fn"):
        return node.fn.findPlug(attr_name, True)
    if hasattr(node, "mobject"):
        return om.MFnDependencyNode(node.mobject).findPlug(attr_name, True)
    if isinstance(node, om.MObject):
        return om.MFnDependencyNode(node).findPlug(attr_name, True)
    return om.MFnDependencyNode(_mobject_from_name(str(node))).findPlug(attr_name, True)


def _mobject_from_name(name):
    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDependNode(0)


def _node_name(node):
    if hasattr(node, "name"):
        name = node.name
        return str(name() if callable(name) else name)
    if hasattr(node, "mobject"):
        return om.MFnDependencyNode(node.mobject).name()
    if isinstance(node, om.MObject):
        return om.MFnDependencyNode(node).name()
    return str(node)


def _plug_attr_name(plug):
    return plug.partialName(useLongNames=True, includeNodeName=False)


def _get_plug_value(plug):
    attr_obj = plug.attribute()

    if attr_obj.hasFn(om.MFn.kNumericAttribute):
        numeric_attr = om.MFnNumericAttribute(attr_obj)
        numeric_type = numeric_attr.numericType()
        if numeric_type == om.MFnNumericData.kBoolean:
            return plug.asBool()
        if numeric_type in _NUMERIC_INT_TYPES:
            return plug.asInt()
        if numeric_type in _NUMERIC_FLOAT_TYPES:
            return plug.asDouble()

    if attr_obj.hasFn(om.MFn.kEnumAttribute):
        return plug.asInt()

    if attr_obj.hasFn(om.MFn.kTypedAttribute):
        try:
            return plug.asString()
        except RuntimeError:
            return cmds.getAttr(plug.name())

    try:
        return plug.asDouble()
    except RuntimeError:
        try:
            return plug.asString()
        except RuntimeError:
            return cmds.getAttr(plug.name())


def _set_plug_value(plug, value):
    if value is None:
        return
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
    if isinstance(value, om.MObject):
        plug.setMObject(value)
        return
    if isinstance(value, (om.MVector, om.MPoint)):
        value = (value.x, value.y, value.z)
    if isinstance(value, (tuple, list)):
        cmds.setAttr(plug.name(), *value)
        return
    cmds.setAttr(plug.name(), value)


def _is_numeric_array_attr(plug):
    try:
        return plug.attribute().hasFn(om.MFn.kNumericAttribute)
    except RuntimeError:
        return False


def _disconnect_existing_destination(destination_plug):
    source = destination_plug.source()
    if source.isNull:
        return
    modifier = om.MDGModifier()
    modifier.disconnect(source, destination_plug)
    modifier.doIt()
