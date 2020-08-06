import os
import shutil
import subprocess
from setuptools.command.sdist import sdist
from setuptools import setup, find_packages

install_requires = [
    'jinja2==2.10.1',
    'flask==1.0.3',
    'pika==1.0.1',
    'pymongo==3.8.0',
    'flask-cors==3.0.8',
    'flask-jwt-extended==3.18.2',
    'dnspython==1.16.0',
    'jsonschema==3.0.1',
    'apscheduler==3.6.0',
    'sentry-sdk==0.14.3',
    # contrib
    'oauthlib==3.1.0',
    'requests==2.22.0',
    'python-twitter==3.5'
]

VERSION = "5.1.0"

tests_require = [
    'mongomock==3.17.0',
    'freezegun==0.3.12'
]


WEB_ARTIFACT_PATH = os.path.join("broccoli_server", "web")


def build_web():
    # check executables which are required to build web
    if not shutil.which("node"):
        raise RuntimeError("node is not found on PATH")
    if not shutil.which("yarn"):
        raise RuntimeError("yarn is not found on PATH")

    # build web
    subprocess.check_call(["yarn", "install"], cwd="web")
    subprocess.check_call(["yarn", "build"], cwd="web")

    # move built artifact
    if os.path.exists(WEB_ARTIFACT_PATH):
        print("removing old web artifact")
        shutil.rmtree(WEB_ARTIFACT_PATH)
    shutil.move(os.path.join("web", "build"), WEB_ARTIFACT_PATH)


class SdistCommand(sdist):
    def run(self):
        build_web()
        sdist.run(self)


setup(
    name='broccoli_server',
    version=VERSION,
    description='A web content crawling and sorting library',
    url='http://github.com/k-t-corp/broccoli-server',
    author='KTachibanaM',
    author_email='whj19931115@gmail.com',
    license='WTFPL',
    packages=find_packages(),
    # this is important for including web when building wheel
    include_package_data=True,
    # this is important for including web when building wheel
    package_data={
        "broccoli_server": ["web"]
    },
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="broccoli_server.tests",
    cmdclass={
        'sdist': SdistCommand
    }
)
