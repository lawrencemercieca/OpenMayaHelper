"""Test helpers for Maya compatibility checks."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import atexit
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEST_MAYA_APP_DIR = Path(tempfile.gettempdir()) / "openmayahelper_test_maya_app_dir"

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

TEST_MAYA_APP_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MAYA_APP_DIR", str(TEST_MAYA_APP_DIR))
os.environ.setdefault("MAYA_SKIP_USERSETUP_PY", "1")


_MAYA_INITIALIZED = False
_MAYA_SHUTDOWN_REGISTERED = False


def ensure_maya_initialized() -> None:
    """Initialize Maya standalone when running under mayapy."""
    global _MAYA_INITIALIZED, _MAYA_SHUTDOWN_REGISTERED
    if _MAYA_INITIALIZED:
        return

    try:
        from maya import cmds
    except ImportError:
        return

    if hasattr(cmds, "file"):
        _MAYA_INITIALIZED = True
        return

    try:
        from maya import standalone

        standalone.initialize(name="python")
    except Exception:
        return

    if not _MAYA_SHUTDOWN_REGISTERED:
        def _shutdown_maya():
            try:
                from maya import cmds as maya_cmds

                if maya_cmds.pluginInfo("polyBoolean", query=True, loaded=True):
                    maya_cmds.unloadPlugin("polyBoolean", force=True)
            except Exception:
                pass
            try:
                standalone.uninitialize()
            except Exception:
                pass
            try:
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception:
                pass

        atexit.register(_shutdown_maya)
        _MAYA_SHUTDOWN_REGISTERED = True

    importlib.import_module("maya.cmds")
    _MAYA_INITIALIZED = True


def has_module(module_name: str) -> bool:
    """Return True when a module can be imported in the current interpreter."""
    try:
        if module_name.startswith("maya."):
            ensure_maya_initialized()
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def import_module(module_name: str):
    if module_name.startswith("maya.") or module_name.startswith("openmayahelper"):
        ensure_maya_initialized()
    return importlib.import_module(module_name)


def reset_scene():
    cmds = import_module("maya.cmds")
    cmds.file(new=True, force=True)
    return cmds


def requires_maya(test_case: unittest.TestCase) -> None:
    if not has_module("maya.cmds"):
        raise unittest.SkipTest("Maya is not available; run these tests under mayapy.")


class MayaTestCase(unittest.TestCase):
    """Base class for tests that require Maya."""

    @classmethod
    def setUpClass(cls):
        requires_maya(cls)

    def setUp(self):
        self.cmds = reset_scene()
