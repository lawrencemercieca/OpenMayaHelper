"""Window-style helpers built on top of uitypes."""

from __future__ import annotations

from .uitypes import Menu, OptionMenu, PyUI, get_ui


def menu(target, q=False, numberOfItems=False):
    if isinstance(target, str):
        target = get_ui(target) or PyUI(target)
    if q and numberOfItems:
        return target.child_count()
    if isinstance(target, Menu):
        return target
    if isinstance(target, OptionMenu):
        return target
    return Menu(str(target))
