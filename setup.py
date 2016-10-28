"""
This is "setup.py" file for maildaemon.
"""

import os
import shutil
import sys
import typing

import setuptools

from maildaemon._version import version

_HERE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
_SRC_DIR = '.'

def clean() -> None:
    if os.path.isdir('build'):
        shutil.rmtree('build')

def long_description() -> str:
    """ Read contents of README.rst file and return them. """

    with open(os.path.join(_HERE, 'README.rst'), encoding='utf-8') as f:
        desc = f.read()
    return desc

def classifiers() -> typing.List[str]:
    """
    Project classifiers.

    See: https://pypi.python.org/pypi?:action=list_classifiers
    """

    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
        ]
    return classifiers

def packages() -> typing.List[str]:
    """ Find packages to pack. """

    exclude = ['test', 'test.*'] if 'bdist_wheel' in sys.argv else ()
    packages = setuptools.find_packages(_SRC_DIR, exclude=exclude)
    return packages

def install_requires() -> typing.List[str]:
    """
    Read contents of requirements.txt file and return its relevant lines.

    Only non-empty and non-comment lines are relevant.
    """

    reqs = []
    with open(os.path.join(_HERE, 'requirements.txt')) as f:
        reqs = [l for l in f.read().splitlines() if l and not l.strip().startswith('#')]
    return reqs

def setup() -> None:
    """ Run setuptools.setup() with correct arguments. """

    name = 'maildaemon'
    description = 'multi-server mail filtering daemon supporting IMAP, POP and SMTP'
    url = 'http://mbdev.pl/'
    author = 'Mateusz Bysiek'
    author_email = 'mb@mbdev.pl'
    license_str = 'Apache License 2.0'
    keywords = ['e-mail', 'filter', 'daemon', 'imap', 'pop', 'smtp']
    # tell distutils wheare all the packages are
    package_dir = {'': _SRC_DIR}
    entry_points = {
        'console_scripts': [
            'maildaemon = maildaemon.__main__:main'
            ]
        }
    test_suite = 'test'

    setuptools.setup(
        name=name, version=version, description=description, long_description=long_description(),
        url=url, author=author, author_email=author_email, license=license_str,
        classifiers=classifiers(), keywords=keywords, packages=packages(), package_dir=package_dir,
        install_requires=install_requires(), entry_points=entry_points, test_suite=test_suite
        )

if __name__ == '__main__':
    clean()
    setup()
