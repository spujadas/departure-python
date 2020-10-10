from tabulate import tabulate

from . import data


def list_stations(stations=None):
    # default: list all stations
    if not stations:
        stations = data.STATIONS

    stations_table = []

    for station_id in sorted(stations):
        stations_table.append([station_id, stations[station_id]["nom"]])

    print(tabulate(stations_table, headers=["stop area id", "name"]))
    print(f"> total: {len(stations)}")


def print_timetable(timetable, current_stop_point_id):
    stop_points = []
    before_current_stop_point = True

    for stop_point in timetable:
        # ignore stops before current stop
        if stop_point["id"] == current_stop_point_id:
            before_current_stop_point = False
            continue

        if before_current_stop_point:
            continue

        # print timetable after current stop
        if stop_point["amended_departure_time"] == stop_point["base_departure_time"]:
            stop_points.append(
                f'{stop_point["name"]} ({stop_point["base_departure_time"]})'
            )
        else:
            stop_points.append(
                f'{stop_point["name"]} ({stop_point["amended_departure_time"]} | '
                f'{stop_point["base_departure_time"]})'
            )

    print(f'  Arrêts : {", ".join(stop_points)}')


def list_trains(trains):
    for train in trains:
        print(f'{train["headsign"]} {train["direction"]} ', end="")
        if train["time"] == train["base_time"]:
            print(f'{train["time"]}', end="")
        else:
            print(f'*{train["time"]} ({train["base_time"]})', end="")
        print(f' ({train["commercial_mode"]})')

        if "timetable" in train:
            print_timetable(train["timetable"], train["stop_point_id"])
