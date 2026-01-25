""" **Step 3 of the pipeline**
    
Preference learning infers, for each user and based on their data,
a model of the user's preferences.
This corresponds to the idea of "algorithmic representatives", 
which will participate in the digital democracy 
to remedy users' lack of activity and reactivity.
"""

from .preference_learning import PreferenceLearning
from .numba_generalized_bradley_terry import NumbaUniformGBT
try:
    from .lbfgs_generalized_bradley_terry import LBFGSUniformGBT
except RuntimeError:
    pass

from .parallelized import ParallelizedPreferenceLearning
from .gbt import FlexibleGeneralizedBradleyTerry
