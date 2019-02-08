import importlib
from typing import Dict, List, Tuple, Union
from worker_manager.base_worker import BaseWorker


def load_object(module: str, class_name: str, args: Dict, global_args: List[str], worker_globals: Dict) \
        -> Tuple[bool, Union[BaseWorker, str]]:
    try:
        clazz = getattr(importlib.import_module(module), class_name)
    except Exception as e:
        return False, str(e)
    final_args = {}
    for arg_name, arg_value in args.items():
        final_args[arg_name] = arg_value
    for global_arg in global_args:
        if global_arg not in worker_globals.keys():
            raise Exception(f"Global arg {global_arg} is not found")
        else:
            final_args[global_arg] = worker_globals[global_arg]
    try:
        obj = clazz(**final_args)
    except Exception as e:
        return False, str(e)
    return True, obj
