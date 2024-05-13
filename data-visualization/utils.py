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


def get_criterion_score(row, name):
    for item in row["collective_rating"]["criteria_scores"]:
        if item["criteria"] == name:
            return item["score"]


def get_tournesol_reco(limit: int, offset: int):
    return requests.get(
        f"https://api.tournesol.app/polls/videos/recommendations/?limit={limit}&offset={offset}&unsafe=true"
    ).json()


def get_metadata(row, metadata):
    return row["entity"]["metadata"][metadata]


def get_collective_n_contributor(row):
    return row["collective_rating"]["n_contributors"]


@st.cache_data
def api_get_tournesol_df():
    """
    Return a DataFrame created from the Tournesol recommendations.
    """
    limit = 2000
    offset = 0

    response = get_tournesol_reco(limit, offset)
    df = pd.DataFrame.from_dict(response["results"])
    offset += limit

    while offset < 100_000:
        response = get_tournesol_reco(limit, offset)

        if not response["results"]:
            break

        df = pd.concat([df, pd.DataFrame.from_dict(response["results"])], ignore_index=True)
        offset += limit

    df["video_id"] = df.apply(lambda x: get_metadata(x, "video_id"), axis=1)
    df["name"] = df.apply(lambda x: get_metadata(x, "name"), axis=1)
    df["description"] = df.apply(lambda x: get_metadata(x, "description"), axis=1)
    df["views"] = df.apply(lambda x: get_metadata(x, "views"), axis=1)
    df["duration"] = df.apply(lambda x: get_metadata(x, "duration"), axis=1)
    df["language"] = df.apply(lambda x: get_metadata(x, "language"), axis=1)
    df["uploader"] = df.apply(lambda x: get_metadata(x, "uploader"), axis=1)
    df["n_contributors"] = df.apply(lambda x: get_collective_n_contributor(x), axis=1)

    for crit in CRITERIA:
        df[crit] = df.apply(lambda x: get_criterion_score(x, crit), axis=1)

    return df
