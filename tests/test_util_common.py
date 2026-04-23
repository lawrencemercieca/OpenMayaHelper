"""OpenMayaHelper port of PyMEL's test_util_common module."""

from __future__ import annotations

import unittest

from openmayahelper.util_common import (
    CappedBuffer,
    CharacterBufferFromIterable,
    FormatError,
    handleChar,
    handleDecimalInt,
    handleString,
    handleWhitespace,
    makeCharBuffer,
    sscanf,
)


class UtilCommonTests(unittest.TestCase):
    def test_buffer_and_ungetch(self):
        buffer = CharacterBufferFromIterable("ong")
        buffer.ungetch("y")
        self.assertEqual(buffer.getch(), "y")
        self.assertEqual(buffer.getch(), "o")

    def test_scanning_helpers(self):
        buffer = makeCharBuffer("    42 hi")
        self.assertEqual(handleWhitespace(buffer), "    ")
        self.assertEqual(handleDecimalInt(buffer), 42)
        self.assertEqual(handleWhitespace(buffer), " ")
        self.assertEqual(handleString(buffer), "hi")
        with self.assertRaises(FormatError):
            handleChar(CharacterBufferFromIterable(""))

    def test_sscanf_and_capped_buffer(self):
        self.assertEqual(sscanf("   42\n   43  ", "%d %d"), (42, 43))
        self.assertEqual(sscanf("   hello world", "%s %s"), ("hello", "world"))
        buffer = CappedBuffer(CharacterBufferFromIterable("super"), 3)
        self.assertEqual(buffer.getch(), "s")
        self.assertEqual(buffer.getch(), "u")
        self.assertEqual(buffer.getch(), "p")
        self.assertEqual(buffer.getch(), "")
