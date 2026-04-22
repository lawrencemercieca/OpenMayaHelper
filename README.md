# mymaya

`mymaya` is a lightweight Maya utility framework built around `maya.cmds` and `maya.api.OpenMaya`.

## Quick Start

```python
from mymaya import my

selected = my.selected
for node in selected:
    print(node.name, node.type_name)
```

```python
from mymaya import my

ctrl = my.get('ctrl_main')
print(ctrl.translate.get())
print(ctrl.translateX.get())
```

```python
from mymaya import my

source = my.get('ctrl_main').translateX
destination = my.get('joint1').translateX
source.connect(destination)
```

```python
from mymaya import my

with my.batch() as b:
    b.set('ctrl_main.translateX', 10.0)
    b.connect('ctrl_main.translateX', 'joint1.translateX')
    b.disconnect('oldDriver.output', 'joint1.translateX')
```

```python
from mymaya.ops.animation import add_linear_keys

add_linear_keys('animCurveTL1', [1, 5, 10], [0.0, 4.0, 8.0])
```

## Notes

- `my.selected` returns wrapped node objects.
- `my.ls()` wraps listed nodes into typed classes automatically.
- `my.get(name)` resolves one node into the appropriate wrapper.
- Curve operations live in `mymaya.ops.curves`.
- Animation curve bulk keying lives in `mymaya.ops.animation`.
