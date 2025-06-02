## Quick start on Tournesol's data

{{ version }}

```py title="Pipeline Usage"
import solidago

# Import dataset
tiny_tournesol = solidago.TinyTournesolExport.download()

# Load a pipeline to process the dataset
pipeline = solidago.FullTournesolPipeline()

# Run pipeline
output_state = pipeline(tiny_tournesol)

# Access results
print(output_state.user_models)
print(output_state.global_model)
```

