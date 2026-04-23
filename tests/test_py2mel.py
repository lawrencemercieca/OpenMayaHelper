"""OpenMayaHelper port of PyMEL's test_py2mel module."""

from __future__ import annotations

import unittest

from openmayahelper.py2mel import py2melCmd


class MyClassNoArgs:
    def noArgs(self):
        return "foo"

    def oneArg(self, arg1):
        return arg1 * 2

    def oneKwarg(self, kwarg1="default"):
        return kwarg1 * 2

    def oneArgTwoKwarg(self, arg1, kwarg1="ate", kwarg2="trex"):
        return f"{arg1} {kwarg1} {kwarg2}!"


class Py2MelTests(unittest.TestCase):
    def test_auto_name_and_no_args(self):
        command = py2melCmd(MyClassNoArgs)
        self.assertEqual(command("noArgs"), "foo")

    def test_one_arg_and_unique_short_flag(self):
        command = py2melCmd(MyClassNoArgs, commandName="myCls")
        self.assertEqual(command("oneArg", "stuff"), "stuffstuff")
        self.assertEqual(command("n"), "foo")

    def test_exclude_flags_and_flag_args(self):
        command = py2melCmd(MyClassNoArgs, commandName="myCls2", excludeFlags=["oneKwarg"])
        with self.assertRaises(AttributeError):
            command("oneKwarg", "goober")

        command = py2melCmd(
            MyClassNoArgs,
            commandName="myCls3",
            excludeFlagArgs={"oneArgTwoKwarg": ["kwarg1"]},
        )
        self.assertEqual(command("oneArgTwoKwarg", "Little Bo PeeP", "Batman"), "Little Bo PeeP ate Batman!")
        with self.assertRaises(TypeError):
            command("oneArgTwoKwarg", "foo")
