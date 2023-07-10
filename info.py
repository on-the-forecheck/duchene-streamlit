import requests

team_codes = {
    "ANAHEIM DUCKS": "ANA",
    "ARIZONA COYOTES": "ARI",
    "ATLANTA FLAMES": "AFM",
    "ATLANTA THRASHERS": "ATL",
    "BOSTON BRUINS": "BOS",
    "BROOKLYN AMERICANS": "BRK",
    "BUFFALO SABRES": "BUF",
    "CALGARY FLAMES": "CGY",
    "CALGARY TIGERS": "CAT",
    "CALIFORNIA GOLDEN SEALS": "CGS",
    "CAROLINA HURRICANES": "CAR",
    "CHICAGO BLACKHAWKS": "CHI",
    "CLEVELAND BARONS": "CLE",
    "COLORADO AVALANCHE": "COL",
    "COLORADO ROCKIES": "CLR",
    "COLUMBUS BLUE JACKETS": "CBJ",
    "DALLAS STARS": "DAL",
    "DETROIT COUGARS": "DCG",
    "DETROIT FALCONS": "DFL",
    "DETROIT RED WINGS": "DET",
    "EDMONTON ESKIMOS": "EDE",
    "EDMONTON OILERS": "EDM",
    "FLORIDA PANTHERS": "FLA",
    "HAMILTON TIGERS": "HAM",
    "HARTFORD WHALERS": "HFD",
    "KANSAS CITY SCOUTS": "KCS",
    "LOS ANGELES KINGS": "LAK",
    "MINNESOTA NORTH STARS": "MNS",
    "MINNESOTA WILD": "MIN",
    "MONTREAL CANADIENS": "MTL",
    "MONTREAL MAROONS": "MMR",
    "MONTREAL WANDERERS": "MWN",
    "NASHVILLE PREDATORS": "NSH",
    "NEW JERSEY DEVILS": "NJD",
    "NEW YORK AMERICANS": "NYA",
    "NEW YORK ISLANDERS": "NYI",
    "NEW YORK RANGERS": "NYR",
    "OAKLAND SEALS": "OAK",
    "OTTAWA SENATORS": "OTT",
    "OTTAWA SENATORS (1917)": "SEN",
    "PHILADELPHIA FLYERS": "PHI",
    "PHILADELPHIA QUAKERS": "QUA",
    "PITTSBURGH PENGUINS": "PIT",
    "PITTSBURGH PIRATES": "PIR",
    "QUEBEC BULLDOGS": "QBD",
    "QUEBEC NORDIQUES": "QUE",
    "SAN JOSE SHARKS": "SJS",
    "SEATTLE KRAKEN": "SEA",
    "SEATTLE METROPOLITANS": "SEA",
    "ST. LOUIS BLUES": "STL",
    "ST. LOUIS EAGLES": "SLE",
    "TAMPA BAY LIGHTNING": "TBL",
    "TORONTO ARENAS": "TAN",
    "TORONTO MAPLE LEAFS": "TOR",
    "TORONTO ST. PATRICKS": "TSP",
    "VANCOUVER CANUCKS": "VAN",
    "VANCOUVER MAROONS": "VMA",
    "VANCOUVER MILLIONAIRES": "VMI",
    "VEGAS GOLDEN KNIGHTS": "VGK",
    "VICTORIA COUGARS": "VIC",
    "WASHINGTON CAPITALS": "WSH",
    "WINNIPEG JETS": "WPG",
    "WINNIPEG JETS (1979)": "WIN",
}

NHL_COLORS = {
    "ANA": {"GOAL": "#F47A38", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "ATL": {"GOAL": "#5C88DA", "SHOT": "#041E42", "MISS": "#D3D3D3"},
    #'ARI': {'GOAL': '#E2D6B5', 'SHOT': '#8C2633', 'MISS': '#D3D3D3'},
    "ARI": {"GOAL": "#A9431E", "SHOT": "#5F259F", "MISS": "#D3D3D3"},
    "BOS": {"GOAL": "#FFB81C", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "BUF": {"GOAL": "#FCB514", "SHOT": "#002654", "MISS": "#D3D3D3"},
    "CAR": {"GOAL": "#CC0000", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "CBJ": {"GOAL": "#CE1126", "SHOT": "#002654", "MISS": "#D3D3D3"},
    "CGY": {"GOAL": "#F1BE48", "SHOT": "#C8102E", "MISS": "#D3D3D3"},
    "CHI": {"GOAL": "#CF0A2C", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "COL": {"GOAL": "#236192", "SHOT": "#6F263D", "MISS": "#D3D3D3"},
    "DAL": {"GOAL": "#006847", "SHOT": "#111111", "MISS": "#D3D3D3"},
    "DET": {"GOAL": "#FFFFFF", "SHOT": "#CE1126", "MISS": "#D3D3D3"},
    "EDM": {"GOAL": "#FF4C00", "SHOT": "#041E42", "MISS": "#D3D3D3"},
    "FLA": {"GOAL": "#C8102E", "SHOT": "#041E42", "MISS": "#D3D3D3"},
    "LAK": {"GOAL": "#A2AAAD", "SHOT": "#111111", "MISS": "#D3D3D3"},
    "MIN": {"GOAL": "#A6192E", "SHOT": "#154734", "MISS": "#D3D3D3"},
    "MTL": {"GOAL": "#AF1E2D", "SHOT": "#192168", "MISS": "#D3D3D3"},
    "NJD": {"GOAL": "#CE1126", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "NSH": {"GOAL": "#FFB81C", "SHOT": "#041E42", "MISS": "#D3D3D3"},
    "NYI": {"GOAL": "#F47D30", "SHOT": "#00539B", "MISS": "#D3D3D3"},
    "NYR": {"GOAL": "#CE1126", "SHOT": "#0038A8", "MISS": "#D3D3D3"},
    "OTT": {"GOAL": "#C2912C", "SHOT": "#C52032", "MISS": "#D3D3D3"},
    "PHI": {"GOAL": "#F74902", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "PIT": {"GOAL": "#FCB514", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "SEA": {"GOAL": "#99D9D9", "SHOT": "#001628", "MISS": "#D3D3D3"},
    "SJS": {"GOAL": "#006D75", "SHOT": "#000000", "MISS": "#D3D3D3"},
    "STL": {"GOAL": "#FCB514", "SHOT": "#002F87", "MISS": "#D3D3D3"},
    "TBL": {"GOAL": "#FFFFFF", "SHOT": "#002868", "MISS": "#D3D3D3"},
    "TOR": {"GOAL": "#FFFFFF", "SHOT": "#00205B", "MISS": "#D3D3D3"},
    "VAN": {"GOAL": "#00843D", "SHOT": "#00205B", "MISS": "#D3D3D3"},
    "VGK": {"GOAL": "#B4975A", "SHOT": "#333F42", "MISS": "#D3D3D3"},
    "WSH": {"GOAL": "#C8102E", "SHOT": "#041E42", "MISS": "#D3D3D3"},
    "WPG": {"GOAL": "#AC162C", "SHOT": "#041E42", "MISS": "#D3D3D3"},
}

label_dict = {
            "toi": 'TIME-ON-ICE',
        "g": 'GOALS',
        "a1": 'PRIMARY ASSISTS',
        "a2": 'SECONDARY ASSISTS',
        "isf": 'SHOTS ON NET',
        "iff": 'FENWICK FOR',
        "icf": 'CORSI FOR',
        "ixg": 'xG',
        "gax": 'GOALS ABOVE EXPECTED',
        "ihdg": 'HIGH-DANGER GOALS',
        "ihdsf": 'HIGH-DANGER SHOTS ON NET',
        "ihdm": 'HIGH-DANGER MISSED SHOTS',
        "ihdf": 'HIGH-DANGER FENWICK',
        "imsf": 'HIGH-DANGER MISSED SHOTS',
        "isb": 'BLOCKED SHOTS (OFF)',
        "ibs": 'BLOCKED SHOTS (DEF)',
        "igive": 'GIVEAWAYS',
        "itake": 'TAKEAWAYS',
        "ihf": 'HITS FOR',
        "iht": 'HITS TAKEN',
        "ifow": 'FACEOFF WINS',
        "ifol": 'FACEOFF LOSSES',
        "iozfw": 'OZ FACEOFF WINS',
        "iozfl": 'OZ FACEOFF LOSSES',
        "inzfw": 'NZ FACEOFF WINS',
        "inzfl": 'NZ FACEOFF LOSSES',
        "idzfw": 'DZ FACEOFF WINS',
        "idzfl": "DZ FACEOFF LOSSES",
        "ipent2": 'MINOR PENALTIES TAKEN',
        "ipent4": 'DOUBLE MINOR PENALTIES TAKEN',
        "ipent5": 'MAJOR PENALTIES TAKEN',
        "ipent10": 'MISCONDUCT PENALTIES TAKEN',
        "ipend2": 'MINOR PENALTIES DRAWN',
        "ipend4": 'DOUBLE MINOR PENALTIES DRAWN',
        "ipend5": 'MAJOR PENALTIES DRAWN',
        "ipend10": 'MISCONDUCT PENALTIES DRAWN',
        "ozs": 'OFFENSIVE ZONE STARTS',
        "nzs": 'NEUTRAL ZONE STARTS',
        "dzs": 'DEFENSIVE ZONE STARTS',
        "otf": 'ON-THE-FLY STARTS',
        "gf": 'GOALS FOR',
        "gf_adj": 'SCORE- & VENUE-ADJUSTED GOALS FOR',
        "hdgf": 'HIGH-DANGER GOALS FOR',
        "ga": 'GOALS AGAINST',
        "ga_adj": 'SCORE- & VENUE-ADJUSTED GOALS AGAINST',
        "hdga": 'HIGH-DANGER GOALS FOR',
        "xgf": 'EXPECTED GOALS FOR',
        "xgf_adj": 'SCORE- & VENUE-ADJUSTED EXPECTED GOALS FOR',
        "xga": 'EXPECTED GOALS AGAINST',
        "xga_adj": 'SCORE- & VENUE-ADJUSTED EXPECTED GOALS AGAINST',
        "sf": 'SHOTS FOR',
        "sf_adj": 'SCORE- & VENUE-ADJUSTED SHOTS FOR',
        "hdsf": 'HIGH-DANGER SHOTS FOR',
        "sa": 'SHOTS AGAINST',
        "sa_adj": 'SCORE- & VENUE-ADJUSTED SHOTS AGAINST',
        "hdsa": 'HIGH-DANGER SHOTS AGAINST',
        "ff": 'FENWICK FOR',
        "ff_adj": 'SCORE- & VENUE-ADJUSTED FENWICK FOR',
        "hdff": 'HIGH-DANGER FENWICK FOR',
        "fa": 'FENWICK AGAINST',
        "fa_adj": 'SCORE- & VENUE-ADJUSTED FENWICK AGAINST',
        "hdfa": 'HIGH-DANGER FENWICK AGAINST',
        "cf": 'CORSI FOR',
        "cf_adj": 'SCORE- & VENUE-ADJUSTED CORSI FOR',
        "ca": 'CORSI AGAINST',
        "ca_adj": 'SCORE- & VENUE-ADJUSTED CORSI AGAINST',
        "bsf": 'BLOCKED SHOTS (OFF)',
        "bsa": 'BLOCKED SHOTS (DEF)',
        "msf": 'MISSED SHOTS FOR',
        "hdmsf": 'HIGH-DANGER MISSED SHOTS FOR',
        "msa": 'MISSED SHOTS AGAINST',
        "hdmsa": 'HIGH-DANGER MISSED SHOTS AGAINST',
        "hf": 'HITS FOR',
        "ht": 'HITS TAKEN',
        "ozf": 'OFFENSIVE ZONE FACEOFFS',
        "nzf": 'NEUTRAL ZONE FACEOFFS',
        "dzf": 'DEFENSIVE ZONE FACEOFFS',
        "fow": 'FACEOFF WINS',
        "fol": 'FACEOFF LOSSES',
        "ozfw": 'OFFENSIVE ZONE FACEOFF WINS',
        "ozfl": 'OFFENSIVE ZONE FACEOFF LOSSES',
        "nzfw": 'NEUTRAL ZONE FACEOFF WINS',
        "nzfl": 'NEUTRAL ZONE FACEOFF LOSSES',
        "dzfw": 'DEFENSIVE ZONE FACEOFF WINS',
        "dzfl": 'DEFENSIVE ZONE FACEOFF LOSSES',
        "pent2": 'MINOR PENALTIES TAKEN',
        "pent4": 'DOUBLE MINOR PENALTIES TAKEN',
        "pent5": 'MAJOR PENALTIES TAKEN',
        "pent10": 'MISCONDUCT PENALTIES TAKEN',
        "pend2": 'MINOR PENALTIES DRAWN',
        "pend4": 'DOUBLE MINOR PENALTIES DRAWN',
        "pend5": 'MAJOR PENALTIES DRAWN',
        "pend10": 'MICONDUCT PENALTIES DRAWN',
        "gf_p60": 'GF / 60',
        "ga_p60": 'GA / 60',
        "xgf_p60": 'xGF / 60',
        "xga_p60": 'xGA / 60',
        "ozf_perc": 'OFF. ZONE FACEOFF %',
        "dzf_perc": 'OFF. ZONE FACEOFF %',
        'xgf_perc': 'xG FOR %',
        'gf_perc': 'GOALS FOR %',
        'cf_perc': 'CORSI FOR %',

}

class NHLTeam:
    """
    Instance that provides information about a given NHL team, e.g., color scheme or logo URL

    Parameters
    ----------
    team : string
        Identifying information for the team, can be three-letter abbreviation,
        EvolvingHockey abbreviation, or full team name

    Attributes
    ----------
    team : string
        Three-letter team abbreviation, e.g., SJS
    eh_team : string
        Team abbreviation used by EvolvingHockey and Micah Blake McCurdy, e.g., S.J
    team_name : string
        Full team name, e.g., SAN JOSE SHARKS
    colors : dictionary
        Primary color scheme, mapped to GOAL, SHOT, MISS,
        e.g., {"GOAL": "#F47A38", "SHOT": "#000000", "MISS": "#D3D3D3"}
    logo_url : string
        URL where you can download the team's logo, e.g.,
        https://raw.githubusercontent.com/chickenandstats/chickenstats/main/logos/nhl/ANA.png

    """

    def __init__(self, team):
        team = team.upper()

        eh_codes = {"SJS": "S.J", "NJD": "N.J", "TBL": "T.B", "LAK": "L.A"}

        team_names = {
            "ANA": "ANAHEIM DUCKS",
            "ARI": "ARIZONA COYOTES",
            "AFM": "ATLANTA FLAMES",
            "ATL": "ATLANTA THRASHERS",
            "BOS": "BOSTON BRUINS",
            "BRK": "BROOKLYN AMERICANS",
            "BUF": "BUFFALO SABRES",
            "CGY": "CALGARY FLAMES",
            "CAT": "CALGARY TIGERS",
            "CGS": "CALIFORNIA GOLDEN SEALS",
            "CAR": "CAROLINA HURRICANES",
            "CHI": "CHICAGO BLACKHAWKS",
            "CLE": "CLEVELAND BARONS",
            "COL": "COLORADO AVALANCHE",
            "CLR": "COLORADO ROCKIES",
            "CBJ": "COLUMBUS BLUE JACKETS",
            "DAL": "DALLAS STARS",
            "DCG": "DETROIT COUGARS",
            "DFL": "DETROIT FALCONS",
            "DET": "DETROIT RED WINGS",
            "EDE": "EDMONTON ESKIMOS",
            "EDM": "EDMONTON OILERS",
            "FLA": "FLORIDA PANTHERS",
            "HAM": "HAMILTON TIGERS",
            "HFD": "HARTFORD WHALERS",
            "KCS": "KANSAS CITY SCOUTS",
            "LAK": "LOS ANGELES KINGS",
            "MNS": "MINNESOTA NORTH STARS",
            "MIN": "MINNESOTA WILD",
            "MTL": "MONTREAL CANADIENS",
            "MMR": "MONTREAL MAROONS",
            "MWN": "MONTREAL WANDERERS",
            "NSH": "NASHVILLE PREDATORS",
            "NJD": "NEW JERSEY DEVILS",
            "NYA": "NEW YORK AMERICANS",
            "NYI": "NEW YORK ISLANDERS",
            "NYR": "NEW YORK RANGERS",
            "OAK": "OAKLAND SEALS",
            "OTT": "OTTAWA SENATORS",
            "SEN": "OTTAWA SENATORS (1917)",
            "PHI": "PHILADELPHIA FLYERS",
            "PHX": "PHOENIX COYOTES",
            "QUA": "PHILADELPHIA QUAKERS",
            "PIT": "PITTSBURGH PENGUINS",
            "PIR": "PITTSBURGH PIRATES",
            "QBD": "QUEBEC BULLDOGS",
            "QUE": "QUEBEC NORDIQUES",
            "SJS": "SAN JOSE SHARKS",
            "SEA": "SEATTLE METROPOLITANS",
            "STL": "ST. LOUIS BLUES",
            "SLE": "ST. LOUIS EAGLES",
            "TBL": "TAMPA BAY LIGHTNING",
            "TAN": "TORONTO ARENAS",
            "TOR": "TORONTO MAPLE LEAFS",
            "TSP": "TORONTO ST. PATRICKS",
            "VAN": "VANCOUVER CANUCKS",
            "VMA": "VANCOUVER MAROONS",
            "VMI": "VANCOUVER MILLIONAIRES",
            "VGK": "VEGAS GOLDEN KNIGHTS",
            "VIC": "VICTORIA COUGARS",
            "WSH": "WASHINGTON CAPITALS",
            "WPG": "WINNIPEG JETS",
            "WIN": "WINNIPEG JETS (1979)",
        }

        NHL_COLORS = {
            "ANA": {"GOAL": "#F47A38", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "AFM": {"GOAL": "#F1BE48", "SHOT": "#C8102E", "MISS": "#D3D3D3"},
            "ATL": {"GOAL": "#5C88DA", "SHOT": "#041E42", "MISS": "#D3D3D3"},
            #'ARI': {'GOAL': '#E2D6B5', 'SHOT': '#8C2633', 'MISS': '#D3D3D3'},
            "ARI": {"GOAL": "#A9431E", "SHOT": "#5F259F", "MISS": "#D3D3D3"},
            "BOS": {"GOAL": "#FFB81C", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "BRK": {"GOAL": "#CE1126", "SHOT": "#0038A8", "MISS": "#D3D3D3"},
            "BUF": {"GOAL": "#FCB514", "SHOT": "#002654", "MISS": "#D3D3D3"},
            "CAR": {"GOAL": "#CC0000", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "CBJ": {"GOAL": "#CE1126", "SHOT": "#002654", "MISS": "#D3D3D3"},
            "CGS": {"GOAL": "#FFC72C", "SHOT": "#00965E", "MISS": "#D3D3D3"},
            "CGY": {"GOAL": "#F1BE48", "SHOT": "#C8102E", "MISS": "#D3D3D3"},
            "CHI": {"GOAL": "#CF0A2C", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "CLE": {"GOAL": "#C8102E", "SHOT": "#111111", "MISS": "#D3D3D3"},
            "CLR": {"GOAL": "#C8102E", "SHOT": "#00205B", "MISS": "#D3D3D3"},
            "COL": {"GOAL": "#236192", "SHOT": "#6F263D", "MISS": "#D3D3D3"},
            "DAL": {"GOAL": "#006847", "SHOT": "#111111", "MISS": "#D3D3D3"},
            "DET": {"GOAL": "#FFFFFF", "SHOT": "#CE1126", "MISS": "#D3D3D3"},
            "EDM": {"GOAL": "#FF4C00", "SHOT": "#041E42", "MISS": "#D3D3D3"},
            "FLA": {"GOAL": "#C8102E", "SHOT": "#041E42", "MISS": "#D3D3D3"},
            "LAK": {"GOAL": "#A2AAAD", "SHOT": "#111111", "MISS": "#D3D3D3"},
            "MIN": {"GOAL": "#A6192E", "SHOT": "#154734", "MISS": "#D3D3D3"},
            "MTL": {"GOAL": "#AF1E2D", "SHOT": "#192168", "MISS": "#D3D3D3"},
            "NJD": {"GOAL": "#CE1126", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "NSH": {"GOAL": "#FFB81C", "SHOT": "#041E42", "MISS": "#D3D3D3"},
            "NYA": {"GOAL": "#CE1126", "SHOT": "#0038A8", "MISS": "#D3D3D3"},
            "NYI": {"GOAL": "#F47D30", "SHOT": "#00539B", "MISS": "#D3D3D3"},
            "NYR": {"GOAL": "#CE1126", "SHOT": "#0038A8", "MISS": "#D3D3D3"},
            "OTT": {"GOAL": "#C2912C", "SHOT": "#C52032", "MISS": "#D3D3D3"},
            "PHI": {"GOAL": "#F74902", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "PHX": {"GOAL": "#A9431E", "SHOT": "#5F259F", "MISS": "#D3D3D3"},
            "PIT": {"GOAL": "#FCB514", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "SEA": {"GOAL": "#99D9D9", "SHOT": "#001628", "MISS": "#D3D3D3"},
            "SJS": {"GOAL": "#006D75", "SHOT": "#000000", "MISS": "#D3D3D3"},
            "STL": {"GOAL": "#FCB514", "SHOT": "#002F87", "MISS": "#D3D3D3"},
            "TBL": {"GOAL": "#FFFFFF", "SHOT": "#002868", "MISS": "#D3D3D3"},
            "TOR": {"GOAL": "#FFFFFF", "SHOT": "#00205B", "MISS": "#D3D3D3"},
            "VAN": {"GOAL": "#00843D", "SHOT": "#00205B", "MISS": "#D3D3D3"},
            "VGK": {"GOAL": "#B4975A", "SHOT": "#333F42", "MISS": "#D3D3D3"},
            "WSH": {"GOAL": "#C8102E", "SHOT": "#041E42", "MISS": "#D3D3D3"},
            "WPG": {"GOAL": "#AC162C", "SHOT": "#041E42", "MISS": "#D3D3D3"},
        }

        if team not in list(eh_codes.values()) + list(team_names.keys()) + list(
            team_names.values()
        ):
            raise ValueError(f"'{team}' is not a supported team".upper())

        if team in eh_codes.values():
            eh_codes_reversed = dict(zip(eh_codes.values(), eh_codes.keys()))

            team = eh_codes_reversed[team]

        if team in team_names.values():
            team_names_reversed = dict(zip(team_names.values(), team_names.keys()))

            team = team_names_reversed[team]

        if team == "PHX":
            self.team == "ARI"

        else:
            self.team = team

        self.eh_team = eh_codes.get(team, team)

        self.team_name = team_names[team]

        self.colors = NHL_COLORS[team]

        logo_url = f"https://raw.githubusercontent.com/chickenandstats/chickenstats/main/logos/nhl/{team}.png"

        self.logo_url = logo_url

    def download_logo(self):
        """
        Downloads logo from chickenstats Github page

        Returns
        ----------
        response : requests.Response object
            Response object from chickenstats Github page

        """

        response = requests.get(self.logo_url)

        return response