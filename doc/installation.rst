..
    :copyright: Copyright (c) 2014 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _installation:

************
Installation
************

.. highlight:: bash

Installing Riffle is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install riffle

If the Cheeseshop (a.k.a. PyPI) is down, you can also install Riffle from one
of the mirrors::

    $ pip install --use-mirrors riffle

Alternatively, you may wish to download manually from Github where Riffle
is `actively developed <https://gitlab.com/4degrees/riffle>`_.

You can clone the public repository::

    $ git clone git@gitlab.com:4degrees/riffle.git

Or download an appropriate
`zipball <https://gitlab.com/4degrees/riffle/repository/archive.zip?ref=master>`_

Once you have a copy of the source, you can install it into your site-packages::

    $ python setup.py install

Dependencies
============

* `Python <http://python.org>`_ >= 2.6, < 3
* `PySide <http://qt-project.org/wiki/PySide>`_ >= 1.2.2, < 2
* `Clique <https://gitlab.com/4degrees/clique>`_ >= 1.2.0, < 2

Additional For testing
----------------------

* `Pytest <http://pytest.org>`_  >= 2.3.5