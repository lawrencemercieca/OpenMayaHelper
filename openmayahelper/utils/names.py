"""Name utility helpers."""


def _to_name(value):
    if hasattr(value, "fullPath") and callable(value.fullPath):
        return str(value.fullPath())
    if hasattr(value, "name"):
        name = value.name
        return str(name() if callable(name) else name)
    return str(value)


def short_name(name):
    """Return the leaf portion of a DAG path."""
    return _to_name(name).rsplit("|", 1)[-1]


def strip_namespace(name):
    """Return the leaf name without namespace."""
    return short_name(name).rsplit(":", 1)[-1]


def namespace(name, include_trailing_colon=True):
    """Return the namespace for a node name."""
    ns, _leaf = split_namespace(name)
    if ns and include_trailing_colon:
        return ns + ":"
    return ns


def split_namespace(name):
    """Split a node name into namespace and leaf name.

    Returns:
        tuple[str, str]: namespace without trailing colon, leaf name.
    """
    short = short_name(name)
    if ":" not in short:
        return "", short
    return short.rsplit(":", 1)


def long_name(name):
    """Best-effort long/full-path name helper."""
    if hasattr(name, "fullPath") and callable(name.fullPath):
        return str(name.fullPath())
    if hasattr(name, "longName") and callable(name.longName):
        return str(name.longName())
    return _to_name(name)


# PyMEL-style aliases.
shortName = short_name
stripNamespace = strip_namespace
splitNamespace = split_namespace
longName = long_name
