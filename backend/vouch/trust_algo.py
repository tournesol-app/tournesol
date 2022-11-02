import logging

import numpy as np
from django.db.models import Q
from numpy.typing import NDArray

from core.models.user import User
from vouch.models import Voucher

logger = logging.getLogger(__name__)

# In this algorithm, we leverage pre-trust (e.g., based on email domains) and
# vouching to securely assign trust scores to a wider set of contributors. The
# algorithm inputs pre-trust status and a vouching directed graph.


# Trust scores are computed iteratively, which yields an approximate solution.
APPROXIMATION_ERROR = 1e-8

# In our model we assume that each participating contributor implicitly
# vouches for a sink. The sink counts for 10 vouchees. As a result, when a
# contributor with less than 10 vouchees vouches for more vouchees,
# the amount of trust scores the contributor assigns grows almost
# linearly, thereby not penalizing previously vouched contributors.
# Vouching is thereby not (too) disincentivized.
SINK_VOUCH = 10

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


def get_weighted_vouch_matrix(vouch_matrix: NDArray) -> NDArray:
    """
    Returns the weighted_vouch_matrix, derived from the vouch_matrix
    (composed of explicit Voucher created by users).

    The weighted_vouch_matrix integrates implicit vouches, i.e vouches
    attributed to a sink, such as the sum of weighted vouches given by
    any voucher is at most one.
    """

    n_vouches_by_voucher = vouch_matrix.sum(axis=1)
    weighted_denominator = n_vouches_by_voucher + SINK_VOUCH
    weighted_vouch_matrix = vouch_matrix / weighted_denominator[:, np.newaxis]
    return weighted_vouch_matrix


def compute_byztrust(weighted_vouch_matrix, pretrusts: NDArray):
    """
    Return a vector of trust scores per user, given the vouch network
    and the pre-trust scores (based on user's email domains).
    ByzTrust is inspired from EigenTrust.
    """
    trusts = pretrusts
    delta = np.inf
    while delta >= APPROXIMATION_ERROR:
        # Apply vouch decay
        new_trusts = pretrusts + VOUCH_DECAY * weighted_vouch_matrix.T.dot(trusts)
        # Clip to avoid power concentration
        new_trusts = new_trusts.clip(max=1.0)

        delta = np.linalg.norm(new_trusts - trusts, ord=1)
        trusts = new_trusts
    return trusts


def trust_algo():
    """
    Improved version of the EigenTrust algorithm.

    Compute a global trust score for all users, based on the set of
    pre-trusted users and on vouching made between users.

    (* the ones with an email from a trusted domain).
    """
    # Import users and pretrust status
    users = list(
        User.objects.all()
        .annotate(with_trusted_email=Q(pk__in=User.with_trusted_email()))
        .only("id")
    )
    users_index__user_id = {
        user.id: user_index for user_index, user in enumerate(users)
    }
    pretrusts = np.array([
        TRUSTED_EMAIL_PRETRUST if u.with_trusted_email else 0.0
        for u in users
    ])
    if np.sum(pretrusts) == 0:
        logger.warning("Trust scores cannot be computed: no pre-trusted user exists")
        return

    nb_users = len(users)

    # Import vouch matrix
    vouch_matrix = np.zeros([nb_users, nb_users], dtype=float)
    for vouch in Voucher.objects.iterator():
        voucher = users_index__user_id[vouch.by_id]
        vouchee = users_index__user_id[vouch.to_id]
        vouch_matrix[voucher][vouchee] = vouch.value

    # Compute weighted vouch matrix (row-substochastic)
    weighted_vouch_matrix = get_weighted_vouch_matrix(vouch_matrix)

    # Compute trust scores using ByzTrust
    trust_scores = compute_byztrust(weighted_vouch_matrix, pretrusts)

    # Update `trust_score` in the database
    for user_no, user_model in enumerate(users):
        user_model.trust_score = float(trust_scores[user_no])
    User.objects.bulk_update(users, ["trust_score"])
