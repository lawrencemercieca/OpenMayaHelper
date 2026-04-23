"""Small Maya utility helpers."""

from maya import cmds


def getMayaVersion():
    """Return Maya's API version integer."""
    return cmds.about(api=True)
