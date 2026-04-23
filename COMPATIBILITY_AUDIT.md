# openmayahelper Compatibility Audit

This package is intended to be an OpenMaya-first replacement layer with a familiar high-level surface.

Highest-value gaps found from the current source:

1. The public surface is still much smaller than a full high-level scene API.
   Only a narrow set of scene helpers is exported locally. Core names such as `about`, `playbackOptions`, and broad wrapped command coverage still need expansion.

2. DAG behavior is still minimal.
   The wrappers do not yet expose major convenience methods such as `getParent`, `getChildren`, `getShape`, `setParent`, `fullPath`, `longName`, and related DAG traversal helpers.

3. Attribute behavior is still minimal.
   The current `Attr` wrapper lacks alias handling, parent/child traversal, indexed compound access, richer typed values, and stable identity behavior across renames.

4. Transform and animation coverage is incomplete.
   `Transform` exposes a `translation` property and `set_translation`, but not the higher-level `getTranslation` / `setTranslation` methods everywhere they are expected. `AnimCurve` coverage is also still narrow.

The tests under `tests/` are intended to keep these gaps measurable:

- `test_import_contract.py` catches forbidden legacy references and nodetype declaration regressions.
- `test_general_compat.py` covers common high-level scene workflows.
- `test_nodetypes_compat.py` covers first-pass nodetype expectations.
- `test_surface_compare.py` verifies the exported surface is internally consistent without extra package dependencies.

Recommended execution:

```powershell
mayapy -m unittest discover -s tests -v
```
