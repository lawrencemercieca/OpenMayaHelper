"""OpenMayaHelper port of PyMEL's test_language module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module


class LanguageTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.lang = import_module("openmayahelper.language")
        from maya.mel import eval as meval

        self.meval = meval

    def test_python_to_mel_cmd(self):
        self.assertEqual(self.lang.pythonToMelCmd("xform", rao=True).strip(), "xform -rao")
        self.assertEqual(
            self.lang.pythonToMelCmd("xform", translation=(1, 2, 3)).strip(),
            "xform -translation 1 2 3",
        )

    def test_mel_globals_set_get(self):
        self.lang.melGlobals.set("openmayahelper_test_int", 37)
        self.assertEqual(self.lang.melGlobals.get("openmayahelper_test_int"), 37)
        self.lang.melGlobals.set("openmayahelper_test_str", "hello")
        self.assertEqual(self.lang.melGlobals.get("openmayahelper_test_str"), "hello")

    def test_env_playback_times(self):
        self.lang.env.playbackTimes = (1, 4, 10, 24)
        self.assertEqual(self.lang.env.playbackTimes, (1, 4, 10, 24))
        self.lang.env.setPlaybackTimes((2, 5, 11, 22))
        self.assertEqual(self.lang.env.getPlaybackTimes(), (2, 5, 11, 22))

    def test_mel_proc_calls(self):
        self.meval(
            """global proc float OpenMayaHelper_test_add(float $inValue1, float $inValue2)
               {
                   return $inValue1 + $inValue2;
               }"""
        )
        self.meval(
            """global proc float OpenMayaHelper_test.Math.getPi()
               {
                   return 3.141;
               }"""
        )
        self.assertEqual(self.lang.mel.OpenMayaHelper_test_add(1.5, 2.2), 3.7)
        self.assertEqual(self.lang.mel.OpenMayaHelper_test.Math.getPi(), 3.141)
