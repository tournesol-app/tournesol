import tensorflow as tf
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
        assert all([isinstance(x, tuple) for x in indices_list]), \
          "all items in indices_list must be tuples"
          
        # checking tuple length
        assert [len(shape) == len(idx) for idx in indices_list], "All tuple lengths must be equal"
        
        self.num_items = len(indices_list)
        # tf.sparse.SparseTensor didn't work with GradientTape, so using own implementation
        self.v = self.add_weight(shape=(self.num_items,), initializer=initializer,
                                 trainable=True, name="var_sparse_values/" + name,
                                 dtype=tf.keras.backend.floatx())
        self.idx = HashMap()
        
        # storing indices
        # TODO: use vectorized implementation
        for i, idx in enumerate(indices_list):
            self.idx.set(i, idx)


    def call(self, inputs, **kwargs):
        # print("INPUT SHAPE", inputs.shape, "WEIGHT SHAPE", self.v.shape)
        
        indices_flat = self.idx.get_keys(inputs)
        return tf.gather(self.v, indices_flat)


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
        **kwargs):
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

    # 2D array (comparison_id, feature) -> float
    theta_eqv = tf.gather(model_tensor, expert_object_feature_v1_flat)
    theta_eqw = tf.gather(model_tensor, expert_object_feature_v2_flat)

    # FIT LOSS SUM
    theta_vw = theta_eqv - theta_eqw
    # print(theta_vw.shape, cmp.shape)
    theta_vw_y = tf.math.multiply(theta_vw, cmp_flat)
    sp = tf.math.softplus(theta_vw_y)
    sp_weighted = tf.math.multiply(sp, weights_flat)

    sp_weighted_flat = tf.reshape(sp_weighted, (-1,))
    sp_weighted_no_nan = tf.boolean_mask(sp_weighted_flat,
                                         tf.math.is_finite(sp_weighted_flat))
    # tf.print("original tensor")
    # tf.print(sp_weighted_flat)

    # tf.print("nonan tensor")
    # tf.print(sp_weighted_no_nan)

    result['loss_fit'] = tf.reduce_sum(sp_weighted_no_nan)

    # LOSS MODEL TO COMMON

    # 2D array (regul_id, feature) -> float
    theta_eqv_common = tf.gather(model_tensor, expert_object_feature_all)
    s_qv = tf.gather(model_tensor, expert_object_feature_agg_all)

    # print("IDX", idx_common.shape, s_qv.shape)

    # coefficient, shape: regul_id
    num_float = tf.cast(num_ratings_all_flat, tf.keras.backend.floatx())
    coef_yev = tf.divide(num_float, C + num_float)
    # print(theta_eqv_common.shape, s_qv.shape)
    # tf.print('thetacomm', theta_eqv_common)
    # tf.print("sqv", s_qv)
    theta_s = tf.abs(theta_eqv_common - s_qv)

    # print("THETAS", theta_s.shape, "COEF", coef_yev.shape, \
    # "COEFR", coef_yev_repeated.shape)
    # tf.print("thetas", theta_s)
    # tf.print("coefyev", coef_yev_repeated)
    theta_s_withcoeff = tf.multiply(theta_s, coef_yev)
    result['loss_m_to_common'] = tf.reduce_sum(
        theta_s_withcoeff) * lambda_

    # LOSS COMMON TO 0
    s_qv_common_to_1 = tf.gather(model_tensor, expert_object_feature_common_to_1)

    sm1 = tf.math.square(s_qv_common_to_1 - default_score_value)

    # print(idx_common_to_1, s_qv_common_to_1, sm1)

    result['loss_common_to_1'] = tf.reduce_sum(sm1) * mu

    # TOTAL LOSS
    result['loss'] = result['loss_fit'] + result['loss_m_to_common'] + result[
        'loss_common_to_1']

    return result
