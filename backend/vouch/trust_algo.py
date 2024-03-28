import logging

import pandas as pd
from django.db.models import Q
from solidago.trust_propagation import LipschiTrust

from core.models.user import User
from vouch.models import Voucher

logger = logging.getLogger(__name__)

# In this algorithm, we leverage pre-trust (e.g., based on email domains) and
# vouching to securely assign trust scores to a wider set of contributors. The
# algorithm inputs pre-trust status and a vouching directed graph.


# Trust scores are computed iteratively, which yields an approximate solution.
APPROXIMATION_ERROR = 1e-8

# In our model we assume that each participating contributor implicitly
# vouches for a sink. The sink counts for SINK_VOUCH vouchees. As a result, when a
# contributor with less than SINK_VOUCH vouchees vouches for more vouchees,
# the amount of trust scores the contributor assigns grows almost
# linearly, thereby not penalizing previously vouched contributors.
# Vouching is thereby not (too) disincentivized.
SINK_VOUCH = 5.0

# The algorithm guarantees that every pre-trusted user is given a trust score
# which is at least TRUSTED_EMAIL_PRETRUST. Moreover, all users' trust score
# will be at most 1.
TRUSTED_EMAIL_PRETRUST = 0.8

# When considering a random walker on the vouch network,
# (1 - VOUCH_DECAY) is the probability that the random walker resets
# its walk at each iteration.
# ByzTrust essentially robustifies the random walk, by frequently
# preventing the walker from visiting too frequently visited contributors,
# thereby bounding the maximal influence of such contributors.
VOUCH_DECAY = 0.8


lipshitrust = LipschiTrust(
    pretrust_value=TRUSTED_EMAIL_PRETRUST,
    decay=VOUCH_DECAY,
    sink_vouch=SINK_VOUCH,
    error=APPROXIMATION_ERROR,
)


def trust_algo():
    """
    Improved version of the EigenTrust algorithm.

    Compute a global trust score for all users, based on the set of
    pre-trusted users and on vouching made between users.

    (* the ones with an email from a trusted domain).
    """
    # Import users and pretrust status
    users = list(
        User.objects.filter(is_active=True)
        .annotate(with_trusted_email=Q(pk__in=User.with_trusted_email()))
        .only("id")
    )

    users_df = pd.DataFrame(
        {
            "user_id": user.id,
            "is_pretrusted": user.with_trusted_email,
        }
        for user in users
    )
    users_df.set_index("user_id", inplace=True)
    if not users_df["is_pretrusted"].any():
        logger.warning("Trust scores cannot be computed: no pre-trusted user exists")
        return

    vouches = pd.DataFrame(
        (
            {"voucher": vouch.by_id, "vouchee": vouch.to_id, "vouch": vouch.value}
            for vouch in Voucher.objects.iterator()
            if vouch.by_id in users_df.index and vouch.to_id in users_df.index
        ),
        columns=["voucher", "vouchee", "vouch"],
    )

    trust_scores = lipshitrust(users=users_df, vouches=vouches)["trust_score"]

    for user in users:
        user.trust_score = trust_scores[user.id]

    # Updating all users at once increases the risk of a database deadlock.
    # We use an explicitly low `batch_size` value to reduce this risk.
    User.objects.bulk_update(users, ["trust_score"], batch_size=1000)
