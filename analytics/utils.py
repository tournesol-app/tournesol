import pandas as pd


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
