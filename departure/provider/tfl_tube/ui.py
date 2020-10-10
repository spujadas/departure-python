"""
UI for TfL tube
"""

from tabulate import tabulate

import departure.commons.helpers as helpers
from . import data


def expanded_station_id(station_id: str) -> str:
    station_id = station_id.upper()
    if len(station_id) == 3:
        return "940GZZLU" + station_id
    return station_id


def expanded_direction(direction: str) -> str:
    direction = direction.lower()
    return {
        "w": "Westbound",
        "e": "Eastbound",
        "s": "Southbound",
        "n": "Northbound",
        "i": "Inner Rail",
        "o": "Outer Rail",
    }.get(direction[0], direction)


def expanded_line_id(line_id: str) -> str:
    line_id = line_id.lower()
    if line_id[0] == "c":
        return {
            "ce": "central",
            "ci": "circle",
        }.get(line_id[:2], line_id)
    return {
        "b": "bakerloo",
        "d": "district",
        "h": "hammersmith-city",
        "j": "jubilee",
        "m": "metropolitan",
        "n": "northern",
        "p": "piccadilly",
        "v": "victoria",
        "w": "waterloo-city",
    }.get(line_id[0], line_id)


def list_lines() -> None:
    table = []
    for line_id in data.lines:
        for canonical_direction in data.lines[line_id]["canonical_directions"]:
            table.append(
                [
                    line_id,
                    canonical_direction,
                    data.lines[line_id]["canonical_directions"][canonical_direction],
                ]
            )

    print(tabulate(table, headers=["line id", "direction", "direction (alt.)"]))


def list_stations(stations=None) -> None:
    # default: list all stations
    if not stations:
        stations = data.STATIONS

    print(
        tabulate(
            [
                [
                    station_id,
                    stations[station_id]["name"],
                    " ".join(stations[station_id]["lines"]),
                ]
                for station_id in sorted(stations)
            ],
            headers=["station id", "station name", "line ids"],
        )
    )

    print(f"> total: {len(stations)}")


def list_trains_single_station(trains: dict):
    table = []
    i = 1

    # populate table
    for train in sorted(trains.values(), key=lambda a: a["time_to_station"]):
        table.append(
            [
                helpers.ordinal_en(i),
                train["towards"],
                helpers.arrival_time_en(train["time_to_station"]),
            ]
        )
        i += 1

    print(tabulate(table, tablefmt="plain"))


def list_trains_multiple_stations(trains: dict):
    # reorganise by station
    trains_by_station = {}

    for train_id in trains:
        station_id = trains[train_id]["station_id"]
        if station_id not in trains_by_station:
            trains_by_station[station_id] = {}
        trains_by_station[station_id][train_id] = trains[train_id]

    # list by station
    for station_id in trains_by_station:
        print(station_id)
        list_trains_single_station(trains_by_station[station_id])
        print()
