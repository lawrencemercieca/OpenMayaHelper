"""Startup-oriented cache helpers."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass


@dataclass(frozen=True)
class CacheFormat:
    ext: str
    writer: object
    reader: object


def _write_json(data, filename):
    with open(filename, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False)


def _read_json(filename):
    with open(filename, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_pickle(data, filename):
    with open(filename, "wb") as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def _read_pickle(filename):
    with open(filename, "rb") as handle:
        return pickle.load(handle)


class OpenMayaHelperCache:
    FORMATS = (
        CacheFormat(".json", _write_json, _read_json),
        CacheFormat(".pickle", _write_pickle, _read_pickle),
    )
