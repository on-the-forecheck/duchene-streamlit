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
from info import NHL_COLORS, team_codes

def zscore_jitter(lines, player, team, season, toi_min, size_col):

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

    player_name = player.replace('..', ' ').replace('.', ' ')

    title_text = f'{player_name} {season} 5v5 LINE COMBINATIONS & PERFORMANCE'

    if size_col != 'EVENLY SIZED':

        title_text = title_text + f' (SIZED FOR {size_col})'

    p = figure(
        height=400,
        x_range=list(xtick_labels.values()),
        sizing_mode="stretch_both",
        title=title_text,
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

    return p