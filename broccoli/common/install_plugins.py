import subprocess
from .getenv_or_raise import getenv_or_raise


def install_plugins():
    for pip_install in getenv_or_raise("PIP_INSTALLS").split(","):
        print(f"Running pip install {pip_install}")
        subprocess.check_output(["pip", "install"] + pip_install.split(" "))
