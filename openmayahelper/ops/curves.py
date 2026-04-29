"""Curve operations implemented with MFnNurbsCurve."""

from maya.api import OpenMaya as om

from ..nodes.nurbs_curve import NurbsCurve


def _coerce_curve(curve):
    if isinstance(curve, NurbsCurve):
        return curve
    if hasattr(curve, "fn_curve"):
        return curve
    if hasattr(curve, "getShape") and callable(curve.getShape):
        shape = curve.getShape()
        if shape is not None:
            return _coerce_curve(shape)
    return NurbsCurve.from_name(str(curve))


def get_cv_positions(curve, space=om.MSpace.kObject):
    return _coerce_curve(curve).cv_positions(space=space)


def set_cv_positions(curve, positions, space=om.MSpace.kObject):
    return _coerce_curve(curve).set_cv_positions(positions, space=space)


def offset_cvs(curve, offset, space=om.MSpace.kObject):
    curve = _coerce_curve(curve)
    delta = offset if isinstance(offset, om.MVector) else om.MVector(*offset)
    positions = [om.MPoint(point + delta) for point in curve.cv_positions(space=space)]
    curve.set_cv_positions(positions, space=space)
    return curve


def scale_cvs(curve, scale, pivot=(0.0, 0.0, 0.0), space=om.MSpace.kObject):
    curve = _coerce_curve(curve)
    sx, sy, sz = scale if isinstance(scale, (tuple, list)) else (scale, scale, scale)
    pivot = pivot if isinstance(pivot, om.MPoint) else om.MPoint(*pivot)
    positions = []
    for point in curve.cv_positions(space=space):
        vec = point - pivot
        positions.append(om.MPoint(pivot.x + vec.x * sx, pivot.y + vec.y * sy, pivot.z + vec.z * sz))
    curve.set_cv_positions(positions, space=space)
    return curve


# PyMEL-style aliases.
getCVPositions = get_cv_positions
setCVPositions = set_cv_positions
offsetCVs = offset_cvs
scaleCVs = scale_cvs
