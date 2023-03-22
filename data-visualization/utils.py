import io
import zipfile

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

CRITERI_EXT = CRITERIA + ["views", "duration"]

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
MSG_NOT_ENOUGH_DATA = "Not enough data to show this section with the selected filters."

DATASET_URL = "https://api.tournesol.app/exports/all/"

# URL to get YouTube thumbnail in high quality
thumbnail_url = "https://img.youtube.com/vi/{uid}/hqdefault.jpg"


@st.cache_data
def set_df():
    """Set up the dataframe"""

    r = requests.get(DATASET_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    for file in z.namelist():
        if "comparisons.csv" in file:
            with z.open(file) as f:
                df_tmp = pd.read_csv(f)
                break

    index = ["video_a", "video_b", "public_username", "week_date"]
    for idx in index + ["criteria"]:
        df_tmp[idx] = df_tmp[idx].astype("category")

    df = df_tmp.pivot(index=index, columns="criteria", values="score")
    df.reset_index(inplace=True)

    for crit in CRITERIA:
        df[crit] = df[crit].astype("float16")
    return df


def get_unique_video_list(df):
    return list(set(df["video_a"]) | set(df["video_b"]))


def get_score(row, crit):
    for item in row["criteria_scores"]:
        if item["criteria"] == crit:
            return item["score"]


@st.cache_data
def api_get_tournesol_scores():
    """Get a dataframe with all videos from tournesol.."""

    response = requests.get(
        f"https://api.tournesol.app/video/?limit=99999&unsafe=true"
    ).json()

    df = pd.DataFrame.from_dict(response["results"])

    for crit in CRITERIA:
        df[crit] = df.apply(lambda x: get_score(x, crit), axis=1)

    df.drop(columns=["criteria_scores"], inplace=True)

    return df
