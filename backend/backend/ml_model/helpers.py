import tensorflow as tf
import numpy as np
import gin
import logging


# make dicts configurable
gin_dict = gin.external_configurable(dict, name='gin_dict')


@gin.configurable
def choice_or_all(arr, n, replace=False):
    """Select a given number of elements, or all of them if there are not enough."""
    if not arr:
        return arr
    if len(arr) < n:
        if replace:
            logging.info(
                "Warning: not enough data to sample, sampling with replacement.")
            return np.random.choice(arr, n, replace=True)
        else:
            logging.info("Warning: not enough data, returning the whole array")
            return arr
    return np.random.choice(arr, n, replace=False)


def tf_to_numpy(var):
    """Dict/list tf->numpy."""
    if isinstance(var, dict):
        return {x: tf_to_numpy(y) for x, y in var.items()}
    elif isinstance(var, list):
        return [tf_to_numpy(x) for x in var]
    elif isinstance(var, tf.Variable):
        return var.numpy()
    else:
        return var


def numpy_to_tf(var):
    """Dict/list numpy->tf."""
    if isinstance(var, dict):
        return {x: numpy_to_tf(y) for x, y in var.items()}
    elif isinstance(var, list):
        return [numpy_to_tf(x) for x in var]
    elif isinstance(var, np.ndarray):
        return tf.Variable(var)
    else:
        return var


def arr_of_dicts_to_dict_of_arrays(arr):
    """ Array of dicts to dict of arrays """
    all_keys = arr[0].keys()
    return {key: [v[key] for v in arr] for key in all_keys}


def convert_to_tf(kwargs):
    """Convert numpy arrays to tensorflow, caring about the dtype."""
    assert tf.keras.backend.floatx() == 'float32'
    for key in kwargs.keys():
        kwargs[key] = np.array(kwargs[key])
        if kwargs[key].dtype == np.float64:
            kwargs[key] = np.array(kwargs[key], dtype=np.float32)
        kwargs[key] = tf.constant(kwargs[key])
    return kwargs


@tf.function(experimental_relax_shapes=True)
def nan_to_zero(g):
    """Replace nan with 0."""
    idx_non_finite = tf.where(~tf.math.is_finite(g))
    zeros = tf.zeros(len(idx_non_finite), dtype=g.dtype)
    return tf.tensor_scatter_nd_update(g, idx_non_finite, zeros)

