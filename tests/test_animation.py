"""OpenMayaHelper port of PyMEL's test_animation module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class AnimationTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.core = import_module("openmayahelper.core")

    def test_set_keyframe_on_attribute(self):
        node = self.core.createNode("transform", name="animNode")
        self.core.setKeyframe(node.translateX, time=1, value=2.5)
        count = self.core.keyframe(node.translateX, query=True, keyframeCount=True)
        self.assertEqual(count, 1)

    def test_keyframe_index_accepts_int(self):
        node = self.core.createNode("transform", name="indexedAnimNode")
        self.core.setKeyframe(node.translateX, time=1, value=1.0)
        self.core.setKeyframe(node.translateX, time=5, value=5.0)
        times = self.core.keyframe(node.translateX, query=True, index=1, timeChange=True)
        self.assertEqual(times, [5.0])

