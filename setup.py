# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import re

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


ROOT_PATH = os.path.dirname(
    os.path.realpath(__file__)
)

SOURCE_PATH = os.path.join(ROOT_PATH, 'source')


class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


with open(os.path.join(SOURCE_PATH, 'riffle', '_version.py')) as _version_file:
    VERSION = re.match(
        r'.*__version__ = \'(.*?)\'',
        _version_file.read(),
        re.DOTALL
    ).group(1)


setup(
    name='Riffle',
    version=VERSION,
    description='Filesystem browser for PySide.',
    long_description=open('README.rst').read(),
    keywords='filesystem, browser, pyside, qt, pyqt',
    url='https://github.com/4degrees/riffle',
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={
        '': 'source'
    },
    install_requires=[
        'PySide >= 1.2.2, < 2',
        'clique >= 1.2.0, < 2'
    ],
    tests_require=[
        'pytest >= 2.3.5, < 3'
    ],
    cmdclass={
        'test': PyTest
    }
)
