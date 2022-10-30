import numpy as np

# On a given entity, an amount of extra voting right is given to users with lowest trust scores.
# This amount is call overtrust and we want it to be low compared to regular trusted voting rights
# such that untrusted users can only have a limited influence on the total voting right.
# overtrust is computed as OVER_TRUST_BIAS + OVER_TRUST_SCALE * total_trust
OVER_TRUST_BIAS, OVER_TRUST_SCALE = 2, 0.1


def compute_voting_rights(trust_scores: np.ndarray) -> np.ndarray:
    if not isinstance(trust_scores, np.ndarray):
        trust_scores = np.array(trust_scores)

    if len(trust_scores) == 0:
        return trust_scores

    if (trust_scores < 0).any() or (trust_scores > 1).any():
        raise ValueError("trust_scores must be between 0 and 1.")

    total_trust = trust_scores.sum()
    over_trust = OVER_TRUST_BIAS + OVER_TRUST_SCALE * total_trust

    sorted_trust_score = np.sort(trust_scores)

    # The number of users with lowest trust scores which will receive voting rights from the
    # overtrust amount
    n_least_trusted = 0
    # The partial sum of trust scores in the least trusted users
    partial_sum = 0.0

    # Can we safely set the min voting right to the trust score of the next least trusted user?
    while (
        n_least_trusted < len(trust_scores)
        and sorted_trust_score[n_least_trusted] * n_least_trusted - partial_sum
        < over_trust
    ):
        partial_sum += sorted_trust_score[n_least_trusted]
        n_least_trusted += 1

    # Now that we have determined the maximum number of users who can receive overtrust voting
    # rights, we can compute the minimum voting right
    min_voting_right = (partial_sum + over_trust) / n_least_trusted
    min_voting_right = min(1, min_voting_right)

    voting_rights = trust_scores.clip(min_voting_right, 1)
    return voting_rights
