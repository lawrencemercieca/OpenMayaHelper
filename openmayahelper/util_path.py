"""Small pathlib-style wrapper."""

from __future__ import annotations

from pathlib import Path


class path:
    def __init__(self, value):
        self._path = Path(value)

    def exists(self):
        return self._path.exists()

    def isfile(self):
        return self._path.is_file()

    def isdir(self):
        return self._path.is_dir()

    def basename(self):
        return path(self._path.name)

    @property
    def namebase(self):
        return self._path.stem

    @property
    def ext(self):
        return self._path.suffix

    def dirname(self):
        return str(self._path.parent)

    def files(self):
        if not self.isdir():
            return []
        return [path(item) for item in self._path.iterdir() if item.is_file()]

    def __str__(self):
        return str(self._path)

    def __fspath__(self):
        return str(self._path)

    def __eq__(self, other):
        return str(self) == str(other)
