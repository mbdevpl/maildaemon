.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python


==========
maildaemon
==========

.. image:: https://img.shields.io/pypi/v/maildaemon.svg
    :target: https://pypi.python.org/pypi/maildaemon
    :alt: package version from PyPI

.. image:: https://travis-ci.org/mbdevpl/maildaemon.svg?branch=master
    :target: https://travis-ci.org/mbdevpl/maildaemon
    :alt: build status from Travis CI

.. image:: https://api.codacy.com/project/badge/Grade/b35bf4a73a724854b0ba1cef4385c6f7
    :target: https://www.codacy.com/app/mbdevpl/maildaemon
    :alt: grade from Codacy

.. image:: https://codecov.io/gh/mbdevpl/maildaemon/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mbdevpl/maildaemon
    :alt: test coverage from Codecov

.. image:: https://img.shields.io/pypi/l/maildaemon.svg
    :target: https://github.com/mbdevpl/maildaemon/blob/master/NOTICE
    :alt: license

Multi-server mail filtering daemon supporting IMAP, POP and SMTP.


user guide
==========


installation
------------

For simplest installation use :bash:`pip`:

.. code:: bash

    pip3 install maildaemon


Python >= 3.5 is required, and required dependencies defined in `<requirements.txt>`_
will be automatically installed too.

Maildaemon works based on a JSON configuration file. If it doesn't exist,
detault one will be generated. An example is provided in `<test/maildaemon_test_config.json>`_


supported protocols
-------------------

Currently, the package has a very limited support for:

-  IMAP4rev1

-  SMTP

-  POP3


filtering options
-----------------


conditions
~~~~~~~~~~

Python expression.


actions
~~~~~~~

Move, mark as read etc.

