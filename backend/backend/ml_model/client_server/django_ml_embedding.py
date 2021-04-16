from backend.rating_fields import VIDEO_FIELDS
from backend.ml_model.preference_aggregation_with_embeddings import \
    PreferenceLearningModelEmbedding, MedianPreferenceAverageRegularizationAggregator
from backend.ml_model.client_server.database_learner import DatabasePreferenceLearner
import gin
import numpy as np
from backend.models import Video, UserPreferences
import tensorflow as tf
tf.compat.v1.enable_eager_execution()


@gin.configurable
class DatabasePreferenceLearnerEmbedding(DatabasePreferenceLearner):
    """Learn models from the database, save/restore."""

    def create_models(self):
        """Create the models."""

        # creating models
        self.user_to_model = {
            user: PreferenceLearningModelEmbedding(
                input_dim=Video.EMBEDDING_LEN,
                output_dim=len(VIDEO_FIELDS),
                name='user_%d_representative' %
                user) for user in self.users}

        # aggregating models
        self.aggregator = MedianPreferenceAverageRegularizationAggregator(
            models=[self.user_to_model[u] for u in self.users])

    def visualize(self):
        """Plot model predictions and losses."""
        # running PCA for visuals
        data = [v.get_embedding_np_array() for v in Video.objects.all()]
        data = np.array(list(filter(lambda x: x is not None, data)))

        self.aggregator.plot_loss_and_decisions(np.array(data))
        self.save_figure()

    def fit(self, **kwargs):
        """Fit on latest database records."""
        # filling data
        user_to_size = {
            user: self.fill_model_data(
                self.user_to_model[user],
                user) for user in self.users}

        self.stats['dataset_size'] = user_to_size

        super(DatabasePreferenceLearnerEmbedding, self).fit(**kwargs)

    def fill_model_data(self, model, user):
        """Populate model data from db."""
        n = 0
        for dct in self.get_dataset(user=user):
            v1_emb, v2_emb, res = [dct[key]
                                   for key in ['v1_emb', 'v2_emb', 'cmp']]
            if v1_emb is None or v2_emb is None:
                continue
            model.register_preference(v1_emb, v2_emb, res)
            n += 1
        return n

    def predict_with_emb_or_None(self, model, videos):
        # valid embeddings
        embeddings = [v.get_embedding_np_array()
                      for v in videos if v.get_embedding_np_array() is not None]

        # result for existing embeddings
        results_emb = self.aggregator(np.array(embeddings))

        # full result
        result = []

        # read index from results_emb
        i = 0
        for v in videos:
            if v.get_embedding_np_array() is not None:
                result.append(results_emb[i])
                i += 1
            else:
                result.append(None)
        return result

    def predict_aggregated(self, videos):
        return self.predict_with_emb_or_None(
            model=self.aggregator, videos=videos)

    def predict_user(self, user, videos):
        assert isinstance(user, UserPreferences)
        model = self.user_to_model[user.id]
        return self.predict_with_emb_or_None(model=model, videos=videos)
