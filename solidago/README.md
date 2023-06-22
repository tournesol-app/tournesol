# Solidago
**Solid** **A**lgorithmic **Go**vernance, used by the Tournesol platform

<a href="https://pypi.org/project/solidago" target="_blank">
    <img src="https://img.shields.io/pypi/v/solidago?color=%2334D058" alt="Package version">
</a>
<a href="#copyright--license">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/solidago">
</a>


## Usage

> **Warning**  
> This library is WIP; its API may change in the near future.

```py
import numpy as np
from solidago.resilient_primitives import QrMed

score = QrMed(W=1, w=1, x=np.array([-1.0, 1.0, 2.0]), delta=np.array([1.0, 1.0, 1.0]))
```

## Publish a new release

1. In a Pull Request, update the version number in [`./src/solidago/__version__.py`](./src/solidago/__version__.py)
2. The package will be published automatically when the new version is merged into "main", by [this Github Action](../.github/workflows/solidago-publish.yml).

## Copyright & License

Copyright 2023 Tournesol Association and contributors.

This program is free software: you can redistribute it and/or modify it under the terms of the [**GNU Lesser General Public License**](./LICENSE.LESSER) as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program. If not, see https://www.gnu.org/licenses/.
