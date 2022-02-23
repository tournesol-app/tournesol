import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

from utils import CRITERIA, CRITERI_EXT, MSG_NO_DATA, TCOLOR, api_get_tournesol_scores


def add_expander_select_filters():

    with st.expander("Select channel(s)"):

        st.markdown(
            "You can select one or several YouTube channels."
            " If you select none, all channels will be use."
        )

        if not isinstance(st.session_state.df_scores, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df_scores
        all_uploaders = df["uploader"].unique()
        selected_uploaders = st.multiselect("", all_uploaders)
        if len(selected_uploaders):
            df = df[df["uploader"].isin(selected_uploaders)]

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


def add_expander_avg_values():

    with st.expander("Average values by channel"):

        if not isinstance(st.session_state.df_scores, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        col1, col2 = st.columns(2)
        with col1:
            min_videos = st.number_input(
                "Minimum number of videos to be included", value=3, min_value=1
            )
        with col2:
            st.write(" ")

        df = st.session_state.df_scores

        df_uploaders = df.groupby(["uploader"]).count()
        df_uploaders = df_uploaders[df_uploaders["video_id"] >= min_videos]
        uploader = df_uploaders.index.values.tolist()

        df_uploader_avg = df.groupby(["uploader"]).mean()
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


def app():

    st.title("Tournesol scores")

    # Load public dataset (the function is cached to not overload the API)
    st.session_state.df_scores = api_get_tournesol_scores()

    # Select uploaders
    add_expander_select_filters()

    # Table of video data
    add_expander_video_data()

    # Table of average values by channel
    add_expander_avg_values()

    # Correlation coefficients
    add_expander_correlation_coefficients()

    # Detailed correlation
    add_expander_detailed_correlation()
