import streamlit as st
from PIL import Image
from pathlib import Path

favicon = Image.open(Path("./assets/otf_logo.png"))

st.set_page_config(page_title="Line combinations and performance", page_icon=favicon)

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
from sql import stats_sql, get_players, lines_sql
from info import NHL_COLORS, team_codes, label_dict
from helper_functions import (calc_per60, calc_zones, calc_percentages, calc_pims, get_averages, prep_lines)
from plot_functions import zscore_jitter, lines_scatter



st.markdown("# Line Combinations & Performance")
st.sidebar.header("Line combinations")
st.write(
    """Interact with the charts below to explore forward line performance"""
)

seasons_label = "SELECT SEASON"

teams_label = "SELECT TEAM"

strength_label = "SELECT STRENGTH STATE"

strengths_list = ["5v5"]

players_label = "SELECT PLAYER"

with st.sidebar:
    years = list(range(2022, 2006, -1))

    season = st.selectbox(seasons_label, years, index=0)

    seasons = [season]

    team = st.selectbox(teams_label, list(NHL_COLORS.keys()), index=18)

    strength_states = st.multiselect(strength_label, strengths_list, default="5v5")

with st.spinner("Downloading list of players from database..."):

    players = get_players(seasons, team)

with st.sidebar:
    player = st.selectbox(players_label, players, index=11)

    toi_min = st.slider(
        "SELECT TIME-ON-ICE THRESHOLD", min_value=None, max_value=None, value=30, step=1
    )

teammates = False
opposition = False

with st.spinner("Downloading data from database..."):
    season_stats = stats_sql(
        years=seasons,
        level="season",
        strengths=strength_states,
        players=player,
        teammates=teammates,
        opposition=opposition,
    )

    lines = lines_sql(
        seasons,
        line_type="f",
        player=False,
        level="season",
        teammates=teammates,
        opposition=opposition,
    )

lines = prep_lines(lines, toi_min)

with st.container():

    col1, col2, col3, col4 = st.columns(4)

    x_y_values = ['xGA / 60', 'xGF / 60', 'xG FOR %', 'GF / 60', 'GA / 60', 'GOALS FOR %', 'CF / 60', 'CA / 60', 'CORSI FOR %', 'OFF. ZONE FACEOFF %', 'DZ FACEOFF %', 'TIME-ON-ICE']

    label_dict_rev = dict(zip(label_dict.values(), label_dict.keys()))

    with col1:
       x_values = st.selectbox('SELECT X-VALUES', x_y_values, index=0)

       x_values = label_dict_rev[x_values]

    with col2:
       y_values = st.selectbox('SELECT Y-VALUES', x_y_values, index=1)

       y_values = label_dict_rev[y_values]

    with col3:
        size_values = ['EVENLY SIZED', 'TIME-ON-ICE'] + x_y_values[:-1]
        size_values = st.selectbox('SELECT SIZING VALUES', size_values, index=0)

        if size_values != 'EVENLY SIZED':

            size_values = label_dict_rev[size_values]

    with col4:
       size_multiplier = st.slider(
        "SELECT SIZE MULTIPLIER", min_value=None, max_value=None, value=50, step=1
    )

    p = lines_scatter(lines, x_values, y_values, size_values, size_multiplier, player, team, season, toi_min)

    st.bokeh_chart(p, use_container_width=True)

with st.container():

    size_col = st.selectbox('SELECT SIZING COLUMN', ['EVENLY SIZED', 'TIME-ON-ICE'], index=0)

    p = zscore_jitter(lines, player, team, season, toi_min, size_col)

    st.bokeh_chart(p, use_container_width=True)
