"""OpenMayaHelper port of PyMEL's test_util_path module."""

from __future__ import annotations

import os
import unittest

from openmayahelper.util_path import path


class UtilPathTests(unittest.TestCase):
    def test_misc(self):
        this_file = path(__file__)
        self.assertTrue(this_file.exists())
        self.assertTrue(this_file.isfile())
        self.assertFalse(this_file.isdir())
        self.assertIn(str(this_file.basename()), ("test_util_path.py", "test_util_path.pyc"))
        self.assertEqual(this_file.namebase, "test_util_path")
        self.assertIn(this_file.ext, (".py", ".pyc"))

        this_dir = path(os.path.dirname(__file__))
        self.assertTrue(this_dir.exists())
        self.assertTrue(this_dir.isdir())
        self.assertFalse(this_dir.isfile())
        self.assertEqual(str(this_dir.basename()), "tests")
        self.assertEqual(this_dir.namebase, "tests")
        self.assertEqual(this_dir.ext, "")
        self.assertIn(this_file, this_dir.files())

        missing = path("slartybartfast_fasdfjlkfjl")
        self.assertFalse(missing.exists())
