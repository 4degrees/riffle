# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os

from PySide import QtGui, QtCore

import riffle.resource
import riffle.model
import riffle.icon_factory


class FilesystemBrowser(QtGui.QDialog):
    '''FilesystemBrowser dialog.'''

    def __init__(self, root='', parent=None, iconFactory=None):
        '''Initialise browser with *root* path.

        Use an empty *root* path to specify the computer.

        *parent* is the optional owner of this UI element.

        *iconFactory* specifies the optional factory to pass to the model for
        customising icons.

        '''
        super(FilesystemBrowser, self).__init__(parent=parent)
        self._root = root
        self._iconFactory = iconFactory
        self._selected = []
        self._construct()
        self._postConstruction()

    def _construct(self):
        '''Construct widget.'''
        self.setLayout(QtGui.QVBoxLayout())

        self._headerLayout = QtGui.QHBoxLayout()

        self._locationWidget = QtGui.QComboBox()
        self._headerLayout.addWidget(self._locationWidget, stretch=1)

        self._upButton = QtGui.QToolButton()
        self._upButton.setIcon(QtGui.QIcon(':riffle/icon/up'))
        self._headerLayout.addWidget(self._upButton)

        self.layout().addLayout(self._headerLayout)

        self._contentSplitter = QtGui.QSplitter()

        self._bookmarksWidget = QtGui.QListView()
        self._contentSplitter.addWidget(self._bookmarksWidget)

        self._filesystemWidget = QtGui.QTableView()
        self._filesystemWidget.setSelectionBehavior(
            self._filesystemWidget.SelectRows
        )
        self._filesystemWidget.setSelectionMode(
            self._filesystemWidget.SingleSelection
        )
        self._filesystemWidget.verticalHeader().hide()

        self._contentSplitter.addWidget(self._filesystemWidget)

        proxy = riffle.model.FilesystemSortProxy(self)
        model = riffle.model.Filesystem(
            path=self._root, parent=self, iconFactory=self._iconFactory
        )
        proxy.setSourceModel(model)
        proxy.setDynamicSortFilter(True)

        self._filesystemWidget.setModel(proxy)
        self._filesystemWidget.setSortingEnabled(True)

        self._contentSplitter.setStretchFactor(1, 1)
        self.layout().addWidget(self._contentSplitter)

        self._footerLayout = QtGui.QHBoxLayout()
        self._footerLayout.addStretch(1)

        self._cancelButton = QtGui.QPushButton('Cancel')
        self._footerLayout.addWidget(self._cancelButton)

        self._acceptButton = QtGui.QPushButton('Choose')
        self._footerLayout.addWidget(self._acceptButton)

        self.layout().addLayout(self._footerLayout)

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        self.setWindowTitle('Filesystem Browser')
        self._filesystemWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # TODO: Remove once bookmarks widget implemented.
        self._bookmarksWidget.hide()

        self._acceptButton.setDefault(True)
        self._acceptButton.setDisabled(True)

        self._acceptButton.clicked.connect(self.accept)
        self._cancelButton.clicked.connect(self.reject)

        self._configureShortcuts()

        self.setLocation(self._root)

        self._filesystemWidget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents
        )
        self._filesystemWidget.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Stretch
        )

        self._upButton.clicked.connect(self._onNavigateUpButtonClicked)
        self._locationWidget.currentIndexChanged.connect(
            self._onNavigate
        )

        self._filesystemWidget.activated.connect(self._onActivateItem)
        selectionModel = self._filesystemWidget.selectionModel()
        selectionModel.currentRowChanged.connect(self._onSelectItem)

    def _configureShortcuts(self):
        '''Add keyboard shortcuts to navigate the filesystem.'''
        self._upShortcut = QtGui.QShortcut(
            QtGui.QKeySequence('Backspace'), self
        )
        self._upShortcut.setAutoRepeat(False)
        self._upShortcut.activated.connect(self._onNavigateUpButtonClicked)

    def _onActivateItem(self, index):
        '''Handle activation of item in listing.'''
        item = self._filesystemWidget.model().item(index)
        if not isinstance(item, riffle.model.File):
            self._acceptButton.setDisabled(True)
            self.setLocation(item.path, interactive=True)

    def _onSelectItem(self, selection, previousSelection):
        '''Handle selection of item in listing.'''
        self._acceptButton.setEnabled(True)
        del self._selected[:]
        item = self._filesystemWidget.model().item(selection)
        self._selected.append(item.path)

    def _onNavigate(self, index):
        '''Handle selection of path segment.'''
        if index > 0:
            self.setLocation(
                self._locationWidget.itemData(index), interactive=True
            )

    def _onNavigateUpButtonClicked(self):
        '''Navigate up a directory on button click.'''
        index = self._locationWidget.currentIndex()
        self._onNavigate(index + 1)

    def _segmentPath(self, path):
        '''Return list of valid *path* segments.'''
        parts = []
        model = self._filesystemWidget.model()

        # Separate root path from remainder.
        remainder = path

        while True:
            if remainder == model.root.path:
                break

            if remainder:
                parts.append(remainder)

            head, tail = os.path.split(remainder)
            if head == remainder:
                break

            remainder = head

        parts.append(model.root.path)
        return parts

    def setLocation(self, path, interactive=False):
        '''Set current location to *path*.

        *path* must be the same as root or under the root.

        .. note::

            Comparisons are case-sensitive. If you set the root as 'D:/' then
            location can be set as 'D:/folder' *not* 'd:/folder'.

        If *interactive* is True, catch any exception occurring and display an
        appropriate warning dialog to the user. Otherwise allow exceptions to
        bubble up as normal.

        '''
        try:
            self._setLocation(path)
        except Exception as error:
            if not interactive:
                raise
            else:
                warning_dialog = QtGui.QMessageBox(
                    QtGui.QMessageBox.Warning,
                    'Location is not available',
                    '{0} is not accessible.'.format(path),
                    QtGui.QMessageBox.Ok,
                    self
                )
                warning_dialog.setDetailedText(str(error))
                warning_dialog.exec_()

    def _setLocation(self, path):
        '''Set current location to *path*.

        *path* must be the same as root or under the root.

        .. note::

            Comparisons are case-sensitive. If you set the root as 'D:/' then
            location can be set as 'D:/folder' *not* 'd:/folder'.

        '''
        model = self._filesystemWidget.model()

        if not path.startswith(model.root.path):
            raise ValueError('Location must be root or under root.')

        # Ensure children for each segment in path are loaded.
        segments = self._segmentPath(path)
        for segment in reversed(segments):
            pathIndex = model.pathIndex(segment)
            model.fetchMore(pathIndex)

        self._filesystemWidget.setRootIndex(model.pathIndex(path))
        self._locationWidget.clear()

        # Add history entry for each segment.
        for segment in segments:
            index = model.pathIndex(segment)
            if not index.isValid():
                # Root item.
                icon = model.iconFactory.icon(
                    riffle.icon_factory.IconType.Computer
                )
                self._locationWidget.addItem(
                    icon, model.root.path or model.root.name, model.root.path
                )
            else:
                icon = model.icon(index)
                self._locationWidget.addItem(icon, segment, segment)

        if self._locationWidget.count() > 1:
            self._upButton.setEnabled(True)
            self._upShortcut.setEnabled(True)
        else:
            self._upButton.setEnabled(False)
            self._upShortcut.setEnabled(False)

    def selected(self):
        '''Return selected paths.'''
        return self._selected[:]
