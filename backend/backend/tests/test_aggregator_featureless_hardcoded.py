import os
import shutil
from uuid import uuid1

from scipy.spatial.distance import cdist
from functools import partial
import numpy as np
import pytest
import tensorflow as tf
from backend.ml_model.preference_aggregation_featureless import (
    FeaturelessMedianPreferenceAverageRegularizationAggregator,
)
from backend.ml_model.preference_aggregation_featureless import (
    FeaturelessPreferenceLearningModel,
    AllRatingsWithCommon,
)
from backend.ml_model.preference_aggregation_featureless_tf_dense import (
    VariableIndexLayer,
    loss_fcn_dense,
)
from backend.ml_model.preference_aggregation_featureless_tf_sparse import (
    SparseVariableIndexLayer,
    loss_fcn_sparse,
    sinh_loss
)
from backend.ml_model.preference_aggregation_featureless_tf_dense import (
    loss_fcn_dense as loss_fcn_tf,
)
from backend.ml_model.preference_aggregation_featureless_np import loss_fcn_np
from backend.toy_preference_dataset import ToyHardcodedDataset, ToyRandomDataset
from matplotlib import pyplot as plt


def call_on_dataset_end(models):
    """Inform all models that data was loaded."""
    for m in models:
        m.on_dataset_end()

    all_ratings = models[0].all_ratings

    # virtual 'common' data
    fplm_common = FeaturelessPreferenceLearningModel(
            expert=AllRatingsWithCommon.COMMON_EXPERT, all_ratings=all_ratings
    )
    fplm_common.on_dataset_end()
    all_ratings.reset_model()


@pytest.mark.parametrize("mode", ['sparse', 'dense'])
def test_hardcoded_dataset(mode):
    assert mode in ['sparse', 'dense']
    dataset = ToyHardcodedDataset()
    dataset._generate_many(100)

    all_ratings = AllRatingsWithCommon(
        experts=dataset.users,
        objects=dataset.objects,
        output_features=dataset.fields,
        name="tst",
        var_init_cls=VariableIndexLayer if mode == 'dense' else SparseVariableIndexLayer,
    )

    # creating models
    models = [
        FeaturelessPreferenceLearningModel(expert=user, all_ratings=all_ratings)
        for user in dataset.users
    ]

    for r in dataset.ratings:
        u_idx = dataset.users.index(r["user"])
        ratings_as_vector = np.array([r["ratings"][k] for k in dataset.fields]) / 100.0
        models[u_idx].register_preference(
            o1=r["o1"],
            o2=r["o2"],
            p1_vs_p2=ratings_as_vector,
            weights=np.ones(len(ratings_as_vector)),
        )

    call_on_dataset_end(models)

    # aggregating models
    aggregator = FeaturelessMedianPreferenceAverageRegularizationAggregator(
        models=models,
        loss_fcn=loss_fcn_dense if mode == 'dense' else loss_fcn_sparse,
        hypers={"C": 1.0, "mu": 1.0, "lambda_": 1.0, "default_score_value": 1.0,
                "sample_every": 100},
        batch_params=dict(
            sample_experts=5000,
            sample_ratings_per_expert=5000,
            sample_objects_per_expert=5000,
        ),
    )

    aggregator.fit(epochs=1000)

    result = aggregator.models[0](["trump_video"])[0]
    assert isinstance(result, np.ndarray), "Wrong output"

    result = aggregator(["trump_video"])[0]
    assert isinstance(result, np.ndarray), "Wrong output"

    aggregator.plot_loss()
    plt.savefig("_test_plot.png")

    def validate_order(dataset, aggregator):
        """Test that downvoted videos have smaller ratings."""
        for user_id, user in enumerate(dataset.users):
            got_scores = aggregator.models[user_id](dataset.objects)
            expect_scores = dataset.scores_dict[user]
            errors = 0
            for i, feature in enumerate(dataset.fields):
                for i1, o1 in enumerate(dataset.objects):
                    for i2, o2 in enumerate(dataset.objects):
                        if o1 == o2:
                            continue
                        delta1 = got_scores[i2][i] - got_scores[i1][i]
                        if (o1, o2) in expect_scores[feature]:
                            delta2 = expect_scores[feature][(o1, o2)]
                        else:
                            delta2 = 100 - expect_scores[feature][(o2, o1)]
                        delta2 = (delta2 - 50) / 50.0
                        if delta1 * delta2 <= 0:
                            print(
                                f"Invalid result: {user} {feature} {o1} {o2} got"
                                f" {got_scores[i1][i]} {got_scores[i2][i]} rating {delta2}"
                            )
                            errors += 1
                        else:
                            print("Valid result")
            assert not errors, "There were %s errors" % errors

    validate_order(dataset, aggregator)


def test_loss_computation_sparse_vs_dense():
    dataset = ToyRandomDataset(n_objects=100, n_users=100)
    dataset._generate_many(1000)

    def create_aggregator(dataset, mode=None, with_weights=True, with_cert=True):
        assert mode in ["sparse", "dense"]

        var_init_cls = (
            VariableIndexLayer if mode == "dense" else SparseVariableIndexLayer
        )
        loss_fcn = loss_fcn_dense if mode == "dense" else loss_fcn_sparse

        all_ratings = AllRatingsWithCommon(
            experts=dataset.users,
            objects=dataset.objects,
            output_features=dataset.fields,
            name="tst",
            var_init_cls=var_init_cls,
        )

        # creating models
        models = [
            FeaturelessPreferenceLearningModel(expert=user, all_ratings=all_ratings)
            for user in dataset.users
        ]

        for r in dataset.ratings:
            u_idx = dataset.users.index(r["user"])
            ratings_as_vector = (
                np.array([r["ratings"][k] for k in dataset.fields]) / 100.0
            )
            if with_weights:
                weights_as_vector = np.array([r["weights"][k] for k in dataset.fields])
            else:
                weights_as_vector = np.ones(len(dataset.fields))

            models[u_idx].register_preference(
                o1=r["o1"],
                o2=r["o2"],
                p1_vs_p2=ratings_as_vector,
                weights=weights_as_vector,
            )

        call_on_dataset_end(models)

        # aggregating models
        aggregator = FeaturelessMedianPreferenceAverageRegularizationAggregator(
            models=models,
            loss_fcn=loss_fcn,
            optimizer=tf.keras.optimizers.SGD(lr=1e-3),
            hypers={"C": 1.0, "mu": 1.0, "lambda_": 1.0, "default_score_value": 1.0},
            batch_params=dict(
                sample_experts=5000,
                sample_ratings_per_expert=5000,
                sample_objects_per_expert=5000,
            ),
        )

        params = aggregator.all_ratings.layer.v
        params.assign(tf.zeros_like(params))

        if with_cert:
            aggregator.certification_status = [
                np.random.rand() > 0.5 for _ in range(len(dataset.users))
            ]

        return aggregator

    seed = int(np.random.rand() * 1000)

    np.random.seed(seed)
    agg_dense = create_aggregator(dataset, mode="dense")
    losses_dense = agg_dense.fit(epochs=15)
    mb_dense = agg_dense.last_mb_np
    print(agg_dense.all_ratings.layer.v)

    np.random.seed(seed)
    agg_sparse = create_aggregator(dataset, mode="sparse")
    losses_sparse = agg_sparse.fit(epochs=15)
    mb_sparse = agg_sparse.last_mb_np
    print(agg_sparse.all_ratings.layer.v)

    print({x: len(y) for x, y in mb_dense.items()})
    #    print(mb_sparse)

    for key in set(mb_dense.keys()).intersection(mb_sparse.keys()):
        assert np.allclose(mb_dense[key], mb_sparse[key]), key
        print(key, "mb sparse=dense")

    print(losses_dense)
    print(losses_sparse)

    assert set(losses_sparse.keys()) == set(losses_dense.keys())
    for key in losses_dense.keys():
        assert np.allclose(losses_dense[key], losses_sparse[key]), (
            key,
            "dense",
            losses_dense[key],
            "sparse",
            losses_sparse[key],
        )


def test_loss_computation():
    """Implementing the loss once again in numpy

    ...and checking that the tf version computes the same thing."""
    users = range(np.random.randint(1, 100))
    objects = range(np.random.randint(1, 1000))
    fields = range(np.random.randint(1, 100))

    # creating the table
    all_ratings = AllRatingsWithCommon(
        experts=users, objects=objects, output_features=fields, name="tst",
        var_init_cls=VariableIndexLayer
    )

    # setting a fixed value as the current model parameters
    ratings_val = np.random.randn(1 + len(users), len(objects), len(fields))
    all_ratings.layer.v.assign(ratings_val)

    # creating models
    models = [
        FeaturelessPreferenceLearningModel(expert=user, all_ratings=all_ratings)
        for user in users
    ]

    # random hyperparamters
    hypers = {
        "C": np.random.rand(),
        "mu": np.random.rand(),
        "lambda_": np.random.rand(),
        "default_score_value": 1.0,
    }

    # aggregating models
    aggregator = FeaturelessMedianPreferenceAverageRegularizationAggregator(
        models=models, hypers=hypers,
        loss_fcn=loss_fcn_dense
    )

    # inputs to the loss function
    experts_rating, objects_rating_v1, objects_rating_v2, cmp, weights = (
        [],
        [],
        [],
        [],
        [],
    )
    experts_all, objects_all, num_ratings_all = [], [], []
    objects_common_to_1 = []

    # generating mock data
    n_ratings = np.random.randint(1, 500)
    n_all = np.random.randint(1, 500)
    for r in range(n_ratings):
        experts_rating.append(np.random.choice(users))
        objects_rating_v1.append(np.random.choice(objects))
        objects_rating_v2.append(np.random.choice(objects))
        cmp.append(np.random.randn(len(fields)))
        weights.append(np.random.rand(len(fields)))

    for v in range(n_all):
        experts_all.append(np.random.choice(users))
        objects_all.append(np.random.choice(objects))
        num_ratings_all.append(np.random.randint(1, 50))

    for v in range(n_all):
        objects_common_to_1.append(np.random.choice(objects))

    def np_loss_fcn(
        experts_rating,
        objects_rating_v1,
        objects_rating_v2,
        cmp,
        weights,
        experts_all,
        objects_all,
        num_ratings_all,
        objects_common_to_1,
    ):
        """Compute the loss using numpy, same as aggregator.loss_fcn."""
        result = {}

        # FIT LOSS CALCULATION
        loss_fit = 0.0
        loss_fit_cnt = 0
        for exp, v1, v2, c, wei in zip(
            experts_rating, objects_rating_v1, objects_rating_v2, cmp, weights
        ):
            for f in range(len(fields)):
                thetav = ratings_val[exp, v1, f]
                thetaw = ratings_val[exp, v2, f]
                y = c[f]
                w = wei[f]
                elem = np.log(1 + np.exp(y * (thetav - thetaw))) * w
                loss_fit += elem
                loss_fit_cnt += 1
        result["loss_fit"] = loss_fit

        # LOSS M to COMMON computation
        loss_reg_common = 0.0
        loss_reg_common_cnt = 0
        for exp, v, n in zip(experts_all, objects_all, num_ratings_all):
            for f in range(len(fields)):
                theta = ratings_val[exp, v, f]
                s = ratings_val[-1, v, f]

                elem = n / (hypers["C"] + n) * np.abs(theta - s)

                loss_reg_common += elem
                loss_reg_common_cnt += 1

        result["loss_m_to_common"] = loss_reg_common * hypers["lambda_"]

        # LOSS COMMON to 1 COMPUTATION
        loss_reg_c1 = 0.0
        loss_reg_c1_cnt = 0

        for v in objects_common_to_1:
            for f in range(len(fields)):
                s = ratings_val[-1, v, f]

                elem = np.square(s - 1)

                loss_reg_c1 += elem
                loss_reg_c1_cnt += 1

        result["loss_common_to_1"] = loss_reg_c1 * hypers["mu"]

        # TOTAL LOSS COMPUTATION
        result["loss"] = (
            result["loss_fit"] + result["loss_m_to_common"] + result["loss_common_to_1"]
        )

        return result

    # computing the loss
    args = [
        experts_rating,
        objects_rating_v1,
        objects_rating_v2,
        cmp,
        weights,
        experts_all,
        objects_all,
        num_ratings_all,
        objects_common_to_1,
    ]
    args_names = [
        "experts_rating",
        "objects_rating_v1",
        "objects_rating_v2",
        "cmp",
        "weights",
        "experts_all",
        "objects_all",
        "num_ratings_all",
        "objects_common_to_1",
    ]
    args = [np.array(x) for x in args]
    args = [
        tf.constant(x, dtype=tf.float32) if x.dtype == np.float64 else tf.constant(x)
        for x in args
    ]
    ans_tf = aggregator.loss_fcn(**dict(zip(args_names, args)))
    ans_tf = {k: v.numpy() for k, v in ans_tf.items()}

    # computing the numpy version
    ans_np = np_loss_fcn(
        experts_rating,
        objects_rating_v1,
        objects_rating_v2,
        cmp,
        weights,
        experts_all,
        objects_all,
        num_ratings_all,
        objects_common_to_1,
    )

    # verifying that the results are the same
    assert ans_tf.keys() == ans_np.keys()
    for key in ans_tf.keys():
        assert np.allclose(ans_tf[key], ans_np[key]), f"Wrong value for loss {key}"
        print(f"Correct value for loss {key}")


@pytest.mark.parametrize("mode", ['sparse', 'dense'])
def test_save_load(mode):
    assert mode in ['sparse', 'dense']
    dataset = ToyRandomDataset()
    dataset._generate_many(100)

    all_ratings1 = AllRatingsWithCommon(
        experts=dataset.users,
        objects=dataset.objects,
        output_features=dataset.fields,
        name="tst",
        var_init_cls=VariableIndexLayer if mode == 'dense' else SparseVariableIndexLayer,
    )

    # creating models
    models1 = [
        FeaturelessPreferenceLearningModel(expert=user, all_ratings=all_ratings1)
        for user in dataset.users
    ]

    def load_data_to(models):
        for r in dataset.ratings:
            u_idx = dataset.users.index(r["user"])
            ratings_as_vector = np.array([r["ratings"][k] for k in dataset.fields]) / 100.0
            models[u_idx].register_preference(
                o1=r["o1"],
                o2=r["o2"],
                p1_vs_p2=ratings_as_vector,
                weights=np.ones(len(ratings_as_vector)),
            )

    load_data_to(models1)
    call_on_dataset_end(models1)

    aggregator1 = FeaturelessMedianPreferenceAverageRegularizationAggregator(
        hypers={"lambda_": 1.0, "mu": 1.0, "C": 1.0, "default_score_value": 1.0},
        models=models1,
        loss_fcn=loss_fcn_dense if mode == 'dense' else loss_fcn_sparse,
    )
    aggregator1.fit(epochs=100)

    all_ratings2 = AllRatingsWithCommon(
        experts=dataset.users,
        objects=dataset.objects,
        output_features=dataset.fields,
        name="tst",
        var_init_cls=VariableIndexLayer if mode == 'dense' else SparseVariableIndexLayer,
    )

    # creating models
    models2 = [
        FeaturelessPreferenceLearningModel(expert=user, all_ratings=all_ratings2)
        for user in dataset.users
    ]

    load_data_to(models2)
    call_on_dataset_end(models2)

    aggregator2 = FeaturelessMedianPreferenceAverageRegularizationAggregator(
        hypers={"lambda_": 1.0, "mu": 1.0, "C": 1.0, "default_score_value": 1.0},
        loss_fcn=loss_fcn_dense if mode == 'dense' else loss_fcn_sparse,
        models=models2,
    )

    def is_close():
        out1 = aggregator1(dataset.objects)
        out2 = aggregator2(dataset.objects)

        assert isinstance(out1, np.ndarray), type(out1)
        assert isinstance(out2, np.ndarray), type(out2)

        assert out1.shape == out2.shape, (out1.shape, out2.shape)

        out1[out1 == None] = np.nan  # noqa: E711
        out2[out2 == None] = np.nan  # noqa: E711
        out1 = np.array(out1, dtype=np.float32)
        out2 = np.array(out2, dtype=np.float32)

        assert out1.dtype == out2.dtype, (out1.dtype, out2.dtype)
        return np.allclose(out1, out2)

    assert not is_close(), "Outputs already the same"

    save_dir = "./test-" + str(uuid1()) + "/"
    os.mkdir(save_dir)
    aggregator1.save(save_dir)
    aggregator2.load(save_dir)
    assert is_close(), "Outputs differ"

    shutil.rmtree(save_dir)


@pytest.mark.parametrize("execution_number", range(10))
def test_np_tf_equal(execution_number):
    print("Repetition", execution_number)

    n_nans = 20

    n_experts = np.random.randint(1, 50)
    n_videos = np.random.randint(1, 1000)
    n_features = np.random.randint(1, 100)

    model_tensor = np.random.randn(n_experts + 1, n_videos, n_features).astype(
        np.float32
    )

    n_minibatch = np.random.randint(1, 512)

    if np.random.rand() <= 0.5:
        n_minibatch = 0
    n_minibatch_all = np.random.randint(1, 512)

    if np.random.rand() <= 0.5:
        n_minibatch_all = 0

    n_minibatch_common_to_1 = np.random.randint(1, 512)

    if np.random.rand() <= 0.5:
        n_minibatch_common_to_1 = 0

    def choice_or_empty(n, **kwargs):
        if n == 0:
            return np.array([], dtype=np.int64)
        else:
            return np.random.choice(n, **kwargs)

    feed_batch = {
        "experts_rating": choice_or_empty(n_experts, size=n_minibatch, replace=True),
        "objects_rating_v1": choice_or_empty(n_videos, size=n_minibatch, replace=True),
        "objects_rating_v2": choice_or_empty(n_videos, size=n_minibatch, replace=True),
        "cmp": np.random.randn(n_minibatch, n_features),
        "weights": np.random.randn(n_minibatch, n_features),
        "num_ratings_all": np.random.randn(n_minibatch_all),
        "experts_all": choice_or_empty(n_experts, size=n_minibatch_all, replace=True),
        "objects_all": choice_or_empty(n_videos, size=n_minibatch_all, replace=True),
        "objects_common_to_1": choice_or_empty(
            n_videos, size=n_minibatch_common_to_1, replace=True
        ),
    }

    print(
        n_nans,
        n_experts,
        n_videos,
        n_features,
        n_minibatch,
        n_minibatch_all,
        n_minibatch_common_to_1,
    )

    # settings some cmps to np.nan
    for _ in range(n_nans):
        if not n_minibatch:
            continue
        random_item = np.random.choice(n_minibatch)
        random_feature = np.random.choice(n_features)
        feed_batch["cmp"][random_item, random_feature] = np.nan

    # transforming type
    for key in feed_batch.keys():
        if feed_batch[key].dtype == np.float64:
            feed_batch[key] = feed_batch[key].astype(np.float32)

    # hyperparameters
    hypers = {
        "aggregate_index": np.random.choice(n_experts + 1),
        "lambda_": np.random.randn(),
        "mu": np.random.randn(),
        "C": np.random.randn(),
        "default_score_value": np.random.randn(),
    }

    print(hypers)

    feed_batch_tf = {key: tf.constant(val) for key, val in feed_batch.items()}

    args_np = {
        **hypers,
        **feed_batch,
        "model_tensor": model_tensor,
    }

    args_tf = {**hypers, **feed_batch_tf, "model_tensor": tf.constant(model_tensor)}

    result_np = loss_fcn_np(**args_np)
    result_tf = loss_fcn_tf(**args_tf)

    result_tf = {key: val.numpy() for key, val in result_tf.items()}

    print(result_np.keys(), result_tf.keys())
    assert set(result_np.keys()) == set(result_tf.keys())
    for key in result_np.keys():
        print(key, result_np[key], result_tf[key])
        assert np.allclose(
            result_np[key], result_tf[key], rtol=1e-3, atol=1e-3, equal_nan=True
        )


def test_sinh_loss():
    def check_variable(out, thr=1e-4):
        assert np.sum(np.isnan(out)) == 0
        z = out.flatten().reshape(-1, 1)
        dst = cdist(z, z)
        dst[range(len(z)), range(len(z))] = 1.0
        assert np.min(dst.flatten()) > thr, np.min(dst.flatten())
        
    def gradient(f, x):
        with tf.GradientTape() as tape:
            y = f(x)
            return tape.gradient(y, x)

    x_rand = tf.Variable(np.random.randn(2, 3).astype(np.float32), trainable=True)
    check_variable(sinh_loss(x_rand).numpy())
    check_variable(gradient(sinh_loss, x_rand).numpy())

    x_custom = tf.Variable(np.array([0, 0.05, 1, 10, 100, 1000], dtype=np.float32))
    check_variable(sinh_loss(x_custom).numpy())
    check_variable(gradient(sinh_loss, x_custom).numpy())

    for delta in [1e-3, 1e-2, 1e-4]:
        threshold = 1e-1
        threshold_high = 10.0
        x_border = tf.Variable(
            np.array([0 + delta,
                      threshold - delta, threshold + delta,
                      threshold_high - delta, threshold_high + delta],
                     dtype=np.float32),
            trainable=True,
        )

        check_variable(sinh_loss(x_border, threshold=threshold, threshold_high=threshold_high).numpy(),
                       thr=1e-7)
        check_variable(gradient(
            partial(sinh_loss, threshold=threshold, threshold_high=threshold_high), x_border).numpy(),
            thr=1e-8
        )
