"""Animation helpers built on OpenMayaAnim."""

from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma


def _get_depend_node(name):
    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDependNode(0)


def add_linear_keys(anim_curve_name, times, values, keep_existing_keys=False):
    """Add linear keys to an animation curve using array-based OpenMaya calls."""
    time_values = list(times)
    keyed_values = list(values)

    if len(time_values) != len(keyed_values):
        raise ValueError('times and values must have the same length')

    anim_curve_obj = _get_depend_node(anim_curve_name)
    anim_curve_fn = oma.MFnAnimCurve(anim_curve_obj)

    maya_times = om.MTimeArray()
    maya_values = om.MDoubleArray()

    for time_value in time_values:
        maya_times.append(om.MTime(time_value, om.MTime.uiUnit()))

    for keyed_value in keyed_values:
        maya_values.append(float(keyed_value))

    if not keep_existing_keys and anim_curve_fn.numKeys:
        for index in range(anim_curve_fn.numKeys - 1, -1, -1):
            anim_curve_fn.remove(index)

    anim_curve_fn.addKeys(
        maya_times,
        maya_values,
        oma.MFnAnimCurve.kTangentLinear,
        oma.MFnAnimCurve.kTangentLinear,
        False,
    )
    return anim_curve_name
