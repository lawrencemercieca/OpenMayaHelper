"""Minimal command-style wrapper generation for Python callables."""

from __future__ import annotations

import inspect


_COMMANDS = {}


class _Py2MelCommand:
    def __init__(self, target, excludeFlags=None, excludeFlagArgs=None):
        self._target = target
        self._exclude_flags = set(excludeFlags or ())
        self._exclude_flag_args = dict(excludeFlagArgs or {})

    def _instance(self):
        if inspect.isclass(self._target):
            return self._target()
        return self._target

    def _resolve_method(self, flag):
        instance = self._instance()
        methods = {
            name: getattr(instance, name)
            for name in dir(instance)
            if not name.startswith("_") and callable(getattr(instance, name))
        }
        if flag in self._exclude_flags:
            raise AttributeError(flag)
        if flag in methods:
            return flag, methods[flag]
        matches = [name for name in methods if name.startswith(flag) and name not in self._exclude_flags]
        if len(matches) == 1:
            return matches[0], methods[matches[0]]
        raise AttributeError(flag)

    def __call__(self, flag, *args):
        method_name, method = self._resolve_method(flag)
        signature = inspect.signature(method)
        blocked = set(self._exclude_flag_args.get(method_name, ()))
        parameters = [
            param
            for param in signature.parameters.values()
            if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
        ]
        visible_parameters = [param for param in parameters if param.name not in blocked]
        required = []
        blocked_seen = False
        for param in parameters:
            if param.name in blocked:
                blocked_seen = True
                continue
            if param.default is inspect._empty or blocked_seen:
                required.append(param)
        if len(args) < len(required) or len(args) > len(visible_parameters):
            raise TypeError(f"{method_name} expected between {len(required)} and {len(visible_parameters)} args")

        provided = iter(args)
        call_kwargs = {}
        for param in parameters:
            if param.name in blocked:
                if param.default is inspect._empty:
                    raise TypeError(f"{method_name} cannot exclude required argument {param.name}")
                call_kwargs[param.name] = param.default
                continue
            try:
                call_kwargs[param.name] = next(provided)
            except StopIteration:
                if param.default is inspect._empty:
                    raise TypeError(f"{method_name} missing argument {param.name}")
                call_kwargs[param.name] = param.default
        return method(**call_kwargs)


def py2melCmd(target, commandName=None, excludeFlags=None, excludeFlagArgs=None):
    name = commandName or target.__name__
    command = _Py2MelCommand(target, excludeFlags=excludeFlags, excludeFlagArgs=excludeFlagArgs)
    _COMMANDS[name] = command
    return command
