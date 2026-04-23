"""Element-wise array helpers."""

from __future__ import annotations


class Array(list):
    def __init__(self, *values):
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = tuple(values[0])
        super().__init__(values)

    def _binary(self, other, op):
        if isinstance(other, Array):
            return Array(op(a, b) for a, b in zip(self, other))
        return Array(op(item, other) for item in self)

    def _rbinary(self, other, op):
        return Array(op(other, item) for item in self)

    def __truediv__(self, other):
        return self._binary(other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        return self._rbinary(other, lambda a, b: a / b)

    def __itruediv__(self, other):
        self[:] = (self / other)
        return self

    def __floordiv__(self, other):
        return self._binary(other, lambda a, b: a // b)

    def __rfloordiv__(self, other):
        return self._rbinary(other, lambda a, b: a // b)

    def __ifloordiv__(self, other):
        self[:] = (self // other)
        return self

    def __mod__(self, other):
        return self._binary(other, lambda a, b: a % b)

    def __rmod__(self, other):
        return self._rbinary(other, lambda a, b: a % b)

    def __imod__(self, other):
        self[:] = (self % other)
        return self
