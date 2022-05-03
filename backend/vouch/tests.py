import math
import random
from django.test import TestCase
import pytest


import trustalgo
from core.tests.factories.user import UserFactory
import numpy as np
from core.models.user import EmailDomain, User
#Create your tests here.
# check trusted user are indeed trusted
@pytest.mark.django_db
class TestTrustAndUntrustUsers(TestCase):
    # prepare fake data : 

    def test_trusted_untrusted_user(self):
        # === prepare fake dats ===
        # users pre-trusted
        user_trusted = User.objects.create_user(username="trusted0", email="test@trusted.test")
        email_domain = EmailDomain.objects.filter(domain="@trusted.test").first()
        email_domain.status = EmailDomain.STATUS_ACCEPTED
        email_domain.save()

        # users not pre-trusted
        user_untrusted = User.objects.create_user(username="untrusted0", email="test@untrustedtrusted.test")

        self.assertTrue(user_trusted.is_trusted)
        self.assertFalse(user_untrusted.is_trusted)

#check that factory does work
@pytest.mark.django_db
class TestTrustAndUntrustUsers(TestCase):
    # user_trusted = User.objects.create_user(username="trusted0", email="test@trusted.test")
    # email_domain = EmailDomain.objects.filter(domain="@trusted.test").first()
    # email_domain.status = EmailDomain.STATUS_ACCEPTED
    # email_domain.save()
    users = []
    def test_trusted_user(self):
        usert = UserFactory(email = 'person{}@trusted.test')
        email_domain = EmailDomain.objects.filter(domain="@trusted.test").first()
        email_domain.status = EmailDomain.STATUS_ACCEPTED
        email_domain.save()
        self.assertTrue(usert.is_trusted)
    
    def test_untrusted_user(self):
        usernt = UserFactory(email = 'person{}@ntrusted.test')
        self.assertFalse(usernt.is_trusted)


class TestGenerationofUsers(TestCase):
    def test_user_set(self):
        usert = UserFactory(email = 'person{}@trusted.test')
        email_domain = EmailDomain.objects.filter(domain="@trusted.test").first()
        email_domain.status = EmailDomain.STATUS_ACCEPTED
        email_domain.save()
        #create multiple users (trusted and untrusted)
        user_trust = np.random.choice([0, 1], size=6, p=[.9, .1]) # 1/10 per user of chance to be trusted
        user_trusted = np.array([UserFactory(email = 'person0@trusted.test'),UserFactory(email = 'person1@trusted.test'),UserFactory(email = 'person2@trusted.test'),UserFactory(email = 'person3@trusted.test'),UserFactory(email = 'person4@trusted.test')])
        user_ntrusted = np.array([UserFactory(email = 'person0@ntrusted.test'),UserFactory(email = 'person1@ntrusted.test'),UserFactory(email = 'person2@ntrusted.test'),UserFactory(email = 'person3@ntrusted.test'),UserFactory(email = 'person4@ntrusted.test')])
        user_set = []
        for i in range(1):
            if user_trust[i] == 1:
                user_set.append(user_trusted[i])
            else :
                user_set.append(user_ntrusted[i])
        
        i = 0
        for u in user_set :
            assert(u.is_trusted == user_trust[i])
            i += 1

# ========== unit tests - trustalgo ===============
class UnitTestTrustAlgo(TestCase):
       
    # ensure normalization works
    def test_normalization(test):
        C = np.random.rand(15,15)
        C_normalized = trustalgo.normalize_trust_values(C)

        for k in range(len(C_normalized[0])):
         assert(math.isclose(sum(C_normalized[k]),1,rel_tol=1e-10))

    # ensure C is assymetrical (for convergence)
    def test_C_assymetrical(test):
        C = np.random.rand(15,15)
        C_normalized = trustalgo.normalize_trust_values(C)
        assert (False == np.allclose(C_normalized, C_normalized.T,rtol=1e-10, atol=1e-08))


    # ensure threshold is respected
    def test_threshold(test):
        user_trust = np.random.choice([0, 1], size=10, p=[.9, .1]) # 1/10 per user of chance to be trusted
        user_trust[0] = 1 #to ensure at least one user is trusted
        threshold = random.randint(0,10)/10.0
        random_vec = np.random.rand(len(user_trust))
        result = trustalgo.rescale_trust_with_threshold(random_vec,user_trust,threshold)
        assert(threshold <= np.sum([result[k] if user_trust[k]==1 else 0 for k in range(len(user_trust))]))

        # # ========== unit tests - trustalgo ===============


        # # ensure trust score are in [0,1]
        # def test_trust_values_range():
        #     global_trust = trust_algo(C,user_trust)
        #     for value in global_trust:
        #         assert (0<=value and value <=1)

