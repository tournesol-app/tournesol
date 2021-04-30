import gin
import tensorflow as tf
from backend.ml_model.client_server.database_learner import DatabasePreferenceLearner
from backend.ml_model.preference_aggregation_featureless import (
    FeaturelessPreferenceLearningModel,
    FeaturelessMedianPreferenceAverageRegularizationAggregator,
    AllRatingsWithCommon,
)
from backend.models import UserPreferences
from backend.ml_model.tqdmem import tqdmem, print_memory

tf.compat.v1.enable_eager_execution()


@gin.configurable
class DatabasePreferenceLearnerFeatureless(DatabasePreferenceLearner):
    """Learn models from the database, save/restore."""

    def create_models(self):
        """Create learning models and the aggregator."""
        self.all_ratings = AllRatingsWithCommon(
            experts=self.users,
            objects=self.videos,
            output_features=self.features,
            name="prod",
        )

        print_memory(stage="DPLF:ratings_nodata_created")

        # creating models
        self.user_to_model = {
            user: FeaturelessPreferenceLearningModel(
                expert=user, all_ratings=self.all_ratings
            )
            for user in self.users
        }

        print_memory(stage="DPLF:models_created")

        # before creating the aggregator, filling models with data
        self.user_to_size = {
            user: self.fill_model_data(self.user_to_model[user], user)
            for user in tqdmem(self.users, desc="fill_data")
        }

        # virtual 'common' data
        fplm_common = FeaturelessPreferenceLearningModel(
            expert=AllRatingsWithCommon.COMMON_EXPERT, all_ratings=self.all_ratings
        )
        fplm_common.on_dataset_end()

        print_memory(stage="DPLF:data_filled")

        # resetting the model given the data
        self.all_ratings.reset_model()

        print_memory(stage="DPLF:model_reset_ok")

        # aggregating models
        self.aggregator = FeaturelessMedianPreferenceAverageRegularizationAggregator(
            models=[self.user_to_model[u] for u in self.users]
        )
        self.aggregator.certification_status = self.user_certified

        print_memory(stage="DPLF:aggregator_created")

    def visualize(self):
        """Plot model predictions and losses."""
        self.aggregator.plot_loss()
        self.save_figure()

    def predict_user(self, user, videos):
        # @todo: use vectorized operations
        assert isinstance(user, UserPreferences)
        model = self.user_to_model[user.id]
        result = list(model([v.video_id for v in videos]))

        for i, video in enumerate(videos):
            if not model.ratings_with_object(video.video_id):
                result[i] = None

        return result

    def predict_aggregated(self, videos):
        # @todo: use vectorized operations
        return self.aggregator([v.video_id for v in videos])

    def fit(self, **kwargs):
        """Fit on latest database records."""

        self.stats["dataset_size"] = self.user_to_size

        super(DatabasePreferenceLearnerFeatureless, self).fit(**kwargs)

    def fill_model_data(self, model, user):
        """Populate model data from db."""
        n = 0
        for dct in self.get_dataset(user=user):
            v1, v2, res, w = [
                dct[key] for key in ["video_1", "video_2", "cmp", "weights"]
            ]
            model.register_preference(v1, v2, res, w)
            n += 1
        model.on_dataset_end()
        return n
