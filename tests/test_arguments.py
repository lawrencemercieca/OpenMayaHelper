"""OpenMayaHelper port of PyMEL's test_arguments module."""

from __future__ import annotations

import numbers
import unittest

from openmayahelper import arguments


class MergeCascadingDictsTests(unittest.TestCase):
    def test_simple_add(self):
        original = {1: "a"}
        arguments.mergeCascadingDicts({2: "b"}, original)
        self.assertEqual(original, {1: "a", 2: "b"})

    def test_nested_add(self):
        original = {1: {"meat": "deinonychus"}}
        arguments.mergeCascadingDicts({1: {"plants": "stegosaurus"}}, original)
        self.assertEqual(original, {1: {"meat": "deinonychus", "plants": "stegosaurus"}})

    def test_remove_key(self):
        original = {1: "a"}
        arguments.mergeCascadingDicts({1: arguments.RemovedKey("a")}, original)
        self.assertEqual(original, {})

    def test_list_merge(self):
        original = {1: ["bad", "mother", "Fer"]}
        arguments.mergeCascadingDicts({1: {0: "samuel", 1: "jackson"}}, original, allowDictToListMerging=True)
        self.assertEqual(original, {1: ["samuel", "jackson", "Fer"]})


class CompareCascadingDictsTests(unittest.TestCase):
    def test_simple_add(self):
        original = {1: "a"}
        new = {1: "a", 2: "b"}
        _, _, _, diff = arguments.compareCascadingDicts(original, new)
        self.assertEqual(diff, {2: "b"})

    def test_simple_remove(self):
        original = {1: "a"}
        new = {}
        _, _, _, diff = arguments.compareCascadingDicts(original, new)
        self.assertEqual(diff, {1: arguments.RemovedKey("a")})


class DeepPatchTests(unittest.TestCase):
    def test_list_patch(self):
        is_number = lambda value: isinstance(value, numbers.Number)
        add_three = lambda value: value + 3
        payload = [3, "some str", 8.4]
        result = arguments.deepPatch(payload, is_number, add_three)
        self.assertEqual(result, [6, "some str", 11.4])

    def test_tuple_patch(self):
        is_string = lambda value: isinstance(value, str)
        add_suffix = lambda value: value + "suffix"
        payload = (3.7, "blah")
        result, altered = arguments.deepPatchAltered(payload, is_string, add_suffix)
        self.assertEqual(result, (3.7, "blahsufﬁx".replace("ﬁ", "fi")))
        self.assertTrue(altered)
