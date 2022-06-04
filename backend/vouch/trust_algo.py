import numpy as np
from vouch.models import Voucher
from core.models import user
from django.db.models import Q
# hyper parameter of algorithm - select them wisely
A = 0.2  # define the minimum ratio of trust that is left to pre-trusted users
EPS = 1e-8
ALPHA = 0.1  # define how much voting weight goes to pre-trusted users for each user


def normalize_trust_values(C, trust_status):
    """
    Normalize the trust values per user, and make users vouch for pre-trusted set.
    If they vouch for other people, shift some of their ouching weight to others
    """
    trust_size = np.sum(np.array(trust_status) > 0, axis=0)  # size of the pre-trusted set
    for i in range(len(C[0])):
        vouching_size = np.sum(np.array(C[i]) > 0, axis=0)
        for j in range(len(C[0])):
            trust_indic = int(trust_status[j] > 0)
            vouch_indic = int(C[i][j] > 0)  
            C[i][j] = ALPHA / (ALPHA * trust_size + vouching_size) * trust_indic
            C[i][j] += 1 / (ALPHA * trust_size + vouching_size) * vouch_indic
    return C


def get_trust_vector(C, p):
    """
    Return a vector of global trust values per user, given the vouchers in the network
    and the set of pre-trusted users. This part comes directly from EigenTrust
    """
    t = p
    newt = t
    delta = 10
    while (delta >= EPS):
        newt = C.T.dot(t)
        newt = (1 - A) * newt + A * p
        delta = np.linalg.norm(newt - t)
        t = newt
    return newt


def rescale(trust_vector, trust_status):
    """
    Go from ratio of trust to actual voting weight that should be assigned
    to users given the trust the network puts in them
    """
    mint = np.amin([trust_vector[i] for i in range(len(trust_vector)) if trust_status[i] > 0])
    return np.array(trust_vector) / mint


def trust_algo():
    """
    Improved version of the EigenTrust algorithm
    Return a global trust score for each user, based on the set of
    pre-trusted users (the ones with an email from a trusted domain)
    and on vouchings made between users
    """
    # list of users, list of their trust status (regarding their email) in same order,
    # and number of users
    users = list(user.User.objects.all().annotate(_is_trusted=Q(pk__in=user.User.trusted_users())))
    trust_status = [int(u._is_trusted) for u in users]
    nb_users = len(users)

    # create a matrix C where entry c_ij is the trust value user i gave to user j

    C_ = np.zeros([nb_users, nb_users], dtype=float)
    for v in Voucher.objects.all():
        i = users.index(v.by)
        j = users.index(v.to)
        C_[i][j] = v.trust_value 
    # improved eigen trust algorithm
    p = trust_status
    p = p/np.sum(p)
    # make the matrix to make it stochastic and give trust of users who didn't
    # vouch much to pre-trusted set
    C = normalize_trust_values(C_, trust_status)
    # get the a vector of trust given to each users by the network
    trust_vector = get_trust_vector(C, p)
    # normalize and rescale it
    trust_vector = trust_vector/np.sum(trust_vector)
    voting_weight = rescale(trust_vector, trust_status)
    for k, u in enumerate(users):
        u.trust_score = float(voting_weight[k])
        u.save(update_fields=["trust_score"])
    return True
