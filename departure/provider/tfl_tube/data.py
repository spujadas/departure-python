import json
import pathlib
import os

import departure.commons.helpers as helpers
from . import api

DATA_DIRNAME = "data"
DATA_PATH = pathlib.Path(__file__).parents[0] / DATA_DIRNAME
STATIONS_DATA_FILENAME = "stations.json"

lines = {
    "bakerloo": {
        "name": "Bakerloo",
        "canonical_directions": {
            "Southbound": "inbound",
            "Northbound": "outbound",
        },
        "termini": {  # Bakerloo Line WTT 43 (10-Dec-2017)
            "940GZZLUEAC": {
                "is_inline": False,
                "arrival": "Southbound",
                "departure": "Northbound",
            },
            "940GZZLUHAW": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUQPS": {
                "is_inline": True,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUSGP": {
                "is_inline": True,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
        },
    },
    "central": {
        "name": "Central",
        # All trains enter the loop via the Inner Rail (from LYS Eastbound /
        # outbound) and leave it via the Outer Rail (at LYS Westbound / inbound),
        # and the loop ends at HLT or WOF (doesn't actually loop around).
        # Therefore, for our purposes, the Inner Rail (resp. Outer Rail) behaves
        # like an extension of the Eastbound (reps. Westbound) services.
        # In reality, canonical directions match geographical directions,
        # i.e.:
        # - inbound is Westbound => Inner Rail north of HLT, Outer Rail south of
        #     HLT
        # - outbound is Eastbound => Outer Rail north of HLT, Inner Rail south
        #     of HLT
        # > see hainault_loop_outer_rail_outbound_stations
        "canonical_directions": {
            "Westbound": "inbound",
            "Eastbound": "outbound",
            "Outer Rail": "inbound",  # actually opposite north of HLT
            "Inner Rail": "outbound",  # actually opposite north of HLT
        },
        "termini": {  # Central Line WTT 69 (07-Aug-2016)
            "940GZZLUNAN": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUEBY": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUEPG": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUHLT": {
                "is_inline": True,  # only when coming from south
                "arrival": "Inner Rail",
                "departure": "Outer Rail",
            },
            "940GZZLUNBP": {
                "is_inline": True,  # only when coming from south
                "arrival": "Inner Rail",
                "departure": "Outer Rail",
            },
            "940GZZLUWOF": {
                "is_inline": True,
                "arrival": "Inner Rail",  # Westbound - Platform 2
                "departure": "Outer Rail",  # Eastbound - Platform 3
            },
            "940GZZLULGN": {
                "is_inline": True,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUNHT": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUWRP": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUWCY": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
                "stations_inverse_terminating_direction": [
                    "940GZZLUEBY",
                    "940GZZLUWTA",
                    "940GZZLUNAN",
                    "940GZZLUEAN",
                ],
            },
        },
    },
    "circle": {
        "name": "Circle",
        "canonical_directions": {
            "Westbound": None,
            "Eastbound": None,
        },
        "merged_lines": ["district", "hammersmith-city"],
        "termini": {
            "940GZZLUHSC": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
                "arrival_rail": "Inner Rail",
                "departure_rail": "Outer Rail",
            },
            "940GZZLUERC": {  # HSC-ALD-ERC, marked as "Edgware Road (Circle)"
                "is_inline": True,
                "arrival": "Eastbound",
                "departure": "Westbound",
                "arrival_rail": "Outer Rail",
                "departure_rail": "Inner Rail",
            },
        },
    },
    "district": {
        "name": "District",
        "canonical_directions": {
            "Westbound": "inbound",
            "Eastbound": "outbound",
        },
        "merged_lines": ["circle", "hammersmith-city"],
        "termini": {  # District Line WTT 150 (20-May-2018)
            "940GZZLUBKG": {
                "is_inline": True,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUEBY": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUERC": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLURMD": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUTWH": {
                "is_inline": True,  # WIM-TWH
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUKOY": {
                "is_inline": True,  # HSK-KOY
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUUPM": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUWIM": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
        },
    },
    "hammersmith-city": {
        "name": "Hammersmith & City",
        "canonical_directions": {
            "Westbound": "inbound",
            "Eastbound": "outbound",
        },
        "merged_lines": ["circle", "district"],
        "termini": {  # Circle and H&C Line WTT 35 (21-May-2017)
            "940GZZLUERC": {
                "is_inline": True,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUBKG": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUHSC": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
        },
    },
    "jubilee": {
        "name": "Jubilee",
        "canonical_directions": {
            "Westbound": "inbound",
            "Northbound": "inbound",
            "Eastbound": "outbound",
            "Southbound": "outbound",
        },
        "termini": {  # Jubilee Line WTT 15 (20-May-2018)
            "940GZZLUSTM": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUSTD": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUWYP": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
        },
    },
    "metropolitan": {
        "name": "Metropolitan",
        "canonical_directions": {
            "Westbound": "inbound",
            "Northbound": "inbound",
            "Eastbound": "outbound",
            "Southbound": "outbound",
        },
        "termini": {  # Metropolitan Line WTT 341 (30-Dec-2018)
            "940GZZLUCSM": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUALD": {
                "is_inline": False,
                "arrival": "Southbound",
                "departure": "Northbound",
            },
            "940GZZLUAMS": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUUXB": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUWAF": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUBST": {
                "is_inline": True,  # WAF-BST
                "arrival": "Southbound",
                "departure": "Northbound",
            },
        },
    },
    "northern": {  # Northern Line WTT 57 (29-Jan-2018)
        "name": "Northern",
        "canonical_directions": {
            "Southbound": "inbound",
            "Northbound": "outbound",
        },
        "termini": {
            "940GZZLUEGW": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUHBT": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUKNG": {
                "is_inline": True,
                "arrival": "Southbound",
                "departure": "Northbound",
            },
            "940GZZLUMHL": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUMDN": {
                "is_inline": False,
                "arrival": "Southbound",
                "departure": "Northbound",
            },
        },
    },
    "piccadilly": {
        "name": "Piccadilly",
        "canonical_directions": {
            "Westbound": "inbound",
            "Eastbound": "outbound",
        },
        "termini": {
            "940GZZLUHR4": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUHR5": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUHRC": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUASG": {
                "is_inline": True,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUCKS": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUNFD": {
                "is_inline": True,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUUXB": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
            "940GZZLUWOG": {
                "is_inline": True,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
        },
    },
    "victoria": {
        "name": "Victoria",
        "canonical_directions": {
            "Southbound": "inbound",
            "Northbound": "outbound",
        },
        "termini": {
            "940GZZLUWWL": {
                "is_inline": False,
                "arrival": "Northbound",
                "departure": "Southbound",
            },
            "940GZZLUBXN": {
                "is_inline": False,
                "arrival": "Southbound",
                "departure": "Northbound",
            },
        },
    },
    "waterloo-city": {
        "name": "Waterloo & City",
        "canonical_directions": {
            "Westbound": "inbound",
            "Eastbound": "outbound",
        },
        "termini": {
            "940GZZLUBNK": {
                "is_inline": False,
                "arrival": "Eastbound",
                "departure": "Westbound",
            },
            "940GZZLUWLO": {
                "is_inline": False,
                "arrival": "Westbound",
                "departure": "Eastbound",
            },
        },
    },
}


# ordered list of stations on Circle Line on the outer rail
circle_line_outer_rail_stations = [  # reserved for possible future use
    "940GZZLUHSC",
    "940GZZLUGHK",
    "940GZZLUSBM",
    "940GZZLUWLA",
    "940GZZLULRD",
    "940GZZLULAD",
    "940GZZLUWSP",
    "940GZZLURYO",
    "940GZZLUPAC",
    "940GZZLUERC",  # through ERC
    "940GZZLUBST",
    "940GZZLUGPS",
    "940GZZLUESQ",
    "940GZZLUKSX",
    "940GZZLUFCN",
    "940GZZLUBBN",
    "940GZZLUMGT",
    "940GZZLULVT",
    "940GZZLUALD",
    "940GZZLUTWH",
    "940GZZLUMMT",
    "940GZZLUCST",
    "940GZZLUMSH",
    "940GZZLUBKF",
    "940GZZLUTMP",
    "940GZZLUEMB",
    "940GZZLUWSM",
    "940GZZLUSJP",
    "940GZZLUVIC",
    "940GZZLUSSQ",
    "940GZZLUSKT",
    "940GZZLUGTR",
    "940GZZLUHSK",
    "940GZZLUNHG",
    "940GZZLUBWT",
    "940GZZLUPAC",
    "940GZZLUERC",  # terminus ERC
]


# list of stations on Circle Line that are eastbound on the outer rail
circle_line_outer_rail_eastbound_stations = [
    "940GZZLUHSC",
    "940GZZLUGHK",
    "940GZZLUSBM",
    "940GZZLUWLA",
    "940GZZLULRD",
    "940GZZLULAD",
    "940GZZLUWSP",
    "940GZZLURYO",
    "940GZZLUPAC",
    "940GZZLUERC",
    "940GZZLUBST",
    "940GZZLUGPS",
    "940GZZLUESQ",
    "940GZZLUKSX",
    "940GZZLUFCN",
    "940GZZLUBBN",
    "940GZZLUMGT",
    "940GZZLULVT",
    "940GZZLUALD",
    "940GZZLUHSK",
    "940GZZLUNHG",
    "940GZZLUBWT",
    "940GZZLUPAC",
]

# list of stations on Circle Line that are westbound on the outer rail
circle_line_outer_rail_westbound_stations = [
    "940GZZLUTWH",
    "940GZZLUMMT",
    "940GZZLUCST",
    "940GZZLUMSH",
    "940GZZLUBKF",
    "940GZZLUTMP",
    "940GZZLUEMB",
    "940GZZLUWSM",
    "940GZZLUSJP",
    "940GZZLUVIC",
    "940GZZLUSSQ",
    "940GZZLUSKT",
    "940GZZLUGTR",
]


alternative_station_names = {  # in currentLocation or towards values
    "Shepherd's Bush": "940GZZLUSBC",
    "Kings Cross": "940GZZLUKSX",
    "King's Cross": "940GZZLUKSX",
    "Kings Cross St. Pancras": "940GZZLUKSX",
    "Elephant and Castle": "940GZZLUEAC",
    "Harrow and Wealdstone": "940GZZLUHAW",
    "Harrow-On-The-Hill": "940GZZLUHOH",
    "Edgware Road (Circle)": "940GZZLUERC",
    "Regents Park": "940GZZLURGP",
    "Heathrow Terminal 1,2,3": "940GZZLUHRC",
    "Chalfont and Latimer": "940GZZLUCAL",
}


alternative_terminus_names = {  # in towards values
    "Heathrow T123 + 5": "940GZZLUHR5",
    "Heathrow via T4 Loop": "940GZZLUHR4",
}


alternative_station_names_ambiguous = {
    "Edgware Road": {
        "bakerloo": "940GZZLUERB",
        "circle": "940GZZLUERC",
        "district": "940GZZLUERC",
        "hammersmith-city": "940GZZLUERC",
    },
    "Hammersmith": {
        "district": "940GZZLUHSD",
        "piccadilly": "940GZZLUHSD",
        "circle": "940GZZLUHSC",
        "hammersmith-city": "940GZZLUHSC",
    },
}


non_station_locations = [
    "Newbury Park Loop",
    "North Acton Junction",
    "Leaving Stanmore",
    "Wood Green Sidings",
    "Northolt Sidings",
]


platform_name_prefix_direction = {  # tight matching
    "Westbound - Platform ": "Westbound",
    "Eastbound - Platform ": "Eastbound",
    "Northbound - Platform ": "Northbound",
    "Southbound - Platform ": "Southbound",
    "Northbound Fast - Platform ": "Northbound",
    "Southbound Fast - Platform ": "Southbound",
    "Outer Rail - Platform ": "Outer Rail",
    "Inner Rail - Platform ": "Inner Rail",
    "Westbound Platform ": "Westbound",
    "WestBound - Platform ": "Westbound",
    "EastBound - Platform ": "Eastbound",
}


hainault_loop_outer_rail_outbound_stations = [
    "940GZZLURVY",
    "940GZZLUCWL",
    "940GZZLUGGH",
]


hainault_loop_real_canonical_directions = [  # reserved for possible future use
    # match outbound = Eastbound, inbound = Westbound
    # north of HLT, Outer Rail is Eastbound
    {
        "stations": ["940GZZLURVY", "940GZZLUCWL", "940GZZLUGGH"],
        "Outer Rail": "outbound",
        "Inner Rail": "inbound",
    },
    # HLT => depends if arriving/departing
    {
        "stations": ["940GZZLUHLT"],
        "Outer Rail": {
            "arrival": "outbound",
            "departure": "inbound",
        },
        "Inner Rail": {
            "arrival": "inbound",
            "departure": "outbound",
        },
    },
    # south of HLT, Outer Rail is Westbound
    {
        "stations": [
            "940GZZLUFLP",
            "940GZZLUBKE",
            "940GZZLUNBP",
            "940GZZLUGTH",
            "940GZZLURBG",
            "940GZZLUWSD",
        ],
        "Outer Rail": "inbound",
        "Inner Rail": "outbound",
    },
]


def stoppoints_by_line(line_id: str):
    line_data_file_name = DATA_PATH / (line_id + ".json")

    if os.path.exists(line_data_file_name):
        # read data from file if it exists
        with open(line_data_file_name, "r", encoding="utf-8") as line_data_file:
            stoppoints = json.load(line_data_file)

    else:
        # download missing line data otherwise
        stoppoints = api.line_stoppoints(line_id)
        with open(line_data_file_name, "w") as line_data_file:
            json.dump(stoppoints, line_data_file)

    return stoppoints


def add_line_data_to_stations_dict(stations_dict: dict, line_id: str):
    stoppoints = stoppoints_by_line(line_id)

    # process stop point data
    for stoppoint in stoppoints:
        # new station
        if stoppoint["naptanId"] not in stations_dict:
            stations_dict[stoppoint["naptanId"]] = {
                "commonName": stoppoint["commonName"],
                "lines": [],
            }

            # friendly name
            if stoppoint["commonName"].endswith(" Underground Station"):
                stations_dict[stoppoint["naptanId"]]["name"] = helpers.rchop(
                    stoppoint["commonName"], " Underground Station"
                )
            elif stoppoint["commonName"].endswith("-Underground"):
                # for "Paddington (H&C Line)-Underground" (PAH)
                stations_dict[stoppoint["naptanId"]]["name"] = helpers.rchop(
                    stoppoint["commonName"], "-Underground"
                )

        # add current line
        stations_dict[stoppoint["naptanId"]]["lines"].append(line_id)

    return stations_dict


def _stations(data_path, stations_data_filename):
    # read from stations data file if available
    stations_data_file_path = data_path / stations_data_filename
    if stations_data_file_path.exists():
        with stations_data_file_path.open(mode="r", encoding="utf-8") as stations_file:
            stations = json.load(stations_file)
        return stations

    # otherwise generate data from individual line files
    stations = {}
    for line_id in lines:
        stations = add_line_data_to_stations_dict(_stations, line_id)

    # read data from file
    with open(stations_data_file_path, "w") as stations_file:
        json.dump(_stations, stations_file)

    return stations


def _station_id_by_name(stations):
    return {stations[station_id]["name"]: station_id for station_id in stations}


STATIONS = _stations(DATA_PATH, STATIONS_DATA_FILENAME)
STATION_ID_BY_NAME = _station_id_by_name(STATIONS)
