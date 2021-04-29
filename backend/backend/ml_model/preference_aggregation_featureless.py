import logging
import os
import pickle

import gin
import numpy as np
import tensorflow as tf
from backend.ml_model.helpers import choice_or_all, arr_of_dicts_to_dict_of_arrays, convert_to_tf
from backend.ml_model.preference_aggregation import PreferencePredictor, MedianPreferenceAggregator
from matplotlib import pyplot as plt
from tqdm.auto import tqdm
from backend.ml_model.preference_aggregation import print_memory, tqdmem

tf.compat.v1.enable_eager_execution()

Adam = gin.external_configurable(tf.keras.optimizers.Adam)
SGD = gin.external_configurable(tf.keras.optimizers.SGD)
Zeros = gin.external_configurable(tf.keras.initializers.Zeros)

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
            default_rating=None,
            var_init_cls=None):

        print_memory('ARWC:init')

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
        self.layer = None
        self.var_init_cls = var_init_cls
        self.indices_list = []
        self.variables = []
        self.expert_id_to_used_videos = {}
        self.default_rating = default_rating

        self.reset_model()
        
    def add_indices(self, indices):
        self.indices_list += indices

    def reset_model(self):
        if self.var_init_cls.NEED_INDICES and not self.indices_list:
            logging.warning("Variable needs indices, and they are not yet available. Skip init...")
            return
        
        logging.warning("Indices: %d" % len(self.indices_list))
        
        self.layer = self.var_init_cls(
            shape=(len(self.experts), len(self.objects), self.output_dim),
            indices_list=self.indices_list)
        self.variables = [self.layer.v]
        # print(self.output_dim)
        
        class adhoc_model():
            def __init__(self1, layer):
                self1.layer = layer
                assert self1.layer.NEED_INDICES, "Dense implementation not supported"
            def __call__(self1, inp):
#                logging.warning('pred_start')
                if not len(inp):
                    return []
                
                output = np.full(fill_value=self.default_rating,
                                 shape=(len(inp), self.output_dim))
                indices_write = []
                values_write = []
                
                indices_read = []
                
                for input_id, (expert_id, object_id) in enumerate(inp):
                    for feature_id in range(self.output_dim):
                        idx = (expert_id, object_id, feature_id)
                        if idx in self.layer.indices_set:
                            idx_flat = self.layer.idx.value_to_key[idx]
                            indices_read.append(idx_flat)
                            indices_write.append((input_id, feature_id))

#                logging.warning('pred_loop_finished')

                if not len(indices_write):
                    return output
                            
                values_write = self.layer.v.numpy()[indices_read]
                
#                logging.warning('pred_values_obtained')
                
#                print(output, values_write, indices_write)
                
                # https://stackoverflow.com/questions/47015578/numpy-assigning-values-to-2d-array-with-list-of-indices
                output[tuple(np.array(indices_write).T)] = values_write
                
#                logging.warning('Prediction end')
                
                return output
                
        self.model = adhoc_model(self.layer)

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
            'layer': self.layer.serialize(),
            'data': self.layer.v.numpy(),
            'features': self.output_features,
            'type': 'sparse' if self.layer.NEED_INDICES else 'dense'
        }
        path = self._save_path(directory=directory)
        pickle.dump(result, open(path, 'wb'))

    def load(self, directory):
        """Load weights."""

        # print("Load weights")

        print_memory('ARWC:load_start')

        path = self._save_path(directory=directory)
        result = pickle.load(open(path, 'rb'))

        print_memory('ARWC:pickle_loaded')

        # setting zero weights
        self.reset_model()

        print_memory('ARWC:model_reset_loaded')

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

        
        print_memory('ARWC:old_indices_loaded')
        # print("experts", len(self.experts), "objects", len(self.objects),
        #       "features", len(self.output_features))

        to_assign_idx = []
        to_assign_vals = []
        
        print_memory('ARWC:start_assign_append_loop')

        if 'type' not in result:
            logging.warning("Old checkpoint (without 'type') is found and not loaded.")
            return {}
        
        def get_old_data(expert_id, object_id, feature_id):            
            if result['type'] == 'dense':
                return result['data'][expert_id, object_id, feature_id]
            elif result['type'] == 'sparse':
                layer = result['layer']
                idx = layer['idx'].get_key((expert_id, object_id, feature_id))
                return result['data'][idx]
            else:
                raise NotImplementedError
            

        for new_expert_idx, expert in enumerate(tqdmem(self.experts, desc="rating_load_expert_loop",
                                             leave=True)):
            old_expert_idx = old_expert_indices.get(expert, None)
            for new_obj_idx, obj in enumerate(tqdmem(self.objects, desc="rating_load_object_loop",
                                              leave=False, disable=True)):
                old_obj_idx = old_object_indices.get(obj, None)
                for new_f_idx, feature in enumerate(self.output_features):
                    old_f_idx = old_feature_indices.get(feature, None)

                    if all([x is not None for x in [old_expert_idx, old_obj_idx, old_f_idx]]):
                        val = get_old_data(old_expert_idx, old_obj_idx, old_f_idx)

                        if not np.isnan(val):
                            to_assign_idx.append((new_expert_idx, new_obj_idx, new_f_idx))
                            to_assign_vals.append(val)
                            restored_items += 1
                            
        print_memory('ARWC:finish_assign_append_loop')

        if to_assign_idx:
            print_memory('ARWC:start_create_layer_variable')
            
            if result['type'] == 'dense':            
                self.layer.v = tf.Variable(
                    tf.tensor_scatter_nd_update(self.layer.v,
                                                to_assign_idx,
                                                to_assign_vals),
                    trainable=True)
            elif result['type'] == 'sparse':
                to_assign_idx_flat = self.layer.idx.get_keys(to_assign_idx)
                
                self.layer.v = tf.Variable(
                    tf.tensor_scatter_nd_update(self.layer.v,
                                                to_assign_idx_flat,
                                                to_assign_vals),
                    trainable=True)
            else:
                raise NotImplementedError
                
            print_memory('ARWC:finish_create_layer_variable')

        # print(to_assign_idx, to_assign_vals)
        # print(self.layer.v)
        
        print_memory('ARWC:alive')

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
        self.used_object_feature_ids = set()
        assert expert in self.all_ratings.experts
        
        if expert == self.all_ratings.COMMON_EXPERT:
            print("Common expert has FPLM")
        
        self.expert = expert
        self.expert_id = self.all_ratings.experts_reverse[expert]
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
        result = self.all_ratings.model(
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

        # indices for features that are used
        used_feature_indices = [i for i, w in enumerate(weights) if not np.allclose(w, 0)]
        
        for f_idx in used_feature_indices:
            self.used_object_feature_ids.add((self.all_ratings.objects_reverse[o1], f_idx))
            self.used_object_feature_ids.add((self.all_ratings.objects_reverse[o2], f_idx))

        self.ratings.append({'o1': o1, 'o2': o2,
                             'ratings': 2 * (np.array(p1_vs_p2) - 0.5),
                             'weights': weights})
            
    def on_dataset_end(self):
        #print("Expert ID", self.expert_id)
        #print("Used objects", self.used_object_feature_ids)
        
        if self.expert_id == self.all_ratings.aggregate_index:
            # common model
            indices = [(self.expert_id, obj_id, feature_id)
                       for obj_id in self.all_ratings.objects_reverse.values()
                       for feature_id in range(self.all_ratings.output_dim)]
        else:
            # individual model, order is fixed here
            indices = [(self.expert_id, obj_id, feature_id)
                       for obj_id, feature_id in self.used_object_feature_ids]
        
        #print("Appending indices", indices)
        
        self.all_ratings.add_indices(indices)
        
        self.all_ratings.expert_id_to_used_videos[self.expert_id] = set(
                [obj_id for obj_id, _ in self.used_object_feature_ids])




@tf.function(experimental_relax_shapes=True)
def transform_grad(g):
    """Replace nan with 0."""
    idx_non_finite = tf.where(~tf.math.is_finite(g))
    zeros = tf.zeros(len(idx_non_finite), dtype=g.dtype)
    return tf.tensor_scatter_nd_update(g, idx_non_finite, zeros)


@gin.configurable
class FeaturelessMedianPreferenceAverageRegularizationAggregator(MedianPreferenceAggregator):
    """Aggregate with median, train with an average set of parameters."""

    def __init__(
            self,
            models,
            epochs=20,
            optimizer=Adam(),
            hypers=None,
            callback=None,
            loss_fcn=None,
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
        self.callback = callback
        self.last_mb_np = None

        # creating the optimized tf loss function
        assert len(self.all_ratings.variables) == 1, "Only support 1-variable models!"
        
        # arg loss_fcn -- the TF callable
        # build_loss_fcn assigns the model_tensor to it
        self.loss_fcn = self.build_loss_fcn(**self.hypers, loss_fcn=loss_fcn)

        self.minibatch = None

    def __call__(self, x):
        """Return predictions for the s_qv."""
        ids = self.all_ratings.get_internal_ids(
            x, experts=[self.all_ratings.COMMON_EXPERT] * len(x))
        result = self.all_ratings.model(np.array(ids, dtype=np.int64))
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

    def build_loss_fcn(self, loss_fcn=None, **kwargs):
        """Create the loss function."""
        kwargs0 = self.loss_fcn_kwargs(**kwargs)

        def fcn(**kwargs1):
            if 'model_tensor' not in kwargs0:
                kwargs0['model_tensor'] = self.all_ratings.variables[0]
            return loss_fcn(**kwargs0, **kwargs1)

        return fcn

    def save(self, directory):
        self.all_ratings.save(directory)

    def load(self, directory):
        try:
            print_memory('FMPARA:pre_rating_load')
            result = self.all_ratings.load(directory)
            print_memory('FMPARA:post_rating_load')
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

    def fit(self, epochs=None, callback=None):
        """Fit with multiple epochs."""
        if epochs is None:
            epochs = self.epochs
        if callback is None:
            callback = self.callback
        with tqdmem(total=epochs, desc="fit_loop") as pbar:
            for i in range(epochs):
                if i % self.hypers.get('sample_every', 1) == 0:
                    self.minibatch = self.sample_minibatch(**self.batch_params)

                losses = self.fit_step()
                self.losses.append(losses)
                pbar.set_postfix(**losses)  # loss=losses['loss']
                pbar.update(1)
                if callable(callback):
                    callback(self, epoch=i, **losses)
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

#        print("OBJECTS", sampled_objects)

        if hasattr(self, 'certification_status') and len(
                self.certification_status) == len(experts_to_sample):
            certified_experts = [x for i, x in enumerate(
                experts_to_sample) if self.certification_status[i]]
            if not certified_experts:
                logging.warning("List of certified experts found but empty")
#            else:
#                logging.warning("List of certified experts non-empty!")
        else:
            logging.warning("List of certified experts not found")
            certified_experts = experts_to_sample

        sampled_certified_experts = choice_or_all(
            certified_experts, sample_experts)

#        print("SAMPLED CERTIFIED", sampled_certified_experts)

        for expert in sampled_certified_experts:
            # print(expert, self.all_ratings.experts_reverse)

            expert_id = self.all_ratings.experts_reverse[expert]
            for obj in sampled_objects:
                object_id = self.all_ratings.objects_reverse[obj]
                
#                print(expert, "USEDV", self.all_ratings.expert_id_to_used_videos[expert_id])
                if object_id not in self.all_ratings.expert_id_to_used_videos[expert_id]:
                    continue
                
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
        
#        print('variable', self.all_ratings.layer.v)
        
        # adding parameters for the sparse tensor, if required
        if self.all_ratings.layer.NEED_INDICES:
            # A to add: expert_object_feature_v1_flat, expert_object_feature_v2_flat, cmp_flat
            #  weights_flat
            # B expert_object_feature_all, expert_object_feature_agg_all, num_ratings_all_flat
            # C expert_object_feature_common_to_1
            
            # filling in A (fit loss)
            expert_object_feature_v1_flat = []
            expert_object_feature_v2_flat = []
            cmp_flat = []
            weights_flat = []
            for c_expert, c_v1, c_v2, c_cmp, c_weights in zip(kwargs['experts_rating'],
                                                              kwargs['objects_rating_v1'],
                                                              kwargs['objects_rating_v2'],
                                                              kwargs['cmp'],
                                                              kwargs['weights']):
                for feature_index, weight in enumerate(c_weights):
                    # weight is 0 -> rating does not have any effect
#                    print('feature index', feature_index, weight, c_cmp[feature_index])
                    if np.allclose(weight, 0):
#                        print("dropping feature")
                        continue
                    
                    expert_object_feature_v1_flat.append((c_expert, c_v1, feature_index))
                    expert_object_feature_v2_flat.append((c_expert, c_v2, feature_index))
                    cmp_flat.append(c_cmp[feature_index])
                    weights_flat.append(weight)
                    
            def arr_to_index_np(arr):
                """Array of tuples -> int64 np array with indices."""
                idxes = self.all_ratings.layer.idx.get_keys(arr)
                return np.array(idxes, dtype=np.int64)
                    
            kwargs['expert_object_feature_v1_flat'] = arr_to_index_np(
                    expert_object_feature_v1_flat)
            
            kwargs['expert_object_feature_v2_flat'] = arr_to_index_np(
                    expert_object_feature_v2_flat)
            
            kwargs['cmp_flat'] = np.array(cmp_flat, dtype=np.float32)
            kwargs['weights_flat'] = np.array(weights_flat, dtype=np.float32)
            
            # filling in B (model to common)
            expert_object_feature_all = []
            expert_object_feature_agg_all = []
            num_ratings_all_flat = []
            for c_expert, c_object, c_num_ratings in zip(kwargs['experts_all'],
                                                         kwargs['objects_all'],
                                                         kwargs['num_ratings_all']):
                for feature_index in range(self.all_ratings.output_dim):
                    if (c_object, feature_index) not in self.models[c_expert].used_object_feature_ids:
                        continue
                    expert_object_feature_all.append((c_expert, c_object, feature_index))
                    expert_object_feature_agg_all.append((self.all_ratings.aggregate_index,
                                                          c_object, feature_index))
                    num_ratings_all_flat.append(c_num_ratings)
                    
            kwargs['expert_object_feature_all'] = arr_to_index_np(expert_object_feature_all)
            kwargs['expert_object_feature_agg_all'] = arr_to_index_np(expert_object_feature_agg_all)
            kwargs['num_ratings_all_flat'] = np.array(num_ratings_all_flat, dtype=np.float32)
            
            # filling in C (common to 1)
            expert_object_feature_common_to_1 = []
            
            for c_object in kwargs['objects_common_to_1']:
                for feature_index in range(self.all_ratings.output_dim):
                    expert_object_feature_common_to_1.append((self.all_ratings.aggregate_index,
                                                              c_object, feature_index))
                
            kwargs['expert_object_feature_common_to_1'] = arr_to_index_np(
                    expert_object_feature_common_to_1)

        self.last_mb_np = dict(kwargs)

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

        # mem: +32mb

        # computing the custom loss
        with tf.GradientTape() as tape:
            losses = self.loss_fcn(**minibatch)

        # mem: +135mb

        # doing optimization (1 step)
        all_variables = self.all_ratings.variables
        grads = tape.gradient(losses['loss'], all_variables,
                              unconnected_gradients=tf.UnconnectedGradients.ZERO)

        # mem: +180mb
        
        grads = [transform_grad(g) for g in grads]

        # mem: +250mb

        optimizer.apply_gradients(zip(grads, all_variables))

        # mem: +500mb
        
        out = {}
        out.update(losses)
        out.update({f"grad{i}": tf.linalg.norm(g)
                    for i, g in enumerate(grads)})

        # returning original losses
        return {x: y.numpy() for x, y, in out.items()}
