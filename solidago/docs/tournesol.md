# Using Tournesol dataset with Solidago

An instance of `TournesolDataset` can be used as a pipeline input in Solidago.

```py
from solidago.pipeline.inputs import TournesolDataset

# Download the latest dataset from Tournesol API.
pipeline_input = TournesolDataset.download()

# Read a local file
pipeline_input = TournesolDataset("path/to/dataset.zip")
```

::: solidago.pipeline.inputs
    options:
        members:
            - TournesolDataset
