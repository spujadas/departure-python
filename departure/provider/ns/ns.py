"""
Core functions for Nederlandse Spoorwegen
"""

from . import api, data, commons


def check_params(station_code: str):
    stations = data.STATIONS_BY_NS_CODE

    if station_code not in stations:
        raise commons.NSException(f"invalid station code {station_code}")


def departures_with_schedule(
    station_code: str, timetable_for_all_trains: bool = False
) -> list:
    trains = departures(station_code)

    for train in trains:
        train["schedule"] = stops(train["train_number"])
        if not timetable_for_all_trains:
            break  # then stop after first train

    return trains


def departures(station_code: str) -> list:
    check_params(station_code)

    departures_json = api.departures(station_code)

    trains = []

    for current_departure in departures_json["payload"]["departures"]:
        if "plannedTrack" in current_departure:
            track = current_departure["plannedTrack"]
        else:
            track = ""

        trains.append(
            {
                "direction": current_departure["direction"],
                "train_long_name": current_departure["name"],
                "planned_time": current_departure["plannedDateTime"][11:16],
                "actual_time": current_departure["actualDateTime"][11:16],
                "track": track,
                "train_number": current_departure["product"]["number"],
                "train_category": current_departure["product"]["longCategoryName"],
                "train_operator": current_departure["product"]["operatorName"],
            }
        )

    return trains


def stops(train_number: str) -> list:
    journey_json = api.journey(train_number)

    schedule = []
    for stop in journey_json["payload"]["stops"]:
        if "arrivals" in stop:
            direction = "arrivals"
        elif "departures" in stop:
            direction = "departures"
        else:
            continue

        planned_time = stop[direction][0]["plannedTime"][11:16]
        if "actualTime" in stop[direction][0]:
            actual_time = stop[direction][0]["actualTime"][11:16]
        else:
            actual_time = f"{planned_time}t"

        schedule.append(
            {
                "stop_name": stop["stop"]["name"],
                "stop_uic": stop["stop"]["uicCode"],
                "planned_time": planned_time,
                "actual_time": actual_time,
            }
        )

    return schedule


def search(station_name_query: str) -> dict:
    stations = data.STATIONS_BY_NS_CODE
    station_name_query = str(station_name_query).lower()

    results = {}

    for station_code in stations:
        if station_name_query in stations[station_code]["name_long"].lower():
            results[station_code] = stations[station_code]

    return results
