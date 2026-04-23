"""Base node wrapper."""

from maya import cmds
from maya.api import OpenMaya as om

from ..attrs.attr import Attr


class _CallableString(str):
    """String subclass that can also be called to return itself."""

    def __call__(self):
        return self

    def __eq__(self, other):
        return str(self) == str(other)

    __hash__ = str.__hash__


class Node:
    """Thin wrapper around a Maya dependency node."""

    def __init__(self, mobject, dag_path=None):
        self._mobject = mobject
        self._dag_path = dag_path

    @classmethod
    def from_name(cls, name):
        from ..registry import wrap_node

        return wrap_node(name)

    @property
    def mobject(self):
        return self._mobject

    @property
    def dag_path(self):
        return self._dag_path

    @property
    def fn(self):
        return om.MFnDependencyNode(self.mobject)

    @property
    def name(self):
        return _CallableString(self.fn.name())

    @property
    def type_name(self):
        return self.fn.typeName

    def attr(self, name):
        return Attr(self, name)

    def has_attr(self, name):
        try:
            self.fn.findPlug(name, True)
            return True
        except RuntimeError:
            return False

    def hasAttr(self, name):
        return self.has_attr(name)

    def addAttr(self, name=None, **kwargs):
        attr_name = kwargs.pop('longName', name)
        if not attr_name:
            raise ValueError('Attribute name is required')
        attr_type = kwargs.pop('type', None)
        if attr_type == 'string':
            kwargs['dataType'] = 'string'
        elif attr_type:
            kwargs['attributeType'] = attr_type
        cmds.addAttr(self.name, longName=attr_name, **kwargs)
        return self.attr(attr_name)

    def deleteAttr(self, name, **kwargs):
        attr_name = name.longName() if isinstance(name, Attr) else str(name)
        cmds.deleteAttr(f'{self.name}.{attr_name}')

    def setAttr(self, name, value):
        self.attr(name).set(value)
        return self

    def getAttr(self, name):
        return self.attr(name).get()

    def rename(self, new_name):
        cmds.rename(self.name, new_name)
        return self.from_name(new_name)

    def nodeName(self):
        return self.name

    def namespace(self):
        short_name = str(self.name).split('|')[-1]
        if ':' not in short_name:
            return ''
        return short_name.rsplit(':', 1)[0] + ':'

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)
        if self.has_attr(item):
            return self.attr(item)
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{item}'")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"
