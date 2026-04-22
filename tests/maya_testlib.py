"""Test helpers for Maya / PyMEL compatibility checks."""

from __future__ import annotations

import importlib
import importlib.util
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SITE_PACKAGES_ROOT = PACKAGE_ROOT.parent

if str(SITE_PACKAGES_ROOT) not in sys.path:
    sys.path.insert(0, str(SITE_PACKAGES_ROOT))


def has_module(module_name: str) -> bool:
    """Return True when a module can be imported in the current interpreter."""
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def import_module(module_name: str):
    return importlib.import_module(module_name)


def reset_scene():
    cmds = import_module("maya.cmds")
    cmds.file(new=True, force=True)
    return cmds


def requires_maya(test_case: unittest.TestCase) -> None:
    if not has_module("maya.cmds"):
        raise unittest.SkipTest("Maya is not available; run these tests under mayapy.")


def requires_pymel(test_case: unittest.TestCase) -> None:
    requires_maya(test_case)
    if not has_module("pymel.core"):
        raise unittest.SkipTest("PyMEL is not available; install it to run comparison tests.")


class MayaTestCase(unittest.TestCase):
    """Base class for tests that require Maya."""

    @classmethod
    def setUpClass(cls):
        requires_maya(cls)

    def setUp(self):
        self.cmds = reset_scene()


class MayaPyMELCompareTestCase(MayaTestCase):
    """Base class for tests that compare mymaya against PyMEL."""

    @classmethod
    def setUpClass(cls):
        requires_pymel(cls)

