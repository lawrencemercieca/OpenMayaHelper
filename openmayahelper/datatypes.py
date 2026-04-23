"""Lightweight math datatypes used by the compatibility surface."""

from __future__ import annotations


class _CoordinateBase:
    size = 0
    shape = ()
    ndim = 1

    def __init__(self, *values, **overrides):
        values = self._normalize(values)
        for index, axis in enumerate(self._axes()):
            if axis in overrides:
                values[index] = float(overrides[axis])
        self._values = values

    @classmethod
    def _axes(cls):
        return ("x", "y", "z", "w")[: cls.size]

    @classmethod
    def _normalize(cls, args):
        if not args:
            return cls._defaults()
        if len(args) == 1:
            value = args[0]
            if isinstance(value, _CoordinateBase):
                values = list(value)
            elif isinstance(value, (tuple, list)):
                values = list(value)
            else:
                values = [value]
        else:
            values = list(args)
        if len(values) == 1:
            values = values * min(cls.size, 3)
        values = [float(item) for item in values]
        while len(values) < cls.size:
            values.append(cls._defaults()[len(values)])
        return values[: cls.size]

    @classmethod
    def _defaults(cls):
        return [0.0] * cls.size

    def assign(self, value):
        self._values = self._normalize((value,))
        return self

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, item):
        return self._values[item]

    def __setitem__(self, item, value):
        if isinstance(item, slice):
            self._values[item] = [float(entry) for entry in value]
            return
        self._values[item] = float(value)

    def __call__(self, index):
        if index >= len(self._values):
            return self._values[-1]
        return self._values[index]

    def __eq__(self, other):
        try:
            return tuple(self) == tuple(other)
        except TypeError:
            return False


class Vector(_CoordinateBase):
    size = 3
    shape = (3,)

    x = property(lambda self: self._values[0], lambda self, value: self.__setitem__(0, value))
    y = property(lambda self: self._values[1], lambda self, value: self.__setitem__(1, value))
    z = property(lambda self: self._values[2], lambda self, value: self.__setitem__(2, value))


class Point(_CoordinateBase):
    size = 4
    shape = (4,)

    @classmethod
    def _defaults(cls):
        return [0.0, 0.0, 0.0, 1.0]

    x = property(lambda self: self._values[0], lambda self, value: self.__setitem__(0, value))
    y = property(lambda self: self._values[1], lambda self, value: self.__setitem__(1, value))
    z = property(lambda self: self._values[2], lambda self, value: self.__setitem__(2, value))
    w = property(lambda self: self._values[3], lambda self, value: self.__setitem__(3, value))
