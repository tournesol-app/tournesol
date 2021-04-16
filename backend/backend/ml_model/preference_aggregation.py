import gin
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt
import numpy as np
import tensorflow as tf
tf.compat.v1.enable_eager_execution()


@gin.configurable
class PreferencePredictor(object):
    """Holds user preferences."""

    def __init__(self, model, show_component=0):
        self.model = model
        self.show_component = show_component

    def __call__(self, x):
        """Do the predictions on inputs x."""
        return self.model(x)

    def plot_with_colors(self, data, idxes=None, component=None):
        """Plot data with model output."""
        if component is None:
            component = self.show_component

        # doing PCA if have >1 components
        if data.shape[1] > 2:
            data_vis = PCA(n_components=2).fit_transform(data)
            xylabel = 'PCA[Input]'
        else:
            data_vis = data
            xylabel = 'Input'

        ys = self(data)[:, component]
        # plt.title("Data")
        plt.xlabel('%s[0]' % xylabel)
        plt.ylabel('%s[1]' % xylabel)
        cm = plt.cm.get_cmap('copper')
        plt.title("Output[%d] Min: %.2f Max: %.2f" % (component,
                                                      np.min(ys), np.max(ys)))
        plt.scatter(data_vis[:, 0], data_vis[:, 1], c=ys, cmap=cm)

        if idxes:
            texts = ["1", "0"]
            for idx, text in zip(idxes, texts):
                plt.text(*data_vis[idx, :], text, fontsize=15, color='red',
                         bbox=dict(facecolor='white', alpha=0.5))

        # plt.xlim((-3, 3))
        # plt.ylim((-3, 3))


class MedianPreferenceAggregator(PreferencePredictor):
    """Aggregate preferences of experts using a median."""

    def __init__(self, models):
        self.models = models
        self.input_dim = self.models[0].input_dim
        self.output_dim = self.models[0].output_dim
        assert all([m.input_dim == self.input_dim for m in self.models])
        assert all([m.output_dim == self.output_dim for m in self.models])
        super(MedianPreferenceAggregator, self).__init__(model=None)

    def __call__(self, x):
        """Aggregate with a median."""
        ys = [model(x) for model in self.models]
        return np.median(ys, axis=0)

    def save(self, directory):
        for m in self.models:
            m.save(directory=directory)

    def load(self, directory):
        exceptions = {}
        for i, m in enumerate(self.models):
            try:
                m.load(directory=directory)
            except Exception as e:
                exceptions[i] = e
        return exceptions
