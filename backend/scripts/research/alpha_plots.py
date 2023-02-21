from os import environ

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from fabric import Connection

PG_HOST = "localhost"
PG_USER = "tournesol"
PG_PWD = environ["PG_PWD"]
PG_DB = "tournesol"

PG_CONNECTION_STRING = f"postgresql://{PG_USER}:{PG_PWD}@{PG_HOST}/{PG_DB}"


def indiv_plot(alpha, with_poll_scaling=False):
    sql_indiv = """
    WITH comparisons_count AS (
        SELECT e.id as entity_id, user_id, COUNT(*) as n_comparisons
            FROM tournesol_entity e
            INNER JOIN tournesol_comparison c ON e.id = c.entity_1_id OR e.id = c.entity_2_id
            GROUP BY e.id, c.user_id
    )
    SELECT  cr.entity_id,
            cr.user_id,
            score AS poll_score,
            raw_score * cs.scale + cs.translation AS scaled_score,
            cc.n_comparisons
        FROM tournesol_contributorratingcriteriascore crcs
        INNER JOIN tournesol_contributorrating cr
            ON cr.id = crcs.contributor_rating_id
        INNER JOIN comparisons_count cc
            ON cc.entity_id = cr.entity_id AND cc.user_id = cr.user_id
        INNER JOIN tournesol_contributorscaling cs
            ON cs.poll_id = cr.poll_id AND cs.user_id = cr.user_id AND cs.criteria = crcs.criteria
        WHERE crcs.criteria = 'largely_recommended'
    """
    df_indiv = pd.read_sql(sql_indiv, con=PG_CONNECTION_STRING)
    df_indiv["n_comparisons"] = pd.cut(df_indiv.n_comparisons, bins=[0, 1, 2, 4, 8, np.inf])
    plt.figure(figsize=(15, 4.5))
    ax = sns.histplot(
        data=df_indiv,
        x="poll_score" if with_poll_scaling else "scaled_score",
        hue="n_comparisons",
        hue_order=sorted(df_indiv["n_comparisons"].unique(), reverse=True),
        palette="coolwarm_r",
        multiple="stack",
        **(
            {"binwidth": 2, "binrange": [-100, 100]}
            if with_poll_scaling
            else {"binwidth": 0.01, "binrange": [-0.9, 0.9]}
        ),
    )

    if with_poll_scaling:
        ax.set_title(f"Scaled individual scores (after poll scaling) | alpha = {alpha:.2f}")
    else:
        ax.set_title(f"Scaled individual scores | alpha = {alpha:.2f}")

    plt.savefig(
        f"indiv_scores_{ 'rescaled_' if with_poll_scaling else '' }{alpha:.2f}.png", dpi=150
    )

    return ax


def global_plot(alpha):
    sql = """
    SELECT uid, tournesol_score, rating_n_contributors
        FROM tournesol_entity e
        WHERE tournesol_score is not null and type = 'video'
    """

    df = pd.read_sql(sql, con=PG_CONNECTION_STRING)
    df["n_contributors"] = df.rating_n_contributors.map(lambda x: str(x) if x <= 3 else "4+")
    plt.figure(figsize=(15, 5))
    ax = sns.histplot(
        data=df,
        x="tournesol_score",
        hue="n_contributors",
        hue_order=sorted(df["n_contributors"].unique()),
        palette="coolwarm",
        multiple="stack",
        binwidth=2,
        binrange=[-100, 100],
    )
    ax.set_title(f"Global scores | alpha = {alpha:.2f}")

    plt.xlabel("score")
    plt.savefig(f"global_scores_{alpha:.2f}.png", dpi=150)

    return ax


def run_ml(alpha):
    alpha = float(alpha)
    conn = Connection("tournesol-vm")
    with conn.cd("/srv/tournesol-backend"):
        conn.run(
            "sudo -u gunicorn SETTINGS_FILE=/etc/tournesol/settings.yaml "
            "./venv/bin/python manage.py ml_train --main-criterion-only "
            f" --alpha={alpha}"
        )


def all_plots():
    for alpha in [0.1, 1.0, 10.0]:
        run_ml(alpha)
        global_plot(alpha)
        indiv_plot(alpha, with_poll_scaling=True)
        indiv_plot(alpha, with_poll_scaling=False)
