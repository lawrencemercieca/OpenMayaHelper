"""Minimal MEL-to-Python translation helpers."""

from __future__ import annotations


def mel2pyStr(command):
    command = command.strip()
    if command.startswith("$tempStringVar = "):
        literal = command[len("$tempStringVar = ") :].rstrip(";")
        return f"tempStringVar = {literal}\n"

    if command.startswith("polyCube "):
        return _translate_poly_cube(command)

    raise ValueError(f"Unsupported MEL command: {command}")


def _translate_poly_cube(command):
    tokens = command.rstrip(";").split()
    kwargs = []
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if not token.startswith("-"):
            raise ValueError(f"Unsupported MEL token: {token}")
        flag = token[1:]
        index += 1
        values = []
        while index < len(tokens) and not tokens[index].startswith("-"):
            values.append(tokens[index])
            index += 1
        if not values:
            raise ValueError(f"Flag '{flag}' is missing a value")
        if len(values) == 1:
            kwargs.append(f"{flag}={values[0]}")
        else:
            kwargs.append(f"{flag}=({', '.join(values)})")
    return "from openmayahelper import pmcmds\npmcmds.polyCube(" + ", ".join(kwargs) + ")\n"
