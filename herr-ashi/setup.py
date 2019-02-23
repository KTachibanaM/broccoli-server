from setuptools import setup

setup(
    name='herr_ashi',
    version='0.1',
    description='Herr ashi',
    url='http://github.com/KTachibanaM/herr-ashi',
    author='KTachibanaM',
    author_email='whj19931115@gmail.com',
    license='WTFPL',
    packages=["herr_ashi"],
    dependency_links=[
        './../broccoli-plugin-base',
    ],
    install_requires=[
        'broccoli_plugin_base',
        "imagehash",
        "feedparser",
        "beautifulsoup4",
        "python-twitter",
        "minio",
        "requests"
    ],
    zip_safe=False
)
