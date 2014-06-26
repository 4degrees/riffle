# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


from PySide import QtGui

import riffle.model


class IconType(object):
    '''Icon types.'''

    Computer = 'Computer',
    File = 'File',
    Directory = 'Directory',
    Mount = 'Mount',
    Collection = 'Collection'
    Unknown = 'Unknown'


class IconFactory(object):
    '''Icon provider.'''

    def icon(self, specification):
        '''Return appropriate icon for *specification*.

        *specification* should be either:

            * An instance of :py:class:`riffle.model.Item`
            * One of the defined icon types (:py:class:`IconType`)

        '''
        if isinstance(specification, riffle.model.Item):
            specification = self.type(specification)

        icon = None

        if specification == IconType.Computer:
            icon = QtGui.QIcon(':riffle/icon/computer')

        elif specification == IconType.Mount:
            icon = QtGui.QIcon(':riffle/icon/drive')

        elif specification == IconType.Directory:
            icon = QtGui.QIcon(':riffle/icon/folder')

        elif specification == IconType.File:
            icon = QtGui.QIcon(':riffle/icon/file')

        elif specification == IconType.Collection:
            icon = QtGui.QIcon(':riffle/icon/collection')

        return icon

    def type(self, item):
        '''Return appropriate icon type for *item*.'''
        iconType = IconType.Unknown

        if isinstance(item, riffle.model.Computer):
            iconType = IconType.Computer

        elif isinstance(item, riffle.model.Mount):
            iconType = IconType.Mount

        elif isinstance(item, riffle.model.Directory):
            iconType = IconType.Directory

        elif isinstance(item, riffle.model.File):
            iconType = IconType.File

        elif isinstance(item, riffle.model.Collection):
            iconType = IconType.Collection

        return iconType
