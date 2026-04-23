"""Nested container patch and diff helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RemovedKey:
    old_value: object


def mergeCascadingDicts(source, target, allowDictToListMerging=False):
    for key, value in source.items():
        if isinstance(value, RemovedKey):
            if isinstance(target, list):
                target.pop(key)
            else:
                target.pop(key, None)
            continue

        if key not in target:
            target[key] = _clone(value)
            continue

        current = target[key]
        if isinstance(current, dict) and isinstance(value, dict):
            mergeCascadingDicts(value, current, allowDictToListMerging=allowDictToListMerging)
            continue
        if allowDictToListMerging and isinstance(current, list) and isinstance(value, dict):
            for index, item in sorted(value.items()):
                if isinstance(item, RemovedKey):
                    current.pop(index)
                elif isinstance(item, dict) and index < len(current) and isinstance(current[index], (dict, list)):
                    mergeCascadingDicts(item, current[index], allowDictToListMerging=allowDictToListMerging)
                elif index < len(current):
                    current[index] = _clone(item)
                else:
                    while len(current) < index:
                        current.append(None)
                    current.append(_clone(item))
            continue
        target[key] = _clone(value)
    return target


def compareCascadingDicts(original, new):
    both = set(original) & set(new)
    only1 = set(original) - set(new)
    only2 = set(new) - set(original)
    diff = {}

    for key in only1:
        diff[key] = RemovedKey(original[key])
    for key in only2:
        diff[key] = _clone(new[key])

    for key in both:
        old_value = original[key]
        new_value = new[key]
        if isinstance(old_value, dict) and isinstance(new_value, dict):
            _, _, _, subdiff = compareCascadingDicts(old_value, new_value)
            if subdiff:
                diff[key] = subdiff
        elif isinstance(old_value, list) and isinstance(new_value, list):
            subdiff = {}
            max_len = max(len(old_value), len(new_value))
            for index in range(max_len):
                if index >= len(old_value):
                    subdiff[index] = _clone(new_value[index])
                elif index >= len(new_value):
                    subdiff[index] = RemovedKey(old_value[index])
                elif old_value[index] != new_value[index]:
                    if isinstance(old_value[index], dict) and isinstance(new_value[index], dict):
                        _, _, _, nested = compareCascadingDicts(old_value[index], new_value[index])
                        subdiff[index] = nested
                    else:
                        subdiff[index] = _clone(new_value[index])
            if subdiff:
                diff[key] = subdiff
        elif old_value != new_value:
            diff[key] = _clone(new_value)

    return both, only1, only2, diff


def deepPatch(input_value, predicate, changer):
    result, _ = deepPatchAltered(input_value, predicate, changer)
    return result


def deepPatchAltered(input_value, predicate, changer):
    if predicate(input_value):
        return changer(input_value), True

    if isinstance(input_value, dict):
        altered = False
        result = {}
        for key, value in input_value.items():
            new_key, key_altered = deepPatchAltered(key, predicate, changer)
            new_value, value_altered = deepPatchAltered(value, predicate, changer)
            result[new_key] = new_value
            altered = altered or key_altered or value_altered
        if altered:
            input_value.clear()
            input_value.update(result)
        return input_value, altered

    if isinstance(input_value, list):
        altered = False
        for index, item in enumerate(list(input_value)):
            new_item, item_altered = deepPatchAltered(item, predicate, changer)
            if item_altered:
                input_value[index] = new_item
                altered = True
        return input_value, altered

    if isinstance(input_value, tuple):
        altered = False
        items = []
        for item in input_value:
            new_item, item_altered = deepPatchAltered(item, predicate, changer)
            items.append(new_item)
            altered = altered or item_altered
        return tuple(items) if altered else input_value, altered

    if isinstance(input_value, set):
        altered = False
        items = []
        for item in input_value:
            new_item, item_altered = deepPatchAltered(item, predicate, changer)
            items.append(new_item)
            altered = altered or item_altered
        return set(items) if altered else input_value, altered

    return input_value, False


def _clone(value):
    if isinstance(value, dict):
        return {key: _clone(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_clone(item) for item in value]
    return value
