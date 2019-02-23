import subprocess
import os


def install_plugins():
    for pip_install in os.getenv("PIP_INSTALLS").split(","):
        print(subprocess.check_output(["pip", "install"] + pip_install.split(" ")))
