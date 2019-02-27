import importlib
from typing import Dict, Tuple, Union
from broccoli_plugin_interface.worker_manager.worker import Worker


def load_object(module: str, class_name: str, args: Dict) -> Tuple[bool, Union[Worker, str]]:
    try:
        clazz = getattr(importlib.import_module(module), class_name)
    except Exception as e:
        return False, str(e)
    final_args = {}
    for arg_name, arg_value in args.items():
        final_args[arg_name] = arg_value
    try:
        obj = clazz(**final_args)
    except Exception as e:
        return False, str(e)
    return True, obj
