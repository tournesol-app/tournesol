import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

from utils import (
    CRITERI_EXT,
    CRITERIA,
    MSG_NO_DATA,
    MSG_NOT_ENOUGH_DATA,
    TCOLOR,
    api_get_tournesol_df,
    thumbnail_url,
)

st.set_page_config(
    page_title="Tournesol - Videos and channels",
    page_icon="🌻",
    initial_sidebar_state="expanded",
)


def add_sidebar_select_channels():

    st.sidebar.title("Filters")

    st.sidebar.markdown(
        "You can select one or several YouTube channels."
        " If you select none, all channels will be use."
    )

    if not isinstance(st.session_state.df_scores, pd.DataFrame):
        st.sidebar.warning(MSG_NO_DATA)
        return

    df = st.session_state.df_scores
    all_uploaders = df["uploader"].unique()
    selected_uploaders = st.sidebar.multiselect("Channel(s)", all_uploaders)
    if len(selected_uploaders):
        df = df[df["uploader"].isin(selected_uploaders)]

    all_languages = df["language"].unique()
    selected_languages = st.sidebar.multiselect("Language(s)", all_languages, [])
    if len(selected_languages):
        df = df[df["language"].isin(selected_languages)]

    min_contributor = st.sidebar.number_input(
        "Minimum number of contributors to be included", value=3, min_value=1
    )
    df = df[df["n_contributors"] >= min_contributor]

    st.session_state.df_scores = df
    st.session_state.all_uploaders = all_uploaders
    st.session_state.selected_uploaders = selected_uploaders


def add_expander_video_data():

    with st.expander("Video data"):

        if not isinstance(st.session_state.df_scores, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df_scores

        col1, col2, col3 = st.columns(3)
        col1.metric("Channel", df["uploader"].nunique())
        col2.metric("Videos", df["video_id"].size)
        col3.metric("Language", df["language"].nunique())

        st.write(df)


def add_expander_video_podium():

    with st.expander("Video Podium"):

        df = st.session_state.df_scores

        if df.shape[0] < 3:
            st.warning(MSG_NOT_ENOUGH_DATA)
            return

        selected_crit = st.selectbox("Select a criteria:", CRITERIA)
        df = df.sort_values(by=selected_crit, ascending=False)

        col1, col2, col3 = st.columns(3)

        col2.metric("podium_first", "1st", label_visibility="hidden")
        col2.image(thumbnail_url.format(uid=df.iloc[0].loc["video_id"]))
        col2.markdown(df.iloc[0].loc["name"])

        col1.markdown(" ")
        col1.metric("podium_second", "2nd", label_visibility="hidden")
        col1.image(thumbnail_url.format(uid=df.iloc[1].loc["video_id"]))
        col1.markdown(df.iloc[1].loc["name"])

        col3.markdown(" ")
        col3.markdown(" ")
        col3.metric("podium_third", "3rd", label_visibility="hidden")
        col3.image(thumbnail_url.format(uid=df.iloc[2].loc["video_id"]))
        col3.markdown(df.iloc[2].loc["name"])


def add_expander_avg_values():

    with st.expander("Average values by channel"):

        if not isinstance(st.session_state.df_scores, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        with st.columns(2)[0]:
            min_videos = st.number_input(
                "Minimum number of videos per channel", value=3, min_value=1
            )

        df = st.session_state.df_scores

        df_uploaders = df.groupby(["uploader"]).count()
        df_uploaders = df_uploaders[df_uploaders["video_id"] >= min_videos]
        uploader = df_uploaders.index.values.tolist()

        df_uploader_avg = df.groupby(["uploader"]).mean(numeric_only=True)
        df_uploader_avg = df_uploader_avg[df_uploader_avg.index.isin(uploader)]

        st.write(df_uploader_avg[CRITERI_EXT])


def add_expander_correlation_coefficients():

    with st.expander("Correlation coefficients"):

        if not isinstance(st.session_state.df_scores, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df_scores
        st.markdown(
            "The table bellow shows the pearson correlation"
            " coefficient between the criteria scores."
        )

        df_correl = df[CRITERIA].corr()

        fig = plt.figure()
        sns.heatmap(
            df_correl,
            cmap="Blues",
            linewidths=0.5,
            annot=True,
            fmt=".2g",
            annot_kws={"size": 7},
        )
        st.pyplot(fig)


def add_expander_detailed_correlation():

    with st.expander("Detailed correlation"):

        if not isinstance(st.session_state.df_scores, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df_scores
        selected_uploaders = st.session_state.selected_uploaders

        col1, col2, col3 = st.columns(3)
        with col1:
            x = st.selectbox("x", CRITERI_EXT, 1)
            log_x = st.checkbox("x log scale")
        with col2:
            y = st.selectbox("y", CRITERI_EXT, 4)
            log_y = st.checkbox("y log scale")
        with col3:
            st.write(" ")

        if len(selected_uploaders):

            fig = go.Figure()
            for u, uploader in enumerate(selected_uploaders):
                df_uploader = df[df["uploader"] == uploader]

                fig.add_trace(
                    go.Scatter(
                        x=df_uploader[x],
                        y=df_uploader[y],
                        name=uploader,
                        mode="markers",
                        marker_color=TCOLOR[u % len(TCOLOR)],
                    )
                )

        else:

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df[x],
                    y=df[y],
                    mode="markers",
                )
            )

        if log_x:
            fig.update_xaxes(type="log")

        if log_y:
            fig.update_yaxes(type="log")

        fig.update_layout(xaxis=dict(title=x), yaxis=dict(title=y))
        fig.update_xaxes(showline=True, linewidth=2, linecolor="black")
        fig.update_yaxes(showline=True, linewidth=2, linecolor="black")
        st.plotly_chart(fig)


st.title("Videos and channels (computed scores)")

# Load the recommendations (the function is cached to not overload the API)
st.session_state.df_scores = api_get_tournesol_df()

# Select uploaders
add_sidebar_select_channels()

# Table of video data
add_expander_video_data()

# Video podium by criteria
add_expander_video_podium()

# Table of average values by channel
add_expander_avg_values()

# Correlation coefficients
add_expander_correlation_coefficients()

# Detailed correlation
add_expander_detailed_correlation()
