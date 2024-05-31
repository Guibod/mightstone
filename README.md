# mightstone


[![PyPi](https://img.shields.io/pypi/v/mightstone.svg)](https://pypi.python.org/pypi/mightstone)
[![Documentation](https://readthedocs.org/projects/mightstone/badge/?version=latest)](https://mightstone.readthedocs.io/en/latest/?badge=latest)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/projects/7037/badge)](https://bestpractices.coreinfrastructure.org/projects/7037)


<div align="center">
  <h3 align="centor">Mightstone</h3>
  <a href="https://github.com/guibod/mighstone">
    <img src="docs/source/mightstone.logo.160.png" alt="Logo" width="160" height="160">
  </a>
    
  A library to manage all things Magic The Gathering related in python.<br>
  <a href="https://mightstone.readthedocs.io/en/stable/"><strong>Explore the docs »</strong></a>

<a href="https://github.com/Guibod/mightstone/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
·
<a href="https://github.com/Guibod/mightstone/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

---

## Features

* Mightstone use `Pydantic`, `Beanie` and `Asyncio` as core feature.
* Integrated persistence support through `Beanie` of many data classes. Download once, and use data offline.
* HTTP cache integration
* Supported services:
  * [Scryfall](https://scryfall.com)
  * [EDHREC](https://edhrec.com/)
  * [MTGJSON](https://mtgjson.com/)
  * [CardConjurer](https://cardconjurer.com/)
  * [Magic The Gathering](https://magic.wizards.com/en/rules>) (rules)

Supported on python 3.9, 3.10, 3.11 and 3.12.

---

## Usage
Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

For more examples, please refer to [the Documentation](https://mightstone.readthedocs.io/en/stable/)

---

## Developing

Run `make` for help

    make install             # Run `poetry install`
    make lint                # Runs bandit, black, mypy in check mode
    make test                # run pytest with coverage
    make build               # run `poetry build` to build source distribution and wheel
    make pyinstaller         # Create a binary executable using pyinstaller

---

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

The project lint step will enforce coding standards through Black, Isort and Mypy.

## System dependencies
    
As an asynchronous data handler, Mightstone must handle large JSON files that’s why it relies on IJSON.
Mightstone use [Ijson](https://github.com/ICRAR/ijson) that relies on [YAJL](https://lloyd.github.io/yajl/). IJson will
use its python backend on the run if YAJL is not installed, but you could benefit from installing YAJL locally.


