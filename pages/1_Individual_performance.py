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
)
from plot_functions import zscore_jitter, lines_scatter

st.markdown("# Individual Career Performance")
st.sidebar.header("Individual performance")
st.write("""Interact with the charts below to explore individual career performance performance""")

seasons_label = "SELECT SEASON"

teams_label = "SELECT TEAM"

strength_label = "SELECT STRENGTH STATE"

strengths_list = ["5v5"]

players_label = "SELECT PLAYER"

with st.sidebar:
    years = list(range(2022, 2006, -1))

    seasons = st.multiselect(seasons_label, years, default=years)

    team = st.selectbox(teams_label, list(NHL_COLORS.keys()), index=18)

    strength_states = st.multiselect(strength_label, strengths_list, default="5v5")

with st.spinner("Downloading list of players from database..."):
    players = get_players(seasons, team)

with st.sidebar:
    player = st.selectbox(players_label, players, index=1)

    toi_min = st.slider(
        "SELECT TIME-ON-ICE THRESHOLD", min_value=None, max_value=None, value=30, step=1
    )

teammates = False
opposition = False

with st.spinner("Downloading data from database..."):

    players = [player]
    season_stats = stats_sql(
        years=seasons,
        level="season",
        strengths=strength_states,
        players=players,
        teammates=teammates,
        opposition=opposition,
    )

    pbp = pbp_sql(
        seasons,
        events = 'shots',
        player = player,
        teammates=teammates,
        opposition=opposition,
    )

st.dataframe(pbp)

st.dataframe(season_stats)