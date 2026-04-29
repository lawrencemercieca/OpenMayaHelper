"""PyMEL-style attribute connection helpers backed by OpenMaya."""

from __future__ import annotations

from maya.api import OpenMaya as om

from .attr import Attr, _coerce_attr


def connect_plugs(source, destination, force=True, nextAvailable=False, **kwargs):
    """Connect two attributes.

    Accepts Attr, MPlug, ``"node.attr"`` strings, PyMEL attributes, or objects
    exposing a compatible ``plug`` property.
    """
    source_attr = _coerce_attr(source)
    destination_attr = _coerce_attr(destination)
    return source_attr.connect(destination_attr, force=force, nextAvailable=nextAvailable, **kwargs)


def disconnect_plugs(source, destination=None):
    """Disconnect attributes.

    If ``destination`` is omitted, all incoming and outgoing connections on
    ``source`` are disconnected, mirroring PyMEL's convenience behaviour.
    """
    source_attr = _coerce_attr(source)
    return source_attr.disconnect(destination) if destination is not None else source_attr.disconnect()


def is_connected(source, destination=None):
    source_attr = _coerce_attr(source)
    if destination is None:
        return source_attr.isConnected()
    destination_attr = _coerce_attr(destination)
    return any(dest == destination_attr for dest in source_attr.destinations())


def list_input_plugs(attr):
    attr = _coerce_attr(attr)
    source = attr.plug.source()
    return [] if source.isNull else [Attr.from_plug(source)]


def list_output_plugs(attr):
    attr = _coerce_attr(attr)
    return [Attr.from_plug(plug) for plug in attr.plug.destinations()]


def connection_pairs(attr):
    """Return ``(source, destination)`` Attr pairs touching attr."""
    attr = _coerce_attr(attr)
    pairs = []
    source = attr.source()
    if source is not None:
        pairs.append((source, attr))
    for destination in attr.destinations():
        pairs.append((attr, destination))
    return pairs
