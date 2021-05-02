import tensorflow as tf
import gin


def variable_index_layer_call(tensor, inputs):
    """Get variable at indices."""
    return tf.gather_nd(tensor, inputs)


@gin.configurable
class VariableIndexLayer(tf.keras.layers.Layer):
    """Layer which outputs a trainable variable on a call."""

    NEED_INDICES = False

    def __init__(self, shape, name="index_layer", initializer=None, **kwargs):
        super(VariableIndexLayer, self).__init__(name=name)
        self.v = self.add_weight(
            shape=shape, initializer=initializer,
            trainable=True, name="var/" + name,
            dtype=tf.keras.backend.floatx())

    def serialize(self):
        return {'v': self.v.numpy(), 'NEED_INDICES': self.NEED_INDICES}

    @tf.function
    def call(self, inputs, **kwargs):
        # print("INPUT SHAPE", inputs.shape, "WEIGHT SHAPE", self.v.shape)

        out = variable_index_layer_call(self.v, inputs)
        # print("INPUT SHAPE", inputs.shape, "WEIGHT SHAPE", self.v.shape, "OUT SHAPE", out.shape)
        return out


# get the loss function for this class
@gin.configurable
@tf.function(experimental_relax_shapes=True)
def loss_fcn_dense(
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
        default_score_value=None,
        **kwargs):
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
    loss = loss_fcn_dense(**kwargs)['loss']
    g = tf.gradients(loss, variable)[0]
    g = tf.gather(g, axis=1, indices=video_indices)
    h = tf.hessians(loss, variable)[0]
    h = tf.gather(h, axis=1, indices=video_indices)
    h = tf.gather(h, axis=4, indices=video_indices)
    return {'loss': loss, 'gradient': g, 'hessian': h}
