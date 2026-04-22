"""Name utility helpers."""


def short_name(name):
    return name.rsplit('|', 1)[-1]


def split_namespace(name):
    short = short_name(name)
    if ':' not in short:
        return '', short
    namespace, leaf = short.rsplit(':', 1)
    return namespace, leaf
