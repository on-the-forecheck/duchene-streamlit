import streamlit as st
import psycopg2
import pandas.io.sql as sqlio
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def sql_engine():
    user = st.secrets["postgres"].user
    password = st.secrets["postgres"].password
    host = st.secrets["postgres"].host
    db = st.secrets["postgres"].dbname
    port = st.secrets["postgres"].port

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    return engine


engine = sql_engine()


@st.cache_data(ttl=600, show_spinner=False)
def get_players(years, team):
    seasons = [f"{year}{year+1}" for year in years]

    seasons = ", ".join(f"'{season}'" for season in seasons)

    sql_str = f"""SELECT player
                FROM historical_stats
                WHERE season IN ({seasons})
                AND team = '{team}'
                AND position IN ('C', 'L', 'R')
                """

    with engine.connect() as conn:
        player_chunks = pd.read_sql(sql_str, conn, chunksize=100000)

    player_df = pd.concat(player_chunks, ignore_index=True)

    players = player_df.player.sort_values().unique().tolist()

    return players


## Read pbp functions
@st.cache_data(ttl=600, show_spinner=False)
def pbp_sql(years, events=None, players = [], strengths = ['5v5'], sessions = ['R'], teammates=True, opposition=True, engine=engine):
    """
    Function to read pbp data from my SQL database
    Can be either current or historical stats

    returns dataframe

    Arguments
        years: list of four digit years
        table: table to pull data from
        cols: list of columns to pull from the database
        events: list events to pull from the database
        conn: SQL alchemy connection to database
    """

    if type(years) != list:
        years = [years]

    cols = [
        "season",
        "session",
        "game_id",
        "game_date",
        "event_index",
        "game_period",
        "game_seconds",
        "period_seconds",
        "clock_time",
        "strength_state",
        "score_state",
        "event_type",
        "event_description",
        "event_detail",
        "event_zone",
        "event_team",
        "opp_team",
        "is_home",
        "coords_x",
        "coords_y",
        "event_player_1",
        "event_player_1_id",
        "event_player_1_pos",
        "event_player_2",
        "event_player_2_id",
        "event_player_2_pos",
        "event_player_3",
        "event_player_3_id",
        "event_player_3_pos",
        "event_length",
        "high_danger",
        "danger",
        "pbp_distance",
        "event_distance",
        "event_angle",
        "zone_start",
        "num_on",
        "num_off",
        "players_on",
        "players_on_id",
        "players_on_pos",
        "players_off",
        "players_off_id",
        "players_off_pos",
    ]

    event_f = ["event_on_f", "event_on_f_id"]
    event_d = ["event_on_d", "event_on_d_id"]
    event_g = ["event_on_g", "event_on_g_id"]

    if teammates == "forwards" or teammates == "f":
        cols.extend(event_f)

    if teammates == "defense" or teammates == "d":
        cols.extend(event_d)

    if teammates == "goalie" or teammates == "g":
        cols.extend(event_g)

    if teammates == "skaters":
        cols.extend(event_f + event_d)

    if teammates == True or teammates == "all":
        cols.extend(event_f + event_d + event_g)

    opp_f = ["opp_on_f", "opp_on_f_id"]
    opp_d = ["opp_on_d", "opp_on_d_id"]
    opp_g = ["opp_on_g", "opp_on_g_id"]

    if opposition == "forwards" or opposition == "f":
        cols.extend(opp_f)

    if opposition == "defense" or opposition == "d":
        cols.extend(opp_d)

    if opposition == "goalie" or opposition == "g":
        cols.extend(opp_g)

    if opposition == "skaters":
        cols.extend(opp_f + opp_d)

    if opposition == True or opposition == "all":
        cols.extend(opp_f + opp_d + opp_g)

    if events == None:
        events = [
            "FAC",
            "HIT",
            "SHOT",
            "STOP",
            "MISS",
            "GIVE",
            "BLOCK",
            "GOAL",
            "TAKE",
            "PENL",
            "DELPEN",
            "CHL",
            "CHANGE",
        ]

    if events == "shots":
        events = ["MISS", "SHOT", "GOAL"]

    stats = [
        "shot",
        "shot_adj",
        "goal",
        "goal_adj",
        "pred_goal",
        "pred_goal_adj",
        "miss",
        "block",
        "corsi",
        "corsi_adj",
        "fenwick",
        "fenwick_adj",
        "hd_shot",
        "hd_goal",
        "hd_miss",
        "hd_fenwick",
        "fac",
        "hit",
        "give",
        "take",
        "pen0",
        "pen2",
        "pen4",
        "pen5",
        "pen10",
        "stop",
        "ozf",
        "nzf",
        "dzf",
        "change",
        "ozs",
        "nzs",
        "dzs",
        "otf",
    ]

    CONCAT_LIST = []

    for year in years:
        if year <= 2022:
            table = "historical_pbp"

        else:
            table = "current_pbp"

        if players == []:

            sql_str = f"""SELECT {', '.join(cols)},
                            {', '.join(stats)}
                            FROM {table}
                            WHERE season = {year}{year + 1}
                            AND strength_state IN ({', '.join(f"'{strength}'" for strength in strengths)})
                            AND event_type IN {str(events).replace('[', '(').replace(']', ')')}
                            AND session IN ({', '.join(f"'{session}'" for session in sessions)})
                            ORDER BY game_date, game_id, event_index"""

        else:

            sql_str = f"""SELECT {', '.join(cols)},
                            {', '.join(stats)}
                            FROM {table}
                            WHERE season = {year}{year + 1}
                            AND strength_state IN ({', '.join(f"'{strength}'" for strength in strengths)})
                            AND event_player_1 IN ({', '.join(f"'{player}'" for player in players)})
                            AND event_type IN {str(events).replace('[', '(').replace(']', ')')}
                            AND session IN ({', '.join(f"'{session}'" for session in sessions)})
                            ORDER BY game_date, game_id, event_index"""


        with engine.connect() as conn:
            current_pbp = pd.read_sql(sql_str, conn, chunksize=100000)

        pbp = pd.concat(current_pbp, ignore_index=True)

        CONCAT_LIST.append(pbp)

    pbp = pd.concat(CONCAT_LIST, ignore_index=True)

    return pbp


## Read stats function
@st.cache_data(ttl=600, show_spinner=False)
def stats_sql(
    years,
    level="game",
    players=[],
    strengths=["5v5"],
    sessions = ['R'],
    teammates=False,
    opposition=False,
    score=False,
    engine=engine,
):
    """
    Function to read stats data from my SQL database
    Can be either current or historical stats

    returns dataframe

    Arguments
        years: list of four digit years
        table: table to pull data from
        level: aggregation, default is game level
        conn: SQL alchemy connection to database
    """

    if type(years) != list:
        years = [years]

    group_cols = [
        "season",
        "session",
        "player",
        "player_id",
        "position",
        "team",
        "strength_state",
    ]

    if level == "game" or level == "period":
        game_cols = ["game_id", "game_date"]

        group_cols[2:2] = game_cols

        group_cols[(group_cols.index("team") + 1) : (group_cols.index("team") + 1)] = [
            "opp_team"
        ]

    if level == "period":
        group_cols.append("game_period")

    if opposition != False:
        group_cols[(group_cols.index("team") + 1) : (group_cols.index("team") + 1)] = [
            "opp_team"
        ]

        f_cols = ["opp_forwards", "opp_forwards_id"]

        d_cols = ["opp_defense", "opp_defense_id"]

        g_cols = ["opp_goalie", "opp_goalie_id"]

        if opposition == "forwards" or opposition == "f":
            opp_cols = f_cols

        if opposition == "defense" or opposition == "d":
            opp_cols = d_cols

        if opposition == "goalie" or opposition == "g":
            opp_cols = g_cols

        elif opposition == True:
            opp_cols = f_cols + d_cols + g_cols

        group_cols.extend(opp_cols)

    if teammates != False:
        f_cols = ["forwards", "forwards_id"]

        d_cols = ["defense", "defense_id"]

        g_cols = ["own_goalie", "own_goalie_id"]

        if teammates == "forwards" or teammates == "f":
            mates_cols = f_cols

        if teammates == "defense" or teammates == "d":
            mates_cols = d_cols

        if teammates == "goalie" or teammates == "g":
            mates_cols = _cols

        elif teammates == True:
            mates_cols = f_cols + d_cols + g_cols

        group_cols.extend(mates_cols)

    if score == True:
        group_cols.append("score_state")

    CONCAT_LIST = []

    for year in years:
        stats_cols = [
            "toi",
            "g",
            "a1",
            "a2",
            "isf",
            "iff",
            "icf",
            "ixg",
            "gax",
            "ihdg",
            "ihdf",
            "ihdsf",
            "ihdm",
            "imsf",
            "isb",
            "ibs",
            "igive",
            "itake",
            "ihf",
            "iht",
            "ifow",
            "ifol",
            "iozfw",
            "iozfl",
            "inzfw",
            "inzfl",
            "idzfw",
            "idzfl",
            "a1_xg",
            "a2_xg",
            "ipent0",
            "ipent2",
            "ipent4",
            "ipent5",
            "ipent10",
            "ipend0",
            "ipend2",
            "ipend4",
            "ipend5",
            "ipend10",
            "ozs",
            "nzs",
            "dzs",
            "otf",
            "gf",
            "gf_adj",
            "hdgf",
            "ga",
            "ga_adj",
            "hdga",
            "xgf",
            "xgf_adj",
            "xga",
            "xga_adj",
            "sf",
            "sf_adj",
            "hdsf",
            "sa",
            "sa_adj",
            "hdsa",
            "ff",
            "ff_adj",
            "hdff",
            "fa",
            "fa_adj",
            "hdfa",
            "cf",
            "cf_adj",
            "ca",
            "ca_adj",
            "bsf",
            "bsa",
            "msf",
            "hdmsf",
            "msa",
            "hdmsa",
            "hf",
            "ht",
            "ozf",
            "nzf",
            "dzf",
            "fow",
            "fol",
            "ozfw",
            "ozfl",
            "nzfw",
            "nzfl",
            "dzfw",
            "dzfl",
            "pent0",
            "pent2",
            "pent4",
            "pent5",
            "pent10",
            "pend0",
            "pend2",
            "pend4",
            "pend5",
            "pend10",
        ]

        stats = [f"SUM({x}) as {x}" for x in stats_cols]

        if level == "season":
            stats.append("COUNT(DISTINCT game_id) as games_played")

        if year <= 2022:
            table = "historical_stats"

        else:
            table = "current_stats"

        order_cols = [
            "season",
            "session",
            "game_date",
            "game_id",
            "team",
            "opp_team",
            "strength_state",
            "score_state",
            "game_period",
            "toi",
        ]

        order_bools = [
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "DESC",
        ]

        order_sql = [
            f"{col} {order_bool}"
            for col, order_bool in zip(order_cols, order_bools)
            if col in group_cols or col in stats_cols
        ]

        if players != []:
            sql_str = f"""SELECT {', '.join(group_cols)},
                            {', '.join(stats)}
                            FROM {table}
                            WHERE season = {year}{year + 1}
                            AND strength_state IN ({', '.join(f"'{strength}'" for strength in strengths)})
                            AND player_id IN ({', '.join(f"'{player}'" for player in players)})
                            AND session IN ({', '.join(f"'{session}'" for session in sessions)})
                            GROUP BY {', '.join(group_cols)}
                            ORDER BY {', '.join(order_sql)}"""

        else:
            sql_str = f"""SELECT {', '.join(group_cols)},
                            {', '.join(stats)}
                            FROM {table}
                            WHERE season = {year}{year + 1}
                            AND strength_state IN ({', '.join(f"'{strength}'" for strength in strengths)})
                            AND session IN ({', '.join(f"'{session}'" for session in sessions)})
                            GROUP BY {', '.join(group_cols)}
                            ORDER BY {', '.join(order_sql)}"""

        with engine.connect() as conn:
            stats_chunks = pd.read_sql(sql_str, conn, chunksize=100000)

        stats_df = pd.concat(stats_chunks, ignore_index=True)

        CONCAT_LIST.append(stats_df)

    stats = pd.concat(CONCAT_LIST, ignore_index=True)

    return stats


## Read lines function
@st.cache_data(ttl=600, show_spinner=False)
def lines_sql(
    years,
    line_type,
    strengths=["5v5"],
    player=False,
    level="game",
    teammates=False,
    opposition=False,
    score=False,
    engine=engine,
):
    """
    Function to read lines data from my SQL database
    Can be either current or historical stats

    returns dataframe

    Arguments
        years: list of four digit years
        table: table to pull data from
        level: aggregation, default is game level
        conn: SQL alchemy connection to database
    """

    if type(years) != list:
        years = [years]

    if line_type == "goalie" or line_type == "g":
        line_type = "goalie"

        group_cols = [
            "season",
            "session",
            f"own_{line_type}",
            f"own_{line_type}_id",
            "team",
        ]

    elif line_type == "forwards" or line_type == "f":
        line_type = "forwards"

        group_cols = ["season", "session", f"{line_type}", f"{line_type}_id", "team"]

    elif line_type == "defense" or line_type == "d":
        line_type = "defense"

        group_cols = ["season", "session", f"{line_type}", f"{line_type}_id", "team"]

    group_cols.append("strength_state")

    if level == "game" or level == "period":
        group_cols[2:2] = ["game_id", "game_date"]

        group_cols[(group_cols.index("team") + 1) : (group_cols.index("team") + 1)] = [
            "opp_team"
        ]

    if level == "period":
        group_cols.append("game_period")

    if teammates != False:
        f_cols = ["forwards", "forwards_id"]

        d_cols = ["defense", "defense_id"]

        g_cols = ["own_goalie", "own_goalie_id"]

        if (
            line_type == "forwards"
            or line_type == "f"
            or teammates == "defense"
            or teammates == "d"
        ):
            mates_cols = d_cols

        if (
            line_type == "defense"
            or line_type == "d"
            or teammates == "forwards"
            or teammates == "f"
        ):
            mates_cols = f_cols

        if (
            line_type == "goalie"
            or line_type == "g"
            or teammates == "goalie"
            or teammates == "g"
        ):
            mates_cols = f_cols + d_cols

        if (line_type != "goalie" and line_type != "g") and teammates == True:
            mates_cols = mates_cols + g_cols

        group_cols.extend(mates_cols)

    if opposition != False:
        if "opp_team" not in group_cols:
            group_cols[
                (group_cols.index("team") + 1) : (group_cols.index("team") + 1)
            ] = ["opp_team"]

        f_cols = ["opp_forwards", "opp_forwards_id"]

        d_cols = ["opp_defense", "opp_defense_id"]

        g_cols = ["opp_goalie", "opp_goalie_id"]

        if opposition == "forwards" or opposition == "f":
            opp_cols = f_cols

        if opposition == "defense" or opposition == "d":
            opp_cols = d_cols

        if opposition == "goalie" or opposition == "g":
            opp_cols = g_cols

        if opposition == "skaters":
            opp_cols = f_cols + d_cols

        if opposition == True:
            opp_cols = f_cols + d_cols + g_cols

        group_cols.extend(opp_cols)

    if score == True:
        group_cols.append("score_state")

    CONCAT_LIST = []

    for year in years:
        stats_cols = [
            "toi",
            "gf",
            "gf_adj",
            "hdgf",
            "ga",
            "ga_adj",
            "hdga",
            "xgf",
            "xgf_adj",
            "xga",
            "xga_adj",
            "sf",
            "sf_adj",
            "hdsf",
            "sa",
            "sa_adj",
            "hdsa",
            "ff",
            "ff_adj",
            "hdff",
            "fa",
            "fa_adj",
            "hdfa",
            "cf",
            "cf_adj",
            "ca",
            "ca_adj",
            "bsf",
            "bsa",
            "msf",
            "hdmsf",
            "msa",
            "hdmsa",
            "ozf",
            "nzf",
            "dzf",
            "fow",
            "fol",
            "ozfw",
            "ozfl",
            "nzfw",
            "nzfl",
            "dzfw",
            "dzfl",
            "hf",
            "ht",
            "give",
            "take",
            "pent0",
            "pent2",
            "pent4",
            "pent5",
            "pent10",
            "pend0",
            "pend2",
            "pend4",
            "pend5",
            "pend10",
        ]

        stats = [f"SUM({x}) as {x}" for x in stats_cols]

        if year <= 2022:
            table = "historical_lines"

        else:
            table = "current_lines"

        order_cols = [
            "season",
            "session",
            "game_date",
            "game_id",
            "team",
            "opp_team",
            "strength_state",
            "score_state",
            "game_period",
            "toi",
        ]

        order_bools = [
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "ASC",
            "DESC",
        ]

        order_sql = [
            f"{col} {order_bool}"
            for col, order_bool in zip(order_cols, order_bools)
            if col in group_cols or col in stats_cols
        ]

        toi_min = 1000

        sql_str = f"""SELECT {', '.join(group_cols)}, 
                    {', '.join(stats)} 
                    FROM {table}
                    WHERE season = {year}{year + 1}
                    AND strength_state IN ({', '.join(f"'{strength}'" for strength in strengths)})
                    GROUP BY {', '.join(group_cols)}
                    ORDER BY {', '.join(order_sql)}"""

        with engine.connect() as conn:
            sql_lines = pd.read_sql(sql_str, conn, chunksize=100000)

        lines = pd.concat(sql_lines, ignore_index=True)

        CONCAT_LIST.append(lines)

    lines = pd.concat(CONCAT_LIST, ignore_index=True)

    return lines


## Read teams functions
@st.cache_data(ttl=600, show_spinner=False)
def teams_sql(years, level="game", strengths=True, score=False, engine=engine):
    """
    Function to read lines data from my SQL database
    Can be either current or historical stats

    returns dataframe

    Arguments
        years: list of four digit years
        table: table to pull data from
        level: aggregation, default is game level
        conn: SQL alchemy connection to database
    """

    if type(years) != list:
        years = [years]

    if level == "season":
        group_cols = ["season", "session", "team"]

    elif level == "game":
        group_cols = ["season", "session", "game_id", "game_date", "team", "opp_team"]

    if strengths == True:
        group_cols.append("strength_state")

    if score == True:
        group_cols.append("score_state")

    CONCAT_LIST = []

    for year in years:
        stats = [
            "toi",
            "gf",
            "gf_adj",
            "hdgf",
            "ga",
            "ga_adj",
            "hdga",
            "xgf",
            "xgf_adj",
            "xga",
            "xga_adj",
            "sf",
            "sf_adj",
            "hdsf",
            "sa",
            "sa_adj",
            "hdsa",
            "ff",
            "ff_adj",
            "hdff",
            "fa",
            "fa_adj",
            "hdfa",
            "cf",
            "cf_adj",
            "ca",
            "ca_adj",
            "bsf",
            "bsa",
            "msf",
            "hdmsf",
            "msa",
            "hdmsa",
            "ozf",
            "nzf",
            "dzf",
            "fow",
            "fol",
            "ozfw",
            "ozfl",
            "nzfw",
            "nzfl",
            "dzfw",
            "dzfl",
            "hf",
            "ht",
            "give",
            "take",
            "pent0",
            "pent2",
            "pent4",
            "pent5",
            "pent10",
            "pend0",
            "pend2",
            "pend4",
            "pend5",
            "pend10",
        ]

        stats = [f"SUM({x}) as {x}" for x in stats]

        if year < 2022:
            table = "historical_team"

        else:
            table = "current_team"

        if level == "game":
            order_sql = "game_date, game_id, team"

        else:
            order_sql = "season, session, team"

        if strengths == True:
            order_sql = f"{order_sql}, strength_state"

        if score == True:
            order_sql = f"{order_sql}, score_state"

        sql_str = f"""SELECT {str(group_cols).replace('[', '').replace(']', '').replace("'", '')},
                    {str(stats).replace('[', '').replace(']', '').replace("'", '')}
                    FROM {table}
                    WHERE season = {year}{year + 1}
                    GROUP BY {str(group_cols).replace('[', '').replace(']', '').replace("'", '')}
                    ORDER BY {order_sql}"""

        with engine.connect() as conn:
            sql_teams = pd.read_sql(sql_str, conn, chunksize=100000)

        teams = pd.concat(sql_teams, ignore_index=True)

        CONCAT_LIST.append(teams)

    teams = pd.concat(CONCAT_LIST, ignore_index=True)

    return teams
