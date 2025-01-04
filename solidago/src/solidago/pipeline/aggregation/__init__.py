""" Step 5 of the pipeline.
    
Aggregation combines the different user models to construct a global model.
The aggregation may also adjust the user models to the learned global model.
"""

from .average import Average
from .entitywise_qr_quantile import EntitywiseQrQuantile
