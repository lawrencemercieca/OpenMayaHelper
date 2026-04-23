"""Convenience functions for attribute connections."""

from ..attrs.attr import _coerce_attr


def connect(source, destination):
    return _coerce_attr(source).connect(_coerce_attr(destination))


def disconnect(source, destination):
    return _coerce_attr(source).disconnect(_coerce_attr(destination))
