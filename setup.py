# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys
import os
import re
import subprocess

from setuptools import setup, find_packages, Command
from distutils.command.build import build as BuildCommand
from setuptools.command.install import install as InstallCommand
from distutils.command.clean import clean as CleanCommand
from setuptools.command.test import test as TestCommand
import distutils


ROOT_PATH = os.path.dirname(
    os.path.realpath(__file__)
)

SOURCE_PATH = os.path.join(
    ROOT_PATH, 'source'
)

RESOURCE_PATH = os.path.join(
    ROOT_PATH, 'resource'
)

RESOURCE_TARGET_PATH = os.path.join(
    SOURCE_PATH, 'riffle', 'resource.py'
)

README_PATH = os.path.join(ROOT_PATH, 'README.rst')


# Custom commands.
class BuildResources(Command):
    '''Build additional resources.'''

    user_options = []

    def initialize_options(self):
        '''Configure default options.'''

    def finalize_options(self):
        '''Finalize options to be used.'''
        self.resource_source_path = os.path.join(RESOURCE_PATH, 'resource.qrc')
        self.resource_target_path = RESOURCE_TARGET_PATH

    def run(self):
        '''Run build.'''
        try:
            pyside_rcc_command = 'pyside-rcc'

            # On Windows, pyside-rcc is not automatically available on the
            # PATH so try to find it manually.
            if sys.platform == 'win32':
                import PySide
                pyside_rcc_command = os.path.join(
                    os.path.dirname(PySide.__file__),
                    'pyside-rcc.exe'
                )

            subprocess.check_call([
                pyside_rcc_command,
                '-o',
                self.resource_target_path,
                self.resource_source_path
            ])
        except (subprocess.CalledProcessError, OSError):
            print(
                'Error compiling resource.py using pyside-rcc. Possibly '
                'pyside-rcc could not be found. You might need to manually add '
                'it to your PATH.'
            )
            raise SystemExit()


class Build(BuildCommand):
    '''Custom build to pre-build resources.'''

    def run(self):
        '''Run build ensuring build_resources called first.'''
        self.run_command('build_resources')
        BuildCommand.run(self)


class Install(InstallCommand):
    '''Custom install to pre-build resources.'''

    def do_egg_install(self):
        '''Run install ensuring build_resources called first.

        .. note::

            `do_egg_install` used rather than `run` as sometimes `run` is not
            called at all by setuptools.

        '''
        self.run_command('build_resources')
        InstallCommand.do_egg_install(self)


class Clean(CleanCommand):
    '''Custom clean to remove built resources and distributions.'''

    def run(self):
        '''Run clean.'''
        relative_resource_path = os.path.relpath(
            RESOURCE_TARGET_PATH, ROOT_PATH
        )
        if os.path.exists(relative_resource_path):
            os.remove(relative_resource_path)
        else:
            distutils.log.warn(
                '\'{0}\' does not exist -- can\'t clean it'
                .format(relative_resource_path)
            )

        relative_compiled_resource_path = relative_resource_path + 'c'
        if os.path.exists(relative_compiled_resource_path):
            os.remove(relative_compiled_resource_path)
        else:
            distutils.log.warn(
                '\'{0}\' does not exist -- can\'t clean it'
                .format(relative_compiled_resource_path)
            )
        CleanCommand.run(self)


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
    setup_requires=[
        'PySide >= 1.2.2, < 2'
    ],
    install_requires=[
        'PySide >= 1.2.2, < 2',
        'clique >= 1.2.0, < 2'
    ],
    tests_require=[
        'pytest >= 2.3.5, < 3'
    ],
    cmdclass={
        'build': Build,
        'build_resources': BuildResources,
        'install': Install,
        'clean': Clean,
        'test': PyTest
    }
)
