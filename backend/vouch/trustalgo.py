import numpy as np
from vouch.models import vouch

from core.models import user


a = 0.5
threshold = 0.7
delta = 10
eps = 0.000001 

def normalize_trust_values(C):
    """
    Normalize the trust values per user, and set diagonal values at 1
    This makes C an ergotic stochastic matrix
    """
    assert(len(C[0])==len(C))
    for i in range(len(C)):
        C[i][i] = 1
        tmp = np.sum(C[i])
        for j in range(len(C)):
            C[i][j] = C[i][j] / float(tmp)
    return C
def get_trust_vector(C,p):
    """
    Return a trust vector given the trust of users and the set of pre-trusted users
    """
    t = p
    newt = t
    while (delta>=eps):
        newt = C.T.dot(t)
        newt = (1-a)*newt + a*p
        delta = np.linalg.norm(newt-t)
        t = newt
    return newt

def rescale_trust_with_threshold(trust_vector, user_trusted, threshold):
    """
    Ensure trust given to the set of pre-trusted users is higher than a treshold
    """
    sum_trusted = np.sum([trust_vector[i] if user_trusted[i] == 1 else 0 for i in range(user_trusted.size) ])

    if sum_trusted < threshold :
        global_trust = [(trust_vector[i]* threshold / sum_trusted) if user_trusted[i] == 1 else (trust_vector[i]* (1-threshold) / (1-sum_trusted))  for i in range(user_trusted.size) ]
    else :
        global_trust = trust_vector
    return global_trust

def trust_algo() :
    """
    Improved version of the EigenTrust algorithm
    Return a global trust score for each user, based on the set of pre-trusted users (the ones with an email from a trusted domain)
    and on vouchings made between users
    """
    user_trusted = [user for user in user.User.objects.all().order_by('id') if user.is_trusted()]
    dim = len(user_trusted)
    C = np.empty([dim,dim], dtype = float)
    vouching_idx,vouchedfor_idx = 0
    for vouchinguser in user.objects.order_by('id') :
        for vouchedforuser in user.objects.order_by('id'):
            C[vouching_idx][vouchedfor_idx] = vouch.objects.filter(vouchinguser = vouchinguser).filter(vouchedforuser=vouchedforuser)
            vouchedfor_idx +=1
        vouching_idx +=1
    p = user_trusted
    p = p/np.sum(p)
    C = normalize_trust_values(C, user_trusted)
    trust_vector = get_trust_vector(C,p)
    trust_vector = trust_vector/np.sum(trust_vector)
    global_trust = rescale_trust_with_threshold(trust_vector,user_trusted,threshold)
    for u in user.objects.sortby('id') :
        u.trust_score = global_trust[k]
        k += 1
        u.save()
    return True


