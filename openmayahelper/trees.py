"""Simple tree containers."""

from __future__ import annotations


class Tree:
    def __init__(self, *items, _parent=None):
        if len(items) == 1 and isinstance(items[0], tuple):
            items = items[0]
        if not items:
            raise ValueError("Tree requires at least one item")
        self.value = items[0]
        self._parent = _parent
        self._children = [self._coerce(item) for item in items[1:]]

    def _coerce(self, item):
        if isinstance(item, Tree):
            item._parent = self
            return item
        if isinstance(item, tuple):
            return Tree(*item, _parent=self)
        return Tree(item, _parent=self)

    def parent(self):
        return self._parent

    def child(self, index):
        return self._children[index]

    def __iter__(self):
        return iter(self._children)

    def __contains__(self, value):
        if self.value == value:
            return True
        return any(value in child for child in self._children)
