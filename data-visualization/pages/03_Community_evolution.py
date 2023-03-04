"""
A page dedicated to the evolution of the Tournesol community.

List of concepts:

    New contributor:
        A new contributor is a user making his/her first public comparison.

    Comparison:
        A public comparison between two videos involves one or more quality
        criteria.
"""

import pandas as pd
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


def add_contributors_evolution():
    """
    Display the number of new contributors per week.
    """
    df = st.session_state.df
    st.markdown("#### Number of new contributors per week.")
    fig = (
        df.groupby("public_username")
        .first()
        .groupby("week_date")
        .size()
        .plot(kind="bar")
    )
    fig.update_xaxes(title="Week")
    fig.update_yaxes(title="New contributors (nbr)")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


def add_contributors_cumulative_evolution():
    """
    Display the cumulative number of new contributors per week.
    """
    df = st.session_state.df
    st.markdown("#### Cumulated number of new contributors per week.")
    fig = (
        df.groupby("public_username")
        .first()
        .groupby("week_date")
        .size()
        .cumsum()
        .plot()
    )
    fig.update_xaxes(title="Week")
    fig.update_yaxes(title="New contributors (nbr)")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


def add_comparisons_evolution():
    """
    Display the number of comparisons.
    """
    df = st.session_state.df
    st.markdown("#### Number of public comparisons per week")
    fig = df.groupby("week_date").size().plot(kind="bar")
    fig.update_xaxes(title="Week")
    fig.update_yaxes(title="Comparisons (nbr)")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


def add_comparisons_cumulative_evolution():
    """
    Display the cumulative number of comparisons.
    """
    df = st.session_state.df
    st.markdown("#### Cumulated number of public comparisons per week")
    fig = df.groupby("week_date").size().cumsum().plot()
    fig.update_xaxes(title="Week")
    fig.update_yaxes(title="Comparisons (nbr)")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


pd.options.plotting.backend = "plotly"
add_contributors_evolution()
add_contributors_cumulative_evolution()
add_comparisons_evolution()
add_comparisons_cumulative_evolution()
