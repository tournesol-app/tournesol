import numpy as np
from django.db.models import Q
from numpy.typing import NDArray

from core.models import user
from vouch.models import Voucher

# In this algorithm, we leverage pretrust (e.g., based on email domains) and vouching
# to securely assign voting rights to a wider set of contributors.
# The algorithm inputs pretrust status and a vouching directed graph.

# If PRETRUST_BIAS == 1, then vouching yields no voting rights to non-pretrusted users.
# If PRETRUST_BIAS is close to 0, then pre-trust vanishes (which is very unsafe).
PRETRUST_BIAS = 0.2

# Voting rights are computed iteratively, which yields an approximate solution.
APPROXIMATION_ERROR = 1e-8

# In our model, users that vouch for few (if any) implicitly vouch for pre-trusted users.
# IMPLICIT_PRETRUST_VOUCH is the implicit amount of vouch given to pretrusted,
# as opposed to the explicit vouches, each of which is of unit value.
IMPLICIT_PRETRUST_VOUCH = 0.1

# The algorithm guarantees that every pretrusted user is allocated a voting right
# which is at least MIN_PRETRUST_VOTING_RIGHT
# Moreover all users' voting rights will be at most 1
MIN_PRETRUST_VOTING_RIGHT = 0.8


def normalize_vouch_matrix(vouch_matrix: NDArray, pretrusts: NDArray) -> NDArray:
    """
    Vouch matrix normalization guarantees three properties:
    - The sum of normalized vouches given by a voucher equals 1.
    - Each voucher vouchees for pretrusted users.
    - Vouchers that explicitly vouch for many barely vouch for pretrusted users

    Keyword arguments:
    vouch_matrix -- A 2 dimensional array of vouch values.
         The 1st dimension is the voucher, the 2nd is the vouchee.
         vouch_matrix[voucher][vouchee] > 0 if voucher vouched for vouchee.
    pretrusts -- pretrusts[u] > 0 if u is pretrusted.
    """
    normalized_vouch_matrix = np.zeros(vouch_matrix.shape)

    nb_users = len(pretrusts)  # Number of users
    nb_pretrusted = np.sum(
        np.array(pretrusts) > 0, axis=0
    )  # Number of pretrusted users

    for voucher in range(nb_users):
        n_vouches_by_voucher = np.sum(np.array(vouch_matrix[voucher]) > 0, axis=0)
        normalization_constant = (
            IMPLICIT_PRETRUST_VOUCH * nb_pretrusted + n_vouches_by_voucher
        )
        for vouchee in range(nb_users):
            if pretrusts[vouchee] > 0:
                normalized_vouch_matrix[voucher][vouchee] += (
                    IMPLICIT_PRETRUST_VOUCH / normalization_constant
                )
            if vouch_matrix[voucher][vouchee] > 0:
                normalized_vouch_matrix[voucher][vouchee] += 1 / normalization_constant
    return normalized_vouch_matrix


def compute_relative_posttrusts(normalized_vouch_matrix, relative_pretrusts: NDArray):
    """
    Return a vector of global trust values per user, given the vouchers in the
    network and the set of pre-trusted users. This part comes directly from
    EigenTrust.
    """
    relative_trusts = relative_pretrusts
    new_relative_trusts = relative_trusts
    delta = 10
    while delta >= APPROXIMATION_ERROR:
        new_relative_trusts = normalized_vouch_matrix.T.dot(relative_trusts)
        new_relative_trusts = (
            1 - PRETRUST_BIAS
        ) * new_relative_trusts + PRETRUST_BIAS * new_relative_trusts
        delta = np.linalg.norm(new_relative_trusts - relative_trusts)
        relative_trusts = new_relative_trusts
    return new_relative_trusts


def compute_voting_rights(relative_posttrusts, pretrusts):
    """
    Go from ratio of trust to actual voting weight that should be assigned to
    users given the trust the network puts in them.
    """
    min_relative_trusts_of_pretrusteds = np.amin(
        relative_posttrusts,
        where=pretrusts > 0,
        initial=MIN_PRETRUST_VOTING_RIGHT,
    )
    scale = MIN_PRETRUST_VOTING_RIGHT / min_relative_trusts_of_pretrusteds
    scaled_relative_trusts = np.array(relative_posttrusts) * scale
    clipped_relative_trusts = scaled_relative_trusts.clip(max=1)
    return clipped_relative_trusts


def trust_algo():
    """
    Improved version of the EigenTrust algorithm.

    Compute a global trust score for all users, based on the set of
    pre-trusted users and on vouching made between users.

    (* the ones with an email from a trusted domain).
    """
    # Import users and pretrust status
    users = list(
        user.User.objects.all().annotate(
            _is_trusted=Q(pk__in=user.User.trusted_users())
        )
    )
    pretrusts = np.array([int(u._is_trusted) for u in users])
    nb_users = len(users)

    # Import vouching matrix
    vouch_matrix = np.zeros([nb_users, nb_users], dtype=float)
    for vouch in Voucher.objects.iterator():
        voucher = users.index(vouch.by)
        vouchee = users.index(vouch.to)
        vouch_matrix[voucher][vouchee] = vouch.trust_value

    # Compute relative posttrusts
    normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, pretrusts)
    relative_pretrusts = pretrusts / np.sum(pretrusts)
    relative_posttrusts = compute_relative_posttrusts(
        normalized_vouch_matrix, relative_pretrusts
    )

    # Turn relative_posttrust into voting rights
    voting_rights = compute_voting_rights(relative_posttrusts, pretrusts)
    for user_no, user_model in enumerate(users):
        user_model.trust_score = float(voting_rights[user_no])
        user_model.save(update_fields=["trust_score"])
    return True
