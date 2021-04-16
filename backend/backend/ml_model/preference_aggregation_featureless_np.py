import numpy as np


def variable_index_layer_call_np(model, idxes1, idxes2):
    """Get values by 2D indices, imitates VariableIndexLayer."""
    return model[idxes1, idxes2]


def loss_fcn_np(
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

    Returns dict of numbers
    """

    result = {}

    # internal indices for experts and objects (ratings)
    #     idx_v1 = torch.stack((experts_rating, objects_rating_v1), dim=1)
    #     idx_v2 = torch.stack((experts_rating, objects_rating_v2), dim=1)

    #     print(idx_v1)

    # 2D array (comparison_id, feature) -> float
    theta_eqv = variable_index_layer_call_np(model_tensor, experts_rating, objects_rating_v1)
    theta_eqw = variable_index_layer_call_np(model_tensor, experts_rating, objects_rating_v2)

    def np_softplus(x):
        return np.log(1 + np.exp(x))

    # FIT LOSS SUM
    theta_vw = theta_eqv - theta_eqw
    # print(theta_vw.shape, cmp.shape)
    theta_vw_y = np.multiply(theta_vw, cmp)
    sp = np_softplus(theta_vw_y)
    sp_weighted = np.multiply(sp, weights)

    sp_weighted_flat = sp_weighted.reshape((-1,))
    sp_weighted_no_nan = sp_weighted_flat[~np.isnan(sp_weighted_flat)]
    # tf.print("original tensor")
    # tf.print(sp_weighted_flat)

    # tf.print("nonan tensor")
    # tf.print(sp_weighted_no_nan)

    result['loss_fit'] = np.sum(sp_weighted_no_nan)

    # LOSS MODEL TO COMMON
    # common expert
    experts_common = np.full(experts_all.shape, aggregate_index, dtype=np.int64)

    # indices for experts for regularization
    #     idx_all = torch.stack((experts_all, objects_all), dim=1)
    #     idx_common = torch.stack((experts_common, objects_all), dim=1)

    # 2D array (regul_id, feature) -> float
    theta_eqv_common = variable_index_layer_call_np(model_tensor, experts_all, objects_all)
    s_qv = variable_index_layer_call_np(model_tensor, experts_common, objects_all)

    # print("IDX", idx_common.shape, s_qv.shape)

    # coefficient, shape: regul_id
    num_float = num_ratings_all.astype(np.float32)
    coef_yev = np.divide(num_float, C + num_float)
    # print(theta_eqv_common.shape, s_qv.shape)
    # tf.print('thetacomm', theta_eqv_common)
    # tf.print("sqv", s_qv)
    theta_s = np.abs(theta_eqv_common - s_qv)
    coef_yev_repeated = np.repeat(np.expand_dims(
        coef_yev,
        axis=1), theta_s.shape[1], axis=1)
    # print("THETAS", theta_s.shape, "COEF", coef_yev.shape, \
    # "COEFR", coef_yev_repeated.shape)
    # tf.print("thetas", theta_s)
    # tf.print("coefyev", coef_yev_repeated)
    theta_s_withcoeff = np.multiply(theta_s, coef_yev_repeated)
    result['loss_m_to_common'] = np.sum(
        theta_s_withcoeff) * lambda_

    # LOSS COMMON TO 0
    experts_common_to_1 = np.full(objects_common_to_1.shape,
                                  aggregate_index, dtype=np.int64)
    #     idx_common_to_1 = torch.stack(
    #         (experts_common_to_1, objects_common_to_1), dim=1)
    s_qv_common_to_1 = variable_index_layer_call_np(model_tensor, experts_common_to_1,
                                                    objects_common_to_1)

    sm1 = np.power(s_qv_common_to_1 - default_score_value, 2.0)

    # print(idx_common_to_1, s_qv_common_to_1, sm1)

    result['loss_common_to_1'] = np.sum(sm1) * mu

    # TOTAL LOSS
    result['loss'] = result['loss_fit'] + result['loss_m_to_common'] + result[
        'loss_common_to_1']

    return result
