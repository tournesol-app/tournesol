from .visualisation import seedall, disp_one_by_line, output_infos
# from .fake_data import generate_data

"""
Not used in production, for testing only
Module called from "ml_train.py" only if env var TOURNESOL_DEV is True

Used to perform some tests on ml algorithm (custom data, plots, ...)
"""


TEST_DATA = [
    [1, 101, 102, "reliability", 70, 0],
    [2, 101, 102, "reliability", 30, 0],
    [0, 103, 104, "reliability", 50, 0],
    [0, 105, 106, "reliability", 70, 0],
    [3, 108, 109, "reliability", 100, 0],
    [3, 109, 110, "reliability", 100, 0],
    [3, 110, 111, "reliability", 100, 0],
    [3, 111, 112, "reliability", 100, 0],
]

NAME = ""
EPOCHS = 60


def run_experiment(comparison_data):
    """ trains and outputs some stats """
    from ..core import ml_run
    seedall(9996465)
    # glob_gt, loc_gt, s_gt, comps_fake = generate_data(
    #     40, 27, 30,
    #     dens=0.8,
    #     noise=0.02)
    print(len(comparison_data))
    glob_scores, loc_scores, infos = ml_run(
        comparison_data[:10000],
        EPOCHS,
        ["reliability"],
        resume=False,
        save=False,
        verb=1,
        compute_uncertainty=False,
        # ground_truths=(glob_gt, loc_gt, s_gt)
        )

    # some prints and plots
    output_infos(*infos)

    # check_one(200, glob_scores, loc_scores)
    # # for c in comparison_data:
    # #     if c[3]=="largely_recommended":
    # #         print(c)
    # # print(s_fake)
    # #disp_fake_pred(glob_gt, glob_scores)
    disp_one_by_line(glob_scores[:20])
    disp_one_by_line(loc_scores[:20])
    print("glob:", len(glob_scores), "local:",  len(loc_scores))
