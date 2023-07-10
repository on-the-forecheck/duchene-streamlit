import pandas as pd
import numpy as np


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


def prep_lines(lines, toi_min):
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

    return lines


## Get averages
def get_averages(data, x_values, y_values, team, weights="toi_min", level="NHL"):
    if level == "team":
        conds = np.logical_and.reduce([data.team == team])

        df = data.loc[conds].copy()

    elif level == "NHL":
        df = data.copy()

    y_avg = np.average(df[y_values].fillna(0), weights=df[weights])

    x_avg = np.average(df[x_values].fillna(0), weights=df[weights])

    return x_avg, y_avg


def prep_pbp(pbp):

    df = pbp.copy()

    pp_list = ['5v4', '5v3', '4v3']
    sh_list = ['4v5', '3v5', '3v4']

    conds = [df.strength_state.isin(pp_list),
    df.strength_state.isin(sh_list),
    df.strength_state == '5v5',
    ]

    values = ['POWERPLAY', 'SHORTHANDED', '5v5']

    df.strength_state = np.select(conds, values, df.strength_state)

    sort_cols = ['game_date', 'event_index']

    df = df.sort_values(by = sort_cols).reset_index(drop = True)

    return df

def prep_stats(stats):

    df = stats.copy()

    pp_list = ['5v4', '5v3', '4v3']
    sh_list = ['4v5', '3v5', '3v4']

    conds = [df.strength_state.isin(pp_list),
    df.strength_state.isin(sh_list),
    df.strength_state == '5v5',
    ]

    values = ['POWERPLAY', 'SHORTHANDED', '5v5']

    df.strength_state = np.select(conds, values, df.strength_state)

    group_list = ['season', 'session', 'game_id', 'game_date', 'player', 'player_id', 'position', 'team', 'opp_team', 'strength_state']

    agg_stats = {x: 'sum' for x in df.columns if x not in group_list}

    df = df.groupby(group_list, as_index = False).agg(agg_stats)

    sort_cols = ['game_date', 'strength_state']

    df = df.sort_values(by = sort_cols).reset_index(drop = True)

    return df