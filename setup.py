import urllib.request
import os
import shutil
import tarfile
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
    'broccoli-interface==1.0',
    'broccoli-ui-interface==1.0'
]
WEB_VERSION = "0.2.4"

tests_require = [
    'mongomock==3.17.0',
    'freezegun==0.3.12'
]


WEB_ARCHIVE_PATH = "web.tar.gz"
WEB_ARTIFACT_PATH = os.path.join("broccoli_server", "web")


class SdistCommand(sdist):
    def run(self):
        if os.path.exists(WEB_ARCHIVE_PATH):
            print("removing old web archive")
            os.remove(WEB_ARCHIVE_PATH)

        print(f"downloading web archive version {WEB_VERSION}")
        urllib.request.urlretrieve(
            f"https://github.com/broccoli-platform/broccoli-web/releases/download/{WEB_VERSION}/web.tar.gz",
            filename=WEB_ARCHIVE_PATH
        )

        if os.path.exists(WEB_ARTIFACT_PATH):
            print("removing old web artifact")
            shutil.rmtree(WEB_ARTIFACT_PATH)

        print(f"populating web artifact version {WEB_VERSION}")
        f = tarfile.open(WEB_ARCHIVE_PATH, 'r')
        f.extractall(path=WEB_ARTIFACT_PATH)

        sdist.run(self)


setup(
    name='broccoli_server',
    version='1.0.3',
    description='The server component of a web content crawling and sorting framework',
    url='http://github.com/KTachibanaM/broccoli-platform',
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
