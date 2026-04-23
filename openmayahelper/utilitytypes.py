"""General-purpose type helpers."""

from __future__ import annotations


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
        self.mapping = dict(mapping)
        self.multiKeys = multiKeys
        self.defaultKeys = dict(defaultKeys or {})

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
