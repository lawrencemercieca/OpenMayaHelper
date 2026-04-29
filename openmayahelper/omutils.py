"""OpenMaya utility helpers used by the PyMEL-compatible surface.

The helpers intentionally accept PyMEL-like inputs: wrapper objects, strings,
MObjects, MDagPaths, and MPlugs.  They return Maya Python API 2.0 objects where
possible and fall back cleanly for commands that are still simpler through cmds.
"""

from __future__ import annotations

from maya.api import OpenMaya as om


def name_of(value):
    """Return a Maya node/plug name for strings, wrappers, MObjects, and MPlugs."""
    if isinstance(value, str):
        return value
    if isinstance(value, om.MPlug):
        return value.name()
    if isinstance(value, om.MObject):
        return om.MFnDependencyNode(value).absoluteName()
    if isinstance(value, om.MDagPath):
        return value.fullPathName()
    if hasattr(value, "full_name"):
        return str(value.full_name)
    if hasattr(value, "name"):
        attr = getattr(value, "name")
        return str(attr() if callable(attr) else attr)
    return str(value)


def selection_list(value):
    sel = om.MSelectionList()
    if isinstance(value, om.MSelectionList):
        return value
    if isinstance(value, (list, tuple, set)):
        for item in value:
            sel.add(name_of(item))
    else:
        sel.add(name_of(value))
    return sel


def mobject(value):
    """Resolve a node-like value to an MObject."""
    if isinstance(value, om.MObject):
        return value
    if isinstance(value, om.MDagPath):
        return value.node()
    if isinstance(value, om.MPlug):
        return value.node()
    sel = selection_list(value)
    try:
        return sel.getDependNode(0)
    except RuntimeError:
        return sel.getDagPath(0).node()


def dag_path(value):
    """Resolve a DAG node-like value to an MDagPath."""
    if isinstance(value, om.MDagPath):
        return value
    sel = selection_list(value)
    return sel.getDagPath(0)


def plug(value):
    """Resolve a plug-like value to an MPlug."""
    if isinstance(value, om.MPlug):
        return value
    text = name_of(value)
    if "." not in text:
        raise ValueError("Expected a plug path such as 'node.attr'")
    sel = selection_list(text)
    return sel.getPlug(0)


def node_type(value):
    return om.MFnDependencyNode(mobject(value)).typeName


def mplug_value(mplug):
    """Read common scalar plug values through OpenMaya API 2.0."""
    attr = mplug.attribute()
    if attr.hasFn(om.MFn.kNumericAttribute):
        unit = om.MFnNumericAttribute(attr).numericType()
        if unit in (om.MFnNumericData.kBoolean,):
            return mplug.asBool()
        if unit in (om.MFnNumericData.kByte, om.MFnNumericData.kShort, om.MFnNumericData.kInt, om.MFnNumericData.kLong):
            return mplug.asInt()
        if unit in (om.MFnNumericData.kFloat, om.MFnNumericData.kDouble):
            return mplug.asDouble()
    if attr.hasFn(om.MFn.kTypedAttribute):
        typed = om.MFnTypedAttribute(attr).attrType()
        if typed == om.MFnData.kString:
            return mplug.asString()
    if attr.hasFn(om.MFn.kEnumAttribute):
        return mplug.asInt()
    raise TypeError(f"Unsupported OpenMaya plug value type: {mplug.name()}")


def set_mplug_value(mplug, value):
    """Set common scalar plug values through OpenMaya API 2.0."""
    mod = om.MDGModifier()
    if isinstance(value, bool):
        mod.newPlugValueBool(mplug, value)
    elif isinstance(value, int):
        mod.newPlugValueInt(mplug, value)
    elif isinstance(value, float):
        mod.newPlugValueDouble(mplug, value)
    elif isinstance(value, str):
        mod.newPlugValueString(mplug, value)
    else:
        raise TypeError(f"Unsupported OpenMaya plug value: {value!r}")
    mod.doIt()
    return None
