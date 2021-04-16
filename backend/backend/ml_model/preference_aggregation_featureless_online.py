import logging
from copy import deepcopy

import gin
import numpy as np
from backend.rating_fields import MAX_VALUE
from matplotlib import pyplot as plt
from scipy.optimize import golden

from .preference_aggregation_featureless_np import loss_fcn_np


@gin.configurable
class FeaturelessOnlineUpdater(object):
    """Update weights online."""

    def __init__(self, hypers=None, golden_params=None):
        if golden_params is None:
            golden_params = {}
        self.golden_params = golden_params
        self.hypers = hypers
        self.model_tensor = None
        self.minibatch = None
        self.to_subtract = {}
        self.silent = False

    def current_loss(self, key='loss'):
        return self.get_closure_loss((0, 0, 0), key=key)(None)

    def set_subtract(self, key='loss'):
        self.to_subtract = self.current_loss(key=key)['metrics']

    def set_minibatch(self, mb):
        for key, val in mb.items():
            assert isinstance(key, str), key
            assert isinstance(val, np.ndarray), val
        self.minibatch = mb

    def set_model_tensor(self, mt):
        assert isinstance(mt, np.ndarray), mt
        self.model_tensor = mt

    def get_value(self, indices):
        """Get one from the tensor."""
        assert len(indices) == 3, indices
        if self.model_tensor is None:
            raise ValueError("Please set the tensor")
        return self.model_tensor[indices[0], indices[1], indices[2]]

    def set_value(self, indices, val):
        """Set value to the tensor."""
        assert len(indices) == 3, indices
        if self.model_tensor is None:
            raise ValueError("Please set the tensor")
        self.model_tensor[indices[0], indices[1], indices[2]] = val
        return val

    def get_closure_loss(self, indices, key='loss'):
        """Return a function that computes the loss given model_tensor[indices]."""

        def f(x=None, self=self, indices=indices[:], key=str(key)):
            if self.minibatch is None:
                raise ValueError("Please set the minibatch first")
            if self.model_tensor is None:
                raise ValueError("Please set the tensor")
            if self.hypers is None:
                raise ValueError("Please use gin to configure hyperparameters")

            if x is not None:
                self.set_value(indices=indices, val=x)
            result = loss_fcn_np(model_tensor=self.model_tensor,
                                 **self.hypers, **self.minibatch)
            return {
                'loss': result[key] - self.to_subtract.get(key, 0.0),
                'metrics': {**result, 'param': x}
            }

        return f

    def best_value_many_indices(self, indices_list, **kwargs):
        """Given a list of indices (with possible repeats), run optimization and return stats."""

        indices_list = [tuple(x) for x in indices_list]

        stats = {indices: [] for indices in set(indices_list)}

        for indices in indices_list:
            stats[indices].append(self.best_value_indices(indices=indices, **kwargs))

        return stats

    def best_value_indices(self, indices, key='loss', assign_at_end=False,
                           give_history=True):
        """Given indices, use Golden Ratio search to compute the best model_tensor[indices]."""

        # remember the original value
        orig_value = self.get_value(indices=indices)

        # function to compute the loss
        loss_closure = self.get_closure_loss(indices=indices, key=key)

        orig_loss = loss_closure(orig_value)['loss']

        # history of metrics
        history = []

        def closure_with_history(x, give_history=give_history):
            """Given a value, compute the loss, store the value (optionally) and return by key."""
            result = loss_closure(x)

            if give_history:
                history.append(result['metrics'])

            return result['loss']

        params = {x: y for x, y in self.golden_params.items()}
        if 'smartbracket' in self.golden_params:
            del params['smartbracket']
            params['brack'] = tuple([orig_value + t for t in self.golden_params['smartbracket']])

        # running optimization
        best_value, best_loss, iterations = golden(closure_with_history,
                                                   full_output=True, **params)

        # restoring the value if requested
        if not assign_at_end:
            self.set_value(indices=indices, val=orig_value)
        else:
            if best_loss < orig_loss:
                self.set_value(indices=indices, val=best_value)
            else:
                if not self.silent:
                    logging.warning(f"No improvement {indices} {key} {assign_at_end}")
                self.set_value(indices=indices, val=orig_value)
                best_value = orig_value
                best_loss = orig_loss

        return {
            'assigned': assign_at_end,
            'history': history,
            'orig_value_param': orig_value,
            'best_value': best_value,
            'best_loss': best_loss,
            'iterations': iterations
        }


# Plotting functions
def get_history(result, ind, only_last=True):
    if only_last:
        res = [z['history'][-1] for z in result[ind]]
    else:
        res = [x for z in result[ind] for x in z['history']]
    return res


def visualize_result_loss(result, indices_lst):
    values_byloss = {'loss': []}
    ind_offset = {ind: 0 for ind in set(indices_lst)}

    for ind in indices_lst:
        val = result[ind][ind_offset[ind]]['best_loss']

        ind_offset[ind] += 1

        values_byloss['loss'].append(val)

    #     for key in val:
    #         if key.startswith('loss'):
    #             if key not in values_byloss:
    #                 values_byloss[key] = []
    #             values_byloss[key].append(val[key])

    plt.figure(figsize=(13, 3))
    for i, key in enumerate(sorted(values_byloss.keys()), 1):
        plt.subplot(1, len(values_byloss), i)
        plt.title(key)
        plt.plot(values_byloss[key])
    #     plt.axhline(online.to_subtract[key])
    plt.show()


def visualize_byindex(result, indices_lst, initial_value):
    for ind in set(indices_lst):

        res = get_history(result, ind)

        res_dct = lstdct2dctlst(res)
        plt.figure(figsize=(13, 3))
        for i, key in enumerate(sorted(res_dct.keys()), 1):
            hst = res_dct[key]
            plt.subplot(1, len(res_dct), i)
            plt.title(key + ' ' + str(ind))

            if key in initial_value[ind]['metrics']:
                initial = initial_value[ind]['metrics'][key]
                hst = [initial] + hst
                plt.axhline(initial)

            if np.min(hst) > 0:
                plt.yscale('log')
            plt.plot(hst)

        plt.show()


def lstdct2dctlst(lst):
    """List of dictionaries -> dictionary of lists."""
    keys = lst[0].keys()
    res = {key: [x[key] for x in lst] for key in keys}
    return res


def compute_online_update(rating_value, mb_np_orig,
                          model_tensor_orig,
                          idx_set,
                          users_get_value=None,
                          n_repeats=1,
                          hotfix_update_hypers=None,
                          plot_charts=False,
                          pbars=None,
                          cancel_updates=False,
                          **kwargs):
    """Compute an online update given a pre-computed minibatch of data, and a model tensor.

    Args:
        rating_value: value of the rating in (-1, 1) to set
        mb_np_orig: minibatch for the loss function
        model_tensor_orig: current scores (users + aggregate)
        idx_set: which rating ID in the minibatch to update?
        users_get_value: if pbar is set, this user's comparison will be used
        n_repeats: number of repetitions of the golden ratio search
        hotfix_update_hypers: updates for hyperparameters
        plot_charts: show visualization
        cancel_updates: do a dummy run without optimization (return current values)
        pbars: if not None, set progress bar to the value of comparison (0-100) for user_get_value
        **kwargs: hotfix updates for the golden ratio algorithm

    Returns:
        if pbar is set, returns None (only sets the value of the progress bar)
        otherwise, returns a dictionary with a response.
    """

    # internal object IDs to update
    obj1 = mb_np_orig['objects_rating_v1'][idx_set]
    obj2 = mb_np_orig['objects_rating_v2'][idx_set]

    # copying the minibatch and the model tensor (will be updated)
    mb_np_copy = deepcopy(mb_np_orig)
    model_tensor_copy = deepcopy(model_tensor_orig)

    if not cancel_updates:
        # SETTING THE RATING VALUE
        mb_np_copy['cmp'][idx_set, 0] = rating_value

    # creating the updater
    online = FeaturelessOnlineUpdater()
    online.hypers['aggregate_index'] = -1

    # hotfix parameter updates
    if hotfix_update_hypers is not None:
        for key, value in hotfix_update_hypers.items():
            online.hypers[key] = value

    for key, value in kwargs.items():
        online.golden_params[key] = value

    # setting data
    online.set_minibatch(mb_np_copy)
    online.set_model_tensor(model_tensor_copy)
    online.set_subtract()
    online.silent = True

    # CONFIGURATION FOR INDICES
    indices_lst = []

    for i in range(model_tensor_orig.shape[0]):
        indices_lst.append((i, obj1, 0))
        indices_lst.append((i, obj2, 0))

    indices_lst *= n_repeats

    # initial value for the loss/index
    initial_value = {ind: online.get_closure_loss(ind)(online.get_value(ind)) for ind in
                     set(indices_lst)}

    if not cancel_updates:
        # RUNNING OPTIMIZATION with GOLDEN RATIO
        result = online.best_value_many_indices(indices_lst, assign_at_end=True)

        # plotting
        if plot_charts:
            visualize_result_loss(result, indices_lst)
            visualize_byindex(result, indices_lst, initial_value)
    else:
        result = None

    if pbars is not None:

        if 'comparison' in pbars:
            assert len(users_get_value) == len(pbars['comparison'])

            for user, pbar in zip(users_get_value, pbars['comparison']):
                # obtaining model scores
                score1 = online.get_value((user, obj1, 0))
                score2 = online.get_value((user, obj2, 0))

                # computing the comparison
                comparison = 1 / (1 + np.exp(score1 - score2)) * MAX_VALUE
                pbar.value = comparison

        if 'v1' in pbars:
            assert len(users_get_value) == len(pbars['v1'])
            for user, pbar in zip(users_get_value, pbars['v1']):
                # obtaining model scores
                score1 = online.get_value((user, obj1, 0))
                pbar.value = score1

        if 'v2' in pbars:
            assert len(users_get_value) == len(pbars['v2'])
            for user, pbar in zip(users_get_value, pbars['v2']):
                # obtaining model scores
                score1 = online.get_value((user, obj2, 0))
                pbar.value = score1

        return None
    else:
        return {
            'new_model_tensor': model_tensor_copy,
            'new_minibatch': mb_np_copy,
            'online_learner': online,
            'indices_lst': indices_lst,
            'result': result,
        }
