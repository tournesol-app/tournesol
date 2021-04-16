import logging
import os
import pickle

import gin
import numpy as np
import tensorflow as tf
from backend.ml_model.helpers import choice_or_all, arr_of_dicts_to_dict_of_arrays, convert_to_tf
from backend.ml_model.preference_aggregation import PreferencePredictor, MedianPreferenceAggregator
from matplotlib import pyplot as plt
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()

Adam = gin.external_configurable(tf.keras.optimizers.Adam)
SGD = gin.external_configurable(tf.keras.optimizers.SGD)
Zeros = gin.external_configurable(tf.keras.initializers.Zeros)


def variable_index_layer_call(tensor, inputs):
    """Get variable at indices."""
    return tf.gather_nd(tensor, inputs)


@gin.configurable
class VariableIndexLayer(tf.keras.layers.Layer):
    """Layer which outputs a trainable variable on a call."""

    def __init__(self, shape, name="index_layer", initializer=None):
        super(VariableIndexLayer, self).__init__(name=name)
        self.v = self.add_weight(
            shape=shape, initializer=initializer,
            trainable=True, name="var/" + name,
            dtype=tf.keras.backend.floatx())

    def call(self, inputs, **kwargs):
        # print("INPUT SHAPE", inputs.shape, "WEIGHT SHAPE", self.v.shape)

        out = variable_index_layer_call(self.v, inputs)
        # print("INPUT SHAPE", inputs.shape, "WEIGHT SHAPE", self.v.shape, "OUT SHAPE", out.shape)
        return out


@gin.configurable
class AllRatingsWithCommon(object):
    COMMON_EXPERT = "__aggregate_expert__"

    """Stores a tensor will ALL ratings, including the common model."""

    def __init__(
            self,
            experts,
            objects,
            output_features,
            name,
            var_init_cls=VariableIndexLayer):

        # experts
        self.name = name
        self.experts = list(experts) + [self.COMMON_EXPERT]
        self.experts_set = set(self.experts)
        self.aggregate_index = len(self.experts) - 1
        assert len(
            self.experts) == len(
            self.experts_set), "Duplicate experts are not allowed"
        self.experts_reverse = {
            expert: i for i, expert in enumerate(self.experts)}

        # features
        self.output_features = list(output_features)
        self.output_dim = len(output_features)

        # objects
        self.objects = list(objects)
        self.objects_set = set(self.objects)
        assert len(
            self.objects_set) == len(
            self.objects), "Duplicate objects are not allowed."
        self.objects_reverse = {obj: i for i, obj in enumerate(self.objects)}

        # outputs
        self.model = None
        self.layer = None
        self.var_init_cls = var_init_cls

        self.reset_model()

    def reset_model(self):
        self.layer = self.var_init_cls(
            shape=(len(self.experts), len(self.objects), self.output_dim))
        # print(self.output_dim)
        self.model_input = tf.keras.Input(shape=(2,), dtype=tf.int64)
        self.model = tf.keras.Model(
            inputs=self.model_input,
            outputs=self.layer(
                self.model_input))

    def _save_path(self, directory):
        path = os.path.join(
            directory,
            f'{self.name}_alldata_featureless_onetensor.pkl')
        return path

    def save(self, directory):
        """Save weights."""
        result = {
            'name': self.name,
            'experts': self.experts,
            'objects': self.objects,
            'data': self.layer.v.numpy(),
            'features': self.output_features,
        }
        assert result['data'].shape == (len(result['experts']), len(
            result['objects']), len(result['features']))
        path = self._save_path(directory=directory)
        pickle.dump(result, open(path, 'wb'))

    def load(self, directory):
        """Load weights."""

        # print("Load weights")

        path = self._save_path(directory=directory)
        result = pickle.load(open(path, 'rb'))

        # setting zero weights
        self.reset_model()

        old_object_indices = {
            obj: idx for idx, obj in enumerate(
                result['objects'])}
        old_feature_indices = {
            feature: idx for idx, feature in enumerate(
                result['features'])}
        old_expert_indices = {
            expert: idx for idx, expert in enumerate(
                result['experts'])}

        restored_items = 0

        # print("experts", len(self.experts), "objects", len(self.objects),
        #       "features", len(self.output_features))

        to_assign_idx = []
        to_assign_vals = []

        for new_expert_idx, expert in tqdm(enumerate(self.experts)):
            old_expert_idx = old_expert_indices.get(expert, None)
            for new_obj_idx, obj in enumerate(self.objects):
                old_obj_idx = old_object_indices.get(obj, None)
                for new_f_idx, feature in enumerate(self.output_features):
                    old_f_idx = old_feature_indices.get(feature, None)

                    if all([x is not None for x in [old_expert_idx, old_obj_idx, old_f_idx]]):
                        val = result['data'][old_expert_idx, old_obj_idx, old_f_idx]

                        if not np.isnan(val):
                            to_assign_idx.append((new_expert_idx, new_obj_idx, new_f_idx))
                            to_assign_vals.append(val)
                            restored_items += 1

        if to_assign_idx:
            self.layer.v = tf.Variable(
                tf.tensor_scatter_nd_update(self.layer.v,
                                            to_assign_idx,
                                            to_assign_vals),
                trainable=True)

        # print(to_assign_idx, to_assign_vals)
        # print(self.layer.v)

        return {'restored_items': restored_items}

    def get_internal_ids(self, objects, experts):
        """Get integer IDs for objects."""
        assert len(objects) == len(experts)
        assert all([expert in self.experts_set for expert in experts])
        assert all([obj in self.objects_set for obj in objects])
        return [(self.experts_reverse[expert], self.objects_reverse[obj])
                for expert, obj in zip(experts, objects)]


@gin.configurable
class FeaturelessPreferenceLearningModel(PreferencePredictor):
    """A model for preference learning."""

    def __init__(self, expert=None, all_ratings=None):
        assert isinstance(all_ratings, AllRatingsWithCommon)
        self.all_ratings = all_ratings
        self.objects = self.all_ratings.objects
        assert expert in self.all_ratings.experts
        self.expert = expert
        self.output_features = self.all_ratings.output_features
        self.clear_data()
        self.ratings = []
        self.input_dim = -1
        self.output_dim = len(self.output_features)
        super(
            FeaturelessPreferenceLearningModel,
            self).__init__(
            model=self.__call__)

    def __call__(self, objects):
        internal_ids = self.all_ratings.get_internal_ids(
            objects, experts=[self.expert] * len(objects))
        result = self.all_ratings.model.predict(
            np.array(internal_ids, dtype=np.int64))
        return result

    def ratings_with_object(self, obj):
        """Number of ratings with a particular object."""
        M_ev = 0
        for r in self.ratings:
            if r['o1'] == obj:
                M_ev += 1
            elif r['o2'] == obj:
                M_ev += 1
        return M_ev

    def clear_data(self):
        """Remove all preferences from the training dataset."""
        self.ratings = []

    def register_preference(self, o1, o2, p1_vs_p2, weights):
        """Save data when preference is available."""
        assert p1_vs_p2.shape == (self.output_dim,), "Wrong preference shape."
        assert o1 in self.objects, "Wrong object %s" % o1
        assert o2 in self.objects, "Wrong object %s" % o2
        val = p1_vs_p2
        val_no_nan = val[~np.isnan(val)]
        assert np.all(
            val_no_nan >= 0) and np.all(
            val_no_nan <= 1), "Preferences should be in [0,1]"

        self.ratings.append({'o1': o1, 'o2': o2,
                             'ratings': 2 * (np.array(p1_vs_p2) - 0.5),
                             'weights': weights})


# get the loss function for this class
@tf.function(experimental_relax_shapes=True)
def loss_fcn(
        experts_rating=None,
        objects_rating_v1=None,
        objects_rating_v2=None,
        cmp=None,
        weights=None,
        experts_all=None,
        objects_all=None,
        num_ratings_all=None,
        objects_common_to_1=None,
        model_tensor=None,
        aggregate_index=None,
        lambda_=None,
        mu=None,
        C=None,
        default_score_value=None):
    """
    Compute the loss function. All IDs are internal (int64).

    See https://www.overleaf.com/project/5f44dd8e84c8540001bf1552
    Equations 1-2-3

    Args:
        experts_rating: 1D tensor with expert IDs
        objects_rating_v1: 1D tensor with LEFT objects, same length as experts_rating
        objects_rating_v2: 1D tensor with RIGHT objects, same length as experts_rating
        cmp: 2D tensor comparison_id, feature_id, same length as experts_rating
        weights: 2D tensor comparison_id, feature_weight, same length as experts_rating
        experts_all: 1D tensor with expert IDs for the regularization loss
        objects_all: 1D tensor with objects (for common loss), same length as experts_all
        num_ratings_all: 1D tensor with number of ratings for expert/object in experts_all
            and objects_all, same length as experts_all
        objects_common_to_1: 1D tensor with object IDs for the common-to-1 loss.

    Returns dict of Tensorflow tensors with the total loss and components
    """

    result = {}

    # internal indices for experts and objects (ratings)
    idx_v1 = tf.stack((experts_rating, objects_rating_v1), axis=1)
    idx_v2 = tf.stack((experts_rating, objects_rating_v2), axis=1)

    # 2D array (comparison_id, feature) -> float
    theta_eqv = variable_index_layer_call(model_tensor, idx_v1)
    theta_eqw = variable_index_layer_call(model_tensor, idx_v2)

    # FIT LOSS SUM
    theta_vw = theta_eqv - theta_eqw
    # print(theta_vw.shape, cmp.shape)
    theta_vw_y = tf.math.multiply(theta_vw, cmp)
    sp = tf.math.softplus(theta_vw_y)
    sp_weighted = tf.math.multiply(sp, weights)

    sp_weighted_flat = tf.reshape(sp_weighted, (-1,))
    sp_weighted_no_nan = tf.boolean_mask(sp_weighted_flat,
                                         tf.math.is_finite(sp_weighted_flat))
    # tf.print("original tensor")
    # tf.print(sp_weighted_flat)

    # tf.print("nonan tensor")
    # tf.print(sp_weighted_no_nan)

    result['loss_fit'] = tf.reduce_sum(sp_weighted_no_nan)

    # LOSS MODEL TO COMMON
    # common expert
    experts_common = aggregate_index * tf.ones(
        shape=experts_all.shape, dtype=tf.int64)

    # indices for experts for regularization
    idx_all = tf.stack((experts_all, objects_all), axis=1)
    idx_common = tf.stack((experts_common, objects_all), axis=1)

    # 2D array (regul_id, feature) -> float
    theta_eqv_common = variable_index_layer_call(model_tensor, idx_all)
    s_qv = variable_index_layer_call(model_tensor, idx_common)

    # print("IDX", idx_common.shape, s_qv.shape)

    # coefficient, shape: regul_id
    num_float = tf.cast(num_ratings_all, tf.keras.backend.floatx())
    coef_yev = tf.divide(num_float, C + num_float)
    # print(theta_eqv_common.shape, s_qv.shape)
    # tf.print('thetacomm', theta_eqv_common)
    # tf.print("sqv", s_qv)
    theta_s = tf.abs(theta_eqv_common - s_qv)
    coef_yev_repeated = tf.repeat(
        tf.expand_dims(
            coef_yev,
            axis=1),
        theta_s.shape[1],
        axis=1)
    # print("THETAS", theta_s.shape, "COEF", coef_yev.shape, \
    # "COEFR", coef_yev_repeated.shape)
    # tf.print("thetas", theta_s)
    # tf.print("coefyev", coef_yev_repeated)
    theta_s_withcoeff = tf.multiply(theta_s, coef_yev_repeated)
    result['loss_m_to_common'] = tf.reduce_sum(
        theta_s_withcoeff) * lambda_

    # LOSS COMMON TO 0
    experts_common_to_1 = aggregate_index * tf.ones(
        shape=objects_common_to_1.shape, dtype=tf.int64)
    idx_common_to_1 = tf.stack(
        (experts_common_to_1, objects_common_to_1), axis=1)
    s_qv_common_to_1 = variable_index_layer_call(model_tensor, idx_common_to_1)

    sm1 = tf.math.square(s_qv_common_to_1 - default_score_value)

    # print(idx_common_to_1, s_qv_common_to_1, sm1)

    result['loss_common_to_1'] = tf.reduce_sum(sm1) * mu

    # TOTAL LOSS
    result['loss'] = result['loss_fit'] + result['loss_m_to_common'] + result[
        'loss_common_to_1']

    return result


@tf.function(experimental_relax_shapes=True)
def loss_fcn_gradient_hessian(video_indices, **kwargs):
    """Compute the loss function, gradient and the Hessian."""
    variable = kwargs['model_tensor']
    loss = loss_fcn(**kwargs)['loss']
    g = tf.gradients(loss, variable)[0]
    g = tf.gather(g, axis=1, indices=video_indices)
    h = tf.hessians(loss, variable)[0]
    h = tf.gather(h, axis=1, indices=video_indices)
    h = tf.gather(h, axis=4, indices=video_indices)
    return {'loss': loss, 'gradient': g, 'hessian': h}


@gin.configurable
class FeaturelessMedianPreferenceAverageRegularizationAggregator(MedianPreferenceAggregator):
    """Aggregate with median, train with an average set of parameters."""

    def __init__(
            self,
            models,
            epochs=20,
            optimizer=Adam(),
            hypers=None,
            batch_params=None):
        assert models, "Models cannot be empty."
        assert all([isinstance(m, FeaturelessPreferenceLearningModel)
                    for m in models]), "Wrong model type."
        super(
            FeaturelessMedianPreferenceAverageRegularizationAggregator,
            self).__init__(models)

        self.all_ratings = self.models[0].all_ratings
        self.losses = []
        self.optimizer = optimizer
        self.epochs = epochs
        self.hypers = hypers if hypers else {}
        self.hypers['aggregate_index'] = self.all_ratings.aggregate_index
        self.batch_params = batch_params if batch_params else {}
        self.callback = None

        # creating the optimized tf loss function
        assert len(self.all_ratings.model.variables) == 1, "Only support 1-variable models!"
        self.loss_fcn = self.build_loss_fcn(**self.hypers)

        self.minibatch = None

    def __call__(self, x):
        """Return predictions for the s_qv."""
        ids = self.all_ratings.get_internal_ids(
            x, experts=[self.all_ratings.COMMON_EXPERT] * len(x))
        result = self.all_ratings.model.predict(np.array(ids, dtype=np.int64))
        return result

    def loss_fcn_kwargs(self, **kwargs):
        """Get keyword arguments for the loss_fcn function."""
        kwargs_subset = {'model_tensor', 'aggregate_index', 'lambda_', 'mu', 'C',
                         'default_score_value'}
        if 'ignore_vals' in kwargs:
            kwargs_subset = kwargs_subset.difference(kwargs['ignore_vals'])
        kwargs_subset_dict = {}
        for k in kwargs_subset.intersection(kwargs.keys()):
            val = kwargs[k]
            if isinstance(val, int):
                val = tf.constant(val, dtype=tf.int64)
            elif isinstance(val, float):
                val = tf.constant(val, dtype=tf.float32)
            kwargs_subset_dict[k] = val

        return kwargs_subset_dict

    def build_loss_fcn(self, **kwargs):
        """Create the loss function."""
        kwargs0 = self.loss_fcn_kwargs(**kwargs)

        def fcn(**kwargs1):
            if 'model_tensor' not in kwargs0:
                kwargs0['model_tensor'] = self.all_ratings.model.variables[0]
            return loss_fcn(**kwargs0, **kwargs1)

        return fcn

    def save(self, directory):
        self.all_ratings.save(directory)

    def load(self, directory):
        try:
            result = self.all_ratings.load(directory)
        except FileNotFoundError as e:
            logging.warning(f"No model restore data {e}")
            result = {'status': str(e)}
        return result

    def plot_loss(self, *args, **kwargs):
        """Plot the losses."""
        losses = arr_of_dicts_to_dict_of_arrays(self.losses)

        plt.figure(figsize=(15, 10))
        plot_h = len(losses)

        for i, key in enumerate(losses.keys(), 1):
            plt.subplot(1, plot_h, i)
            plt.title(key)
            plt.plot(losses[key])

    def fit(self, epochs=None):
        """Fit with multiple epochs."""
        if epochs is None:
            epochs = self.epochs
        with tqdm(total=epochs) as pbar:
            for i in range(epochs):
                if i % self.hypers.get('sample_every', 1) == 0:
                    self.minibatch = self.sample_minibatch(**self.batch_params)

                losses = self.fit_step()
                self.losses.append(losses)
                pbar.update(1)
                pbar.set_postfix(**losses)  # loss=losses['loss'])
                if callable(self.callback):
                    self.callback(self, epoch=i, **losses)
        if self.losses:
            return self.losses[-1]
        else:
            return {}

    def sample_minibatch(
            self,
            sample_experts=50,
            sample_ratings_per_expert=50,
            sample_objects_per_expert=50):
        """Get one mini-batch.

        Args:
            sample_experts: number of experts to sample at each mini-batch
                for RATINGS/REGULARIZATION
            sample_ratings_per_expert: number of ratings to sample at each mini-batch for RATINGS
            sample_objects_per_expert: number of objects to sample at each mini-batch
                for REGULARIZATION

        Returns:
            dict with tensors
        """
        # sampled mini-batch
        experts_rating, objects_rating_v1, objects_rating_v2, cmp, weights = [], [], [], [], []
        experts_all, objects_all, num_ratings_all = [], [], []
        # sampled_objects = []

        # sampling the mini-batch: ratings
        # ignoring the common expert here
        experts_to_sample = self.all_ratings.experts[:-1]
        sampled_experts = choice_or_all(experts_to_sample, sample_experts)

        # print("EXPERTS", experts_all, sampled_experts)

        for expert in sampled_experts:
            expert_id = self.all_ratings.experts_reverse[expert]
            # print("EXPERT", expert, self.models)
            sampled_ratings = choice_or_all(
                self.models[expert_id].ratings,
                sample_ratings_per_expert)
            for rating in sampled_ratings:
                # format: ({'o1': o1, 'o2': o2, 'ratings': p1_vs_p2, 'weights': weights})

                experts_rating.append(expert_id)
                objects_rating_v1.append(
                    self.all_ratings.objects_reverse[rating['o1']])
                objects_rating_v2.append(
                    self.all_ratings.objects_reverse[rating['o2']])
                cmp.append(rating['ratings'])
                weights.append(rating['weights'])

        # sampling the mini-batch: regularization
        sampled_objects = choice_or_all(
            self.all_ratings.objects,
            sample_objects_per_expert)

        # print("EXPERTS", experts_all, sampled_experts)

        if hasattr(self, 'certification_status') and len(
                self.certification_status) == len(experts_to_sample):
            certified_experts = [x for i, x in enumerate(
                experts_to_sample) if self.certification_status[i]]
        else:
            logging.warning("List of certified experts not found")
            certified_experts = experts_to_sample

        sampled_certified_experts = choice_or_all(
            certified_experts, sample_experts)

        # print("SAMPLED CERTIFIED", sampled_certified_experts)

        for expert in sampled_certified_experts:
            # print(expert, self.all_ratings.experts_reverse)

            expert_id = self.all_ratings.experts_reverse[expert]
            for obj in sampled_objects:
                object_id = self.all_ratings.objects_reverse[obj]
                experts_all.append(expert_id)
                objects_all.append(object_id)
                num_ratings_all.append(
                    self.models[expert_id].ratings_with_object(obj))

        # videos to plug into the "common_to_1" loss term
        sampled_object_ids = [self.all_ratings.objects_reverse[obj]
                              for obj in sampled_objects]

        # total number of ratings
        # total_ratings = sum([len(m.ratings) for m in self.models])

        if not experts_rating:
            logging.warning("No data to train.")
            return {}

        kwargs = {
            'experts_rating': np.array(experts_rating, dtype=np.int64),
            'objects_rating_v1': np.array(objects_rating_v1, dtype=np.int64),
            'objects_rating_v2': np.array(objects_rating_v2, dtype=np.int64),
            'cmp': np.array(cmp, dtype=np.float32),
            'weights': np.array(weights, dtype=np.float32),
            'experts_all': np.array(experts_all, dtype=np.int64),
            'objects_all': np.array(objects_all, dtype=np.int64),
            'num_ratings_all': np.array(num_ratings_all, dtype=np.float32),
            'objects_common_to_1': np.array(sampled_object_ids, dtype=np.int64)
        }

        kwargs = convert_to_tf(kwargs)

        # print(kwargs)

        return kwargs

    def fit_step(self):
        """Fit using the custom magic loss...

        Returns:
            dict of losses (numpy)
        """
        optimizer = self.optimizer
        minibatch = self.minibatch

        if not minibatch:
            return {}

        # computing the custom loss
        with tf.GradientTape() as tape:
            losses = self.loss_fcn(**minibatch)

        # doing optimization (1 step)
        all_variables = self.all_ratings.model.variables
        grads = tape.gradient(losses['loss'], all_variables,
                              unconnected_gradients=tf.UnconnectedGradients.ZERO)

        def transform_grad(g):
            """Replace nan with 0."""
            return tf.raw_ops.Select(condition=tf.math.is_finite(g), x=g, y=tf.zeros_like(g))

        grads = [transform_grad(g) for g in grads]

        optimizer.apply_gradients(zip(grads, all_variables))

        out = {}
        out.update(losses)
        out.update({f"grad{i}": tf.linalg.norm(g)
                    for i, g in enumerate(grads)})

        # returning original losses
        return {x: y.numpy() for x, y, in out.items()}
