from django.core.management.base import BaseCommand
import gin
from django_react.settings import load_gin_config
from backend.rating_fields import VIDEO_FIELDS
from gin_tune import tune_gin
from ray import tune
import numpy as np
import pandas as pd
import os
import pickle
import logging
from backend.ml_model.tqdmem import print_memory


@gin.configurable
def learner(cls=None):
    """Get learner class"""
    return cls


@gin.configurable
def callback(self, epoch, report_every=50, metric_every=1000, **kwargs):
    """Called at every iteration."""

    def compute_metrics():
        # computing mean(mean and std scores) per-model and aggregated
        obj = self.all_ratings.objects
        predicted = [m(obj) for m in self.models]
        pred_std = [np.std(x) for x in predicted]
        pred_mean = [np.mean(x) for x in predicted]
        agg = self(obj)

        metrics = {
            "agg_std": np.std(agg),
            "agg_mean": np.mean(agg),
            "pred_mean_mean": np.mean(pred_mean),
            "pred_mean_std": np.mean(pred_std),
        }

        return metrics

    is_last = epoch == (self.epochs - 1)

    if is_last or epoch % report_every == 0:
        metrics = {}
        if is_last or epoch % metric_every == 0:
            logging.warning(f"Computing metrics at epoch {epoch}")
            metrics = compute_metrics()
        logging.warning(f"Reporting at epoch {epoch}")
        tune.report(epoch=epoch, **kwargs, **metrics)


def df_learner_info(learner):
    """Get top/bottom predictions for learner."""
    # obtaining keys for videos
    from backend.models import Video

    video_info_keys = ["uploader", "language", "views", "publication_date", "name"]
    video_info = {
        v.video_id: {k: getattr(v, k) for k in video_info_keys}
        for v in Video.objects.all()
    }

    # list of videos
    objs = learner.all_ratings.objects

    # aggregate predictions
    predictions = learner.aggregator(objs)

    # features
    F = learner.all_ratings.output_features

    # preferences with equal entries
    preferences = [1 for _ in F]

    # total scores
    scores = predictions @ preferences

    # sorted objects
    sorted_idx = np.argsort(scores)[::-1]

    result = {}
    itr = list(enumerate(sorted_idx))

    def res_add(key, val):
        if key not in result:
            result[key] = []
        result[key].append(val)

    for i, idx in itr[:5] + itr[-5:]:
        video_id = objs[idx]
        total_score = scores[idx]
        preds = predictions[idx]
        v_info = video_info[video_id]
        # print(idx, video_id, total_score, preds, v_info)
        res_add("index", i)
        res_add("video_id", video_id)
        res_add("total_score", total_score)
        for f, pred in zip(F, preds):
            res_add(f, pred)
        for k, v in v_info.items():
            res_add(k, v)

    return pd.DataFrame(result)


def experiment(config, checkpoint_dir=None):
    """Experiment for hyperparameter search."""
    learner_obj = learner()()
    learner_obj.aggregator.callback = callback
    learner_obj.fit()
    with tune.checkpoint_dir(step=learner_obj.aggregator.epochs) as checkpoint_dir:
        predictions_path = os.path.join(checkpoint_dir, "predictions.csv")
        df_learner_info(learner_obj).to_csv(
            predictions_path
        )
        logging.warning(f"Predictions saved to {predictions_path}")

        ckpt_path = os.path.join(checkpoint_dir, "learner_ckpt.pkl")
        state = learner_obj.__getstate__()
        with open(ckpt_path, 'wb') as f:
            pickle.dump(state, f)
        print(f"State saved to {ckpt_path}")


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            "--config",
            help="Gin-config file",
            type=str,
            action="append",
            default=["backend/ml_model/config/featureless_config.gin"],
        )
        parser.add_argument(
            "--tune", help="Run hyperparameter search", action="store_true"
        )
        parser.add_argument(
            "--tune_resume", help="Resume a failed tune trial", action="store_true",
        )
        parser.add_argument(
            "--features",
            help="Only update given features",
            type=str,
            action="append",
            default=None,
        )
        parser.add_argument(
            "--epochs_override",
            help="Set this number of epochs to train (overrides gin config, useful for debug)",
            type=int,
            required=False,
            default=None,
        )

    def handle(self, **options):
        print_memory(stage="Command init")

        features = options["features"]

        if features is None:
            features = VIDEO_FIELDS

        for f in features:
            assert f in VIDEO_FIELDS, f"Feature {f} not recognized, {VIDEO_FIELDS}"

        print(f"Using features {', '.join(features)}")

        for config in options["config"]:
            print("Loading config", config)
            load_gin_config(config)

        # running parallel hparam tuning with Ray
        if options["tune"]:

            def pre_parse():
                """Load django before reading configuration (otherwise have import error)."""
                import os

                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_react.settings")

                import django

                django.setup()

            if options["tune_resume"]:
                gin.bind_parameter('tune_run.resume', True)

            tune_gin(experiment, pre_parse=pre_parse)

        # regular training
        else:
            print_memory(stage="pre-learner init")
            learner_obj = learner()(features=features)

            print_memory(stage="learner created")

            #            print("pre-fit reached... entering infinite loop")
            #            from time import sleep
            #            while True:
            #                sleep(1)
            #
            #            print_mem_epoch = partial(print_memory, stage='EPOCH')
            learner_obj.fit(epochs=options["epochs_override"])

            print_memory(stage="post train")

            learner_obj.update_features()

            print_memory(stage="post update")
