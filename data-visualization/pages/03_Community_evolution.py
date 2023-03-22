"""
A page dedicated to the evolution of the Tournesol community.

List of concepts:

    New contributor:
        A new contributor is a user making his/her first public comparison.

    Comparison:
        A public comparison between two videos involves one or more quality criteria.
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
        fig = (df.groupby("public_username").first().groupby("week_date").size().cumsum().plot())
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

add_contributors_evolution()
add_comparisons_evolution()
