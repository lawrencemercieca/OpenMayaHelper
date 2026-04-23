"""OpenMayaHelper port of PyMEL's test_utilitytypes module."""

from __future__ import annotations

import unittest

from openmayahelper.utilitytypes import Enum, Singleton


class BasicSingleton(metaclass=Singleton):
    pass


class DictSingleton(dict, metaclass=Singleton):
    def _singleton_reset(self, *args, **kwargs):
        self.clear()
        self.update(*args, **kwargs)


class UtilityTypesTests(unittest.TestCase):
    def setUp(self):
        DictSingleton().clear()

    def test_singleton_reuses_instance(self):
        self.assertIs(BasicSingleton(), BasicSingleton())

    def test_dict_singleton_reinitializes_same_instance(self):
        instance = DictSingleton({"A": 1})
        self.assertEqual(instance, {"A": 1})
        self.assertIs(DictSingleton({}), instance)
        self.assertEqual(instance, {})

    def test_enum_equality_and_hash(self):
        enum1 = Enum("enum", {"foo": 1, "bar": 7})
        enum2 = Enum("enum", {"foo": 1, "bar": 7})
        enum3 = Enum("enum", {"foo": 1, "bar": 7, "baz": 7}, multiKeys=True, defaultKeys={7: "baz"})
        self.assertEqual(enum1, enum2)
        self.assertEqual(hash(enum1), hash(enum2))
        self.assertNotEqual(enum1, enum3)
