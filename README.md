# crdppf_core

Core / generic parts of the CRDPPF project

This has to be used as a submodule in your own CRDPPF project.

See https://github.com/sitn/crdppf

## Requirements for Linux

For Linux, you will need python-dev and python-venv, which
can be installed with:

    sudo apt-get install python3-dev
    sudo apt-get install python3-venv

In your Makfile, you should also overwrite the following variables:

    VENV_BIN ?= .build/venv/bin
    PYTHON_EXE ?= python3

## Development

### Python code

When developping some Python code, you should run Flake8 on it, to be
sure that your code follows pep8

    buildout\bin\flake8 crdppf_core\crdppf\util
    buildout\bin\flake8 crdppf_core\crdppf\views
    buildout\bin\flake8 crdppf_core\crdppf\models.py
    buildout\bin\flake8 crdppf_core\crdppf\__init__.py
    ...

(Do not run it on the whole package, because it contains a lot of external
libs).

It might also be good to check the McCabe complexity from time to time.

    buildout\bin\flake8 --max-complexity 10 crdppf_core\crdppf\util
    buildout\bin\flake8 --max-complexity 10 crdppf_core\crdppf\views
    buildout\bin\flake8 --max-complexity 10 crdppf_core\crdppf\models.py
    buildout\bin\flake8 --max-complexity 10 crdppf_core\crdppf\__init__.py
    ...
