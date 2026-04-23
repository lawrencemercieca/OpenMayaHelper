"""OpenMayaHelper port of PyMEL's test_util_arrays module."""

from __future__ import annotations

import unittest

from openmayahelper.util_arrays import Array


class UtilArraysTests(unittest.TestCase):
    def test_true_division(self):
        self.assertEqual(Array(1, 2, 3) / 2, Array(0.5, 1, 1.5))
        self.assertEqual(2 / Array(1, 2, 4), Array(2, 1, 0.5))

    def test_floor_division(self):
        self.assertEqual(Array(1, 2, 3) // 2, Array(0, 1, 1))
        self.assertEqual(2 // Array(1, 2, 4), Array(2, 1, 0))

    def test_modulus(self):
        self.assertEqual(Array(1, 2, 3) % 2, Array(1, 0, 1))
        self.assertEqual(2 % Array(1, 2, 4), Array(0, 0, 2))
