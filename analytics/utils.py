import pandas as pd
import requests
import streamlit as st


CRITERIA = [
    "largely_recommended",
    "reliability",
    "importance",
    "engaging",
    "pedagogy",
    "layman_friendly",
    "entertaining_relaxing",
    "better_habits",
    "diversity_inclusion",
    "backfire_risk",
]

CRITERI_EXT = CRITERIA + ["views", "duration", "tournesol_score"]

TCOLOR = [
    "#1282b2",
    "#DC8A5D",
    "#C28BED",
    "#4C72D5",
    "#4BB061",
    "#D37A80",
    "#DFC642",
    "#76C6CB",
    "#9DD654",
    "#D8836D",
]

MSG_NO_DATA = "You should first load the public dataset at the top of the page."


def set_df(data, users=[]):
    """Set up the dataframe"""

    df_tmp = pd.read_csv(data)

    index = ["video_a", "video_b", "public_username"]

    df = df_tmp.pivot(index=index, columns="criteria", values="score")
    df.reset_index(inplace=True)

    if users:
        df = df[df["public_username"].isin(users)]

    return df


def get_unique_video_list(df):

    return list(set(df["video_a"].tolist() + df["video_b"].tolist()))


def get_score(row, crit):
    for item in row["criteria_scores"]:
        if item["criteria"] == crit:
            return item["score"]


@st.cache
def api_get_tournesol_scores():
    """Get a dataframe with all videos from tournesol.."""

    response = requests.get(
        f"https://api.tournesol.app/video/?limit=9999&unsafe=true"
    ).json()

    df = pd.DataFrame.from_dict(response["results"])

    for crit in CRITERIA:
        df[crit] = df.apply(lambda x: get_score(x, crit), axis=1)

    df.drop(columns=["criteria_scores"], inplace=True)

    df["tournesol_score"] = df[CRITERIA].sum(axis=1)

    return df
