"""Small attribute connection helpers."""

from .attr import Attr, _coerce_attr


def connect_plugs(source, destination, force=True):
    source_attr = _coerce_attr(source) if not isinstance(source, Attr) else source
    destination_attr = _coerce_attr(destination) if not isinstance(destination, Attr) else destination
    return source_attr.connect(destination_attr, force=force)


def disconnect_plugs(source, destination):
    source_attr = _coerce_attr(source) if not isinstance(source, Attr) else source
    destination_attr = _coerce_attr(destination) if not isinstance(destination, Attr) else destination
    return source_attr.disconnect(destination_attr)
