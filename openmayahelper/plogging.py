"""Logging helpers compatible with the PyMEL raiseLog pattern."""

from __future__ import annotations

import logging


ERRORLEVEL = logging.ERROR


def raiseLog(logger, level, message, errorClass=RuntimeError):
    logger.log(level, message)
    if level >= ERRORLEVEL:
        raise errorClass(message)


def getLogger(name):
    logger = logging.getLogger(name)
    if not hasattr(logger, "raiseLog"):
        logger.raiseLog = lambda level, message, errorClass=RuntimeError: raiseLog(  # noqa: B023
            logger, level, message, errorClass=errorClass
        )
    return logger
