import pkgutil
from importlib import import_module

def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)

def make_class_instance(package, name_pattern, class_name):
    all_names = [name for _, name, _ in pkgutil.iter_modules([package])]
    if name_pattern in all_names:
        matches = [name_pattern]
    else:
        matches = sorted([x for x in all_names if name_pattern in x])
    if len(matches) == 0:
        raise Exception(f"Could not find module with the pattern '{name_pattern}'")
    if len(matches) > 1:
        print(f"Info: multiple matches found for module with the pattern '{name_pattern}'")
    actual_name = matches[0]
    actual_class = import_from(f"{package}.{actual_name}", class_name)
    return actual_name, actual_class()
