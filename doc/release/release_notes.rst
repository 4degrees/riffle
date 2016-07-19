..
    :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _release/release_notes:

*************
Release Notes
*************

.. release:: Upcoming

    .. change:: new
        :tags: interface

        :kbd:`Backspace` key now navigates up a level in the browser.

.. release:: 0.2.1
    :date: 2016-07-19

    .. change:: fixed
        :tags: documentation

        Documentation fails to build on Read the Docs due to PySide dependency.

.. release:: 0.2.0
    :date: 2016-07-18

    .. change:: fixed
        :tags: interface

        Empty contents displayed when an error occurs navigating to a location
        interactively. Now a warning dialog is displayed and the navigation
        aborted.

        .. seealso:: :meth:`riffle.browser.FilesystemBrowser.setLocation`.

    .. change:: fixed
        :tags: API

        :class:`riffle.model.FilesystemSortProxy` swallowed exceptions
        incorrectly when fetching additional items from the source model.

    .. change:: fixed
        :tags: test

        Interactive test hangs on exit due to second execution loop started.

    .. change:: changed
        :tags: test

        Interactive test now sizes test browser to half of current screen
        dimensions on startup.

    .. change:: new

        Added :ref:`release` to documentation.

.. release:: 0.1.0
    :date: 2014-06-26

    .. change:: new

        Initial release supporting navigation of standard filesystems. Also
        provides support for viewing and navigating file sequences.
