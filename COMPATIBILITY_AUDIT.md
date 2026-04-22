# mymaya Compatibility Audit

This package is not yet a drop-in `pymel.core` replacement.

Highest-value gaps found from the current source:

1. `mymaya.core` still imports `pymel.core` directly.
   `core/__init__.py` and `compat.py` both require PyMEL at import time, which defeats the goal of replacing `from pymel.core import ...` with `from mymaya.core import ...`.

2. `mymaya.core` delegates missing names back to PyMEL.
   `core/__init__.py::__getattr__` forwards unresolved symbols to `pymel.core`, so missing coverage is hidden instead of implemented locally.

3. `pm.nt` is not PyMEL-compatible yet.
   `nt.Transform`, `nt.Joint`, and related entries are tuples of `(mymaya wrapper, pymel nodetype)` instead of callable nodetype classes.

4. The public surface is far smaller than `pymel.core`.
   Only a narrow set of scene helpers is exported locally. Core names such as `about`, `playbackOptions`, and broad wrapped command coverage currently depend on PyMEL passthrough behavior.

5. DAG behavior is still minimal.
   The wrappers do not yet expose major PyMEL-style methods such as `getParent`, `getChildren`, `getShape`, `setParent`, `fullPath`, `longName`, and related DAG traversal helpers.

6. Attribute behavior is still minimal.
   The current `Attr` wrapper lacks important PyMEL semantics such as alias handling, parent/child traversal, indexed compound access, richer typed values, and stable identity behavior across renames.

7. Transform and animation coverage is incomplete.
   `Transform` exposes a `translation` property and `set_translation`, but not PyMEL-style `getTranslation` / `setTranslation` methods. `AnimCurve` coverage is also much smaller than the PyMEL API.

The tests under `tests/` are intended to make these gaps measurable:

- `test_import_contract.py` catches hard PyMEL dependencies and tuple-based nodetype declarations.
- `test_general_compat.py` covers common `pymel.core` usage patterns.
- `test_nodetypes_compat.py` covers first-pass nodetype expectations.
- `test_surface_compare.py` compares `mymaya.core` directly against `pymel.core` when both are installed in Maya.

Recommended execution:

```powershell
mayapy -m unittest discover -s D:\plastic\ctech\site-packages\mymaya\tests -v
```

If PyMEL is installed in that Maya environment, the side-by-side comparison tests will run as well.
