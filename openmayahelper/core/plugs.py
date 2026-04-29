"""MPlug utility helpers with PyMEL-style compatibility."""

from maya.api import OpenMaya as om

from .objects import as_name, get_mobject


_NUMERIC_SETTERS = {
    om.MFnNumericData.kBoolean: "setBool",
    om.MFnNumericData.kByte: "setChar",
    om.MFnNumericData.kChar: "setChar",
    om.MFnNumericData.kShort: "setShort",
    om.MFnNumericData.kInt: "setInt",
    om.MFnNumericData.kLong: "setInt",
    om.MFnNumericData.kFloat: "setFloat",
    om.MFnNumericData.kDouble: "setDouble",
}


def split_plug_name(plug_name):
    """Split ``node.attr`` into ``(node, attr)``.

    Unlike ``str.split('.')`` this keeps child/compound attr paths intact.
    """
    if not isinstance(plug_name, str):
        plug_name = as_name(plug_name)
    if "." not in plug_name:
        raise ValueError("Expected a plug name in 'node.attr' form")
    return plug_name.split(".", 1)


def _plug_from_pymel_attr(value):
    # PyMEL Attribute objects expose __apimplug__ in supported Maya versions.
    method = getattr(value, "__apimplug__", None)
    if callable(method):
        try:
            plug = method()
            if isinstance(plug, om.MPlug):
                return plug
        except Exception:
            pass
    return None


def find_plug(node_or_name, attr_name=None, want_networked_plug=True):
    """Return an ``MPlug`` from PyMEL/OpenMaya/string-style inputs.

    Accepted forms:
        ``find_plug('pCube1.tx')``
        ``find_plug('pCube1', 'tx')``
        ``find_plug(PyNode('pCube1'), 'tx')``
        ``find_plug(PyNode('pCube1').tx)``
        ``find_plug(MObject, 'tx')``
        ``find_plug(MPlug)``
    """
    if isinstance(node_or_name, om.MPlug):
        return om.MPlug(node_or_name)

    pymel_plug = _plug_from_pymel_attr(node_or_name)
    if pymel_plug is not None and attr_name is None:
        return pymel_plug

    if attr_name is None:
        node_name, attr_name = split_plug_name(node_or_name)
        node_or_name = node_name

    mobject = get_mobject(node_or_name)
    fn = om.MFnDependencyNode(mobject)
    return fn.findPlug(attr_name, want_networked_plug)


# PyMEL-friendly alias.
as_plug = find_plug


def plug_name(plug):
    """Return a full plug name for a plug-like input."""
    return find_plug(plug).name()


def get_plug_value(plug):
    """Return a Python value from a simple MPlug.

    Compound/multi attrs return child/element values recursively where practical.
    For complex typed data, the raw MObject data handle is returned.
    """
    plug = find_plug(plug)

    if plug.isArray:
        return [get_plug_value(plug.elementByPhysicalIndex(i)) for i in range(plug.numElements())]

    if plug.isCompound:
        return [get_plug_value(plug.child(i)) for i in range(plug.numChildren())]

    attr = plug.attribute()

    if attr.hasFn(om.MFn.kNumericAttribute):
        unit_type = om.MFnNumericAttribute(attr).unitType()
        if unit_type == om.MFnNumericData.kBoolean:
            return plug.asBool()
        if unit_type in (om.MFnNumericData.kFloat, om.MFnNumericData.kDouble):
            return plug.asDouble()
        return plug.asInt()

    if attr.hasFn(om.MFn.kTypedAttribute):
        attr_type = om.MFnTypedAttribute(attr).attrType()
        if attr_type == om.MFnData.kString:
            return plug.asString()
        return plug.asMObject()

    if attr.hasFn(om.MFn.kUnitAttribute):
        unit_type = om.MFnUnitAttribute(attr).unitType()
        if unit_type == om.MFnUnitAttribute.kAngle:
            return plug.asMAngle()
        if unit_type == om.MFnUnitAttribute.kDistance:
            return plug.asMDistance()
        if unit_type == om.MFnUnitAttribute.kTime:
            return plug.asMTime()

    if attr.hasFn(om.MFn.kEnumAttribute):
        return plug.asInt()

    try:
        return plug.asString()
    except Exception:
        return plug.asMObject()


def set_plug_value(plug, value, modifier=None):
    """Set a simple MPlug value.

    If ``modifier`` is supplied, supported values are queued on the modifier;
    otherwise they are applied immediately. This mirrors PyMEL-style convenience
    while allowing batch-friendly OpenMaya usage.
    """
    plug = find_plug(plug)

    if modifier is not None:
        if isinstance(value, bool):
            modifier.newPlugValueBool(plug, value)
        elif isinstance(value, int):
            modifier.newPlugValueInt(plug, value)
        elif isinstance(value, float):
            modifier.newPlugValueDouble(plug, value)
        elif isinstance(value, str):
            modifier.newPlugValueString(plug, value)
        else:
            raise TypeError("Modifier plug setting only supports bool/int/float/str values")
        return plug

    if isinstance(value, bool):
        plug.setBool(value)
        return plug
    if isinstance(value, int) and not isinstance(value, bool):
        plug.setInt(value)
        return plug
    if isinstance(value, float):
        plug.setDouble(value)
        return plug
    if isinstance(value, str):
        plug.setString(value)
        return plug

    if isinstance(value, om.MAngle):
        plug.setMAngle(value)
        return plug
    if isinstance(value, om.MDistance):
        plug.setMDistance(value)
        return plug
    if isinstance(value, om.MTime):
        plug.setMTime(value)
        return plug

    if isinstance(value, (tuple, list)) and plug.isCompound:
        if len(value) != plug.numChildren():
            raise ValueError("Compound value length does not match plug child count")
        for index, child_value in enumerate(value):
            set_plug_value(plug.child(index), child_value)
        return plug

    raise TypeError("Unsupported plug value type: {!r}".format(type(value).__name__))


def connect_plugs(source, destination, force=False, modifier=None):
    """Connect two plugs using ``MDGModifier``.

    This is the OpenMaya equivalent of ``cmds.connectAttr``/PyMEL ``connect``.
    """
    source_plug = find_plug(source)
    destination_plug = find_plug(destination)

    mod = modifier or om.MDGModifier()

    if force:
        for existing in destination_plug.connectedTo(True, False):
            mod.disconnect(existing, destination_plug)

    mod.connect(source_plug, destination_plug)

    if modifier is None:
        mod.doIt()

    return destination_plug


def disconnect_plugs(source, destination, modifier=None):
    """Disconnect two plugs using ``MDGModifier``."""
    source_plug = find_plug(source)
    destination_plug = find_plug(destination)

    mod = modifier or om.MDGModifier()
    mod.disconnect(source_plug, destination_plug)

    if modifier is None:
        mod.doIt()

    return destination_plug


# PyMEL/cmds-inspired aliases.
getAttr = get_plug_value
setAttr = set_plug_value
connectAttr = connect_plugs
disconnectAttr = disconnect_plugs
