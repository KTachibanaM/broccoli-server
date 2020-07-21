from typing import Dict, Tuple, Callable, Union
from broccoli_server.interface.worker import Worker


class WorkerCache(object):
    def __init__(self):
        self._cache = {}  # type: Dict[Tuple[str, str], Callable]

    def add(self, module: str, class_name: str, constructor):
        self._cache[(module, class_name)] = constructor

    def load(self, module, class_name, args: Dict) -> Tuple[bool, Union[str, Worker]]:
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
