""" Step 4 of the pipeline.
    
Scaling addresses the "Parisian" and the "Marseillais" problems,
i.e. users with too extreme scores, 
or whose negative scores correspond to entities that others rate as positive.
This latter effect is particularly an issue in comparison-based preference learning,
assuming each user has a very specific selection bias of rated entities.
"""

from .mehestan import Mehestan
from .lipschitz_quantile_shift import LipschitzQuantileShift, LipschitzQuantileZeroShift
from .lipschitz_standardize import LipschitzStandardize
