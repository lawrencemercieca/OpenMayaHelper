"""Static contract tests for a PyMEL-compatible, OpenMaya-first facade."""

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
    def test_core_module_does_not_import_pymel(self):
        imports = imported_modules("core/__init__.py")
        self.assertNotIn(
            "pymel.core",
            imports,
            "mymaya.core must not depend on pymel.core for import-time behavior.",
        )

    def test_compat_module_does_not_import_pymel(self):
        imports = imported_modules("compat.py")
        self.assertNotIn(
            "pymel.core",
            imports,
            "compat.py still imports pymel.core directly, which blocks drop-in replacement.",
        )

    def test_core_module_does_not_delegate_unknown_symbols_to_pymel(self):
        source = read_module("core/__init__.py")
        self.assertNotIn(
            "return getattr(_pm, name)",
            source,
            "Delegating unresolved names to pymel.core hides missing local implementations.",
        )

    def test_nodetypes_are_not_declared_as_tuples(self):
        source = read_module("core/__init__.py")
        self.assertNotIn(
            "Transform = (_WrappedTransform, _pm.nodetypes.Transform)",
            source,
            "nodetypes should expose callable node classes, not tuples of wrappers and PyMEL types.",
        )


if __name__ == "__main__":
    unittest.main()

