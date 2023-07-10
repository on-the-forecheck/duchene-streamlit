import streamlit as st
from PIL import Image
from pathlib import Path

favicon = Image.open(Path("./assets/otf_logo.png"))

st.set_page_config(page_title="Individual performance", page_icon=favicon)

import pandas as pd
import numpy as np

from bokeh.models import (
    HoverTool,
    ColumnDataSource,
    Title,
    Div,
    NumeralTickFormatter,
    Label,
    Line,
    Span,
    CDSView,
    BooleanFilter,
)
from bokeh.plotting import figure
from bokeh.transform import factor_cmap, jitter
from bokeh.layouts import gridplot, column

import sys

sys.path.append("duchene-streamlit")
from sql import stats_sql, get_players, lines_sql, pbp_sql
from info import NHL_COLORS, team_codes, label_dict
from helper_functions import (
    calc_per60,
    calc_zones,
    calc_percentages,
    calc_pims,
    get_averages,
    prep_lines,
    prep_pbp,
    prep_stats
)
from plot_functions import zscore_jitter, lines_scatter

st.markdown("# Individual Career Performance")
st.sidebar.header("Individual performance")
st.write("""Interact with the charts below to explore individual career performance performance""")

seasons_label = "SELECT SEASON"

teams_label = "SELECT TEAM"

strength_label = "SELECT STRENGTH STATE"

strengths_list = ["5v5", '5v4', '5v3', '4v3']

players_label = "SELECT PLAYER"

with st.sidebar:
    years = list(range(2022, 2006, -1))

    seasons = st.multiselect(seasons_label, years, default=years)

    team = st.selectbox(teams_label, list(NHL_COLORS.keys()), index=18)

    strength_states = st.multiselect(strength_label, strengths_list, default=strengths_list)

with st.spinner("Downloading list of players from database..."):
    players = get_players(seasons, team)

with st.sidebar:
    players = st.multiselect(players_label, players, default='MATT.DUCHENE')

    sessions = st.multiselect(
        "SELECT REGULAR SEASON OR PLAYOFFS", ['R', 'P'], default = ['R']
    )

teammates = False
opposition = False

with st.spinner("Downloading data from database..."):

    game_stats = stats_sql(
        years=seasons,
        level="game",
        sessions = sessions,
        strengths=strength_states,
        players=players,
        teammates=teammates,
        opposition=opposition,
    )

    pbp = pbp_sql(
        seasons,
        sessions = sessions,
        events = 'shots',
        players = players,
        strengths = strength_states,
        teammates=teammates,
        opposition=opposition,
    )

game_stats = prep_stats(game_stats)

pbp = prep_pbp(pbp)

st.dataframe(pbp)

st.dataframe(game_stats)