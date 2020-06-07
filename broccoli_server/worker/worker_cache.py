from typing import Dict, Tuple, Callable


class WorkerCache(object):
    def __init__(self):
        self._cache = {}  # type: Dict[Tuple[str, str], Callable]

    def add(self, module: str, class_name: str, constructor):
        self._cache[(module, class_name)] = constructor

    # not specifying return type of broccoli_server.interface.worker.Worker because of circular dep
    def load(self, module, class_name, args: Dict):
        if (module, class_name) not in self._cache:
            return False, f"class with module {module} and class name {class_name} not found"

        clazz = self._cache[(module, class_name)]
        final_args = {}
        for arg_name, arg_value in args.items():
            final_args[arg_name] = arg_value
        try:
            obj = clazz(**final_args)
        except Exception as e:
            return False, str(e)
        return True, obj
