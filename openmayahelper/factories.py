"""Small conversion helpers and API enum maps."""

from __future__ import annotations

try:
    import maya.OpenMaya as om
except ImportError:  # pragma: no cover
    om = None


def _build_api_maps():
    if om is None:
        return {}, {}
    type_to_enum = {}
    enum_to_type = {}
    for name in dir(om.MFn):
        if not name.startswith("k"):
            continue
        value = getattr(om.MFn, name)
        if not isinstance(value, int):
            continue
        type_to_enum[name] = value
        enum_to_type.setdefault(value, name)
    return type_to_enum, enum_to_type


apiTypesToApiEnums, apiEnumsToApiTypes = _build_api_maps()


def maybeConvert(value, converter):
    if isinstance(value, list):
        return [maybeConvert(item, converter) for item in value]
    try:
        return converter(value)
    except Exception:
        return value
