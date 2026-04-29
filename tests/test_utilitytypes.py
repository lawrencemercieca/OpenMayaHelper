"""OpenMayaHelper port of PyMEL's test_utilitytypes module."""

from __future__ import annotations

import unittest

from openmayahelper.testingutils import TestCaseExtended
from openmayahelper.utilitytypes import Enum, EquivalencePairs, Singleton, proxyClass


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

    def test_enum_construction_and_reverse_lookup(self):
        enum1 = Enum("enum", {"Red": 0, "Green": 1, "Blue": 2})
        enum2 = Enum("enum", ("Red", "Green", "Blue"))
        enum3 = Enum("enum", [("Green", 1), ("Blue", 2), ("Red", 0)])
        self.assertEqual(enum1, enum2)
        self.assertEqual(enum1, enum3)
        self.assertEqual(enum1[2], "Blue")
        self.assertEqual(enum1["Red"], 0)

    def test_enum_multikey_defaults_and_repr(self):
        enum1 = Enum("enum", [("foo", 1), ("bar", 7), ("baz", 7)], multiKeys=True)
        enum2 = eval(repr(enum1), {"Enum": Enum})
        self.assertEqual(enum1, enum2)
        self.assertEqual(enum1[7], "bar")


class EquivalencePairsTests(TestCaseExtended):
    def test_init_and_lookup(self):
        pairs = EquivalencePairs(((1, "foo"), (2, "bar")))
        self.assertEqual(pairs[1], "foo")
        self.assertEqual(pairs["foo"], 1)
        self.assertEqual(pairs[2], "bar")
        self.assertEqual(pairs["bar"], 2)

    def test_overwrite_pairs_removes_old_links(self):
        pairs = EquivalencePairs({1: "a", 2: "b"})
        pairs[1] = 2
        with self.assertRaises(KeyError):
            _ = pairs["a"]
        with self.assertRaises(KeyError):
            _ = pairs["b"]
        self.assertEqual(pairs[1], 2)
        self.assertEqual(pairs[2], 1)


class ProxyClassTests(unittest.TestCase):
    class MyClass:
        "MyClass's doc string!"
        data = 3.14

        def __init__(self, ident):
            self.id = ident

        @classmethod
        def clsMeth(cls):
            return cls

        @staticmethod
        def statMeth():
            return "static"

        def instMeth(self):
            return (self, self.id)

    def test_proxy_class_wraps_data_and_methods(self):
        Wrapped = proxyClass(self.MyClass, "Wrapped", dataAttrName="_data", makeDefaultInit=True)
        self.assertEqual(Wrapped.__doc__, self.MyClass.__doc__)
        self.assertEqual(Wrapped.data, self.MyClass.data)
        self.assertEqual(Wrapped.clsMeth(), self.MyClass)
        self.assertEqual(Wrapped.statMeth(), "static")
        wrapped_result = Wrapped("bar").instMeth()
        my_class_result = self.MyClass("bar").instMeth()
        self.assertEqual(wrapped_result[0].__class__, my_class_result[0].__class__)
        self.assertEqual(wrapped_result[1], my_class_result[1])

    def test_proxy_class_handles_builtin_descriptors(self):
        Wrapped = proxyClass(str, "WrappedStr", dataAttrName="_data", makeDefaultInit=True)
        wrapped = Wrapped("Fun times were had by all!")
        self.assertEqual(wrapped[3:7], " tim")
        self.assertEqual(Wrapped.__len__(wrapped), len("Fun times were had by all!"))
