"""Animation helpers built on OpenMayaAnim.

These functions are intentionally tolerant about inputs so they can be used from
PyMEL-style code, raw strings, this package's node wrappers, or OpenMaya types.
"""

from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma


def _coerce_mobject(value):
    """Return an MObject for a node-like value."""
    if isinstance(value, om.MObject):
        return value
    if hasattr(value, "mobject"):
        mobject = value.mobject
        return mobject() if callable(mobject) else mobject
    if hasattr(value, "__apimobject__"):
        return value.__apimobject__()

    selection = om.MSelectionList()
    selection.add(str(value))
    return selection.getDependNode(0)


def _coerce_anim_curve_fn(value):
    """Return an MFnAnimCurve for a node-like or curve-function value."""
    if isinstance(value, oma.MFnAnimCurve):
        return value
    return oma.MFnAnimCurve(_coerce_mobject(value))


def _num_keys(anim_curve_fn):
    """Handle Maya API versions where numKeys may be method-like/property-like."""
    value = anim_curve_fn.numKeys
    return value() if callable(value) else int(value)


def _as_mtime(value):
    if isinstance(value, om.MTime):
        return value
    return om.MTime(float(value), om.MTime.uiUnit())


def add_linear_keys(anim_curve, times, values, keep_existing_keys=False):
    """Add linear keys to an animation curve using batched OpenMaya calls.

    Args:
        anim_curve: curve name, PyMEL node, OpenMaya MObject, wrapper, or MFnAnimCurve.
        times: iterable of frame/time values or MTime objects.
        values: iterable of numeric keyed values.
        keep_existing_keys: if False, removes current keys before adding new ones.

    Returns:
        The original ``anim_curve`` argument for PyMEL-style chaining.
    """
    time_values = list(times)
    keyed_values = list(values)

    if len(time_values) != len(keyed_values):
        raise ValueError("times and values must have the same length")

    anim_curve_fn = _coerce_anim_curve_fn(anim_curve)

    if not keep_existing_keys:
        for index in range(_num_keys(anim_curve_fn) - 1, -1, -1):
            anim_curve_fn.remove(index)

    maya_times = om.MTimeArray()
    maya_values = om.MDoubleArray()

    for time_value in time_values:
        maya_times.append(_as_mtime(time_value))
    for keyed_value in keyed_values:
        maya_values.append(float(keyed_value))

    anim_curve_fn.addKeys(
        maya_times,
        maya_values,
        oma.MFnAnimCurve.kTangentLinear,
        oma.MFnAnimCurve.kTangentLinear,
        False,
    )
    return anim_curve


def clear_keys(anim_curve):
    """Remove all keys from an animation curve."""
    anim_curve_fn = _coerce_anim_curve_fn(anim_curve)
    for index in range(_num_keys(anim_curve_fn) - 1, -1, -1):
        anim_curve_fn.remove(index)
    return anim_curve


def key_count(anim_curve):
    """Return the number of keys on an animation curve."""
    return _num_keys(_coerce_anim_curve_fn(anim_curve))


# PyMEL-ish aliases.
numKeys = key_count
