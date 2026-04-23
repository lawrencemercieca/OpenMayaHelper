"""Helpers for mirrored PyMEL test-port scaffolds."""

from __future__ import annotations

import unittest


def make_port_placeholder(module_name: str):
    class TestPortScaffold(unittest.TestCase):
        @unittest.skip(f"PyMEL test port scaffold for {module_name}; OpenMayaHelper equivalent not implemented yet.")
        def test_port_pending(self):
            pass

    TestPortScaffold.__name__ = f"TestPortScaffold_{module_name.replace('.', '_')}"
    return TestPortScaffold

