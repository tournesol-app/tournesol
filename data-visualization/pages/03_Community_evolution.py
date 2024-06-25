"""
A page dedicated to the evolution of the Tournesol community.

List of concepts:

    New contributor:
        A new contributor is a user making his/her first public comparison.

    Comparison:
        A public comparison between two videos involves one or more quality criteria.
"""

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from utils import set_df

st.set_page_config(
    page_title="Tournesol - Community evolution",
    page_icon="🌻",
    initial_sidebar_state="expanded",
)


st.title("Community evolution (public dataset)")

# Load public dataset (the function is cached to not overload the API)
st.session_state.df = set_df().sort_values("week_date")
assert (
    st.session_state.df.week_date.is_monotonic_increasing
), "dataframe should be ordered by increasing date"


def add_users_growth_plot():
    """
    Display the number of new users, active users and total users per week
    """

    st.markdown("#### Active contributors")

    df: pd.DataFrame = st.session_state.df

    # Prepare dataframe for needed data
    df = df.drop_duplicates(subset=["public_username", "week_date"])[
        ["public_username", "week_date"]
    ].reset_index(
        drop=True
    )  # Keep only needed data, remove duplicates
    df.week_date = pd.to_datetime(df.week_date, infer_datetime_format=True, utc=True).astype(
        "datetime64[ns]"
    )  # Convert dates to sortable dates
    weeks = pd.date_range(
        start=df.week_date.min(), end=df.week_date.max(), freq="W-MON"
    ).to_list()  # List of all weeks

    # Cut data before 2022 (nothing interresting there)
    df = df[df.week_date >= datetime(2022, 1, 1)]

    # Number of new users for every week_date
    new_users = df.groupby("public_username").first().groupby("week_date").size()

    # Number of users who stopped using the platform
    # Shift weeks by 1 in the future (consider them quitting the first week they didnt compare anything)
    # Ignore last month (consider users having done comparison in the last month as still active)
    quit_users = (
        df.groupby("public_username").last().groupby("week_date").size().shift(1).drop(weeks[-4:])
    )

    # Cumulative Number of active users for every week_date (users that are counted in new but not yet in quit)
    week_active = (new_users - quit_users).cumsum()

    # Number of total users per date (cumulative)
    total_users = df.groupby("week_date").size().cumsum()

    # Merge previous computed series into one, by week_date
    sub_dfs = [("New users", new_users), ("Active users", week_active), ("All users", total_users)]
    dtf = pd.DataFrame({"week_date": weeks}).reset_index()
    for name, subdf in sub_dfs:
        dtf = pd.merge(dtf, subdf.to_frame(name=name), on="week_date")

    # Plot
    fig = px.line(
        dtf,
        x="week_date",
        y=[name for name, _ in sub_dfs],
        log_y=True,
        labels={"value": "Users", "week_date": "Week"},
    )
    st.plotly_chart(fig)


def add_contributors_evolution():
    """
    Display the number of new contributors per week or cumulative sum of new contributors.
    """

    st.markdown("#### New contributors")

    df = st.session_state.df

    week_tab, total_tab = st.tabs(["Per week", "Total"])

    with week_tab:
        fig = df.groupby("public_username").first().groupby("week_date").size().plot(kind="bar")
        fig.update_xaxes(title="Week")
        fig.update_yaxes(title="New contributors per week")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    with total_tab:
        fig = df.groupby("public_username").first().groupby("week_date").size().cumsum().plot()
        fig.update_xaxes(title="Week")
        fig.update_yaxes(title="Total number of public contributors")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)


def add_comparisons_evolution():
    """
    Display the number of public comparisons per week or cumulative sum of public comparisons.
    """

    st.markdown("#### Public comparisons")

    df = st.session_state.df

    week_tab, total_tab = st.tabs(["Per week", "Total"])

    with week_tab:
        fig = df.groupby("week_date").size().plot(kind="bar")
        fig.update_xaxes(title="Week")
        fig.update_yaxes(title="Comparisons per week")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    with total_tab:
        fig = df.groupby("week_date").size().cumsum().plot()
        fig.update_xaxes(title="Week")
        fig.update_yaxes(title="Toral number of public comparisons")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)


pd.options.plotting.backend = "plotly"

add_users_growth_plot()
add_contributors_evolution()
add_comparisons_evolution()
