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
from info import NHL_COLORS, team_codes, label_dict
from helper_functions import (
    calc_per60,
    calc_zones,
    calc_percentages,
    calc_pims,
    get_averages,
    prep_lines,
)

plot_colors = {
    "dark_gray": "#36454F",
    "light_gray": "#D3D3D3",
    "medium_gray": "#808080",
}


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

    plot_data["size_col"] = (
        (plot_data.toi_min - plot_data.toi_min.min())
        / (plot_data.toi_min.max() - plot_data.toi_min.min())
        * 100
    )

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
        np.logical_and(
            plot_data.team != team, ~plot_data.forwards_id.str.contains(player)
        ),
        np.logical_and(
            plot_data.team == team, ~plot_data.forwards_id.str.contains(player)
        ),
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
        plot_data.variable = np.where(
            plot_data.variable == old_name, new_name, plot_data.variable
        )

    x_range = plot_data.variable.unique().tolist()

    TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,box_select,poly_select,lasso_select,save"

    player_name = player.replace("..", " ").replace(".", " ")

    title_text = f"{player_name} {season} 5v5 LINE COMBINATIONS & PERFORMANCE"

    if size_col != "EVENLY SIZED":
        title_text = title_text + f" (SIZED FOR {size_col})"

    p = figure(
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

        if size_col == "EVENLY SIZED":
            size = 13

        elif size_col == "TIME-ON-ICE":
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

    p.yaxis.axis_label = "Z-SCORE"

    return p


def lines_scatter(
    lines,
    x_values,
    y_values,
    size_values,
    size_multiplier,
    player,
    team,
    season,
    toi_min,
):
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

    if size_values != "EVENLY SIZED":
        plot_data["size_col"] = (
            (plot_data[size_values] - plot_data[size_values].min())
            / (plot_data[size_values].max() - plot_data[size_values].min())
            * size_multiplier
        )

    colors = NHL_COLORS[team]

    plot_data["edgecolors"] = np.where(
        plot_data.forwards_id.str.contains(player), colors["SHOT"], "white"
    )

    conds = [
        np.logical_and(
            plot_data.team != team, ~plot_data.forwards_id.str.contains(player)
        ),
        np.logical_and(
            plot_data.team == team, ~plot_data.forwards_id.str.contains(player)
        ),
        plot_data.forwards_id.str.contains(player),
    ]

    values = [colors["MISS"], colors["SHOT"], colors["GOAL"]]

    plot_data["colors"] = np.select(conds, values)

    TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,box_select,poly_select,lasso_select,save"

    player_name = player.replace("..", " ").replace(".", " ")

    title_text = f"{player_name} {season} 5v5 LINE COMBINATIONS & PERFORMANCE"

    if x_values == "gf_perc":
        plot_data[x_values].fillna(0)

    if y_values == "gf_perc":
        plot_data[y_values].fillna(0)

    if size_values != "EVENLY SIZED":
        title_text = title_text + f" (SIZED FOR {label_dict[size_values]})"

    p = figure(
        sizing_mode="stretch_both",
        title=title_text,
        tools=TOOLS,
    )

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    source = ColumnDataSource(plot_data)

    plot_colors = [colors["MISS"], colors["SHOT"], colors["GOAL"]]

    for color in plot_colors:
        filters = [True if x == color else False for x in source.data["colors"]]

        view = CDSView(source=source, filters=[BooleanFilter(filters)])

        alpha = 0.35
        line_width = 2
        tooltips_name = "background"
        tools = ""

        if size_values == "EVENLY SIZED":
            size = 13

        else:
            size = "size_col"

        if color == colors["GOAL"] or color == colors["SHOT"]:
            alpha = 0.75
            line_width = 2
            tooltips_name = "main"
            tools = "hover"

        if color == colors["GOAL"]:
            special_lines = p.circle(
                x_values,
                y_values,
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
                x_values,
                y_values,
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
                x_values,
                y_values,
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

    p.yaxis.axis_label = label_dict[y_values]

    p.xaxis.axis_label = label_dict[x_values]

    x_avg, y_avg = get_averages(plot_data, x_values, y_values, team, level="NHL")

    plot_colors = {
        "dark_gray": "#36454F",
        "light_gray": "#D3D3D3",
        "medium_gray": "#808080",
    }

    vline = Span(
        location=x_avg,
        dimension="height",
        line_color=plot_colors["light_gray"],
        line_width=2,
        level="underlay",
    )
    # Horizontal line
    hline = Span(
        location=y_avg,
        dimension="width",
        line_color=plot_colors["light_gray"],
        line_width=2,
        level="underlay",
    )

    p.add_layout(vline)
    p.add_layout(hline)

    return p



def gsax_lines(pbp, player, team, strengths):

    df = pbp.copy()

    player_name = player.replace('..', ' ').replace('.', ' ')

    TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,box_select,poly_select,lasso_select,save"

    p = figure(title=f"{player_name} CAREER SCORING",
        x_axis_label='CUMULATIVE SHOTS TAKEN',
        y_axis_label='CUMULATIVE GOALS SCORED ABOVE EXPECTED',
        tools = TOOLS,
        )

    plot_data = df.loc[np.logical_and(df.strength_state.isin(strengths), df.event_player_1 == player)]

    colors = NHL_COLORS[team]

    conds = [plot_data.strength_state == '5v5', plot_data.strength_state == 'POWERPLAY']

    values = [colors['GOAL'], colors['SHOT']]

    plot_data['colors'] = np.select(conds, values, colors['MISS'])

    for strength in strengths:

        if strength == '5v5':

            color = colors['GOAL']

        if strength == 'POWERPLAY':

            color = colors['SHOT']

        source = ColumnDataSource(plot_data.loc[plot_data.colors == color])

        p.line('cum_shots', 'cum_gsax', color = color, legend_label = strength, source = source, line_width=4)

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

    return p





