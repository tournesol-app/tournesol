import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression
from utils import CRITERIA, MSG_NO_DATA, TCOLOR, get_unique_video_list, set_df

st.set_page_config(
    page_title="Tournesol - Users' comparisons",
    page_icon="🌻",
    initial_sidebar_state="expanded",
)


def add_sidebar_select_user():

    st.sidebar.title("Select user(s)")

    st.sidebar.markdown(
        "You can select one or several users. "
        "If you select none the entire public data set will be use."
    )

    if not isinstance(st.session_state.df, pd.DataFrame):
        st.sidebar.warning(MSG_NO_DATA)
        return

    df = st.session_state.df
    all_users = df["public_username"].unique()
    selected_users = st.sidebar.multiselect("selected_users", all_users, label_visibility="hidden")
    if len(selected_users):
        df = df[df["public_username"].isin(selected_users)]
        st.session_state.df = df
    st.session_state.all_users = all_users
    st.session_state.selected_users = selected_users


def add_expander_raw_data():

    with st.expander("Raw data"):

        if not isinstance(st.session_state.df, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df
        st.write(f"There are {df['video_a'].size} comparisons in this dataset")
        st.write(df)


def add_expander_statistics():

    with st.expander("Statistics"):

        if not isinstance(st.session_state.df, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df
        df_stats = (
            df["public_username"]
            .value_counts()
            .pipe(lambda x: x[x>0])
            .reset_index()
            .rename(
                columns={
                    "index": "public_username",
                    "public_username": "Nb of public comparison",
                }
            )
        )

        df_stats["Nb of video"] = df_stats["public_username"].apply(
            lambda x: len(get_unique_video_list(df[df["public_username"] == x])))

        col1, col2, col3 = st.columns(3)
        col1.metric("Users", df["public_username"].nunique())
        col2.metric("Videos", pd.concat([df["video_a"], df["video_b"]]).unique().size)
        col3.metric("Comparisons", df["video_a"].size)

        st.write("Number of public comparisons by user:")
        st.write(df_stats)


def add_expander_correlation_coefficients():

    with st.expander("Correlation coefficients"):

        if not isinstance(st.session_state.df, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df
        st.markdown(
            "The table bellow shows the pearson correlation coefficient between the criteria."
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

        if not isinstance(st.session_state.df, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df
        selected_users = st.session_state.selected_users

        # Select data
        col1, col2, col3 = st.columns(3)
        with col1:
            x = st.selectbox("x", CRITERIA, 1)
        with col2:
            y = st.selectbox("y", CRITERIA, 4)
        with col3:
            st.write(" ")

        # Filter
        col1_exp, col2_exp = st.columns(2)
        with col1_exp:
            filt = st.selectbox("Filter:", CRITERIA)
        with col2_exp:
            score_filt = st.slider("Filter between:", -10, 10, (-10, 10), 1)

        df_filt = df.loc[(df[filt] >= score_filt[0]) & (df[filt] <= score_filt[1])]
        add_regressions = False

        if len(selected_users):
            add_regressions = st.checkbox("Add linear regressions")
            users = selected_users
        else:
            users = st.session_state.all_users
            add_regressions = False
        fig = go.Figure()

        for u, user in enumerate(users):
            df_user = df_filt[df_filt["public_username"] == user]
            fig.add_trace(
                go.Scatter(
                    x=df_user[x],
                    y=df_user[y],
                    name=user,
                    mode="markers",
                    marker_color=TCOLOR[u % len(TCOLOR)],
                )
            )

            # TODO: Cloud be improved/simplified
            if add_regressions:
                df_user.dropna(inplace=True)
                x_fit = df_user[x].to_numpy().reshape((-1, 1))
                y_fit = df_user[y].to_numpy().reshape((-1, 1))
                model = LinearRegression()
                model.fit(x_fit, y_fit)
                x_range = np.linspace(-10, 10, 100).reshape((-1, 1)).tolist()
                y_range = model.predict(x_range).tolist()
                x_range = [val[0] for val in x_range]
                y_range = [val[0] for val in y_range]

                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=y_range,
                        name=f"linear reg",
                        mode="lines",
                        marker_color=TCOLOR[u % len(TCOLOR)],
                    )
                )

        fig.update_layout(xaxis=dict(title=x), yaxis=dict(title=y))
        fig.update_xaxes(showline=True, linewidth=2, linecolor="black")
        fig.update_yaxes(showline=True, linewidth=2, linecolor="black")
        st.plotly_chart(fig)


def add_expander_cursor_position():

    with st.expander("Cursor position histogram"):

        if not isinstance(st.session_state.df, pd.DataFrame):
            st.warning(MSG_NO_DATA)
            return

        df = st.session_state.df
        selected_users = st.session_state.selected_users

        st.markdown("For any criteria, you can see how user(s) place the cursor.")

        selected_crit = st.selectbox("Select a criteria:", CRITERIA)

        fig = go.Figure()

        if len(selected_users):

            for user in selected_users:
                df_user = df[df["public_username"] == user]
                fig.add_trace(
                    go.Histogram(x=df_user[selected_crit], name=user, nbinsx=21)
                )

        else:
            fig.add_trace(
                go.Histogram(x=df[selected_crit], name="all users", nbinsx=21)
            )

        fig.update_layout(barmode="overlay")
        fig.update_traces(opacity=0.7)
        st.plotly_chart(fig)


st.title("Users' comparisons (public dataset)")

# Load public dataset (the function is cached to not overload the API)
st.session_state.df = set_df()

# Select users
add_sidebar_select_user()

# Plot raw data
add_expander_raw_data()

# Statistics
add_expander_statistics()

# Correlation coefficients
add_expander_correlation_coefficients()

# Detailed correlation
add_expander_detailed_correlation()

# Cursor position
add_expander_cursor_position()
