# Solidago

[![PyPi](https://img.shields.io/pypi/v/solidago)](https://pypi.org/project/solidago)
[![License](https://img.shields.io/pypi/l/solidago.svg)](https://github.com/tournesol-app/tournesol/tree/main/solidago#copyright--license)
[![CI status](https://github.com/tournesol-app/tournesol/actions/workflows/solidago-test.yml/badge.svg)](https://github.com/tournesol-app/tournesol/actions/workflows/solidago-test.yml)

A toolbox for **Solid** **A**lgorithmic **Go**vernance, used by the Tournesol platform.

**Documentation**: https://solidago.tournesol.app

---

## Development

### Tests

To run tests, setup a virtual environment, activate it, install dependencies and run pytest.
```sh
python3 -m venv devenv
source devenv/bin/activate
pip install -e .[test]
pytest
```
Depending on the platform, you may need to replace ```source devenv/bin/activate``` by another call.
See the [venv doc](https://docs.python.org/3/library/venv.html#how-venvs-work) for more information.

### Docs

The documentation website (deployed to https://solidago.tournesol.app) is built using [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

To build the documentation locally:

1. Install the "docs" dependencies in your virtual environment
```sh
pip install -e .[docs]
```

2. Start the MkDocs development server
```sh
mkdocs serve -a localhost:9000
```
Find more options on https://www.mkdocs.org/user-guide/cli/


## Synthetic experiments

To run experiments, once the virtual environement setup, you may run the experiments on synthetic data using.
```
python3 experiments/synthetic.py experiments/resilience.json
python3 experiments/synthetic.py experiments/engagement_bias.json
```
The results will be exported in ```experiments/results```.
You may modify the experiments by editing ```experiments/resilience.json```, 
or by creating a new ```.json``` file.


## Publish a new release

1. In a Pull Request, update the version number in [`./src/solidago/__version__.py`](./src/solidago/__version__.py)
2. The package will be published automatically when the new version is merged into "main", by [this Github Action](../.github/workflows/solidago-publish.yml).


## Copyright & License

Copyright 2023-2025 Tournesol Association and contributors.

This program is free software: you can redistribute it and/or modify it under the terms of the [**GNU Lesser General Public License**](./LICENSE.LESSER) as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program. If not, see https://www.gnu.org/licenses/.
