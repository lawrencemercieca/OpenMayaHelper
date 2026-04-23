"""High-level MEL and playback helpers."""

from __future__ import annotations

from maya import cmds, mel as maya_mel


class MelError(RuntimeError):
    """Base MEL interaction error."""


class MelConversionError(MelError):
    """Raised when Python values cannot be converted to MEL."""


class MelArgumentError(MelError):
    """Raised when MEL procedures are called with bad arguments."""


class MelUnknownProcedureError(MelError):
    """Raised when a MEL procedure is missing."""


def _mel_flag(flag):
    return f"-{flag}"


def _mel_value(value):
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, (tuple, list)):
        return " ".join(_mel_value(item) for item in value)
    if isinstance(value, (int, float)):
        return str(value)
    raise MelConversionError(f"Cannot convert {value!r} to MEL")


def pythonToMelCmd(command, **kwargs):
    parts = [command]
    for key, value in kwargs.items():
        if value is True and key in {"force", "rao"}:
            parts.append(_mel_flag(key))
            continue
        parts.append(_mel_flag(key))
        parts.append(_mel_value(value))
    return " ".join(parts)


class _MelGlobals:
    def __init__(self):
        self._values = {}

    @staticmethod
    def _normalize(name):
        return name[1:] if name.startswith("$") else name

    def initVar(self, mel_type, name):
        maya_mel.eval(f"global {mel_type} ${self._normalize(name)};")
        self._values.setdefault(self._normalize(name), None)

    def set(self, name, value):
        clean = self._normalize(name)
        if isinstance(value, str):
            maya_mel.eval(f'global string ${clean}; ${clean} = "{value}";')
            self._values[clean] = value
            return
        if isinstance(value, int):
            maya_mel.eval(f"global int ${clean}; ${clean} = {value};")
            self._values[clean] = value
            return
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            values = ",".join(f'"{item}"' for item in value)
            maya_mel.eval(f"global string ${clean}[]; ${clean} = {{{values}}};")
            self._values[clean] = list(value)
            return
        if isinstance(value, list) and all(isinstance(item, int) for item in value):
            values = ",".join(str(item) for item in value)
            maya_mel.eval(f"global int ${clean}[]; ${clean} = {{{values}}};")
            self._values[clean] = list(value)
            return
        raise TypeError(f"Unsupported MEL global value: {value!r}")

    def get(self, name):
        clean = self._normalize(name)
        if clean not in self._values:
            raise KeyError(clean)
        return self._values[clean]

    def get_dict(self, name, default=None):
        try:
            return self.get(name)
        except RuntimeError:
            return default

    def getType(self, name):
        clean = self._normalize(name)
        if clean not in self._values:
            raise TypeError(clean)
        probe = self._values[clean]
        if isinstance(probe, str):
            return "string"
        if isinstance(probe, list) and probe and isinstance(probe[0], str):
            return "string[]"
        if isinstance(probe, list):
            return "int[]"
        return "int"

    def keys(self):
        return [f"${key}" for key in self._values]

    def __contains__(self, name):
        clean = self._normalize(name)
        return f"${clean}" in self.keys()

    def __getitem__(self, name):
        if name not in self and self._normalize(name) not in self:
            raise KeyError(name)
        return self.get(name)

    def __setitem__(self, name, value):
        self.set(name, value)


melGlobals = _MelGlobals()
MelGlobals = melGlobals


class _Env:
    @property
    def animStartTime(self):
        return cmds.playbackOptions(query=True, animationStartTime=True)

    @animStartTime.setter
    def animStartTime(self, value):
        cmds.playbackOptions(animationStartTime=value)

    @property
    def minTime(self):
        return cmds.playbackOptions(query=True, minTime=True)

    @minTime.setter
    def minTime(self, value):
        cmds.playbackOptions(minTime=value)

    @property
    def maxTime(self):
        return cmds.playbackOptions(query=True, maxTime=True)

    @maxTime.setter
    def maxTime(self, value):
        cmds.playbackOptions(maxTime=value)

    @property
    def animEndTime(self):
        return cmds.playbackOptions(query=True, animationEndTime=True)

    @animEndTime.setter
    def animEndTime(self, value):
        cmds.playbackOptions(animationEndTime=value)

    @property
    def playbackTimes(self):
        return (self.animStartTime, self.minTime, self.maxTime, self.animEndTime)

    @playbackTimes.setter
    def playbackTimes(self, values):
        self.animStartTime, self.minTime, self.maxTime, self.animEndTime = values

    def getAnimStartTime(self):
        return self.animStartTime

    def setAnimStartTime(self, value):
        self.animStartTime = value

    def getMinTime(self):
        return self.minTime

    def setMinTime(self, value):
        self.minTime = value

    def getMaxTime(self):
        return self.maxTime

    def setMaxTime(self, value):
        self.maxTime = value

    def getAnimEndTime(self):
        return self.animEndTime

    def setAnimEndTime(self, value):
        self.animEndTime = value

    def getPlaybackTimes(self):
        return self.playbackTimes

    def setPlaybackTimes(self, values):
        self.playbackTimes = values


env = _Env()


class _MelProc:
    def __init__(self, path=()):
        self._path = path

    def __getattr__(self, item):
        return _MelProc(self._path + (item,))

    def __call__(self, *args):
        if not self._path:
            raise MelUnknownProcedureError("No MEL procedure specified")
        proc_name = ".".join(self._path)
        try:
            arg_text = ", ".join(_mel_value(arg) for arg in args)
        except MelConversionError:
            raise
        try:
            return maya_mel.eval(f"{proc_name}({arg_text})")
        except RuntimeError as exc:
            message = str(exc)
            if "Cannot find procedure" in message:
                raise MelUnknownProcedureError(message)
            if "Wrong number of arguments" in message:
                raise MelArgumentError(message)
            raise MelError(message)


mel = _MelProc()
