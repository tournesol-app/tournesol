"""
A page dedicated to the evolution of the Tournesol community.

List of concepts:

    New contributor:
        A new contributor is a user making his/her first public comparison.

    Comparison:
        A public comparison between two videos involves one or more quality criteria.

    Active contributor (during a period of time):
        An active contributor is a user who makes at least one public comparison during a given
        period of time.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from dateutil.relativedelta import relativedelta
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


def add_comparisons_evolution_grouped_by_contributors_age():
    """
    Display the number of active contributors per week, grouped by age.
    """

    st.markdown("#### Active contributors grouped by age")
    st.info(
        "An active contributor is a user who makes at least one public comparison during a given"
        " period of time.",
    )

    df = st.session_state.df

    # Keep only the required data, remove duplicates.
    df = df.drop_duplicates(subset=["public_username", "week_date"])[
        ["public_username", "week_date"]
    ].reset_index(drop=True)

    # Categorize week_date to make them orderable.
    df.week_date = df.week_date.cat.as_ordered()
    overall_first_week = df.week_date.min()
    overall_last_week = df.week_date.max()

    # Categories: one category for each season between min(week_date) and max(week_date).
    # A season is a period of 3 months.
    seasons = pd.date_range(
        start=f"{overall_first_week[:4]}-01-01",
        end=overall_last_week,
        freq="3M",
    ).to_list()

    # For each season, create a new dataframe.
    sub_dfs = []

    # Generate a new dataframe. For each public_username, 
    # assign the season of their first public comparison.
    users_seasons = (
        df.groupby("public_username", as_index=False)
        .min()
        .rename(columns={"week_date": "first_week"})
    )
    last_user_weeks = (
        df.groupby("public_username", as_index=False)
        .max()
        .rename(columns={"week_date": "last_week"})
    )
    users_seasons["last_week"] = last_user_weeks["last_week"]

    # Add new column in users_seasons. The value is the minimum season such as the week_date is
    # greater than the season date.
    users_seasons["season"] = users_seasons.first_week.apply(
        lambda first_week: max((s for s in seasons if s.isoformat() <= first_week), default=seasons[0])
    ).reindex()

    # If user min week_date is same as user max week_date, change its season by 'single week'
    # to differentiate them as they make a large group.
    users_seasons.loc[
        users_seasons.loc[users_seasons.first_week.eq(users_seasons.last_week)].index, "season"
    ] = "single week"
    seasons_users = users_seasons.groupby("season")["public_username"].aggregate(list).to_dict()

    for s in seasons_users:
        # Filter df to keep only users of season s.
        season_df = (
            df.loc[df.public_username.isin(seasons_users[s])]
            .groupby("week_date")
            .public_username.nunique()
        )

        if s == "single week":
            sub_dfs.append(("= last comparison date", season_df))
        else:
            category = s.strftime("%Y %b") + " to " + (s + relativedelta(months=2)).strftime("%b")
            sub_dfs.append((category, season_df))

    # Merge previous computed series into one, by week_date.
    dtf = pd.DataFrame({"week_date": []}).reset_index()
    for name, sub_df in sub_dfs:
        dtf = pd.merge(dtf, sub_df.to_frame(name=name), on="week_date", how="outer").fillna(0)

    fig = px.bar(
        dtf,
        x="week_date",
        y=[name for name, _ in sub_dfs],
        labels={
            "value": "Active contributors",
            "week_date": "Week",
            "variable": "First comparison date",
        },
        color_discrete_sequence=px.colors.sample_colorscale("turbo", samplepoints=len(sub_dfs)),
        color_discrete_map={"= last comparison date": "grey"},
    )
    fig.update_layout(legend={'traceorder': 'reversed'})
    st.plotly_chart(fig)


pd.options.plotting.backend = "plotly"

add_contributors_evolution()
add_comparisons_evolution()
add_comparisons_evolution_grouped_by_contributors_age()
