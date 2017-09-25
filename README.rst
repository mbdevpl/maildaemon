.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python


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


requirements
------------

This package is intended for Python 3.5 and above. It was tested on 64 bit Ubuntu,
but it might work on other versions and systems too.


installation
------------

For simplest installation use :bash:`pip`:

.. code:: bash

    pip3 install maildaemon

You can also build your own version:

.. code:: bash

    git clone https://github.com/mbdevpl/maildaemon
    cd maildaemon
    cp .maildaemon.config{.sample,}
    nano .maildaemon.config # make sure that connections parameters are valid
    python3 -m unittest discover # make sure the tests pass
    python3 setup.py bdist_wheel
    ls -1tr dist/*.whl | tail -n 1 | xargs pip3 install


supported protocols
-------------------

Currently, the package has a very limited support for:

-  IMAP4rev1

-  SMTP

-  POP3


filtering options
-----------------

?


conditions
~~~~~~~~~~

?


actions
~~~~~~~

?
