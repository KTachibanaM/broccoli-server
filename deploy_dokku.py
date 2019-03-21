import os
import sys
import json
import subprocess


def execute(command):
    print("Executing " + str(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), ''):  # replace '' with b'' for Python 3
        sys.stdout.write(c)
        f.write(c)

if __name__ == "__main__":
    if not os.path.exists("deploy_dokku.json"):
        print("deploy_dokku.json doesn't exist")
        sys.exit(1)
    with open("deploy_dokku.json") as f:
        config = json.load(f)
        for c in config:
            canonical_name = c["canonicalName"]
            host = c["host"]
            app_name = c["appName"]
            execute(["git", "remote", "remove", canonical_name])
            execute(["git", "remote", "add", canonical_name, "dokku@" + host + ":" + app_name])
            execute(["git", "push", canonical_name, "master"])
            execute(["git", "remote", "remove", canonical_name])
