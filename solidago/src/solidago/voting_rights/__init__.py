""" Step 2 of the pipeline.
    
Voting rights are assigned per user and per entity,
based on users' trust scores and privacy settings.
"""

from .base import VotingRights, VotingRightsAssignment
from .affine_overtrust import AffineOvertrust
