"""
A page dedicated to the evolution of the Tournesol community.

List of concepts:

    New contributor:
        A new contributor is a user making his/her first comparison.

    Contribution:
        A contribution is comparison between two videos involving one or more
        criteria.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression
from utils import CRITERIA, MSG_NO_DATA, TCOLOR, get_unique_video_list, set_df


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


def add_contributors_evolution():
    """
    Display the number of new contributors per week.
    """
    df = st.session_state.df
    st.markdown("Number of new contributors per week.")
    fig = df.groupby("public_username").first().groupby("week_date").size().plot()
    st.plotly_chart(fig)


def add_contributors_cumulative_evolution():
    """
    Display the cumulative number of new contributors per week.
    """
    df = st.session_state.df
    st.markdown("Cumulated Number of new contributors per week.")
    fig = (
        df.groupby("public_username")
        .first()
        .groupby("week_date")
        .size()
        .cumsum()
        .plot()
    )
    st.plotly_chart(fig)


def add_contributions_evolution():
    """
    Display the number of contributions.
    """
    df = st.session_state.df
    st.markdown("Number of contributions per week.")
    fig = df.groupby("week_date").size().plot()
    st.plotly_chart(fig)


def add_contributions_cumulative_evolution():
    """
    Display the cumulative number of contributions.
    """
    df = st.session_state.df
    st.markdown("Cumulated number of contributions per week")
    fig = df.groupby("week_date").size().cumsum().plot()
    st.plotly_chart(fig)


pd.options.plotting.backend = "plotly"

add_contributors_evolution()
add_contributors_cumulative_evolution()
add_contributions_evolution()
add_contributions_cumulative_evolution()
