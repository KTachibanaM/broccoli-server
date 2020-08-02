from typing import Dict, Tuple, Callable, Union, List
from broccoli_server.interface.worker import Worker


class WorkerCache(object):
    def __init__(self):
        self._cache = {}  # type: Dict[str, Callable]

    def register_module(self, module_name: str, constructor):
        self._cache[module_name] = constructor

    def get_modules_names(self) -> List[str]:
        return list(sorted(self._cache.keys()))

    def load(self, module_name: str, args: Dict) -> Tuple[bool, Union[str, Worker]]:
        if module_name not in self._cache:
            return False, f"Module {module_name} not found"

        clazz = self._cache[module_name]
        final_args = {}
        for arg_name, arg_value in args.items():
            final_args[arg_name] = arg_value
        try:
            obj = clazz(**final_args)
        except Exception as e:
            return False, str(e)
        return True, obj
