import json
import logging
from collections import defaultdict, Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from solidago.aggregation.entitywise_qr_quantile import EntitywiseQrQuantile
from solidago.pipeline import Pipeline
from solidago.pipeline.inputs import TournesolInput, TournesolInputFromPublicDataset
from solidago.pipeline.outputs import PipelineOutputInMemory
from solidago.preference_learning import LBFGSUniformGBT
from solidago.scaling import Mehestan, ScalingCompose, Standardize
from solidago.scaling.quantile_zero_shift import QuantileShift


def get_dataset():
    return TournesolInputFromPublicDataset("./dataset_2024-06-27.zip")


def get_pipeline(
    shift_quantile: float,
    agg_quantile: float,
    std_dev_quantile: float,
    gbt_prior_std_dev: float,
    gbt_high_ll_thr: float,
    shift_target_score: float,
):
    return Pipeline(
        preference_learning=LBFGSUniformGBT(
            prior_std_dev=gbt_prior_std_dev,
            high_likelihood_range_threshold=gbt_high_ll_thr,
        ),
        scaling=ScalingCompose(
            Mehestan(),
            Standardize(dev_quantile=std_dev_quantile),
            QuantileShift(
                quantile=shift_quantile,
                target_score=shift_target_score,
            ),
        ),
        aggregation=EntitywiseQrQuantile(quantile=agg_quantile),
    )


def run_pipeline(dataset: TournesolInput, pipeline: Pipeline, criterion: str):
    output = PipelineOutputInMemory()
    pipeline.run(input=dataset, criterion=criterion, output=output)

    user_to_n_comparisons = defaultdict(Counter)
    for c in dataset.get_comparisons(criteria=criterion).itertuples():
        user_to_n_comparisons[c.user_id].update([c.entity_a, c.entity_b])

    indiv_scores = output.individual_scores
    indiv_scores["comparisons"] = indiv_scores.apply(
        lambda s: user_to_n_comparisons[s.user_id][s.entity_id], axis=1
    )
    indiv_scores["n_comparisons"] = pd.cut(indiv_scores.comparisons, bins=[0, 1, 2, 4, 8, np.inf])
    indiv_scores["video_id"] = indiv_scores.entity_id.map(dataset.entity_id_to_video_id)

    global_scores = output.entity_scores
    global_scores["contributors"] = global_scores["entity_id"].map(
        output.individual_scores.groupby("entity_id")["user_id"].nunique()
    )
    global_scores["n_contributors"] = global_scores["contributors"].map(
        lambda x: str(x) if x <= 3 else "4+"
    )
    global_scores["video_id"] = global_scores.entity_id.map(dataset.entity_id_to_video_id)

    return indiv_scores, global_scores


def plot_individual_scores(indiv_scores, subtitle="", dir=None):
    plt.figure(figsize=(15, 4))
    ax = sns.histplot(
        data=indiv_scores,
        x="score",
        hue="n_comparisons",
        hue_order=sorted(indiv_scores["n_comparisons"].unique(), reverse=True),
        palette="coolwarm_r",
        multiple="stack",
        linewidth=0.5,
        binwidth=2,
        binrange=(-100, 100),
    )
    ax.set_title("Displayed user scores $\\theta_{ue}^{\\bf display}$\n" + subtitle)
    if dir is not None:
        plt.tight_layout()
        plt.savefig(dir / f"indiv_scores.png", dpi=150)
    plt.close()


def plot_global_scores(global_scores, subtitle="", dir=None):
    plt.figure(figsize=(15, 4))
    ax = sns.histplot(
        data=global_scores,
        x="score",
        hue="n_contributors",
        hue_order=sorted(global_scores["n_contributors"].unique()),
        palette="coolwarm",
        multiple="stack",
        binwidth=2,
        binrange=(-30, 70),
        linewidth=0.5,
    )
    ax.set_title("Displayed global scores $\\rho_e^{\\bf display}$\n" + subtitle)
    if dir is not None:
        plt.tight_layout()
        plt.savefig(dir / f"global_scores.png", dpi=150)
    plt.close()


runs = [
    #     dict(pipeline=Pipeline(), subtitle="default pipeline"),
    #     dict(pipeline=Pipeline(use_old_qr_quantile=True), subtitle="default pipeline_with_old_qr_quantile"),
    # ] + [
    dict(
        pipeline=get_pipeline(
            gbt_prior_std_dev=gbt_prior_std_dev,
            gbt_high_ll_thr=gbt_high_ll_thr,
            shift_quantile=shift_q,
            agg_quantile=agg_q,
            std_dev_quantile=std_dev_q,
            shift_target_score=shift_target,
        ),
        subtitle=f"shift_quantile = {shift_q} | agg_quantile = {agg_q} | std_dev_quantile = {std_dev_q}",
    )
    for shift_q in [0.10, 0.15]
    for gbt_high_ll_thr in [0.25, 0.5, 1.0]
    for agg_q in [0.4, 0.5]
    for std_dev_q in [0.8, 0.9]
    for gbt_prior_std_dev in [7.0]
    # shift_target = 0.2 uses an approximation of the recommendability threshold
    # in the shift process: as the aggregation is using lipshitz=0.1, the maximum
    # score that can be reached with 2 contributors (before squash) is 0.2.
    # After squash, this corresponds to a score of ~ 19.6, close to the recommendability
    # threshold defined to be 20 (i.e only reachable with at least 3 contributors).
    for shift_target in [0.0, 0.2]
]


def get_summary(pattern: str):
    run_stats = []
    for run_dir in Path(".").glob(pattern):
        if not run_dir.is_dir():
            continue
        pipeline_json = json.load((run_dir / "pipeline.json").open())
        stats_json = json.load((run_dir / "stats.json").open())
        run_stats.append(
            dict(
                run=run_dir.name,
                gbt_prior_std_dev=pipeline_json["preference_learning"][1]["prior_std_dev"],
                gbt_high_ll_thr=pipeline_json["preference_learning"][1][
                    "high_likelihood_range_threshold"
                ],
                standardize_dev_q=pipeline_json["scaling"][1][1][1]["dev_quantile"],
                shift_q=pipeline_json["scaling"][1][2][1]["quantile"],
                shift_target=pipeline_json["scaling"][1][2][1]["target_score"],
                aggregation_qr_q=pipeline_json["aggregation"][1]["quantile"],
                **stats_json,
            )
        )
    return pd.DataFrame(run_stats).set_index("run").sort_index()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dirs_prefix = "runR"

    with ProcessPoolExecutor(max_workers=6) as pool:
        submissions = dict()

        for idx, run in enumerate(runs):
            dataset = get_dataset()
            fut = pool.submit(
                run_pipeline,
                dataset=dataset,
                pipeline=run["pipeline"],
                criterion="largely_recommended",
            )
            submissions[fut] = (idx, run)

        for future in as_completed(submissions.keys()):
            idx, run = submissions[future]
            dir = Path(f"./{dirs_prefix}_{idx:02}")
            dir.mkdir()
            pipeline = run["pipeline"]
            json.dump(pipeline.to_json(), (dir / "pipeline.json").open("w"))
            indiv_scores, global_scores = future.result()
            indiv_scores.to_csv(dir / "indiv_scores.csv")
            global_scores.to_csv(dir / "global_scores.csv")
            plot_individual_scores(indiv_scores, subtitle=run["subtitle"], dir=dir)
            plot_global_scores(global_scores, subtitle=run["subtitle"], dir=dir)

            json.dump(
                {
                    "indiv_score_neg_ratio": (indiv_scores["score"] < 0).mean(),
                    "videos_score_gt_20": int((global_scores["score"] > 20).sum()),
                    "videos_score_max": global_scores["score"].max(),
                },
                (dir / "stats.json").open("w"),
            )

        summary = get_summary(f"{dirs_prefix}*")
        summary.to_csv(f"{dirs_prefix}_summary.csv")
