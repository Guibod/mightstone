# mightstone


[![PyPi](https://img.shields.io/pypi/v/mightstone.svg)](https://pypi.python.org/pypi/mightstone)
[![Documentation](https://readthedocs.org/projects/mightstone/badge/?version=latest)](https://mightstone.readthedocs.io/en/latest/?badge=latest)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A library manage all things Magic The Gathering related in python


## Developing

Run `make` for help

    make install             # Run `poetry install`
    make showdeps            # run poetry to show deps
    make lint                # Runs bandit and black in check mode
    make format              # Formats you code with Black
    make test                # run pytest with coverage
    make build               # run `poetry build` to build source distribution and wheel
    make pyinstaller         # Create a binary executable using pyinstaller


## System dependencies

Mightstone use [Ijson](https://github.com/ICRAR/ijson) that relies on [YAJL](https://lloyd.github.io/yajl/). IJson will
use its python backend on the run if YAJL is not installed, but you cold benefit from installing YAJL locally.


