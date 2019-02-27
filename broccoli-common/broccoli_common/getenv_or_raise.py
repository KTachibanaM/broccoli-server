import os


def getenv_or_raise(env):
    if env not in os.environ:
        raise RuntimeError(f"{env} does not exist")
    return os.environ[env]
