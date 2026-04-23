"""Plugin discovery helpers."""

from __future__ import annotations

import os


def _iter_plugin_names():
    plugin_path = os.environ.get("MAYA_PLUG_IN_PATH", "")
    seen = set()
    for directory in plugin_path.split(os.pathsep):
        if not directory or not os.path.isdir(directory):
            continue
        for entry in os.listdir(directory):
            base, ext = os.path.splitext(entry)
            if ext.lower() not in {".mll", ".py", ".so", ".bundle"}:
                continue
            if base in seen:
                continue
            seen.add(base)
            yield entry


def _matches_filter(plugin_name, filter_value):
    if isinstance(filter_value, str):
        return os.path.splitext(plugin_name)[0] == filter_value
    if hasattr(filter_value, "search"):
        return bool(filter_value.search(os.path.splitext(plugin_name)[0]))
    if callable(filter_value):
        return bool(filter_value(plugin_name))
    return False


def mayaPlugins(filters=None):
    plugins = list(_iter_plugin_names())
    if not filters:
        return plugins
    return [plugin for plugin in plugins if not any(_matches_filter(plugin, item) for item in filters)]
