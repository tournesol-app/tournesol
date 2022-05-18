import random

from attr import Factory
import numpy as np
import pytest
from vouch.models import Voucher

from trust_algo import normalize_trust_values, get_trust_vector, rescale, trust_algo
"""
Test module for vouch and trust algo
"""
from django.test import TestCase
from core.models.user import EmailDomain, User
from core.tests.factories.user import UserFactory


# ========== unit tests - trustalgo ===============
# ensure normalization works
@pytest.mark.django_db
class UnitTest(TestCase):
    def test_normalization(self):
        C = np.random.rand(10,10)
        user_trust = np.random.randint(2, size=10)
        C_normalized = normalize_trust_values(C,user_trust)
        for k in range(len(C_normalized[0])):
            assert(np.sum(C_normalized[k])==1)

    # ensure C is assymetrical (for convergence)
    def test_C_assymetrical(self):
        C = np.random.rand(10,10)
        user_trust = np.random.randint(2, size=10)
        C_normalized = normalize_trust_values(C,user_trust)
        rtol=1e-05
        atol=1e-08
        assert (False == np.allclose(C_normalized, C_normalized.T, rtol=rtol, atol=atol))



    # ensure trust score are in [0,1]
    def test_trust_values_range(self):
        C = np.random.rand(10,10)
        global_trust = trust_algo()
        for value in global_trust:
            assert (0<=value and value <=1)

    # # # ======= unit tests - vouching connections =======
    # #create 10 users from scratch
    # users_nb = 12
    # users = []
    # for i in range (users_nb):    
    #     users[i]= User.objects.create_user(username=f"test-user{i}", email=f"test{i}@example{i}.test")
    #     if i == (users_nb % 4) :
    #         email_domain = EmailDomain.objects.filter(domain="@example{i}.test").first()
    #         email_domain.status = EmailDomain.STATUS_ACCEPTED
    #         email_domain.save()
            
    # #create vouching connections between them
    # vouching = np.array(size=(users_nb,users_nb))
    # for i in range(users_nb):
    #     for j in range(users_nb):
    #         if i != j :
    #             if (random.randint(0,10) < 10):
    #                 vouching[i][j] = Voucher.objects.create(vouching = users[i],vouchedfor=users[j],trust_value = random.randint(0,10)/10.0)







