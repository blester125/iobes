------------
Installation
------------

Using pip
=========

PyPI install with ``pip``:

.. code:: bash

    pip install iobes

From source
===========

To install from the source, clone the github repository and install with pip.

.. code:: bash

    git clone https://github.com/blester125/iobes.git
    cd iobes
    pip install .

Local Development
-----------------

If you want to install the package and run tests install the optional testing dependencies. You can use the ``-e``
option to install in "editable" mode so that changes you make in the source code will get used without re-installing the package.

.. code:: bash

    pip install .[test]

Run the tests with ``pytest``.

.. code:: bash

    pytest

Set up ``pre-commit`` hooks to autoformat your changes with `black <https://black.readthedocs.io/en/stable>`_.

.. code:: bash

    pip install pre-commit
    pre-commit install

Building the Docs
-----------------

To build the documentation locally install the documentation requirements and run make.

.. code:: bash

    pip install -r requirements-docs.txt
    cd docs
    make html
    open build/html/index.html
