import streamlit as st

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

from sql import stats_sql, get_players, lines_sql
from info import NHL_COLORS, team_codes


## Calculating on percentages
def calc_percentages(df):
    stats_for = ["xgf", "cf", "ff", "gf", "msf", "sf", "ozfw", "nzfw", "dzfw", "hf"]

    stats_against = ["xga", "ca", "fa", "ga", "msa", "sa", "ozfl", "nzfl", "dzfl", "ht"]

    stats_dict = dict(zip(stats_for, stats_against))

    for stat_f, stat_a in stats_dict.items():
        if stat_f not in df.columns or stat_a not in df.columns:
            continue

        df[f"{stat_f}_perc"] = df[f"{stat_f}"] / (df[f"{stat_f}"] + df[f"{stat_a}"])

    return df


## Calculating normalized per 60 stats
def calc_per60(df, calc_type):
    if "toi_min" in df.columns:
        toi_col = df.toi_min

    else:
        toi_col = df.toi

    def on_ice(df):
        stats_for = ["xgf", "cf", "ff", "gf", "msf", "sf", "hf"]

        stats_against = ["xga", "ca", "fa", "ga", "msa", "sa", "ht"]

        others = [
            "ozf",
            "nzf",
            "dzf",
            "ozfw",
            "ozfl",
            "nzfw",
            "nzfl",
            "dzfw",
            "dzfl",
            "iozfw",
            "iozfl",
            "inzfw",
            "inzfl",
            "idzfw",
            "idzfl",
        ]

        stats = stats_for + stats_against + others

        stats = [x for x in stats if x in df.columns]

        for stat in stats:
            df[f"{stat}_p60"] = df[stat] / toi_col * 60

        return df

    def individual(df):
        ind_stats = [
            "g",
            "a1",
            "a2",
            "isf",
            "iff",
            "icf",
            "ixg",
            "missed_shots",
            "shots_blocked_off",
            "give",
            "take",
            "ihf",
            "iht",
            "fow",
            "fol",
            "a1_xg",
            "a2_xg",
            "ipent0",
            "ipent2",
            "ipent4",
            "ipent5",
            "ipend0",
            "ipend2",
            "ipend4",
            "ipend5",
            "ipend10",
            "ipimt",
            "ipimd",
        ]

        for ind_stat in ind_stats:
            if ind_stat not in df.columns:
                continue

            df[f"{ind_stat}_p60"] = df[ind_stat] / toi_col * 60

        return df

    if calc_type == "on_ice":
        df = on_ice(df)

    if calc_type == "individual":
        df = individual(df)

    if calc_type == "all":
        df = individual(df)

        df = on_ice(df)

    return df


## Calculating zone percentages
def calc_zones(df):
    zone_cols = ["ozf", "dzf"]

    for col in zone_cols:
        df[f"{col}_perc"] = df[col] / (df.ozf + df.nzf + df.dzf)

    return df


def calc_faceoffs(df):
    df["ifow_perc"] = df.ifow / (df.ifow + df.ifol)

    return df


def calc_pims(df):
    df["ipimt"] = (df.ipent2 * 2) + (df.pent4 * 4) + (df.pent5 * 5) + (df.pent10 * 10)

    df["ipimd"] = (df.ipend2 * 2) + (df.pend4 * 4) + (df.pend5 * 5) + (df.pend10 * 10)

    return df


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
    player = st.selectbox(players_label, players, index=0)

    toi_min = st.slider(
        "SELECT TIME-ON-ICE THRESHOLD", min_value=None, max_value=None, value=30, step=1
    )

    size_col = st.selectbox('SELECT SIZING COLUMN', ['EVENLY SIZED', 'TIME-ON-ICE'], index=0)

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

lines = lines.loc[lines.toi >= toi_min * 60].reset_index(drop=True)

lines["toi_min"] = lines.toi / 60

lines = calc_per60(lines, "on_ice")

lines = calc_percentages(lines)

lines = calc_zones(lines)

agg_stats = [
    x
    for x in lines.columns
    if lines[x].dtype == float
    and "mean" not in x
    and "std" not in x
    and "zscore" not in x
]

group_list = ["season", "session", "strength_state"]

concat_list = [lines]

for stat in agg_stats:
    if f"{stat}_zscore" in lines.columns:
        continue

    zscore_calc = lambda x: (x - x.mean()) / x.std()

    zscore = (
        lines.groupby(group_list, as_index=False)[stat]
        .transform(zscore_calc)
        .rename(index=f"{stat}_zscore")
    )

    concat_list.append(zscore)

if len(concat_list) > 1:
    lines = pd.concat(concat_list, axis=1)

sessions = ["R"]

conds = np.logical_and.reduce(
    [
        lines.toi_min >= toi_min,
        lines.session.isin(sessions),
    ]
)

plot_data = (
    lines.loc[conds].sort_values(by="toi", ascending=False).reset_index(drop=True)
)

plot_data["size_col"] = (plot_data.toi_min - plot_data.toi_min.min()) / (
    plot_data.toi_min.max() - plot_data.toi_min.min()
) * 100

id_vars = [
    "season",
    "session",
    "forwards",
    "forwards_id",
    "team",
    "strength_state",
    "toi_min",
    "size_col",
    "xgf_p60",
    "xga_p60",
    "gf_p60",
    "ga_p60",
    "cf_p60",
    "ca_p60",
    "ozf_perc",
    "dzf_perc",
]

value_vars = [
    "xgf_p60_zscore",
    "xga_p60_zscore",
    "gf_p60_zscore",
    "ga_p60_zscore",
    "cf_p60_zscore",
    "ca_p60_zscore",
    "ozf_perc_zscore",
    "dzf_perc_zscore",
]

plot_data = plot_data.melt(id_vars=id_vars, value_vars=value_vars).sort_values(
    by="toi_min", ascending=False
)

colors = NHL_COLORS[team]

plot_data["edgecolors"] = np.where(
    plot_data.forwards_id.str.contains(player), colors["SHOT"], "white"
)

conds = [
    np.logical_and(plot_data.team != team, ~plot_data.forwards_id.str.contains(player)),
    np.logical_and(plot_data.team == team, ~plot_data.forwards_id.str.contains(player)),
    plot_data.forwards_id.str.contains(player),
]

values = [colors["MISS"], colors["SHOT"], colors["GOAL"]]

plot_data["colors"] = np.select(conds, values)

xtick_labels = [
    "xGF / 60",
    "xGA / 60",
    "GF / 60",
    "GA / 60",
    "CF / 60",
    "CA / 60",
    "OZF %",
    "DZF %",
]

xtick_labels = dict(zip(value_vars, xtick_labels))

for old_name, new_name in xtick_labels.items():

	plot_data.variable = np.where(plot_data.variable == old_name, new_name, plot_data.variable)

x_range = plot_data.variable.unique().tolist()

TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,box_select,poly_select,lasso_select,save"

p = figure(
    height=400,
    x_range=list(xtick_labels.values()),
    sizing_mode="stretch_both",
    title=f'{player} 5v5 LINE COMBINATIONS & PERFROMANCE',
    tools=TOOLS,
)

p.xgrid.grid_line_color = None

source = ColumnDataSource(plot_data)

plot_colors = [colors["MISS"], colors["SHOT"], colors["GOAL"]]

for color in plot_colors:
    filters = [True if x == color else False for x in source.data["colors"]]

    view = CDSView(source=source, filters=[BooleanFilter(filters)])

    alpha = 0.35
    line_width = 2
    tooltips_name = "background"
    tools = ""

    if size_col == 'EVENLY SIZED':

    	size = 13

    elif size_col == 'TIME-ON-ICE':

    	size = "size_col"

    if color == colors["GOAL"] or color == colors["SHOT"]:
        alpha = 0.75
        line_width = 2
        tooltips_name = "main"
        tools = "hover"

    if color == colors["GOAL"]:
        special_lines = p.circle(
            jitter("variable", 0.3, range=p.x_range),
            "value",
            source=source,
            view=view,
            alpha=alpha,
            size=size,
            line_color="edgecolors",
            line_width=line_width,
            color="colors",
            radius_units="screen",
        )
    elif color == colors["SHOT"]:
        other_lines = p.circle(
            jitter("variable", 0.3, range=p.x_range),
            "value",
            source=source,
            view=view,
            alpha=alpha,
            size=size,
            line_color="edgecolors",
            line_width=line_width,
            color="colors",
            radius_units="screen",
        )

    else:
        p.circle(
            jitter("variable", 0.3, range=p.x_range),
            "value",
            source=source,
            view=view,
            alpha=alpha,
            size=size,
            line_color="edgecolors",
            line_width=2,
            color="colors",
            name=tooltips_name,
            radius_units="screen",
        )


hover = p.select(dict(type=HoverTool))
hover.tooltips = [
    ("LINE", "@forwards"),
    ("TEAM", "@team"),
    ("TOI", "@toi_min{0.0}"),
    ("OZF%", "@ozf_perc{0.0%}"),
    ("xGF / 60", "@xgf_p60{0.0}"),
    ("xGA / 60", "@xga_p60{0.0}"),
    ("GF / 60", "@gf_p60"),
    ("GA / 60", "@ga_p60"),
    ("CF / 60", "@cf_p60"),
    ("CA / 60", "@ca_p60"),
]

hover.mode = "mouse"

hover.renderers = [special_lines, other_lines]

p.yaxis.axis_label = 'Z-SCORE'

st.bokeh_chart(p, use_container_width=True)
