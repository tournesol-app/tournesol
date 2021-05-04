import logging
import os
import string
from contextlib import contextmanager
from uuid import uuid1

import gin
import numpy as np
import pytest
import shortuuid
import tensorflow as tf
from backend.cycle_preference_inconsistency import inconsistencies_3_for_queryset, \
    get_cycles_weights_3, get_edges_list_db
from backend.ml_model.client_server.django_ml_embedding import DatabasePreferenceLearnerEmbedding
from backend.ml_model.client_server.django_ml_featureless import \
    DatabasePreferenceLearnerFeatureless
from backend.ml_model.preference_aggregation_featureless_tf_dense import VariableIndexLayer
from backend.models import ExpertRating, VideoRating, UserInformation, EmailDomain, \
    VerifiableEmail, VideoRateLater, VideoRatingPrivacy
from backend.models import Video, UserPreferences, DjangoUser, VideoSelectorSkips
from backend.rating_fields import MAX_VALUE
from backend.rating_fields import VIDEO_FIELDS
from backend.sample_video_active_learning import get_active_features, \
    sample_video_with_other_helper
from backend.sample_video_active_learning import sample_first_video_helper
from django.core import serializers
from django.db.models import Q
from django.db.utils import IntegrityError
from django.test import TestCase
from django_react.settings import load_gin_config, BASE_DIR
from tqdm import tqdm
from backend.ml_model.preference_aggregation_featureless_online import compute_online_update
from backend.ml_model.preference_aggregation_featureless_online_db import OnlineRatingUpdateContext
from backend.sample_video_active_learning import ActiveLearningException
from backend.add_videos import VideoManager
from django.db.models import CharField, TextField
from django.db.models.functions import Length


def create_accepted_domain(domain="@tournesol.app"):
    """Create an accepted e-mail domain."""
    EmailDomain.objects.create(
        domain=domain,
        status=EmailDomain.STATUS_ACCEPTED)

    return domain


def create_rejected_domain(domain="@rejected.com"):
    """Create an accepted e-mail domain."""
    EmailDomain.objects.create(
        domain=domain,
        status=EmailDomain.STATUS_REJECTED)

    return domain


class IndexerLayerTestCase(TestCase):
    def test_index_layer_1d(self):
        arr = np.random.randn(50)
        indices = np.random.choice(
            range(len(arr)), 1000, replace=True).reshape(-1, 1)
        idx_layer = VariableIndexLayer(
            shape=arr.shape,
            name="test_layer",
            initializer=tf.keras.initializers.Zeros())
        idx_layer.v.assign(arr)
        out = idx_layer(indices)
        assert np.allclose(out.numpy(), arr[indices[:, 0]])

    def test_train_changes_weights(self):
        arr = np.random.randn(50, 1)
        indices = np.array(np.random.choice(
            range(len(arr)), 10, replace=True), dtype=np.int64).reshape(-1, 1)
        idx_layer = VariableIndexLayer(
            shape=arr.shape,
            name="test_layer",
            initializer=tf.keras.initializers.Zeros())
        idx_layer.v.assign(arr)

        inp = tf.keras.Input(shape=(1,), dtype=tf.int64)

        model = tf.keras.Model(inputs=inp, outputs=idx_layer(inp))
        model.summary()

        print(arr[indices].shape, model.predict(indices).shape)
        assert np.allclose(model.predict(indices), arr[indices[:, 0]])

        model.compile('adam', 'mse')
        model.fit(np.array(range(50)), np.random.randn(50, 1), epochs=1)

        assert not np.allclose(model.predict(indices), arr[indices[:, 0]])


class LoadGinConfigTestCase(TestCase):
    """Test that can load all .gin files in the project."""

    def test_gin_files(self):
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                path = os.path.join(root, file)
                if file.endswith('.gin') and os.path.isfile(path):
                    load_gin_config(path)
                    gin.clear_config()


class DatabaseLearnerBasicTestCase(TestCase):
    """Test that can run the preference learning at all."""

    def setUp(self):
        load_gin_config("backend/ml_model/config/common.gin")
        load_gin_config("backend/ml_model/config/featureless_config.gin")
        self.v1 = Video.objects.create(video_id="a")
        self.v2 = Video.objects.create(video_id="b")
        self.videos = [self.v1, self.v2]

        for v in self.videos:
            v.set_embedding(np.random.randn(Video.EMBEDDING_LEN))
            v.save()

        self.djangouser = DjangoUser.objects.create_user(
            username="rater", password="1234")
        self.prefs = UserPreferences.objects.create(user=self.djangouser)

        # making the user verified
        self.ui = UserInformation.objects.create(user=self.djangouser)
        accepted_domain = create_accepted_domain()

        self.vemail = VerifiableEmail.objects.create(
            user=self.ui, email=f"{uuid1()}{accepted_domain}", is_verified=True)

        data = {k: np.random.rand() * 100 for k in VIDEO_FIELDS}
        self.rating = ExpertRating.objects.create(
            video_1=self.v1, video_2=self.v2, user=self.prefs, **data)

    def _check_output(self):
        for video in Video.objects.all():
            for user in UserPreferences.objects.all():
                nratings = ExpertRating.objects.filter(user=user)
                if not nratings:
                    continue
                print(video, user)
                r = VideoRating.objects.get(video=video, user=user)
                for f in VIDEO_FIELDS:
                    assert getattr(r, f) != 0
            for f in VIDEO_FIELDS:
                assert getattr(video, f) != 0

    def test_dummyrun_featureless_learner(self):
        gin.bind_parameter(
            "FeaturelessMedianPreferenceAverageRegularizationAggregator.epochs", 10)
        learner_obj = DatabasePreferenceLearnerFeatureless(load=False)
        learner_obj.fit()
        learner_obj.update_features()
        gin.clear_config()

        # now should have video ratings for the aggregated model
        self._check_output()

    def test_dummyrun_embedding_learner(self):
        learner_obj = DatabasePreferenceLearnerEmbedding(load=False)
        learner_obj.fit()
        learner_obj.update_features()

        # now should have video ratings for the aggregated model
        self._check_output()


class DatabaseLearnerFeaturelessManyInputs(TestCase):
    """Test that non-certified experts are not counted."""

    def setUp(self):
        load_gin_config("backend/ml_model/config/featureless_config.gin")
        gin.bind_parameter(
            "FeaturelessMedianPreferenceAverageRegularizationAggregator.epochs", 1000)

        # creating videos
        self.videos = [
            Video.objects.create(
                video_id=f"video{i}") for i in tqdm(
                range(200))]

        # creating users
        self.djangousers = [
            DjangoUser.objects.create_user(
                username=f"rater{i}",
                password=f"1234{i}") for i in tqdm(
                range(10))]
        self.userprefs = [
            UserPreferences.objects.create(
                user=u) for u in self.djangousers]

        # making the user verified
        self.userinfos = [
            UserInformation.objects.create(
                user=u) for u in self.djangousers]
        accepted_domain = create_accepted_domain()
        self.vemails = [
            VerifiableEmail.objects.create(
                user=ui,
                email=f"{uuid1()}{accepted_domain}",
                is_verified=True) for ui in self.userinfos]

        # creating expert ratings
        ratings = []
        for _ in tqdm(range(1000)):
            v1 = np.random.choice(self.videos)
            v2 = np.random.choice(self.videos)
            u = np.random.choice(self.userprefs)
            data = {k: np.random.rand() * 100 for k in VIDEO_FIELDS}
            ratings.append(
                ExpertRating(
                    video_1=v1,
                    video_2=v2,
                    user=u,
                    **data))

        ExpertRating.objects.bulk_create(ratings, ignore_conflicts=True)

    def test_featureless_learner(self):
        learner_obj = DatabasePreferenceLearnerFeatureless(load=False)
        learner_obj.fit()
        learner_obj.update_features()


class DatabaseLearnerFeaturelessCertification(TestCase):
    """Test that can run the preference learning at all."""

    def setUp(self):
        load_gin_config("backend/ml_model/config/featureless_config.gin")
        gin.bind_parameter(
            "FeaturelessMedianPreferenceAverageRegularizationAggregator.epochs", 1000)

        # creating videos
        self.videos = [
            Video.objects.create(
                video_id=f"video{i}") for i in tqdm(
                range(2))]

        # creating users
        self.djangousers = [
            DjangoUser.objects.create_user(
                username=f"rater{i}",
                password=f"1234{i}") for i in tqdm(
                range(2))]
        self.userprefs = [
            UserPreferences.objects.create(
                user=u) for u in self.djangousers]

        # making the user verified
        self.userinfos = [
            UserInformation.objects.create(
                user=u) for u in self.djangousers]
        self.verify = [False, True]
        accepted_domain = create_accepted_domain()
        self.vemails = [
            VerifiableEmail.objects.create(
                user=ui,
                email=f"{uuid1()}{accepted_domain}",
                is_verified=verify) for ui, verify in zip(
                self.userinfos,
                self.verify)]

        data_rest = {k: 50 for k in VIDEO_FIELDS[1:]}
        self.f = VIDEO_FIELDS[0]

        # rater0 likes video0, rater1 likes video1
        ExpertRating.objects.create(user=self.userprefs[0], video_1=self.videos[0],
                                    video_2=self.videos[1],
                                    **data_rest, **{self.f: 0})
        ExpertRating.objects.create(user=self.userprefs[1], video_1=self.videos[0],
                                    video_2=self.videos[1],
                                    **data_rest, **{self.f: 100})

    def _check_output(self):
        for video in Video.objects.all():
            for user in UserPreferences.objects.all():
                nratings = ExpertRating.objects.filter(user=user)
                if not nratings:
                    continue
                print(video, user)
                r = VideoRating.objects.get(video=video, user=user)
                print(r, self.f, getattr(r, self.f))
                for f in VIDEO_FIELDS:
                    assert hasattr(r, f)

            print('global', getattr(video, self.f))
            for f in VIDEO_FIELDS:
                assert hasattr(video, f)

        assert Video.objects.all().count() == 2
        assert VideoRating.objects.all().count() == 4

        v0u0 = getattr(
            VideoRating.objects.get(
                video=self.videos[0],
                user=self.userprefs[0]),
            self.f)
        v0u1 = getattr(
            VideoRating.objects.get(
                video=self.videos[0],
                user=self.userprefs[1]),
            self.f)
        v1u0 = getattr(
            VideoRating.objects.get(
                video=self.videos[1],
                user=self.userprefs[0]),
            self.f)
        v1u1 = getattr(
            VideoRating.objects.get(
                video=self.videos[1],
                user=self.userprefs[1]),
            self.f)

        assert v0u0 > v0u1
        assert v1u0 < v1u1
        assert v0u0 > v0u1
        assert v1u0 < v1u1

        self.videos[0].refresh_from_db()
        self.videos[1].refresh_from_db()
        v0g = getattr(self.videos[0], self.f)
        v1g = getattr(self.videos[1], self.f)

        assert v0g < v1g

    def test_featureless_certification(self):
        learner_obj = DatabasePreferenceLearnerFeatureless(load=False)
        print("CERTIFIED USERS", learner_obj.aggregator.certification_status)
        learner_obj.fit()
        learner_obj.update_features()
        self._check_output()


class ExpertRatingTestCase(TestCase):
    """Test that can't create duplicate ratings/ratings with v1-v2 swapped."""

    def setUp(self):
        self.v1 = Video.objects.create(video_id="a")
        self.v2 = Video.objects.create(video_id="b")
        self.data = {k: np.random.rand() * 100 for k in VIDEO_FIELDS}

        self.djangouser = DjangoUser.objects.create_user(
            username="doppel", password="ganger")
        self.prefs = UserPreferences.objects.create(user=self.djangouser)

    def test_disallow_duplicates(self):
        ExpertRating.objects.create(
            video_1=self.v1,
            video_2=self.v2,
            user=self.prefs,
            **self.data)

        # see
        # https://stackoverflow.com/questions/38973348/fail-on-testing-integrityerror-unique-constraint
        with self.assertRaises(Exception) as raised:
            ExpertRating.objects.create(
                video_1=self.v1,
                video_2=self.v2,
                user=self.prefs,
                **self.data)
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_disallow_pair_duplicates(self):
        ExpertRating.objects.create(
            video_1=self.v1,
            video_2=self.v2,
            user=self.prefs,
            **self.data)

        # see
        # https://stackoverflow.com/questions/38973348/fail-on-testing-integrityerror-unique-constraint
        with self.assertRaises(Exception) as raised:
            ExpertRating.objects.create(
                video_1=self.v2,
                video_2=self.v1,
                user=self.prefs,
                **self.data)
        self.assertEqual(IntegrityError, type(raised.exception))


class CertifiedDomainTestCase(TestCase):
    def test_certified_email(self):
        # creating user
        u = DjangoUser.objects.create_user(username="aba" + str(uuid1()))
        ui = UserInformation.objects.create(user=u)

        accepted_domain = create_accepted_domain()
        rejected_domain = create_rejected_domain()

        # not certified
        # should only be certified if exists a verified email of certified
        # domain

        ui.refresh_from_db()
        # checking certification correctness
        assert ui.is_certified is False

        VerifiableEmail.objects.create(
            email=f"{str(uuid1())}{rejected_domain}", user=ui)

        ui.refresh_from_db()
        # checking certification correctness
        assert ui.is_certified is False

        VerifiableEmail.objects.create(
            email=f"{str(uuid1())}{rejected_domain}",
            user=ui,
            is_verified=True)

        ui.refresh_from_db()
        # checking certification correctness
        assert ui.is_certified is False

        VerifiableEmail.objects.create(
            email=f"{str(uuid1())}{accepted_domain}",
            user=ui,
            is_verified=False)

        ui.refresh_from_db()

        # checking certification correctness
        assert ui.is_certified is False

        VerifiableEmail.objects.create(
            email=f"{str(uuid1())}{accepted_domain}",
            user=ui,
            is_verified=True)

        ui.refresh_from_db()

        # checking certification correctness
        assert ui.is_certified is True

        VerifiableEmail.objects.filter(
            user=ui, is_verified=True, domain=accepted_domain).delete()

        ui.refresh_from_db()

        # checking certification correctness
        assert ui.is_certified is False


@contextmanager
def set_active_features(user, features):
    """Set active features and then restore preferences."""

    user_orig = serializers.serialize("xml", [user])
    for f in VIDEO_FIELDS:
        setattr(user, f + "_enabled", f in features)
    print(f"Setting active features for {user.username} to: [{', '.join(features)}]")
    user.save()

    yield

    print(f"Restoring active features for {user.username}")
    list(serializers.deserialize("xml", user_orig))[0].save()
    user.refresh_from_db()


@contextmanager
def no_active_features(user):
    """Set all features as inactive."""
    with set_active_features(user, []):
        yield


@contextmanager
def all_active_features(user):
    """Set all features as active."""
    with set_active_features(user, VIDEO_FIELDS):
        yield


@contextmanager
def random_active_features(user):
    """Set random features as active and inactive."""
    subset = [f for f in VIDEO_FIELDS if np.random.choice(2) > 0]
    if not subset:
        subset = [np.random.choice(VIDEO_FIELDS)]
    with set_active_features(user, subset):
        yield subset


class TestVideoSamplingV3(TestCase):
    n_tests_probabilistic = 3

    def setUp(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    def create_user(self):
        dj_u = DjangoUser.objects.create_user(username='test')
        u = UserPreferences.objects.create(user=dj_u)
        return u

    def test_contextmanager(self):
        """Test that context managers work."""
        u = self.create_user()

        orig_active = get_active_features(u)

        with no_active_features(u):
            assert not get_active_features(u)
        assert get_active_features(u) == orig_active

        with all_active_features(u):
            assert set(get_active_features(u)) == set(VIDEO_FIELDS)
        assert get_active_features(u) == orig_active

        for i in range(10):
            with random_active_features(u) as subset:
                assert set(get_active_features(u)) == set(subset)
        assert get_active_features(u) == orig_active

    def test_first_no_videos(self):
        """Test that no videos result in a Value Error since the graph is complete."""
        u = self.create_user()

        cms_all = [all_active_features] + [
            random_active_features] * self.n_tests_probabilistic

        # testing with NO VIDEOS
        base_qs = Video.objects.none()

        with no_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_first_video_helper(u, do_log=True, base_qs=base_qs)
            assert excinfo.value.reason.name == 'NO_FEATURES', \
                excinfo.value.reason.name

        for cm in cms_all:
            with cm(u):
                with pytest.raises(ActiveLearningException) as excinfo:
                    sample_first_video_helper(u, do_log=True, base_qs=base_qs)
                assert excinfo.value.reason.name == 'NO_RATE_LATER_NO_RATED', \
                    excinfo.value.reason.name

    def test_first_rate_later(self):
        """Testing with I RATE LATER (sampling only from rate_later)."""

        u = self.create_user()

        # creating videos
        n_videos = 50
        video_ids = [str(uuid1()) for _ in range(n_videos)]
        videos_lst = Video.objects.bulk_create([Video(video_id=vid) for vid in video_ids])
        videos_qs = Video.objects.filter(video_id__in=video_ids)

        assert len(videos_qs) == len(videos_lst)

        # randomly adding some to RATE LATER
        vrl = [VideoRateLater(video=v, user=u) for v in videos_qs if np.random.rand() > 0.5]
        vrl_ids = [x.video.video_id for x in vrl]
        VideoRateLater.objects.bulk_create(vrl)

        for _ in range(self.n_tests_probabilistic):
            assert sample_first_video_helper(u, do_log=False,
                                             base_qs=videos_qs).video_id in vrl_ids

    def test_first_no_rating_active_f(self):
        """II. No active features -> exception, active features, othr -> sampling from empty."""
        u = self.create_user()

        n_videos = 50
        video_ids = [f"{i}-{str(uuid1())}" for i in range(n_videos)]
        Video.objects.bulk_create([Video(video_id=vid) for vid in video_ids])
        videos_qs = Video.objects.filter(video_id__in=video_ids)
        videos_lst = [videos_qs.get(video_id=vid) for vid in video_ids]

        # creating a rating with null values
        r = ExpertRating.objects.create(video_1=videos_lst[0], video_2=videos_lst[1], user=u)

        # rating has all empty values -> no rating -> sampling these two videos
        for _ in range(self.n_tests_probabilistic):
            with all_active_features(u):
                v = sample_first_video_helper(u, do_log=False, base_qs=videos_qs)
                assert v.video_id in video_ids[:2]

        # no active features -> exception
        with no_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_first_video_helper(u, do_log=False, base_qs=videos_qs)
            assert excinfo.value.reason.name == 'NO_FEATURES', \
                excinfo.value.reason.name

        # adding value for reliability for the rating
        r.reliability = 0.5
        r.save()

        # print('line 584')

        # active reliability -> complete graph
        with set_active_features(u, ['reliability']):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_first_video_helper(u, do_log=True, base_qs=videos_qs)
            assert excinfo.value.reason.name == 'NO_RATE_LATER_ALL_RATED', \
                excinfo.value.reason.name

        # other feature -> sampling from empty
        with set_active_features(u, ['backfire_risk']):
            v = sample_first_video_helper(u, do_log=False, base_qs=videos_qs)
            assert v.video_id in video_ids[:2]

        with no_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_first_video_helper(u, do_log=False, base_qs=videos_qs)
            assert excinfo.value.reason.name == 'NO_FEATURES', \
                excinfo.value.reason.name

        # rating two other videos
        # 1-2, 1-3, but not 2-3. should only sample from 2-3
        r2 = ExpertRating.objects.create(video_1=videos_lst[0], video_2=videos_lst[2], user=u)

        # graph: 0-1, reliability=set
        #        0-2, reliability=none
        # 1, 2 are in zero-rating
        # since we didn't have set the value, we sample from v_zero_rating
        with set_active_features(u, ['reliability']):
            v = sample_first_video_helper(u, do_log=True, base_qs=videos_qs)
            print("SAMPLED:", v)
            assert v.video_id in [video_ids[1], video_ids[2]], v

        r2.reliability = 1.0
        r2.save()

        # setting uncertainty for videos[1]
        VideoRating.objects.create(user=u, video=videos_lst[1], reliability_uncertainty=10)

        # since we didn't have set the value, we sample from v_zero_rating
        for _ in range(self.n_tests_probabilistic):
            with set_active_features(u, ['reliability']):
                v = sample_first_video_helper(u, do_log=True, base_qs=videos_qs)
                assert v.video_id == video_ids[1]

    def test_sample_with_other(self):
        u = self.create_user()
        n_videos = 4
        video_ids = [f"{i}-{str(uuid1())}" for i in range(n_videos)]
        Video.objects.bulk_create([Video(video_id=vid) for vid in video_ids])
        videos_qs = Video.objects.filter(video_id__in=video_ids)
        videos_lst = [videos_qs.get(video_id=vid) for vid in video_ids]

        v_first = videos_lst[0]

        base_qs = videos_qs
        n_tests_probabilistic = self.n_tests_probabilistic

        # test no rate later, no ratings -> all exceptions

        for _ in range(n_tests_probabilistic):
            with random_active_features(u):
                with pytest.raises(ActiveLearningException) as excinfo:
                    sample_video_with_other_helper(v_first, u, base_qs=base_qs)
                assert excinfo.value.reason.name == 'FIRST_RATED_AGAINST_ALL_RATED',\
                    excinfo.value.reason.name

        with all_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_video_with_other_helper(v_first, u, base_qs=base_qs)
            assert excinfo.value.reason.name == 'FIRST_RATED_AGAINST_ALL_RATED', \
                excinfo.value.reason.name

        with no_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_video_with_other_helper(v_first, u, base_qs=base_qs)
            assert excinfo.value.reason.name == 'NO_FEATURES', \
                excinfo.value.reason.name

        # same for NO VIDEOS

        for _ in range(n_tests_probabilistic):
            with random_active_features(u):
                with pytest.raises(ActiveLearningException) as excinfo:
                    sample_video_with_other_helper(v_first, u, base_qs=base_qs.none())
                assert excinfo.value.reason.name == 'FIRST_RATED_AGAINST_ALL_RATED', \
                    excinfo.value.reason.name

        with all_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_video_with_other_helper(v_first, u, base_qs=base_qs.none())
            assert excinfo.value.reason.name == 'FIRST_RATED_AGAINST_ALL_RATED', \
                excinfo.value.reason.name

        with no_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_video_with_other_helper(v_first, u, base_qs=base_qs.none())
            assert excinfo.value.reason.name == 'NO_FEATURES', \
                excinfo.value.reason.name

        # adding some to RATE LATER
        VideoRateLater.objects.create(user=u, video=videos_lst[0])
        VideoRateLater.objects.create(user=u, video=videos_lst[1])

        # only sampling the [1] video, as the [0] is equal to v_first

        for _ in range(n_tests_probabilistic):
            with random_active_features(u):
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                       video_ids[1]

            with all_active_features(u):
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                       video_ids[1]

            with no_active_features(u):
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                       video_ids[1]

        VideoRateLater.objects.filter(user=u).delete()

        # looking for videos with zero rating on active features
        r = ExpertRating.objects.create(user=u, video_1=videos_lst[0],
                                        video_2=videos_lst[1])

        # have v_rated=0, 1, but 1 doesn't have any valid ratings

        for _ in range(n_tests_probabilistic):
            with random_active_features(u):
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                       video_ids[1]

            with all_active_features(u):
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                       video_ids[1]

        with no_active_features(u):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_video_with_other_helper(v_first, u, base_qs=base_qs.none())
            assert excinfo.value.reason.name == 'NO_FEATURES', \
                excinfo.value.reason.name

        # setting value for reliability
        r.reliability = 1.0
        r.save()

        # should have an error, because there are no videos in v_rated we
        # could compare v_first to (v[1] is already taken)
        with set_active_features(u, ['reliability']):
            with pytest.raises(ActiveLearningException) as excinfo:
                sample_video_with_other_helper(v_first, u, base_qs=base_qs)
            assert excinfo.value.reason.name == 'FIRST_RATED_AGAINST_ALL_RATED', \
                excinfo.value.reason.name

        # for another feature, we still need to rate them
        with set_active_features(u, ['backfire_risk']):
            assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                   video_ids[1]

        # rating 0-2
        # this way, v_rated=0,1,2, and 2 has no ratings on backfire_risk (but 0, 1 have)
        r2 = ExpertRating.objects.create(user=u, video_1=videos_lst[0],
                                         video_2=videos_lst[2])

        with set_active_features(u, ['reliability']):
            assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                   video_ids[2]

        # adding some value. this way, all are rated 0-1, 0-2, so there should be an exception
        r2.reliability = 0.5
        r2.save()

        with set_active_features(u, ['reliability']):
            with pytest.raises(ActiveLearningException) as excinfo:
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                       video_ids[2]
            assert excinfo.value.reason.name == 'FIRST_RATED_AGAINST_ALL_RATED', \
                excinfo.value.reason.name

        # deleting r2 and adding r2
        r2.delete()

        # rating 1-2
        # this way, v_rated=0,1,2, (0-1, 1-2), but 2 is unrated, so it will be returned from case 2
        r3 = ExpertRating.objects.create(user=u, video_1=videos_lst[1],
                                         video_2=videos_lst[2])

        with set_active_features(u, ['reliability']):
            assert sample_video_with_other_helper(v_first, u, base_qs=base_qs).video_id == \
                   video_ids[2]

        # now, setting some value. this way, all videos have _some_ values on all quality features
        r3.reliability = 0.5
        r3.save()

        # gin.bind_parameter('sample_video_with_other_helper.c_noise', 0.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_exploration', 0.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_skipped', 0.0)

        # testing theta part...

        r4 = ExpertRating.objects.create(video_1=videos_lst[0],
                                         video_2=videos_lst[3],
                                         user=u)

        r4.reliability = 0.5
        r4.save()

        VideoRating.objects.filter(user=u).delete()

        VideoRating.objects.create(video=videos_lst[0], reliability=1, user=u)
        VideoRating.objects.create(video=videos_lst[1], reliability=2, user=u)
        VideoRating.objects.create(video=videos_lst[2], reliability=3, user=u)
        VideoRating.objects.create(video=videos_lst[3], reliability=4, user=u)

        # checking THETA part computation
        for _ in range(n_tests_probabilistic):
            with set_active_features(u, ['reliability', 'engaging']):
                qs = sample_video_with_other_helper(v_first, u, base_qs=base_qs, c_noise=0,
                                                    debug_return_qs=True)
                assert len(qs) == 3
                entries = [qs.get(video_id=video_ids[id_])._theta_part for id_ in [1, 2, 3]]
                assert np.allclose(entries, [0.5, 1, 1.5])
                vid_return = sample_video_with_other_helper(v_first, u,
                                                            base_qs=base_qs,
                                                            c_noise=0).video_id
                assert vid_return == video_ids[2], (vid_return, video_ids)
                # correct 1, but returning not rated 2

        # gin.bind_parameter('sample_video_with_other_helper.c_noise', 0.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_exploration', 1.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_skipped', 0.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_theta', 0.0)

        test_v_ids = [video_ids[z] for z in [1, 2, 3]]
        for _ in range(n_tests_probabilistic):
            with set_active_features(u, ['reliability', 'engaging']):
                qs = sample_video_with_other_helper(v_first, u, base_qs=base_qs, c_noise=0,
                                                    debug_return_qs=True)

                assert len(qs) == 3

                got_vals = [qs.get(video_id=vid)._exploration_part for vid in test_v_ids]

                correct_vals = [2. / ExpertRating.objects.filter(Q(user=u) &
                                                                 (Q(video_1__video_id=v) |
                                                                  Q(video_2__video_id=v))).count()
                                for v in test_v_ids]

                assert np.allclose(got_vals, correct_vals)
                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs,
                                                      c_noise=0).video_id == video_ids[2]
                # correct 1, but returning not rated 2

        # gin.bind_parameter('sample_video_with_other_helper.c_noise', 0.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_exploration', 0.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_skipped', 1.0)
        gin.bind_parameter('annotate_active_score_with_other_nonoise.c_theta', 0.0)

        # testing SKIPS part
        VideoSelectorSkips.objects.create(video=videos_lst[1], user=u)
        VideoSelectorSkips.objects.create(video=videos_lst[1], user=u)
        VideoSelectorSkips.objects.create(video=videos_lst[2], user=u)

        test_v_ids = [video_ids[z] for z in [1, 2, 3]]
        for _ in range(n_tests_probabilistic):
            with set_active_features(u, ['reliability', 'engaging']):
                qs = sample_video_with_other_helper(v_first, u, base_qs=base_qs, c_noise=0,
                                                    debug_return_qs=True)
                assert len(qs) == 3

                correct_vals = [2, 1, 0]
                got_vals = [qs.get(video_id=vid)._skipped_part for vid in test_v_ids]
                assert np.allclose(correct_vals, got_vals)

                assert sample_video_with_other_helper(v_first, u, base_qs=base_qs,
                                                      c_noise=0).video_id == video_ids[2]
                # correct 3, but returning not rated 2


def random_alphanumeric(length=10, alphabet=None):
    """UUID1 without -."""
    if alphabet is None:
        alphabet = string.ascii_lowercase + string.digits
    res = shortuuid.ShortUUID(alphabet=alphabet).random(length=length)
    return str(res).replace('-', '')


class TestInconsistencies3(TestCase):
    n_videos = 10000
    n_ratings = 10000

    @staticmethod
    def add_inconsistency(user, feature):
        """Create an inconsistency of 3 videos were v0 better v1 better v2 better v0."""

        video_ids = ["%09d-%s-inc" % (i, random_alphanumeric()) for i in range(3)]
        objs = [Video(video_id=vid) for vid in video_ids]
        _ = Video.objects.bulk_create(objs)
        videos = [Video.objects.get(video_id=vid) for vid in video_ids]

        # create rating where 1 is better than 2
        # reverse -- create in other order (but same meaning!)
        def create_rating(idx1, idx2, reverse=False):
            if reverse:
                ExpertRating.objects.create(user=user, **{feature: MAX_VALUE},
                                            video_1=videos[idx2],
                                            video_2=videos[idx1])
            else:
                ExpertRating.objects.create(user=user, **{feature: 0},
                                            video_1=videos[idx1],
                                            video_2=videos[idx2])

        create_rating(0, 1, reverse=np.random.rand() < 0.5)
        create_rating(1, 2, reverse=np.random.rand() < 0.5)
        create_rating(2, 0, reverse=np.random.rand() < 0.5)

        return tuple([x.id for x in videos])

    def create_user(self):
        un = 'inconsistent_person'
        DjangoUser.objects.filter(username=un).delete()
        dj_u = DjangoUser.objects.create_user(username=un)
        user, _ = UserPreferences.objects.get_or_create(user=dj_u)
        Video.objects.filter(video_id__endswith='-inc').delete()

        return user

    def test_inc(self, n_inc=10):
        user = self.create_user()
        n_videos, n_ratings = self.n_videos, self.n_ratings

        video_ids = ["%09d-%s-inc" % (i, random_alphanumeric()) for i in range(n_videos)]
        objs = [Video(video_id=vid) for vid in video_ids]
        _ = Video.objects.bulk_create(objs)
        videos_lst = list(Video.objects.filter(video_id__in=video_ids))
        videos_dct = {}
        for v in videos_lst:
            videos_dct[v.video_id] = v
        videos = [videos_dct[k] for k in video_ids]

        # creating random ratings
        video_firsts = np.random.choice(n_videos - 1, n_ratings, replace=True) + 1
        video_seconds = []
        for i in video_firsts:
            video_seconds.append(np.random.choice(i))
        assert len(video_firsts) == len(video_seconds)
        pairs = list(zip(video_firsts, video_seconds))

        assert all([x > y] for x, y in pairs)
        assert (len(pairs) - len(set(pairs))) / len(pairs) < 0.05
        pairs = set(pairs)

        ratings = [ExpertRating(user=user, video_1=videos[int(i)], video_2=videos[int(j)],
                                **{f: np.random.rand() * MAX_VALUE for f in VIDEO_FIELDS}
                                ) for i, j in pairs]

        _ = ExpertRating.objects.bulk_create(ratings)

        ground_truth_inconsistencies = [TestInconsistencies3.add_inconsistency(
            user, feature='reliability') for _ in range(n_inc)]

        qs = ExpertRating.objects.filter(user=user)

        edges = get_edges_list_db(qs, 'reliability')
        cycles_3, weights_3 = get_cycles_weights_3(edges)

        assert set(ground_truth_inconsistencies).issubset(cycles_3)

        inc_founds = inconsistencies_3_for_queryset(user)

        for (v1id, v2id, v3id) in ground_truth_inconsistencies:
            v1 = Video.objects.get(pk=v1id)
            v2 = Video.objects.get(pk=v2id)
            v3 = Video.objects.get(pk=v3id)

            yt_ids = [v1.video_id, v2.video_id, v3.video_id]

            founds = []
            for inc_found in inc_founds:
                if inc_found['feature'] != 'reliability':
                    continue
                if set(yt_ids) != set(inc_found['videos']):
                    continue
                founds.append(inc_found)
            assert len(founds) == 1, (founds, yt_ids)

            inc_found = founds[0]

            cmp = inc_found['comparisons']
            assert cmp[0]['videoA'] == yt_ids[0], (cmp, yt_ids)
            assert cmp[0]['videoB'] == yt_ids[1], (cmp, yt_ids)
            assert cmp[0]['score'] == 0.0

            assert cmp[1]['videoA'] == yt_ids[1], (cmp, yt_ids)
            assert cmp[1]['videoB'] == yt_ids[2], (cmp, yt_ids)
            assert cmp[1]['score'] == 0.0

            assert cmp[2]['videoA'] == yt_ids[2], (cmp, yt_ids)
            assert cmp[2]['videoB'] == yt_ids[0], (cmp, yt_ids)
            assert cmp[2]['score'] == 0.0

            assert inc_found['videos'] == yt_ids + [yt_ids[0]]
            assert inc_found['weight'] == 0.5


class TestOnlineUpdates(TestCase):
    def test_simple(self):
        load_gin_config('backend/ml_model/config/featureless_config.gin')
        username = 'test_user'
        dj_user = DjangoUser.objects.create(username=username)
        up = UserPreferences.objects.create(user=dj_user)
        v1 = Video.objects.create(video_id="online-1", reliability=0)
        v2 = Video.objects.create(video_id="online-2", reliability=1.0)
        VideoRating.objects.create(video=v1, user=up, reliability=0)
        VideoRating.objects.create(video=v2, user=up, reliability=1.0)
        r = ExpertRating.objects.create(user=up, video_1=v1, video_2=v2,
                                        reliability=100)
        field = 'reliability'

        update_context = OnlineRatingUpdateContext(r, field)

        def get_scores_online(rating):
            result = compute_online_update(rating_value=rating, idx_set=update_context.idx_set,
                                           model_tensor_orig=update_context.model_tensor,
                                           mb_np_orig=update_context.mb_np)
            update_context.write_updates_to_db(result['new_model_tensor'])

            s1 = VideoRating.objects.get(video=v1, user=up).reliability
            s2 = VideoRating.objects.get(video=v2, user=up).reliability
            return s1, s2

        s1, s2 = get_scores_online(-1)
        assert s1 > s2

        s1, s2 = get_scores_online(1)
        assert s1 < s2


class VideoDownloaderTestCase(TestCase):
    def test_download_metadata(self):
        CharField.register_lookup(Length, 'length')
        TextField.register_lookup(Length, 'length')
        load_gin_config('backend/add_videos.gin')

        example_unlisted_video = 'dHFYikxUatY'
        example_correct_video = '9bZkp7q19f0'
        example_wrong_url_video = 'w$url'
        example_notfound_video = 'notfoundvid'
        test_videos = [example_unlisted_video,
                       example_correct_video,
                       example_wrong_url_video,
                       example_notfound_video]
        test_responses = [
            {'name__length__gt': 5,
             'is_unlisted': True,
             'description__length__gt': 1,
             'publication_date__isnull': False,
             'language__isnull': False,
             'views__isnull': False,
             'metadata_timestamp__isnull': False,
             'uploader__isnull': False,
             'duration__isnull': False,
             'last_download_time__isnull': False,
             'download_attempts__gt': 0,
             'add_time__isnull': False,
             'download_failed': False},
            {'name__length__gt': 5,
             'is_unlisted': False,
             'views__isnull': False,
             'description__length__gt': 1,
             'publication_date__isnull': False,
             'uploader__isnull': False,
             'duration__isnull': False,
             'language__isnull': False,
             'metadata_timestamp__isnull': False,
             'wrong_url': False,
             'last_download_time__isnull': False,
             'download_attempts__gt': 0,
             'add_time__isnull': False,
             'download_failed': False},
            {'name': "",
             'is_unlisted': False,
             'metadata_timestamp__isnull': True,
             'wrong_url': True,
             'last_download_time__isnull': False,
             'download_attempts__gt': 0,
             'add_time__isnull': False,
             'download_failed': True},
            {'name': "",
             'is_unlisted': False,
             'metadata_timestamp__isnull': True,
             'wrong_url': False,
             'last_download_time__isnull': False,
             'download_attempts__gt': 0,
             'add_time__isnull': False,
             'download_failed': True}
        ]

        for v, resp in zip(test_videos, test_responses):
            Video.objects.filter(video_id=v).delete()
            vm = VideoManager(only_download=[v])
            vm.fill_info()
            vm.add_videos_in_folder_to_db()
            qs = Video.objects.filter(video_id=v)
            assert qs.count() == 1

            # format: key, val
            errors = []
            for key, val in resp.items():
                sub_qs = qs.filter(**{key: val})
                if sub_qs.count() != 1:
                    errors.append((key, val))

            assert not errors, (v, resp, errors)

            o = qs.get()
            print(o)


class TestVideoRatingPrivacyAnnotation(TestCase):
    """Test that video rating privacy annotation works correctly."""

    def setUp(self):
        self.user = DjangoUser.objects.create(username='test')
        self.video = Video.objects.create(video_id='testv')
        self.user_prefs = UserPreferences.objects.create(user=self.user)
        self.rating = VideoRating.objects.create(user=self.user_prefs, video=self.video)

    def test_privacy(self):
        VideoRatingPrivacy.objects.all().delete()

        qs = Video.objects.all()
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix='videoratingprivacy',
                                                  field_user=self.user_prefs,
                                                  default_value=True)
        assert len(qs) == 1
        assert qs[0]._is_public is True

        qs = Video.objects.all()
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix='videoratingprivacy',
                                                  field_user=self.user_prefs,
                                                  default_value=False)
        assert len(qs) == 1
        assert qs[0]._is_public is False

        VideoRatingPrivacy.objects.all().delete()
        VideoRatingPrivacy.objects.create(video=self.video, user=self.user_prefs,
                                          is_public=True)

        qs = Video.objects.all()
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix='videoratingprivacy',
                                                  field_user=self.user_prefs,
                                                  default_value=True)
        assert len(qs) == 1
        assert qs[0]._is_public is True

        qs = Video.objects.all()
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix='videoratingprivacy',
                                                  field_user=self.user_prefs,
                                                  default_value=False)
        assert len(qs) == 1
        assert qs[0]._is_public is True

        VideoRatingPrivacy.objects.all().delete()
        VideoRatingPrivacy.objects.create(video=self.video, user=self.user_prefs,
                                          is_public=False)

        qs = Video.objects.all()
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix='videoratingprivacy',
                                                  field_user=self.user_prefs,
                                                  default_value=True)
        assert len(qs) == 1
        assert qs[0]._is_public is False

        qs = Video.objects.all()
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix='videoratingprivacy',
                                                  field_user=self.user_prefs,
                                                  default_value=False)
        assert len(qs) == 1
        assert qs[0]._is_public is False


class TestVideoSignalUpdate(TestCase):
    """Test that update signals work correctly for computed properties."""

    def test_props(self):
        domain = EmailDomain.objects.create(domain="@domain.com",
                                            status=EmailDomain.STATUS_ACCEPTED)
        video = Video.objects.create(video_id='test_video')
        video_other = Video.objects.create(video_id='test_video_other')
        user = DjangoUser.objects.create(username='test_user')
        up = UserPreferences.objects.create(user=user)
        ui = UserInformation.objects.create(user=user, show_my_profile=False)

        vrp = VideoRatingPrivacy.objects.create(user=up, video=video, is_public=False)
        er = ExpertRating.objects.create(user=up, video_1=video, video_2=video_other)

        def check_video(**kwargs):
            Video.recompute_computed_properties(only_pending=True)
            qs = Video.objects.filter(video_id='test_video')
            qs_test = qs.filter(**kwargs)
            assert qs_test.count() == 1, qs.values()

        check_video(rating_n_experts=0, rating_n_ratings=0,
                    n_public_experts=0, n_private_experts=0)

        ve = VerifiableEmail.objects.create(user=ui, email="a@domain.com", is_verified=False)
        check_video(rating_n_experts=0, rating_n_ratings=0,
                    n_public_experts=0, n_private_experts=0)

        ve.is_verified = True
        ve.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=0, n_private_experts=1)

        ui.show_my_profile = True
        ui.save()
        vrp.is_public = True
        vrp.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=1, n_private_experts=0)

        ui.show_my_profile = False
        ui.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=0, n_private_experts=1)

        ui.show_my_profile = True
        ui.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=1, n_private_experts=0)

        vrp.is_public = False
        vrp.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=0, n_private_experts=1)

        vrp.is_public = True
        vrp.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=1, n_private_experts=0)
        public_experts = Video.objects.get(video_id='test_video').public_experts
        assert public_experts[0]['username'] == 'test_user'

        domain.status = EmailDomain.STATUS_REJECTED
        domain.save()
        check_video(rating_n_experts=0, rating_n_ratings=0,
                    n_public_experts=0, n_private_experts=0)

        domain.status = EmailDomain.STATUS_ACCEPTED
        domain.save()
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=1, n_private_experts=0)

        ve.delete()
        VerifiableEmail.objects.all().delete()
        check_video(rating_n_experts=0, rating_n_ratings=0,
                    n_public_experts=0, n_private_experts=0)

        ve = VerifiableEmail.objects.create(user=ui, email="a@domain.com", is_verified=True)
        check_video(rating_n_experts=1, rating_n_ratings=1,
                    n_public_experts=1, n_private_experts=0)

        er.delete()
        check_video(rating_n_experts=0, rating_n_ratings=0,
                    n_public_experts=0, n_private_experts=0)


class TestQuantile(TestCase):
    """Test that the quantile computation works properly."""

    def test_quantile(self, n_videos=100):
        fdata = []

        # 0.0 ... 1.0
        quantile_direct = np.linspace(0.0, 1.0, n_videos)

        # random permutations for each feature
        permutations = {f: np.random.permutation(n_videos) for f in VIDEO_FIELDS}

        # squaring and permuting
        fdata = [{f: 10 - 3 * quantile_direct[permutations[f]][v] ** 2
                  for f in VIDEO_FIELDS}
                 for v in range(n_videos)]

        # creating videos
        [Video.objects.create(video_id='test%05d' % i, **fdata[i])
         for i in range(n_videos)]

        # computing quantiles
        Video.recompute_quantiles()

        # validating results
        videos = Video.objects.all().order_by('video_id')
        for i, v in enumerate(videos):
            for f in VIDEO_FIELDS:
                quantile_expected = quantile_direct[permutations[f]][i]
                quantile_obtained = getattr(v, f + "_quantile")
                assert np.allclose(quantile_expected, quantile_obtained), \
                       (v, f, quantile_expected, quantile_obtained)


class TestParetoOptimality(TestCase):
    """Test that the pareto-optimality computation works properly."""

    def test_pareto(self):
        assert len(VIDEO_FIELDS) >= 2

        feature1 = VIDEO_FIELDS[0]
        feature2 = VIDEO_FIELDS[1]

        v = Video.objects.create(video_id='v0', **{feature1: 0, feature2: 0})
        assert v.pareto_optimal is False
        Video.objects.create(video_id='v1', **{feature1: 1, feature2: 0})
        Video.objects.create(video_id='v2', **{feature1: 0, feature2: 1})
        Video.objects.create(video_id='v3', **{feature1: 1, feature2: 1})

        Video.recompute_pareto()

        assert Video.objects.get(video_id='v0').pareto_optimal is False
        assert Video.objects.get(video_id='v1').pareto_optimal is False
        assert Video.objects.get(video_id='v2').pareto_optimal is False
        assert Video.objects.get(video_id='v3').pareto_optimal is True
