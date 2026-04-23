"""OpenMayaHelper port of PyMEL's test_factories module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class FactoriesTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.factories = import_module("openmayahelper.factories")
        self.om = import_module("maya.OpenMaya")

    def test_api_type_maps_match_mfn_values(self):
        for name in ("kTransform", "kDependencyNode", "kMesh"):
            self.assertEqual(getattr(self.om.MFn, name), self.factories.apiTypesToApiEnums[name])

    def test_inverse_map_is_consistent(self):
        for enum_value, name in self.factories.apiEnumsToApiTypes.items():
            self.assertEqual(getattr(self.om.MFn, name), enum_value)

    def test_maybe_convert(self):
        self.assertTrue(self.factories.maybeConvert(1, bool))
        self.assertEqual(self.factories.maybeConvert("3", int), 3)
        self.assertEqual(self.factories.maybeConvert("foo", int), "foo")
        self.assertEqual(self.factories.maybeConvert([0, 1, 2], bool), [False, True, True])
