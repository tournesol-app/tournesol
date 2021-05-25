import tensorflow as tf
import numpy as np
import gin


class HashMap(object):
    """Maps objects from keys to values and vice-versa."""

    def __init__(self):
        self.key_to_value = {}
        self.value_to_key = {}

    def set(self, key, value):
        self.key_to_value[key] = value
        self.value_to_key[value] = key

    def get_value(self, key):
        return self.key_to_value[key]

    def get_key(self, value):
        if value not in self.value_to_key:
            raise KeyError(f"{value} not found in all {len(self.value_to_key)} entries")
        return self.value_to_key[value]

    def get_keys(self, values):
        """Get multiple keys given values. Can be parallelized!"""
        return [self.get_key(value) for value in values]


@gin.configurable
class SparseVariableIndexLayer(tf.keras.layers.Layer):
    """Layer which outputs a trainable variable on a call, sparse storage."""

    NEED_INDICES = True

    def __init__(self, shape, indices_list, name="index_layer", initializer=None):
        super(SparseVariableIndexLayer, self).__init__(name=name)

        assert isinstance(indices_list, list), "indices_list must be a list"
        assert indices_list, "List of indices must be non-empty!"
        assert all(
            [isinstance(x, tuple) for x in indices_list]
        ), "all items in indices_list must be tuples"

        # checking tuple length
        assert [
            len(shape) == len(idx) for idx in indices_list
        ], "All tuple lengths must be equal"

        self.num_items = len(indices_list)
        # tf.sparse.SparseTensor didn't work with GradientTape, so using own implementation
        self.v = self.add_weight(
            shape=(self.num_items,),
            initializer=initializer,
            trainable=True,
            name="var_sparse_values/" + name,
            dtype=tf.keras.backend.floatx(),
        )
        self.idx = HashMap()
        self.indices_list = indices_list
        self.indices_set = set(indices_list)

        assert len(self.indices_list) == len(self.indices_set), "Indices must be unique"

        # storing indices
        # TODO: use vectorized implementation
        for i, idx in enumerate(indices_list):
            self.idx.set(i, idx)

    def serialize(self):
        return {"v": self.v.numpy(), "NEED_INDICES": self.NEED_INDICES, "idx": self.idx}

    def call(self, inputs, **kwargs):
        # print("INPUT SHAPE", inputs.shape, "WEIGHT SHAPE", self.v.shape)

        indices_flat = self.idx.get_keys(inputs)
        return tf.gather(self.v, indices_flat)


@tf.function(experimental_relax_shapes=True)
def sinh_loss(x, threshold=1e-1, threshold_high=10.0, eps=1e-6):
    """First term of the new learning function: ln(2sinhx/x). See #88."""

    # the function is even
    x_abs = tf.abs(x)

    # three options require different ranges for x
    # so that there are no overflows
    x_small = tf.clip_by_value(x_abs,
                               clip_value_min=0,
                               clip_value_max=threshold)

    x_normal = tf.clip_by_value(x_abs,
                                clip_value_min=threshold,
                                clip_value_max=threshold_high)

    x_large = tf.clip_by_value(x_abs,
                               clip_value_min=threshold_high,
                               clip_value_max=np.inf)

    # Taylor expansion
    option_close_to_0 = tf.math.pow(x_small, 2) / 6.0 + tf.math.log(2.0)

    # original loss
    option_far_from_0 = tf.math.log(2 * tf.math.sinh(x_normal) / x_normal)

    # the function has an asymptote y~x+...
    option_infty = - tf.math.log(x_large) + x_large

    # Taylor or original?
    condition_close_to_0 = tf.abs(x) < threshold

    # original vs infty
    condition_infty = tf.abs(x) >= threshold_high

    # Taylor or original?
    result = tf.where(condition=condition_close_to_0,
                      x=option_close_to_0,
                      y=option_far_from_0)

    # original/Taylor VS infty
    result = tf.where(condition=condition_infty,
                      x=option_infty,
                      y=result)

    return result


# get the loss function for this class
@gin.configurable
@tf.function(experimental_relax_shapes=True)
def loss_fcn_sparse(
    # RATINGS
    expert_object_feature_v1_flat=None,
    expert_object_feature_v2_flat=None,
    cmp_flat=None,
    weights_flat=None,
    # Regularization: expert to common
    expert_object_feature_all=None,
    expert_object_feature_agg_all=None,
    num_ratings_all_flat=None,
    # Regularization: common to 1
    expert_object_feature_common_to_1=None,
    # trainable
    model_tensor=None,
    # hyperparameters
    lambda_=None,
    mu=None,
    C=None,
    default_score_value=None,
    **kwargs,
):
    """
    Compute the loss function. All IDs are internal (int64).

    See https://www.overleaf.com/project/5f44dd8e84c8540001bf1552
    Equations 1-2-3

    Args:
        expert_object_feature_v1_flat: 1D tensor with IDs inside model_tensor (LEFT video)
        expert_object_feature_v2_flat: 1D tensor with IDs inside model_tensor (RIGHT video),
            same length as expert_object_feature_v1_flat
        cmp_flat: 1D tensor with comparisons, same length as expert_object_feature_v1_flat
        weights_flat: 1D tensor same length as expert_object_feature_v1_flat

        expert_object_feature_all: 1D tensor with expert IDs inside model_tensor, INDIV. expert
            for regularization (model to common)
        expert_object_feature_agg_all: 1D tensor with expert IDs inside model_tensor, AGGR. expert
            for regularization (model to common)
        num_ratings_all_flat: 1D tensor with number of ratings for expert/object/feature in
            expert_object_feature_all, same length as expert_object_feature_all

        expert_object_feature_common_to_1: 1D tensor with object IDs inside model_tensor
            for the common-to-1 loss.

    Returns dict of Tensorflow tensors with the total loss and components
    """

    result = {}

    # TERM 1/3: 'loss_fit' obtains scores from pairwise comparisons
    # 2D array (comparison_id, feature) -> float
    theta_eqv = tf.gather(model_tensor, expert_object_feature_v1_flat)
    theta_eqw = tf.gather(model_tensor, expert_object_feature_v2_flat)

    # difference between scores of left and right videos
    #  (theta_left - theta_right)
    theta_vw = theta_eqv - theta_eqw
    theta_vw_y = tf.math.multiply(theta_vw, cmp_flat)

    # old learning function (softplus), see #88
    sp = tf.math.softplus(theta_vw_y)

    # new learning function with sinh, see #88
    # disabled until issues are resolved by Le
    # TODO: enable this line and comment out the previous one
    # when the loss is ready...
    # sp = sinh_loss(theta_vw) + theta_vw_y

    # multiply by comparison weights and flatten
    sp_weighted = tf.math.multiply(sp, weights_flat)
    sp_weighted_flat = tf.reshape(sp_weighted, (-1,))

    # some ratings might have nan as values, removing those
    sp_weighted_no_nan = tf.boolean_mask(
        sp_weighted_flat, tf.math.is_finite(sp_weighted_flat)
    )

    # storing the result
    result["loss_fit"] = tf.reduce_sum(sp_weighted_no_nan)

    # TERM 2/3: 'loss_m_to_common' brings individual scores close to
    #  the aggregated ones

    # 2D array (regul_id, feature) -> float
    theta_eqv_common = tf.gather(model_tensor, expert_object_feature_all)
    s_qv = tf.gather(model_tensor, expert_object_feature_agg_all)

    # coefficient, shape: regul_id
    num_float = tf.cast(num_ratings_all_flat, tf.keras.backend.floatx())
    coef_yev = tf.divide(num_float, C + num_float)

    # l1 term: aggregated - individual
    theta_s = tf.abs(theta_eqv_common - s_qv)

    # weighting the l1 term with the coefficient
    theta_s_withcoeff = tf.multiply(theta_s, coef_yev)

    # storing the result
    result["loss_m_to_common"] = tf.reduce_sum(theta_s_withcoeff) * lambda_

    # TERM 3/3: 'loss_common_to_1' brings aggregated scores close to 1
    #  (=default_score_value)
    s_qv_common_to_1 = tf.gather(model_tensor, expert_object_feature_common_to_1)

    # squared distance between scores and 1
    sm1 = tf.math.square(s_qv_common_to_1 - default_score_value)

    # storing the result
    result["loss_common_to_1"] = tf.reduce_sum(sm1) * mu

    # TOTAL LOSS
    result["loss"] = (
        result["loss_fit"] + result["loss_m_to_common"] + result["loss_common_to_1"]
    )

    return result
