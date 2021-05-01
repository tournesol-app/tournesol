import datetime
import logging
import os

import gin
import tensorflow as tf
from annoying.functions import get_object_or_None
from backend.models import (
    Video,
    ExpertRating,
    UserPreferences,
    VideoRating,
    UserInformation,
)
from backend.rating_fields import MAX_VALUE
from backend.rating_fields import VIDEO_FIELDS
from django_react.settings import BASE_DIR, COUNT_UNCERTIFIED_USERS
from matplotlib import pyplot as plt
import numpy as np
from backend.ml_model.tqdmem import print_memory, tqdmem
from django.db import transaction
from django.db.models import Q

tf.compat.v1.enable_eager_execution()


@gin.configurable
class DatabasePreferenceLearner(object):
    """Learn models from the database, save/restore."""

    def __init__(
        self,
        directory=None,
        load=True,
        save=True,
        user_queryset=None,
        video_queryset=None,
        users_to_ratings=None,
        features=None,
    ):
        # determining the directory to save results to
        if directory is None:
            directory = os.path.join(BASE_DIR, "..", ".models")
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

        print_memory("DPL:init")

        # all users
        self.user_queryset = (
            UserPreferences.objects.all() if user_queryset is None else user_queryset
        )
        self.users = [x.id for x in self.user_queryset]

        print_memory("DPL:users_loaded")

        # is the user certified?
        # if not, will not be used for aggregation

        def is_certified(user_pref_id):
            if COUNT_UNCERTIFIED_USERS:
                return True
            else:
                obj = get_object_or_None(
                    UserInformation, user__userpreferences__id=user_pref_id
                )
                return obj.is_certified if obj is not None else False

        self.user_certified = [is_certified(user) for user in self.users]

        print_memory("DPL:is_certified_all")

        # all videos
        self.video_queryset = (
            Video.objects.all() if video_queryset is None else video_queryset
        )
        self.videos = [x.video_id for x in self.video_queryset]
        self.videos_set = set(self.videos)

        print_memory("DPL:all_videos_loaded")

        # user -> all expert rating array
        self.users_to_ratings = (
            {user: ExpertRating.objects.filter(user=user) for user in self.users}
            if users_to_ratings is None
            else users_to_ratings
        )

        print_memory("DPL:users_ratings_loaded")

        for u in self.users:
            assert (
                u in self.users_to_ratings
            ), f"users_to_ratings must contain a user {u}"

        print_memory("DPL:user_rating_check_ok")

        # models and aggregator (empty)
        self.user_to_model = {user: None for user in self.users}

        print_memory("DPL:models_initialized")

        # the aggregator (will be created
        self.aggregator = None

        # creating the list of features
        if features is None:
            features = VIDEO_FIELDS

        assert isinstance(features, list), features
        assert all([f in VIDEO_FIELDS for f in features]), (features, VIDEO_FIELDS)

        self.features = features

        print_memory("DPL:pre_model_create")

        print(f"Learner uses features {self.features}")

        # actually creating the models
        # aggregator is set here
        self.create_models()

        print_memory("DPL:models_created")

        # load/save variables
        self.save_after_train = save

        # loading weights if requested
        if load:
            self.load()

        print_memory("DPL:weights_loaded")

        self.train_counter = 0
        self.stats = {}

        print_memory("DPL:READY")

    def __getstate__(self):
        result = {
            'directory': self.directory,
            'aggregator': self.aggregator if self.aggregator is None
            else self.aggregator.__getstate__(),
        }
        return result

    def create_models(self):
        """Fill the user_to_model and aggregator fields."""
        raise NotImplementedError

    def save_figure(self):
        plt.suptitle("Train call %d" % self.train_counter, wrap=True)
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plt.savefig(
            os.path.join(
                self.directory,
                f"train_{type(self).__name__}_{date}_%05d.pdf" % self.train_counter,
            ),
            bbox_inches="tight",
        )
        plt.clf()
        plt.close(plt.gcf())

    def fit(self, **kwargs):
        """Fit on latest database records."""
        # fitting on data
        self.aggregator.user_certified = self.user_certified

        self.stats.update(self.aggregator.fit(**kwargs))

        logging.info(f"Fit iteration finished {self.stats}")

        # incrementing the train counter
        self.train_counter += 1

        if self.save_after_train:
            # saving weights
            self.save()

            # showing image
            self.visualize()

    def predict_user(self, user, videos):
        """Prediction for one user, or None if there's nothing there."""
        return []

    def predict_aggregated(self, videos):
        """Predictions for the aggregated model."""
        return []

    def update_features(self):
        """Update the features for all videos in the database using the fitted model."""
        logging.info("Loading scores into the database.")
        videos = self.video_queryset

        # todo: reimplement so that there's no double loop
        # in a transaction, reset all ratings, and then load the new ones

        # saving per-user scores
        for user in tqdmem(self.users, desc="user_scores_write"):
            user_pref = UserPreferences.objects.get(id=user)

            # intermediate results are not visible to site visitors
            with transaction.atomic():
                # deleting old ratings
                VideoRating.objects.filter(user=user_pref).delete()

                # selecting rated videos by this person
                rated_videos = Video.objects.filter(
                    Q(expertrating_video_1__user=user_pref)
                    | Q(expertrating_video_2__user=user_pref)
                ).distinct()

                # only selecting "pre-registered" videos
                rated_videos = [x for x in rated_videos if x.video_id in self.videos_set]

                if rated_videos:
                    result_user = self.predict_user(user=user_pref, videos=rated_videos)
                    for i, video in enumerate(rated_videos):
                        result = result_user[i]
                        param_dict = dict(user=user_pref, video=video)

                        if result is not None:
                            rating_record = VideoRating.objects.get_or_create(
                                **param_dict
                            )[0]
                            for j, attribute in enumerate(self.features):
                                setattr(rating_record, attribute, result[j])
                            rating_record.save()

        # saving overall scores
        # intermediate results are not visible to site visitors
        with transaction.atomic():

            # only selecting "pre-registered" videos
            videos = [x for x in videos if x.video_id in self.videos_set]

            results = self.predict_aggregated(videos=videos)
            for i, video in enumerate(tqdmem(videos, desc="agg_scores_write")):
                result = results[i]

                # no raters -> score is 0 (-> not shown in search)
                if not video.rating_n_experts:
                    result = [0.0 for _ in result]

                for i, attribute in enumerate(self.features):
                    setattr(video, attribute, result[i])
                video.save()

    def get_dataset(self, user):
        """Get dataset for a user. Format: (v_emb1, v_emb2, result)."""

        for comparison in self.users_to_ratings[user]:
            v1 = comparison.video_1.video_id
            v2 = comparison.video_2.video_id

            v1_emb = comparison.video_1.get_embedding_np_array()
            v2_emb = comparison.video_2.get_embedding_np_array()

            def vector_subset(features, v, orig_features):
                """Take a subset of components from a vector."""
                idxes = [orig_features.index(f) for f in features]
                return np.array(v)[idxes]

            comparison_vector = comparison.features_as_vector_centered / MAX_VALUE
            weights_vector = comparison.weights_vector()

            comparison_vector = vector_subset(
                features=self.features, orig_features=VIDEO_FIELDS, v=comparison_vector
            )

            weights_vector = vector_subset(
                features=self.features, orig_features=VIDEO_FIELDS, v=weights_vector
            )

            if v1 is None or v2 is None:
                continue

            yield {
                "video_1": v1,
                "video_2": v2,
                "cmp": comparison_vector,
                "weights": weights_vector,
                "v1_emb": v1_emb,
                "v2_emb": v2_emb,
            }

    def load(self):
        """Load weights."""
        print_memory("DPL:pre_load")
        r = self.aggregator.load(self.directory)
        print_memory("DPL:post_load")
        logging.info(f"Weights load result: {r}")
        return r

    def save(self):
        """Save weights."""
        logging.info("Saving weights")
        self.aggregator.save(self.directory)
