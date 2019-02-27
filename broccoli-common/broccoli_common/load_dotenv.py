import os
import dotenv
import pathlib


def load_dotenv(file_obj, env_filename):
    path = os.path.join(
        os.path.dirname(os.path.realpath(file_obj)),
        env_filename
    )
    if os.path.exists(path):
        print(f"Loading {path}")
        dotenv.load_dotenv(dotenv_path=pathlib.Path(path))
    else:
        print(f"{path} does not exist")
