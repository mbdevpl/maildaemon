.. role:: bash(code)
    :language: bash

.. role:: json(code)
    :language: json


==========
maildaemon
==========

Multi-server mail filtering daemon supporting IMAP, POP and SMTP.

.. image:: https://img.shields.io/pypi/v/maildaemon.svg
    :target: https://pypi.org/project/maildaemon
    :alt: package version from PyPI

.. image:: https://github.com/mbdevpl/maildaemon/actions/workflows/python.yml/badge.svg?branch=main
    :target: https://github.com/mbdevpl/maildaemon/actions
    :alt: build status from GitHub

.. image:: https://codecov.io/gh/mbdevpl/maildaemon/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/mbdevpl/maildaemon
    :alt: test coverage from Codecov

.. image:: https://api.codacy.com/project/badge/Grade/b35bf4a73a724854b0ba1cef4385c6f7
    :target: https://app.codacy.com/gh/mbdevpl/maildaemon
    :alt: grade from Codacy

.. image:: https://img.shields.io/github/license/mbdevpl/maildaemon.svg
    :target: NOTICE
    :alt: license

The goal of this library is to enable unified filtering for various e-mail servers,
as well as inter-account filtering. Additional aim of this project is to enable filtering e-mails
in a centralized way as opposed to some filters being applied by the server,
and another filters by the client.

Eventually, maildaemon should make provider-dependent and client-dependent mail filtering settings obsolete.
It is currently in development and doesn't achieve its goals yet.

Usage examples are shown in `<examples.ipynb>`_

.. contents::
    :backlinks: none


Installation
============

For simplest installation use :bash:`pip`:

.. code:: bash

    pip3 install maildaemon


Python 3.11 or later is required, and required dependencies defined in `<requirements.txt>`_
will be automatically installed too.

Maildaemon works based on a JSON configuration file. If it doesn't exist,
default one will be generated. An example is provided in `<test/maildaemon_test_config.json>`_.


Supported protocols
===================

Currently, the package has a very limited support for:

*   IMAP4rev1 -- via Python built-in `imaplib <https://docs.python.org/3/library/imaplib.html>`_ module.

    You can see how the module works in `<examples/imap_examples.ipynb>`_.

*   SMTP -- via Python built-in `smtplib <https://docs.python.org/3/library/smtplib.html>`_ module.

    You can see how the module works in `<examples/smtp_examples.ipynb>`_.

*   POP3 -- via Python built-in `poplib <https://docs.python.org/3/library/poplib.html>`_ module.

    You can see how the module works in `<examples/pop_examples.ipynb>`_.


Supported authentication
========================

*   password
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

For password authentication, connection parameters are:

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

For Oauth authentication, the password can be left empty, but additional parameters
need to be configured instead. Simplified list of parameters to connect to Gmail is provided below:

.. code:: json

    {
      "test-gmail": {
        "protocol": "IMAP",
        "domain": "",
        "ssl": true,
        "port": 993,
        "oauth": true,
        "oauth-data": {
          "token_path": "/path/to/where/tokenfile/will/be/stored.json",
          "client_id": "???.apps.googleusercontent.com",
          "project_id": "???",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "auth_uri_params": {"access_type": "offline", "prompt": "select_account"},
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_secret": "???",
          "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
          "scopes": ["https://mail.google.com/"]
        },
        "login": "my-gmail@gmail.com",
        "password": ""
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

Details to be decided.


Filter actions
~~~~~~~~~~~~~~

*   move -- Move the message to a specific folder on a specific account.

    "move:Gmail/INBOX/my mailing list" will move the message to a folder "/INBOX/my mailing list"
    in account named "Gmail".

    "move:/Archive/2018" will move the message to the "/Archive/2018" folder within the same account.

*   mark -- Used to mark messages as read, unread etc.

    "mark:read" will mark message as read.

    "mark:unread" will mark message as unread.

    "mark:important" will mark a message as important. Effect may vary between clients.
    In Gmail web mail client this is visible as star, in Mac mail client as a red flag,
    in Evolution as "Important message".

*   More actions to be implemented.


Testing locally
===============

Start Greenmail server in docker:

.. code:: bash

    docker run --rm -d --name greenmail -p 3143:3143 -p 3993:3993 -p 310:3110 -p 3995:3995 -p 3025:3025 -p 3465:3465 -e GREENMAIL_OPTS='-Dgreenmail.verbose -Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.users=login:password@domain.com -Dgreenmail.users.login=email -Dgreenmail.auth.disabled' -t greenmail/standalone:2.0.0

Make sure that services are running:

.. code:: bash

    .build/check_ports.sh

Run tests:

.. code:: bash

    TEST_COMM=1 python3 -m coverage run --branch --source . -m unittest -v test.test_smtp_connection
    TEST_COMM=1 python3 -m coverage run --branch --source . -m unittest -v

Stop the Greenmail server:

.. code:: bash

    docker container kill greenmail
