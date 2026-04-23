"""OpenMayaHelper port of PyMEL's test_mel2py module."""

from __future__ import annotations

from maya_testlib import MayaTestCase, import_module

from openmayahelper.mel2py import mel2pyStr


class Mel2PyTests(MayaTestCase):
    def setUp(self):
        super().setUp()
        self.mel = import_module("maya.mel")

    def assertMelAndPyStringsEqual(self, mel_string):
        mel_command = f"$tempStringVar = {mel_string};"
        mel_value = self.mel.eval(mel_command)
        py_command = mel2pyStr(mel_command)
        namespace = {}
        exec(py_command, namespace)
        self.assertEqual(mel_value, namespace["tempStringVar"])

    def test_backslash_quote_strings(self):
        for mel_string in [
            r'''"\\"''',
            r'''"\""''',
            r'''"\"\""''',
            r'''"\\\""''',
            r'''"\"\\"''',
            r'''"\\\\\""''',
            r'''"\\\\\\\""''',
        ]:
            self.assertMelAndPyStringsEqual(mel_string)

    def test_basic_command_conversion(self):
        self.assertEqual(
            mel2pyStr("polyCube -w 1 -h 1 -d 1 -sx 1 -sy 1 -sz 1 -ax 0 1 0 -cuv 4 -ch 1;"),
            "from openmayahelper import pmcmds\npmcmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1)\n",
        )
