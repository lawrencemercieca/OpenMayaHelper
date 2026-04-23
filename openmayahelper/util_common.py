"""Common text scanning helpers."""

from __future__ import annotations

import re


class FormatError(ValueError):
    pass


class IncompleteCaptureError(FormatError):
    pass


class CharacterBufferFromIterable:
    def __init__(self, value):
        self._items = list(value)
        self._pushback = []

    def getch(self):
        if self._pushback:
            return self._pushback.pop()
        if not self._items:
            return ""
        return self._items.pop(0)

    def ungetch(self, value):
        self._pushback.append(value)

    def scanCharacterSet(self, allowed, limit=None):
        result = []
        while limit is None or len(result) < limit:
            char = self.getch()
            if char and char in allowed:
                result.append(char)
                continue
            if char:
                self.ungetch(char)
            break
        return "".join(result)

    def scanPredicate(self, predicate):
        result = []
        while True:
            char = self.getch()
            if char and predicate(char):
                result.append(char)
                continue
            if char:
                self.ungetch(char)
            break
        return "".join(result)


class CappedBuffer:
    def __init__(self, buffer, cap):
        self._buffer = buffer
        self._remaining = cap
        self._pushback = []

    def getch(self):
        if self._pushback:
            return self._pushback.pop()
        if self._remaining <= 0:
            return ""
        self._remaining -= 1
        return self._buffer.getch()

    def ungetch(self, value):
        self._pushback.append(value)


def makeCharBuffer(value):
    return CharacterBufferFromIterable(value)


def handleWhitespace(buffer):
    return buffer.scanPredicate(str.isspace)


def handleChar(buffer):
    char = buffer.getch()
    if not char:
        raise FormatError("expected char")
    return char


def handleDecimalInt(buffer):
    token = buffer.scanPredicate(lambda char: char in "+-" or char.isdigit())
    if not token or token in {"+", "-"}:
        raise FormatError("expected integer")
    return int(token)


def handleString(buffer):
    token = buffer.scanPredicate(lambda char: not char.isspace())
    if not token:
        raise FormatError("expected string")
    return token


def sscanf(source, pattern):
    source = source.lstrip()
    tokens = pattern.split()
    results = []
    remaining = source
    for token in tokens:
        remaining = remaining.lstrip()
        if token == "%d":
            match = re.match(r"[+-]?\d+", remaining)
            if not match:
                raise IncompleteCaptureError(pattern)
            results.append(int(match.group(0)))
            remaining = remaining[match.end() :]
        elif token == "%s":
            match = re.match(r"\S+", remaining)
            if not match:
                raise IncompleteCaptureError(pattern)
            results.append(match.group(0))
            remaining = remaining[match.end() :]
        else:
            raise FormatError(token)
    return tuple(results)


def fscanf(source, pattern):
    return sscanf(source.read(), pattern)


def compile(pattern):
    return lambda source: sscanf(source, pattern)
