"""OpenMayaHelper port of PyMEL's test_plogging module."""

from __future__ import annotations

import logging
import unittest

import openmayahelper.plogging as plogging


class PLoggingTests(unittest.TestCase):
    def setUp(self):
        self.logger = plogging.getLogger("openmayahelper.tests")

    def test_raise_log_function_obeys_error_level(self):
        old_level = plogging.ERRORLEVEL
        plogging.ERRORLEVEL = logging.ERROR
        try:
            plogging.raiseLog(self.logger, logging.WARNING, "warning message")
            with self.assertRaises(RuntimeError):
                plogging.raiseLog(self.logger, logging.ERROR, "error message")
        finally:
            plogging.ERRORLEVEL = old_level

    def test_raise_log_method_accepts_custom_exception(self):
        old_level = plogging.ERRORLEVEL
        plogging.ERRORLEVEL = logging.INFO
        try:
            with self.assertRaises(TypeError):
                self.logger.raiseLog(logging.INFO, "custom error", errorClass=TypeError)
        finally:
            plogging.ERRORLEVEL = old_level
