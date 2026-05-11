""" **Step 2 in the pipeline**
    
Voting rights are assigned per user and per entity,
based on users' trust scores and privacy settings.
"""

from .is_trust import Trust2VotingRights
from .affine_overtrust import AffineOvertrust
from .follows import Follows
from .likes import LikesVolumes
from .mentions import Mentions
from .volume import AggregateVolumes