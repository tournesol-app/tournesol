""" **Step 2 in the pipeline**
    
Voting rights are assigned per user and per entity,
based on users' trust scores and privacy settings.
"""

from .voting_rights import VotingRights

from .base import VotingRightsAssignment
from .is_trust import IsTrust
from .affine_overtrust import AffineOvertrust

from .compute_voting_rights import compute_voting_rights


__all__ = ["VotingRightsAssignment", "IsTrust", "AffineOvertrust"]
