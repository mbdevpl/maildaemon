.. role:: bash(code)
    :language: bash

.. role:: json(code)
    :language: json


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


Installation
============

For simplest installation use :bash:`pip`:

.. code:: bash

    pip3 install maildaemon


Python >= 3.5 is required, and required dependencies defined in `<requirements.txt>`_
will be automatically installed too.

Maildaemon works based on a JSON configuration file. If it doesn't exist,
detault one will be generated. An example is provided in `<test/maildaemon_test_config.json>`_.


Supported protocols
===================

Currently, the package has a very limited support for:

*  IMAP4rev1
*  SMTP
*  POP3


Supported authentication
========================

*   usual
*   oauth


Configuration
=============

The configuration file has two sections:

.. code:: json

    {
      "connections": { },
      "filters": { }
    }

A complete example is provided in `<test/maildaemon_test_config.json>`_.


Connections
-----------

The "connections" section is a dictionary where keys are human-readable connection names,
and values are dictionaries that describe connection parameters.

Connection parameters are:

*   protocol -- IMAP, POP or SMTP
*   domain -- a string of characters
*   ssl -- a boolean flag
*   port -- a number
*   login -- a string of characters
*   password -- a string of characters

.. code:: json

    {
      "test-imap-ssl": {
        "protocol": "IMAP",
        "domain": "127.0.0.1",
        "ssl": true,
        "port": 993,
        "login": "testuser",
        "password": "applesauce"
      },
      "test-pop-ssl": {
        "protocol": "POP",
        "domain": "127.0.0.1",
        "ssl": true,
        "port": 995,
        "login": "testuser",
        "password": "applesauce"
      }
    }


Filters
-------

The "filters" section is a dictionary as well, where keys are human-readable filter names,
and values are dictionaries that describe filter parameters.

Filter parameters are:

*   connections -- a list of human-readable connection names defined in the "connections" section
*   condition -- a Python expression, described in detail below
*   actions -- a list (sequence) of commands to perform, described in detail below


.. code:: json

    {
      "facebook-notification": {
        "connections": [
          "test-imap"
        ],
        "condition": "from_address.endswith('@facebookmail.com') and from_address.startswith('notification')",
        "actions": [
          "mark:read"
        ]
      }
    }


Filter condition
~~~~~~~~~~~~~~~~

TODO


Filter actions
~~~~~~~~~~~~~~

*   move -- Move the message to a specific folder within a specific account.

    "move:Gmail/INBOX/my mailing list" will move the message to a folder "/INBOX/my mailing list"
    in account named "Gmail".

    "move:/Archive/2018" will move the message to the "/Archive/2018" folder within the same account.

*   mark -- Used to mark messages as read, unread etc.

    "mark:read" will mark message as read.

    "mark:unread" will mark message as unread.

    "mark:important" will mark a message as important. Effect may vary between clients.
    In Gmail web mail client this is visible as star, in Mac mail client as a red flag,
    in Evolution as "Important message".
