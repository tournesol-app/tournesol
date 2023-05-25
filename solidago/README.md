# Solidago
**Solid** **A**lgorithmic **Go**vernance, used by the Tournesol platform

<a href="https://pypi.org/project/solidago" target="_blank">
    <img src="https://img.shields.io/pypi/v/solidago?color=%2334D058" alt="Package version">
</a>


## Usage

> **Warning**  
> This library is WIP; its API may change in the near future.

```py
import numpy as np
from solidago.mehestan import QrMed

score = QrMed(W=1, w=1, x=np.array([-1.0, 1.0, 2.0]), delta=np.array([1.0, 1.0, 1.0]))
```

## Publish a new release

1. In a Pull Request, update the version number in [`./src/solidago/__version__.py`](./src/solidago/__version__.py)
2. The package will be published automatically when the new version is merged into "main", by [this Github Action](../.github/workflows/solidago-publish.yml).
