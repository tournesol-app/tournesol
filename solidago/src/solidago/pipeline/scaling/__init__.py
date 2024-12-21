""" Step 4 of the pipeline.
    
Scaling addresses the "Parisian" and the "Marseillais" problems,
i.e. users with too extreme scores, 
or whose negative scores correspond to entities that others rate as positive.
This latter effect is particularly an issue in comparison-based preference learning,
assuming each user has a very specific selection bias of rated entities.
"""

from .base import Scaling
from .compose import ScalingCompose
from .no_scaling import NoScaling
from .mehestan import Mehestan
from .quantile_zero_shift import QuantileShift, QuantileZeroShift
from .standardize import Standardize
