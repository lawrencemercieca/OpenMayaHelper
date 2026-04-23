"""Curve operations implemented with MFnNurbsCurve."""

from maya.api import OpenMaya as om

from ..nodes.nurbs_curve import NurbsCurve


def _coerce_curve(curve):
    return curve if isinstance(curve, NurbsCurve) else NurbsCurve.from_name(curve)


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
