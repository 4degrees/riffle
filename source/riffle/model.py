# :coding: utf-8
# :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
from datetime import datetime

from PySide.QtCore import Qt, QAbstractItemModel, QModelIndex, QDir
from PySide.QtGui import QSortFilterProxyModel
import clique


def ItemFactory(path):
    '''Return appropriate :py:class:`Item` instance for *path*.

    If *path* is null then return Computer root.

    '''
    if not path:
        return Computer()

    elif os.path.isfile(path):
        return File(path)

    elif os.path.ismount(path):
        return Mount(path)

    elif os.path.isdir(path):
        return Directory(path)

    else:
        raise ValueError('Could not determine correct type for path: {0}'
                         .format(path))


class Item(object):
    '''Represent filesystem item.'''

    def __init__(self, path):
        '''Initialise item with *path*.'''
        super(Item, self).__init__()
        self.path = path

        self.children = []
        self.parent = None
        self._fetched = False

    def __repr__(self):
        '''Return representation.'''
        return '<{0} {1}>'.format(self.__class__.__name__, self.path)

    @property
    def name(self):
        '''Return name of item.'''
        return os.path.basename(self.path) or self.path

    @property
    def size(self):
        '''Return size of item.'''
        return os.path.getsize(self.path)

    @property
    def type(self):
        '''Return type of item as string.'''
        return ''

    @property
    def modified(self):
        '''Return last modified date of item.'''
        return datetime.fromtimestamp(os.path.getmtime(self.path))

    @property
    def row(self):
        '''Return index of this item in its parent or 0 if no parent.'''
        if self.parent:
            return self.parent.children.index(self)

        return 0

    def addChild(self, item):
        '''Add *item* as child of this item.'''
        if item.parent and item.parent != self:
            item.parent.removeChild(item)

        self.children.append(item)
        item.parent = self

    def removeChild(self, item):
        '''Remove *item* from children.'''
        item.parent = None
        self.children.remove(item)

    def canFetchMore(self):
        '''Return whether more items can be fetched under this one.'''
        if not self._fetched:
            if self.mayHaveChildren():
                return True

        return False

    def mayHaveChildren(self):
        '''Return whether item may have children.'''
        return True

    def fetchChildren(self):
        '''Fetch and return new children.

        Will only fetch children whilst canFetchMore is True.

        .. note::

            It is the caller's responsibility to add each fetched child to this
            parent if desired using :py:meth:`Item.addChild`.

        '''
        if not self.canFetchMore():
            return []

        children = self._fetchChildren()
        self._fetched = True

        return children

    def _fetchChildren(self):
        '''Fetch and return new child items.

        Override in subclasses to fetch actual children and return list of
        *unparented* :py:class:`Item` instances.

        '''
        return []

    def refetch(self):
        '''Reload children.'''
        # Reset children
        for child in self.children[:]:
            self.removeChild(child)

        # Enable children fetching
        self._fetched = False


class Computer(Item):
    '''Represent root.'''

    def __init__(self):
        '''Initialise item.'''
        super(Computer, self).__init__('')

    @property
    def name(self):
        '''Return name of item.'''
        return 'Computer'

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Root'

    def _fetchChildren(self):
        '''Fetch and return new child items.'''
        children = []
        for entry in QDir.drives():
            path = os.path.normpath(entry.canonicalFilePath())
            children.append(Mount(path))

        return children


class File(Item):
    '''Represent file.'''

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'File'

    def mayHaveChildren(self):
        '''Return whether item may have children.'''
        return False


class Directory(Item):
    '''Represent directory.'''

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Directory'

    def _fetchChildren(self):
        '''Fetch and return new child items.'''
        children = []

        # List paths under this directory.
        paths = []
        for name in os.listdir(self.path):
            paths.append(os.path.normpath(os.path.join(self.path, name)))

        # Handle collections.
        collections, remainder = clique.assemble(
            paths, [clique.PATTERNS['frames']]
        )

        for path in remainder:
            try:
                child = ItemFactory(path)
            except ValueError:
                pass
            else:
                children.append(child)

        for collection in collections:
            children.append(Collection(collection))

        return children


class Mount(Directory):
    '''Represent mount point.'''

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Mount'

    @property
    def size(self):
        '''Return size of item.'''
        return None

    @property
    def modified(self):
        '''Return last modified date of item.'''
        return None


class Collection(Item):
    '''Represent collection.'''

    def __init__(self, collection):
        '''Initialise item with *collection*.

        *collection* should be an instance of :py:class:`clique.Collection`.

        '''
        self._collection = collection
        super(Collection, self).__init__(self._collection.format())

    @property
    def type(self):
        '''Return type of item as string.'''
        return 'Collection'

    @property
    def size(self):
        '''Return size of item.'''
        return None

    @property
    def modified(self):
        '''Return last modified date of item.'''
        return None

    def _fetchChildren(self):
        '''Fetch and return new child items.'''
        children = []
        for path in self._collection:
            try:
                child = ItemFactory(path)
            except ValueError:
                pass
            else:
                children.append(child)

        return children


class Filesystem(QAbstractItemModel):
    '''Model representing filesystem.'''

    ITEM_ROLE = Qt.UserRole + 1

    def __init__(self, path='', parent=None, iconFactory=None):
        '''Initialise with root *path*.'''
        super(Filesystem, self).__init__(parent=parent)
        self.root = ItemFactory(path)
        self.columns = ['Name', 'Size', 'Type', 'Date Modified']

        if iconFactory is None:
            # Local import to circumvent circular dependency.
            import riffle.icon_factory
            iconFactory = riffle.icon_factory.IconFactory()

        self.iconFactory = iconFactory

    def rowCount(self, parent):
        '''Return number of children *parent* index has.'''
        if parent.column() > 0:
            return 0

        if parent.isValid():
            item = parent.internalPointer()
        else:
            item = self.root

        return len(item.children)

    def columnCount(self, parent):
        '''Return amount of data *parent* index has.'''
        return len(self.columns)

    def flags(self, index):
        '''Return flags for *index*.'''
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def index(self, row, column, parent):
        '''Return index for *row* and *column* under *parent*.'''
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            item = self.root
        else:
            item = parent.internalPointer()

        try:
            child = item.children[row]
        except IndexError:
            return QModelIndex()
        else:
            return self.createIndex(row, column, child)

    def pathIndex(self, path):
        '''Return index of item with *path*.'''
        if path == self.root.path:
            return QModelIndex()

        if not path.startswith(self.root.path):
            return QModelIndex()

        parts = []
        while True:
            if path == self.root.path:
                break

            head, tail = os.path.split(path)
            if head == path:
                if path:
                    parts.append(path)
                break

            parts.append(tail)
            path = head

        parts.reverse()
        if parts:
            item = self.root
            count = 0

            for count, part in enumerate(parts):
                matched = False

                for child in item.children:
                    if child.name == part:
                        item = child
                        matched = True
                        break

                if not matched:
                    break

            if count + 1 == len(parts):
                return self.createIndex(item.row, 0, item)

        return QModelIndex()

    def parent(self, index):
        '''Return parent of *index*.'''
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if not item:
            return QModelIndex()

        parent = item.parent
        if not parent or parent == self.root:
            return QModelIndex()

        return self.createIndex(parent.row, 0, parent)

    def item(self, index):
        '''Return item at *index*.'''
        return self.data(index, role=self.ITEM_ROLE)

    def icon(self, index):
        '''Return icon for index.'''
        return self.data(index, role=Qt.DecorationRole)

    def data(self, index, role):
        '''Return data for *index* according to *role*.'''
        if not index.isValid():
            return None

        column = index.column()
        item = index.internalPointer()

        if role == self.ITEM_ROLE:
            return item

        elif role == Qt.DisplayRole:

            if column == 0:
                return item.name
            elif column == 1:
                if item.size:
                    return item.size
            elif column == 2:
                return item.type
            elif column == 3:
                if item.modified is not None:
                    return item.modified.strftime('%c')

        elif role == Qt.DecorationRole:
            if column == 0:
                return self.iconFactory.icon(item)

        elif role == Qt.TextAlignmentRole:
            if column == 1:
                return Qt.AlignRight
            else:
                return Qt.AlignLeft

        return None

    def headerData(self, section, orientation, role):
        '''Return label for *section* according to *orientation* and *role*.'''
        if orientation == Qt.Horizontal:
            if section < len(self.columns):
                column = self.columns[section]
                if role == Qt.DisplayRole:
                    return column

        return None

    def hasChildren(self, index):
        '''Return if *index* has children.

        Optimised to avoid loading children at this stage.

        '''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()
            if not item:
                return False

        return item.mayHaveChildren()

    def canFetchMore(self, index):
        '''Return if more data available for *index*.'''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()

        return item.canFetchMore()

    def fetchMore(self, index):
        '''Fetch additional data under *index*.'''
        if not index.isValid():
            item = self.root
        else:
            item = index.internalPointer()

        if item.canFetchMore():
            startIndex = len(item.children)
            additionalChildren = item.fetchChildren()
            endIndex = startIndex + len(additionalChildren) - 1
            if endIndex >= startIndex:
                self.beginInsertRows(index, startIndex, endIndex)
                for newChild in additionalChildren:
                    item.addChild(newChild)
                self.endInsertRows()

    def reset(self):
        '''Reset model'''
        self.beginResetModel()
        self.root.refetch()
        self.endResetModel()


class FilesystemSortProxy(QSortFilterProxyModel):
    '''Sort directories before files.'''

    def lessThan(self, left, right):
        '''Return ordering of *left* vs *right*.'''
        sourceModel = self.sourceModel()
        if sourceModel:
            leftItem = sourceModel.item(left)
            rightItem = sourceModel.item(right)

            if (isinstance(leftItem, Directory)
                and not isinstance(rightItem, Directory)):
                return self.sortOrder() == Qt.AscendingOrder

            elif (not isinstance(leftItem, Directory)
                and isinstance(rightItem, Directory)):
                return self.sortOrder() == Qt.DescendingOrder

        return super(FilesystemSortProxy, self).lessThan(left, right)

    @property
    def root(self):
        '''Return root of model.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return None

        return sourceModel.root

    @property
    def iconFactory(self):
        '''Return iconFactory of model.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return None

        return sourceModel.iconFactory

    def pathIndex(self, path):
        '''Return index of item with *path*.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return QModelIndex()

        return self.mapFromSource(sourceModel.pathIndex(path))

    def item(self, index):
        '''Return item at *index*.'''
        sourceModel = self.sourceModel()

        if not sourceModel:
            return None

        return sourceModel.item(self.mapToSource(index))

    def icon(self, index):
        '''Return icon for index.'''
        sourceModel = self.sourceModel()
        if not sourceModel:
            return None

        return sourceModel.icon(self.mapToSource(index))

    def hasChildren(self, index):
        '''Return if *index* has children.'''
        sourceModel = self.sourceModel()

        if not sourceModel:
            return False

        return sourceModel.hasChildren(self.mapToSource(index))

    def canFetchMore(self, index):
        '''Return if more data available for *index*.'''
        sourceModel = self.sourceModel()

        if not sourceModel:
            return False

        return sourceModel.canFetchMore(self.mapToSource(index))

    def fetchMore(self, index):
        '''Fetch additional data under *index*.'''
        sourceModel = self.sourceModel()

        if not sourceModel:
            return False

        return sourceModel.fetchMore(self.mapToSource(index))
