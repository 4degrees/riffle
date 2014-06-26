..
    :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _usage:

*****
Usage
*****

To use the browser, first create an instance of it and configure the size as
desired::

    import riffle.browser

    browser = riffle.browser.FilesystemBrowser()
    browser.setMinimumSize(800, 400)

Then open it in blocking mode and retrieve any selected files chosen by the
user::

    if browser.exec_():
        selected = browser.selected()
        print('Selected: {0}'.format(selected))

.. image:: /image/browser.png

.. code-block:: text

    Selected: [u'C:\\Users\\Martin\\data\\scratch\\ftrack_test.mov']

The browser can also identify sequences of files (using
`Clique <https://github.com/4degrees/clique>`_). They will be displayed as a
special *collection* item and can be navigated into like a directory to see and
select individual files.

.. image:: /image/browser_sequence.png

.. image:: /image/browser_sequence_item.png

Each browser instance can be configured with a root path. The browser will not
be able to navigate above this root path::

    browser = riffle.browser.FilesystemBrowser('C:\\Users')
    browser.show()

.. image:: /image/browser_root.png

In addition to a root, a browser also has a location that can be set
to change the currently displayed location::

    browser.setLocation('C:\\Users\\Martin')

.. image:: /image/browser_location.png

.. note::

    It is not possible to set a location that is outside the root path tree. An
    error is raised if attempted.

Icons
=====

Icons displayed for entries in the browser are provided by an
:py:class:`~riffle.icon_factory.IconFactory`. You can pass in your own icon
factory to the browser to customise the icons used::

    class AllFilesIconFactory(object):
        '''Force all icons to be file icons.'''

        def icon(self, specification):
            '''Return appropriate icon for *specification*.

            *specification* should be either:

                * An instance of :py:class:`riffle.model.Item`
                * One of the defined icon types (:py:class:`IconType`)

            '''
            return QtGui.QIcon(':riffle/icon/file')


    browser = riffle.browser.FilesystemBrowser(
        iconFactory=AllFilesIconFactory()
    )

.. image:: /image/browser_custom_icons.png