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


assert st.session_state.df.week_date.is_monotonic_increasing, "dataframe should be ordered by increasing date"

# User evolution
def add_contributor_evolution():
    df = st.session_state.df
    st.markdown("Number of new contributors per week.")
    fig = df.query("").groupby("public_username").first().groupby("week_date").size().plot()
    st.plotly_chart(fig)
    
def add_contributor_cumulative_evolution():
    df = st.session_state.df
    st.markdown("Cumulated Number of new contributors per week.")
    fig = df.groupby("public_username").first().groupby("week_date").size().cumsum().plot()
    st.plotly_chart(fig)


def add_vote_evolution():
    df = st.session_state.df
    st.markdown("Number of contributions per week.")
    fig = df.query("criteria=='largely_recommended'").groupby("week_date").size().plot()
    st.plotly_chart(fig)

def add_vote_cumulative_evolution():
    df = st.session_state.df
    st.markdown("Cumulated number of contributions per week")
    fig = df.query("criteria=='largely_recommended'").groupby("week_date").size().cumsum().plot()
    st.plotly_chart(fig)

pd.options.plotting.backend = "plotly"
# Cursor position
add_contributor_evolution()
add_contributor_cumulative_evolution()
add_vote_evolution()
add_vote_cumulative_evolution()