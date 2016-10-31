
==========
maildaemon
==========

.. image:: https://img.shields.io/pypi/v/maildaemon.svg
    :target: https://pypi.python.org/pypi/maildaemon
    :alt: package version from PyPI

.. image:: https://travis-ci.org/mbdevpl/maildaemon.svg?branch=master
    :target: https://travis-ci.org/mbdevpl/maildaemon
    :alt: build status from Travis CI

.. image:: https://coveralls.io/repos/github/mbdevpl/typed-astunparse/badge.svg?branch=master
    :target: https://coveralls.io/github/mbdevpl/typed-astunparse?branch=master
    :alt: test coverage from Coveralls

.. image:: https://img.shields.io/pypi/l/maildaemon.svg
    :alt: license

.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python

Multi-server mail filtering daemon supporting IMAP, POP and SMTP.


------------
requirements
------------

This package is intendended for Python 3.5 and above. It was tested on 64 bit Ubuntu,
but it might work on other versions and systems too.


------------
installation
------------

For simplest installation use :bash:`pip`:

.. code:: bash

    pip3.5 install maildaemon

You can also build your own version:

.. code:: bash

    git clone https://github.com/mbdevpl/maildaemon
    cd maildaemon
    cp .maildaemon.config{.sample,}
    nano .maildaemon.config # make sure that connections parameters are valid
    python3.5 -m unittest discover # make sure the tests pass
    python3.5 setup.py bdist_wheel
    ls -1tr dist/*.whl | tail -n 1 | xargs pip3.5 install


-------------------
supported protocols
-------------------

Currently, the package has a very limited support for:

-  IMAP4rev1

-  SMTP

-  POP3


-----------------
filtering options
-----------------

?


conditions
__________

?


actions
_______

?
