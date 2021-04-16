from backend.ml_model.preference_aggregation import PreferencePredictor, MedianPreferenceAggregator
import os
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
import tensorflow as tf
tf.compat.v1.enable_eager_execution()


class PreferenceLearningModelEmbedding(PreferencePredictor):
    """A model for preference learning."""

    def __init__(self, input_dim=2, output_dim=1, name=None):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.reset_model()
        self.clear_data()
        self.data_points = []
        super(
            PreferenceLearningModelEmbedding,
            self).__init__(
            model=self.model)

    def __call__(self, x):
        """Do the predictions on inputs x."""
        return self.model(x).numpy()

    def reset_model(self):
        """Re-create the model."""
        self.model = self.build_score_model()
        self.model_pref = PreferenceLearningModelEmbedding.build_preference_model(
            self.model)
        self.losses = []

    def _save_path(self, directory, name=None):
        if name is None:
            name = self.name
        assert name is not None, "Either set name on creation or on save/restore call."
        path = os.path.join(directory, name + '.h5')
        return path

    def save(self, directory):
        """Save weights."""
        path = self._save_path(directory=directory)
        self.model.save_weights(path)

    def load(self, directory):
        """Load weights."""
        path = self._save_path(directory=directory)
        self.model.load_weights(path)

    def clear_data(self):
        """Remove all preferences from the training dataset."""
        self.xs = []
        self.ys = []

    def register_preference(self, data_pt_1, data_pt_2, p1_vs_p2):
        """Save data when preference is available."""
        assert p1_vs_p2.shape == (self.output_dim,), "Wrong preference shape."
        assert data_pt_1.shape == (
            self.input_dim,) and data_pt_2.shape == (
            self.input_dim,), "Wrong input shape"
        x = np.hstack([data_pt_1, data_pt_2])
        val = p1_vs_p2
        assert np.all(
            val >= 0) and np.all(
            val <= 1), "Preferences should be in [0,1]"
        y = np.array([*val, *(1 - val)])

        self.xs.append(x)
        self.ys.append(y)

    def fit(self, epochs=20):
        """Fit on the data."""
        history = self.model_pref.fit(np.array(self.xs), np.array(self.ys),
                                      epochs=epochs, verbose=0)
        self.losses += history.history['loss']

    def plot_loss(self):
        """Plot all losses."""
        plt.title('Loss')
        plt.plot(self.losses)
        # plt.show()

    def plot_loss_and_decisions(self, data, idxes=None):
        """Plot both the loss and the decision fcn."""
        plt.figure(figsize=(12, 5))

        for dim in range(self.output_dim):
            plt.subplot(1, 1 + self.output_dim, dim + 1)
            self.plot_with_colors(data, idxes, component=dim)

        plt.subplot(1, 1 + self.output_dim, 1 + self.output_dim)
        plt.title("Train loss")
        self.plot_loss()
        plt.show()

    def iteration(
            self,
            data,
            override_input_fcn=None,
            do_plot=True,
            do_fit=True,
            min_data_to_train=5,
            epochs=100,
            epochs_many=1000):
        """Show the state and query the user."""
        # choosing two at random
        idx_1 = np.random.choice(range(len(data)))
        idx_2 = np.random.choice(range(len(data)))

        # plotting loss and current predictions
        if do_plot:
            self.plot_loss_and_decisions(data, idxes=[idx_1, idx_2])

        # user input
        if override_input_fcn:
            val = override_input_fcn(idx_1, idx_2)
        else:
            assert self.output_dim == 1, "Only support 1 dim for human input."
            val = input()

        # terminal commands
        if isinstance(val, str):
            # clear -- reset training data
            if val == 'clear':
                self.clear_data()

            # x -- fit with more iterations
            elif (val == 'x') and do_fit:
                self.fit(epochs=epochs_many)

            # stop -- stop the loop
            elif val == 'stop':
                return False

            # converting everything else to a float
            else:
                try:
                    val = float(val)
                    val = max(val, 0)
                    val = min(val, 1)
                    val = np.array([val])
                except Exception as e:
                    print(e)

        # otherwise registering data and doing a regular fit
        try:
            self.register_preference(data[idx_1, :], data[idx_2, :], val)
            if (len(self.xs) > min_data_to_train) and do_fit:
                self.fit(epochs=epochs)
        except Exception as e:
            print(e)
        return True

    @staticmethod
    def _build_score_model(input_dim, output_dim):
        """Build a model to score objects."""
        model = tf.keras.Sequential([
            tf.keras.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(output_dim, activation=None, use_bias=True,
                                  kernel_regularizer='l2', bias_regularizer='l2')
        ])
        # model.summary()
        return model

    def build_score_model(self):
        """Build a score model with known dimensions."""
        return PreferenceLearningModelEmbedding._build_score_model(
            input_dim=self.input_dim, output_dim=self.output_dim)

    @staticmethod
    def build_preference_model(model):
        """Build a model to train by comparison."""
        input_dim = model.input_shape[1]
        output_dim = model.output_shape[1]
        inputs = tf.keras.Input(shape=(2 * input_dim,))
        input_1 = inputs[:, :input_dim]
        input_2 = inputs[:, input_dim:]
        out_1 = model(input_1)
        out_2 = model(input_2)

        # stacking inputs together
        y = tf.stack([out_1, out_2], axis=2)

        # applying softmax
        y = tf.keras.layers.Softmax(axis=2)(y)

        # unpacking data
        o1 = tf.reshape(y, (-1, output_dim, 2))[:, :, 0]
        o2 = tf.reshape(y, (-1, output_dim, 2))[:, :, 1]

        # creating a stacked output
        out = tf.concat([o1, o2], axis=1)

        # only works for 1d
        # out = tf.keras.layers.concatenate([out_1, out_2])

        # creating a keras model
        model_pref = tf.keras.Model(inputs=inputs, outputs=out)

        model_pref.compile(
            'adam', tf.keras.losses.CategoricalCrossentropy(
                from_logits=False))
        # model_pref.summary()
        return model_pref


@tf.function
def flatten_array_of_tensors(W):
    """Take an array of tensor and turn into a single flat tensor."""
    return tf.concat([tf.reshape(w, (-1,)) for w in W], axis=0)


class MedianPreferenceAverageRegularizationAggregator(
        MedianPreferenceAggregator):
    """Aggregate with median, train with an average set of parameters."""

    def __init__(self, models):
        # should have right models to train them
        assert all([isinstance(m, PreferenceLearningModelEmbedding)
                    for m in models])
        super(
            MedianPreferenceAverageRegularizationAggregator,
            self).__init__(models)
        self.common_model = self.models[0].build_score_model()
        self.losses = []

    def plot_loss(self, *args, **kwargs):
        """Plot the loss, inherit from models[0]."""
        type(self.models[0]).plot_loss(self, *args, **kwargs)

    def plot_loss_and_decisions(self, data, idxes=None):
        """Plot the losses and decision boundary."""
        def arr_of_dicts_to_dict_of_arrays(arr):
            """ Array of dicts to dict of arrays """
            all_keys = arr[0].keys()
            return {key: [v[key] for v in arr] for key in all_keys}

        losses = arr_of_dicts_to_dict_of_arrays(self.losses)

        plt.figure(figsize=(15, 10))
        plot_h = max(self.output_dim, len(losses))

        for dim in range(self.output_dim):
            plt.subplot(2, plot_h, dim + 1)
            self.plot_with_colors(data, idxes=idxes, component=dim)

        for i, key in enumerate(losses.keys(), 1):
            plt.subplot(2, plot_h, i + self.output_dim)
            plt.title(key)
            plt.plot(losses[key])

        # plt.show()

    def fit(self, epochs=20, **kwargs):
        """Fit with multiple epochs"""
        for _ in tqdm(range(epochs)):
            self.fit_step(**kwargs)

        if self.losses:
            return self.losses[-1]
        else:
            return {}

    # @tf.function
    def fit_step(self, reg_common_to_0=1e-3, reg_m_to_common=1e-3):
        """Fit using the custom magic loss..."""
        optimizer = self.models[0].model_pref.optimizer

        # loss function
        loss_fcn = tf.keras.losses.CategoricalCrossentropy(from_logits=False)

        # defining the custom loss
        with tf.GradientTape() as tape:
            # model fits to data
            losses_fit = [
                loss_fcn(
                    np.array(
                        model.ys), model.model_pref(
                        np.array(
                            model.xs))) for model in self.models if len(
                    model.xs) > 0]

            # common model weights are small
            loss_common_to_0 = tf.norm(
                flatten_array_of_tensors(
                    self.common_model.weights), ord=2)

            # models are close to the common model
            losses_dist_to_common = []
            for model in self.models:
                losses_dist_to_common.append(
                    tf.norm(
                        flatten_array_of_tensors(
                            model.model.weights) -
                        flatten_array_of_tensors(
                            self.common_model.weights),
                        ord=1))

            fit_loss = tf.reduce_sum(losses_fit)
            m_to_common_loss = tf.reduce_sum(losses_dist_to_common)

            total_loss = fit_loss + \
                reg_common_to_0 * loss_common_to_0 + \
                reg_m_to_common * m_to_common_loss

        all_variables = [
            model.model.trainable_variables for model in self.models]
        all_variables.append(self.common_model.trainable_variables)

        def list_of_lists_to_list(lst_of_lst):
            """Flatten a list of lists"""
            return [x for lst in lst_of_lst for x in lst]

        grads = tape.gradient(total_loss, all_variables)
        optimizer.apply_gradients(zip(list_of_lists_to_list(grads),
                                      list_of_lists_to_list(all_variables)))

        # print(total_loss, fit_loss, tf.executing_eagerly())

        self.losses.append({'total': total_loss.numpy(),
                            'fit': fit_loss.numpy(),
                            'common_to_0': loss_common_to_0.numpy(),
                            'm_to_common': m_to_common_loss.numpy()})
