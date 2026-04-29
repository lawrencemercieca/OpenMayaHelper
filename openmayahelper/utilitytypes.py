"""General-purpose type helpers."""

from __future__ import annotations

import types


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        instance = cls._instances.get(cls)
        if instance is None:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        elif args or kwargs:
            reset = getattr(instance, "_singleton_reset", None)
            if callable(reset):
                reset(*args, **kwargs)
        return instance


class Enum:
    def __init__(self, name, mapping, multiKeys=False, defaultKeys=None):
        self.name = name
        self.multiKeys = multiKeys
        self._items = _normalize_enum_mapping(mapping)
        self.mapping = dict(self._items)
        self.multiKeys = multiKeys
        self.defaultKeys = _build_default_keys(self._items, defaultKeys)
        self.reverse_mapping = {}
        for key, value in self._items:
            if value in self.reverse_mapping and not self.multiKeys:
                raise ValueError(f"Duplicate enum value {value!r} without multiKeys=True")
            self.reverse_mapping.setdefault(value, key)
        self.reverse_mapping.update(self.defaultKeys)

    def __getitem__(self, item):
        if item in self.mapping:
            return self.mapping[item]
        return self.reverse_mapping[item]

    def __eq__(self, other):
        if not isinstance(other, Enum):
            return NotImplemented
        return (
            self.name == other.name
            and self.mapping == other.mapping
            and self.multiKeys == other.multiKeys
            and self.defaultKeys == other.defaultKeys
        )

    def __hash__(self):
        return hash((self.name, tuple(sorted(self.mapping.items())), self.multiKeys, tuple(sorted(self.defaultKeys.items()))))

    def __repr__(self):
        return (
            f"Enum({self.name!r}, {self._items!r}, "
            f"multiKeys={self.multiKeys!r}, defaultKeys={self.defaultKeys!r})"
        )


class EquivalencePairs(dict):
    def __init__(self, pairs=()):
        super().__init__()
        if isinstance(pairs, EquivalencePairs):
            pairs = pairs.items()
        elif isinstance(pairs, dict):
            pairs = pairs.items()
        for left, right in pairs:
            self[left] = right

    def __setitem__(self, left, right):
        for key in (left, right):
            if key in self:
                partner = dict.__getitem__(self, key)
                dict.__delitem__(self, partner)
                dict.__delitem__(self, key)
        dict.__setitem__(self, left, right)
        dict.__setitem__(self, right, left)


def proxyClass(target_cls, proxy_name, dataAttrName="_data", makeDefaultInit=False):
    namespace = {"__doc__": target_cls.__doc__, "_proxy_target": target_cls}

    if makeDefaultInit:
        def __init__(self, *args, **kwargs):
            if len(args) == 1 and not kwargs and isinstance(args[0], target_cls):
                setattr(self, dataAttrName, args[0])
            else:
                setattr(self, dataAttrName, target_cls(*args, **kwargs))

        namespace["__init__"] = __init__

    def __getattr__(self, item):
        return getattr(getattr(self, dataAttrName), item)

    namespace["__getattr__"] = __getattr__

    for name, member in target_cls.__dict__.items():
        if name in namespace or name in {"__dict__", "__weakref__", "__new__", "__init__"}:
            continue
        if isinstance(member, classmethod):
            namespace[name] = classmethod(_wrap_classmethod(target_cls, member.__func__))
        elif isinstance(member, staticmethod):
            namespace[name] = staticmethod(member.__func__)
        elif isinstance(member, (types.FunctionType, types.MethodDescriptorType, types.WrapperDescriptorType)):
            namespace[name] = _wrap_instance_method(dataAttrName, name)
        elif not callable(member):
            namespace[name] = member

    return type(proxy_name, (object,), namespace)


def _wrap_classmethod(target_cls, func):
    def wrapper(cls, *args, **kwargs):
        del cls
        return func(target_cls, *args, **kwargs)

    return wrapper


def _wrap_instance_method(data_attr_name, method_name):
    def wrapper(self, *args, **kwargs):
        target = getattr(self, data_attr_name)
        return getattr(target, method_name)(*args, **kwargs)

    return wrapper


def _normalize_enum_mapping(mapping):
    if isinstance(mapping, dict):
        return list(mapping.items())
    values = list(mapping)
    if not values:
        return []
    first = values[0]
    if isinstance(first, str):
        return [(name, index) for index, name in enumerate(values)]
    return [(name, value) for name, value in values]


def _build_default_keys(items, default_keys):
    defaults = {}
    for key, value in items:
        defaults.setdefault(value, key)
    if default_keys:
        defaults.update(default_keys)
    return defaults
