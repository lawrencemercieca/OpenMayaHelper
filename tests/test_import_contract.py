"""Static contract tests for an OpenMaya-first facade."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def read_module(relative_path: str) -> str:
    return (PACKAGE_ROOT / relative_path).read_text(encoding="utf-8")


def imported_modules(relative_path: str) -> set[str]:
    tree = ast.parse(read_module(relative_path), filename=relative_path)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


class ImportContractTests(unittest.TestCase):
    FORBIDDEN_FRAGMENT = "py" + "mel"

    def test_core_module_does_not_reference_legacy_dependency(self):
        imports = imported_modules("openmayahelper/core/__init__.py")
        source = read_module("openmayahelper/core/__init__.py").lower()
        self.assertFalse(
            any(self.FORBIDDEN_FRAGMENT in name.lower() for name in imports),
            "openmayahelper.core must not depend on the legacy package for import-time behavior.",
        )
        self.assertNotIn(self.FORBIDDEN_FRAGMENT, source)

    def test_compat_module_does_not_reference_legacy_dependency(self):
        imports = imported_modules("openmayahelper/compat.py")
        source = read_module("openmayahelper/compat.py").lower()
        self.assertFalse(
            any(self.FORBIDDEN_FRAGMENT in name.lower() for name in imports),
            "compat.py must not depend on the legacy package.",
        )
        self.assertNotIn(self.FORBIDDEN_FRAGMENT, source)

    def test_nodetypes_are_declared_as_factories(self):
        source = read_module("openmayahelper/compat.py")
        self.assertIn("_NodeTypeFactory", source)
        self.assertNotIn("= (_Wrapped", source)


if __name__ == "__main__":
    unittest.main()
