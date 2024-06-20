import io
from multiprocessing.pool import ThreadPool
import threading
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

thread_local_storage = threading.local()


@st.cache_data
def set_df():
    """Set up the dataframe"""

    r = requests.get(DATASET_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    with z.open("comparisons.csv") as f:
        df_tmp = pd.read_csv(f)

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


def get_url_json(url):
    if not hasattr(thread_local_storage, "session"):
        thread_local_storage.session = requests.Session()
    response = thread_local_storage.session.get(url)
    response.raise_for_status()
    return response.json()


def get_tournesol_reco(limit: int, offset: int):
    return get_url_json(
        f"https://api.tournesol.app/polls/videos/recommendations/?limit={limit}&offset={offset}&unsafe=true"
    )


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

    response = get_tournesol_reco(limit, 0)
    results = response["results"]
    total_count = response["count"]

    reco_params = [(limit, offset) for offset in range(limit, total_count, limit)]
    with ThreadPool(10) as pool:
        for result in pool.starmap(get_tournesol_reco, reco_params):
            if not result["results"]:
                continue
            results.extend(result["results"])

    return pd.DataFrame(
        [
            {
                meta: get_metadata(x, meta)
                for meta in [
                    "video_id",
                    "name",
                    "views",
                    "duration",
                    "language",
                    "uploader",
                ]
            }
            | {"n_contributors": get_collective_n_contributor(x)}
            | {crit: get_criterion_score(x, crit) for crit in CRITERIA}
            for x in results
        ]
    )
