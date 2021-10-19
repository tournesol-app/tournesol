"""
Not used in production, for testing only
Module called from "ml_train_dev.py" only if env var TOURNESOL_DEV is True

Used to perform some tests on ml algorithm (custom data, plots, ...)
"""

from ml.core import TOURNESOL_DEV
from .licchavi_dev import LicchaviDev
from .visualisation import seedall, disp_one_by_line, output_infos
from ..core import ml_run


if not TOURNESOL_DEV:
    raise Exception('Dev module called whereas TOURNESOL_DEV=0')


TEST_DATA = [
    [1, 100, 101, "reliability", 100, 0],
    [2, 101, 102, "reliability", 100, 0],
    # [0, 103, 104, "reliability", 50, 0],
    # [0, 105, 106, "reliability", 70, 0],
    # [3, 108, 109, "reliability", 100, 0],
    # [3, 109, 110, "reliability", 100, 0],
    # [3, 110, 111, "reliability", 100, 0],
    # [3, 111, 112, "reliability", 100, 0],
]

NAME = ""


def run_experiment(comparison_data):
    """ trains and outputs some stats """
    seedall(654)
    # glob_gt, loc_gt, s_gt, comps_fake = generate_data(
    #     40, 27, 30,
    #     dens=0.8,
    #     noise=0.02)
    print(len(comparison_data))
    glob_scores, loc_scores, infos = ml_run(
        comparison_data,
        epochs=20,
        criterias=["reliability"],
        licchavi_class=LicchaviDev,
        resume=False,
        save=False,
        verb=1,
        compute_uncertainty=False,
        # ground_truths=(glob_gt, loc_gt, s_gt)
        )

    # some prints and plots
    output_infos(*infos)

    disp_one_by_line(glob_scores[:20])
    disp_one_by_line(loc_scores[:20])
    print("glob:", len(glob_scores), "local:",  len(loc_scores))
