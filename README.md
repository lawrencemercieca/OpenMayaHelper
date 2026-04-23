# OpenMayaHelper

OpenMayaHelper is an OpenMaya-first package intended to replace common high-level `pymel.core` workflows without depending on PyMEL.

The repository is structured as a normal Python package:

- `openmayahelper/` contains the distributable package code.
- `tests/` contains the top-level test suite.
- `benchmark_test.py` contains local Maya benchmarking and smoke-test helpers.

## Goals

- Provide a familiar high-level scene API on top of `maya.api.OpenMaya`
- Let projects swap from `pymel.core` usage to `openmayahelper.core`
- Keep the runtime free of any PyMEL dependency

## Package Surface

The primary import target is:

```python
import openmayahelper.core as pm
```

That surface exposes helpers such as `PyNode`, `createNode`, `ls`, `addAttr`, `getAttr`, `setAttr`, `connectAttr`, `nt`, `mel`, and `general`.

## Development

Run the static contract tests with a normal Python interpreter:

```powershell
python -m unittest tests.test_import_contract
```

Run the Maya-backed suite under `mayapy`:

```powershell
mayapy -m unittest discover -s tests -v
```
