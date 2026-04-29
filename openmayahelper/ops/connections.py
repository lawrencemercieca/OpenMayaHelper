"""Convenience functions for attribute connections."""

from maya.api import OpenMaya as om

from ..attrs.attr import Attr, _coerce_attr


def _as_attr(value):
    if isinstance(value, Attr):
        return value
    if isinstance(value, om.MPlug):
        from ..attrs.attr import _attr_from_plug

        return _attr_from_plug(value)
    return _coerce_attr(value)


def connect(source, destination, force=True):
    """Connect two attributes and return the destination, matching PyMEL style."""
    return _as_attr(source).connect(_as_attr(destination), force=force)


def disconnect(source, destination=None):
    """Disconnect attributes.

    If destination is omitted, disconnect all outgoing destinations from source.
    """
    source_attr = _as_attr(source)
    if destination is None:
        for dest in source_attr.destinations():
            source_attr.disconnect(dest)
        return source_attr
    return source_attr.disconnect(_as_attr(destination))


def list_connections(attr, **kwargs):
    return _as_attr(attr).listConnections(**kwargs)


# PyMEL/cmds-style aliases.
connectAttr = connect
disconnectAttr = disconnect
listConnections = list_connections
