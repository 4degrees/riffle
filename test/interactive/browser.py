# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

from PySide import QtGui

import riffle.browser


def main(arguments=None):
    '''Interactive test of custom filesystem browser.'''
    if arguments is None:
        arguments = sys.argv

    application = QtGui.QApplication(arguments)

    browser = riffle.browser.FilesystemBrowser()

    screen_size = application.desktop().availableGeometry()
    browser.setMinimumSize(screen_size.width() / 2, screen_size.height() / 2)

    if browser.exec_():
        selected = browser.selected()
        print('Selected: {0}'.format(selected))


if __name__ == '__main__':
    raise SystemExit(main())

