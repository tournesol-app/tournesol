import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression

from utils import CRITERIA, MSG_NO_DATA, TCOLOR, get_unique_video_list, set_df


def app():

    st.title("Public Dataset")

    # Load public dataset
    with st.expander("Load the public dataset (*.csv)", expanded=True):
        st.session_state.data = st.file_uploader("")

        if st.session_state.data:
            st.success("Data have been loaded!")
            df = set_df(st.session_state.data)

    # Select users
    with st.expander("Select user(s)"):
        st.markdown(
            "You can select one or several users. If you select none the entire public data set will be use."
        )

        if st.session_state.data:
            all_users = df["public_username"].unique()
            selected_users = st.multiselect("", all_users)
            if len(selected_users):
                df = df[df["public_username"].isin(selected_users)]
        else:
            st.warning(MSG_NO_DATA)

    # Plot raw data
    with st.expander("Raw data"):

        if st.session_state.data:
            st.write(f"There are {df['video_a'].size} comparisons in this dataset")
            st.write(df)
        else:
            st.warning(MSG_NO_DATA)

    # Statistics
    with st.expander("Statistics"):

        if st.session_state.data:

            df_stats = (
                df["public_username"]
                .value_counts()
                .reset_index()
                .rename(
                    columns={
                        "index": "public_username",
                        "public_username": "Nb of public comparison",
                    }
                )
            )

            df_stats["Nb of video"] = df_stats["public_username"].apply(
                lambda x: len(get_unique_video_list(df[df["public_username"] == x]))
            )
            st.write("Number of public comparisons by user:")
            st.write(df_stats)
        else:
            st.warning(MSG_NO_DATA)

    # Correlation coefficients
    with st.expander("Correlation coefficients"):

        if st.session_state.data:

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

        else:
            st.warning(MSG_NO_DATA)

    # Detailed correlation
    with st.expander("Detailed correlation"):

        if st.session_state.data:

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
                users = all_users
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

        else:
            st.warning(MSG_NO_DATA)

    # Cursor position
    with st.expander("Cursor position histogram"):

        if st.session_state.data:
            st.markdown("For any criteria, you can see how user(s) place the cursor.")

            selected_crit = st.selectbox("Select a criteria:", CRITERIA)

            fig = go.Figure()

            if len(selected_users):

                for user in selected_users:
                    df_user = df_filt[df_filt["public_username"] == user]
                    fig.add_trace(go.Histogram(x=df_user[selected_crit], name=user, nbinsx=21))

            else:
                fig.add_trace(go.Histogram(x=df[selected_crit], name="all users", nbinsx=21))

            fig.update_layout(barmode="overlay")
            fig.update_traces(opacity=0.7)
            st.plotly_chart(fig)

        else:
            st.warning(MSG_NO_DATA)
