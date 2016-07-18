..
    :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _release/release_notes:

*************
Release Notes
*************

.. release:: Upcoming

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
