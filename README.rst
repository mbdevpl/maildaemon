.. role:: bash(code)
    :language: bash

.. role:: json(code)
    :language: json


==========
maildaemon
==========

Multi-server mail filtering daemon supporting IMAP, POP and SMTP.

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

.. image:: https://img.shields.io/github/license/mbdevpl/maildaemon.svg
    :target: https://github.com/mbdevpl/maildaemon/blob/master/NOTICE
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


Python 3.5 or later is required, and required dependencies defined in `<requirements.txt>`_
will be automatically installed too.

Maildaemon works based on a JSON configuration file. If it doesn't exist,
detault one will be generated. An example is provided in `<test/maildaemon_test_config.json>`_.


Supported protocols
===================

Currently, the package has a very limited support for:

*   IMAP4rev1 -- via Python built-in `imaplib<https://docs.python.org/3/library/imaplib.html>`_ module.

    You can see how the module works in `<examples/imap_examples.ipynb>`_.

*   SMTP -- via Python built-in `smtplib<https://docs.python.org/3/library/smtplib.html>`_ module.

    You can see how the module works in `<examples/smtp_examples.ipynb>`_.

*   POP3 -- via Python built-in `poplib<https://docs.python.org/3/library/poplib.html>`_ module.

    You can see how the module works in `<examples/pop_examples.ipynb>`_.


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

Details to be decided.


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


Testing locally
===============

Running IMAP and POP server in vagrant:

.. code:: bash

    git clone https://github.com/mbdevpl/DovecotTesting.git
    cd DovecotTesting/vagrant
    vagrant up --provision
    sudo -E ssh -F ssh_config DovecotTesting -p $(vagrant port --guest 22)  # ssh password: "vagrant"

Running SMTP server in docker:

.. code:: bash

    (sudo) docker pull gessnerfl/fake-smtp-server
    (sudo) docker run -d --name fake-smtp -p 25:5025 -e "fakesmtp_authentication_username=testuser" -e "fakesmtp_authentication_password=applesauce" gessnerfl/fake-smtp-server

Check if services are running:

.. code:: bash

    ./DovecotTesting/VerifyEnvironment.sh  # IMAP and POP
    sudo docker ps  # SMTP

Running tests:

.. code:: bash

    vagrant provision  # to reset IMAP/POP mailboxes after previous tests
    TEST_COMM=1 TEST_SMTP=1 python3 -m coverage run --branch --source . -m unittest discover --verbose

The vagrant service has a built-in 30 min timeout, and will turn off after it.
Running "vagrant provision" resets the countdown.
If you miss the timeout, run "vagrant up --provision" and ssh again.

Stop the services:

.. code:: bash

    vagrant down  # IMAP and POP
    (sudo) docker container kill fake-smtp  # SMTP
