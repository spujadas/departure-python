"""
UI for Nederlandse Spoorwegen
"""

from tabulate import tabulate

import departure.commons.helpers as helpers
from . import data


def list_departures_with_schedule(
    departures_with_schedule: list, current_station_ns_code: str
) -> None:
    """List departures with schedule.

    Args:
        departures_with_schedule (list): departures with schedule, as returned by
            ns.departures_with_schedule
        current_station_ns_code (str): NS code of the current station, used to only
            show stops after the current station
    """
    for i, train in enumerate(departures_with_schedule):
        print(
            f'{helpers.ordinal_en(i+1)} {train["train_number"]} '
            f'{train["direction"]} ',
            end="",
        )
        if train["actual_time"] == train["planned_time"]:
            print(f'{train["actual_time"]}', end="")
        else:
            print(f'*{train["actual_time"]} ({train["planned_time"]})', end="")
        print(f' ({train["train_category"]})')

        if "schedule" in train:
            print_schedule(train["schedule"], current_station_ns_code)


def print_schedule(schedule: list, current_station_ns_code: str):
    stations_by_uic = data.STATIONS_BY_UIC
    current_station_uic = data.STATIONS_BY_NS_CODE[current_station_ns_code]["uic"]
    before_current_station = True

    stops = []
    for stop in schedule:
        # ignore stops before current station
        if stop["stop_uic"] == current_station_uic:
            before_current_station = False
            continue

        if before_current_station:
            continue

        # print schedule after current station
        if stop["stop_uic"] in stations_by_uic:
            stop_name = stations_by_uic[stop["stop_uic"]]["name_medium"]
        else:  # don't attempt to resolve using UIC if stop is outside NL
            stop_name = f"{stop['stop_name']}"
        stops.append(f"{stop_name} ({stop['actual_time']} / {stop['planned_time']})")

    print(f"  Calling at: {', '.join(stops)}")


def list_stations(stations: list):
    print(
        tabulate(
            [
                [
                    station_id,
                    stations[station_id]["uic"],
                    stations[station_id]["name_medium"],
                    stations[station_id]["name_long"],
                ]
                for station_id in sorted(
                    stations, key=lambda i: stations[i]["name_long"]
                )
            ],
            headers=["NS code", "UIC", "name (medium)", "name (long)"],
        )
    )

    print(f"> total: {len(stations)}")


def print_station_by_ns_code(ns_code: str):
    stations = data.STATIONS_BY_NS_CODE

    if ns_code in stations:
        print(f"{stations[ns_code]['name_long']} ({stations[ns_code]['uic']})")
    else:
        print(f"! invalid NS code: {ns_code}")
