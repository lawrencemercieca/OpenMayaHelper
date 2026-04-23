"""OpenMayaHelper port of PyMEL's test_startup module."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from openmayahelper.startup import OpenMayaHelperCache


class StartupCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_dump_load(self):
        smiley = "\U0001F600"
        datasets = {
            "unicode": {"foo": smiley},
            "ascii": {"foo": 7},
        }

        filebase = os.path.join(self.tmpdir, "test_cache")
        for name, data in datasets.items():
            for fmt in OpenMayaHelperCache.FORMATS:
                filename = f"{filebase}_{name}{fmt.ext}"
                fmt.writer(data, filename)
                read_data = fmt.reader(filename)
                self.assertEqual(read_data, data)
                self.assertIs(type(read_data), type(data))
