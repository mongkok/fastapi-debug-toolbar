import sys
import typing as t


def import_string(import_name: str) -> t.Any:
    try:
        __import__(import_name)
    except ImportError:
        if "." not in import_name:
            raise
    else:
        return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit(".", 1)
    module = __import__(module_name, globals(), locals(), [obj_name])
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e)


def get_name_from_obj(obj: t.Any) -> str:
    if hasattr(obj, "__name__"):
        name = obj.__name__
    else:
        name = obj.__class__.__name__

    if hasattr(obj, "__module__"):
        module = obj.__module__
        name = f"{module}.{name}"
    return name


def pluralize(value: float, arg: str = "s") -> str:
    if "," not in arg:
        arg = f",{arg}"

    bits = arg.split(",")

    if len(bits) > 2:
        return ""

    singular_suffix, plural_suffix = bits[:2]

    if float(value) == 1:
        return singular_suffix
    return plural_suffix
