from setuptools import setup

setup(
    name='broccoli_plugin_base',
    version='0.1',
    description='Base dependencies for broccoli plugins',
    url='http://github.com/KTachibanaM/broccoli-platform',
    author='KTachibanaM',
    author_email='whj19931115@gmail.com',
    license='WTFPL',
    packages=['broccoli_plugin_base'],
    install_requires=[
        'pika',
        "pymongo",
        "requests"
    ],
    zip_safe=False
)
