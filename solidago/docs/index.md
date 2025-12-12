# solidago [![pypi](https://img.shields.io/pypi/v/solidago.svg?color=%2334D058)](https://pypi.python.org/pypi/solidago) [![license](https://img.shields.io/pypi/l/solidago)](https://github.com/tournesol-app/tournesol/blob/main/solidago/README.md#copyright--license)

A toolbox for **Soli**d **A**lgorithmic **Go**vernance, used by the [Tournesol](https://tournesol.app) platform.

{{ version }}


## Usage

```py title="Pipeline Usage"
import logging
from solidago.pipeline import Pipeline
from solidago.pipeline.inputs import TournesolDataset
from solidago.pipeline.outputs import PipelineOutputInMemory

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize pipeline with its input and output
tournesol_dataset = TournesolDataset.download()
pipeline = Pipeline()
output = PipelineOutputInMemory()

# Run pipeline
pipeline.run(
    input=tournesol_dataset,
    output=output,
    criterion="largely_recommended",
)

# Access results
print(output.individual_scores)
print(output.entity_scores)
```

## Installation

**`solidago`** requires **Python >= 3.13**

### From PyPI

Using `pip`:

```bash
pip install solidago
```

### From source

To install `solidago` from branch "main":

```bash
pip install "git+https://github.com/tournesol-app/tournesol.git@main#egg=solidago&subdirectory=solidago"
```