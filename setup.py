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
    'pymongo-schema @ https://github.com/pajachiet/pymongo-schema/tarball/0dd312c23f5d38fb7c1a1f3bbe977e79a814a119#egg=pymongo-schema'
]

tests_require = [
    'mongomock==3.17.0',
    'freezegun==0.3.12'
]

setup(
    name='broccoli_server',
    version='0.1',
    description='The server component of a web content crawling and sorting framework',
    url='http://github.com/KTachibanaM/broccoli-platform',
    author='KTachibanaM',
    author_email='whj19931115@gmail.com',
    license='WTFPL',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="broccoli_server.tests",
)
