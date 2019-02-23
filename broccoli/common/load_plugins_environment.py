import os
import io
import importlib
import dotenv


def load_plugins_environment():
    for module in os.getenv("PIP_ENVIRONMENT_MODULES").split(","):
        print(f"Injecting variable `Environment` from module {module}.environment")
        environment_str = getattr(importlib.import_module(f"{module}.environment"), "Environment")
        f = io.StringIO(environment_str)
        f.seek(0)
        dotenv.load_dotenv(stream=f)
