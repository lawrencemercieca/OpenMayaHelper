"""OpenMayaHelper port of PyMEL's test_datatypes module."""

from __future__ import annotations

import unittest

from openmayahelper.datatypes import Point, Vector


class DataTypesTests(unittest.TestCase):
    def test_vector_attrs_and_assignment(self):
        vector = Vector()
        self.assertEqual(vector.shape, (3,))
        self.assertEqual(vector.ndim, 1)
        self.assertEqual(vector.size, 3)
        vector.assign(Vector(1, 2, 3))
        self.assertEqual((vector.x, vector.y, vector.z), (1.0, 2.0, 3.0))

    def test_vector_construction_and_indexing(self):
        vector = Vector([1, 2], z=3)
        vector[0:2] = [4, 5]
        self.assertEqual(vector(0), 4.0)
        self.assertEqual(vector(5), 3.0)
        self.assertEqual(vector, Vector(4, 5, 3))

    def test_point_defaults_w_component(self):
        point = Point(1, 2, 3)
        self.assertEqual(point, Point([1, 2, 3, 1]))
