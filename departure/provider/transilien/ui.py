from tabulate import tabulate

from . import data


def list_stations(stations=None):
    # default: list all stations
    if stations is None:
        stations = data.STATIONS

    print(
        tabulate(
            [
                [
                    station_id,
                    stations[station_id]["nom"],
                    stations[station_id]["libelle"],
                ]
                for station_id in sorted(stations)
            ],
            headers=["id", "name", "label"],
        )
    )

    print(f"> total: {len(stations)}")


def list_trains(trains):
    print(
        tabulate(
            [
                [train["mission"], train["time"], train["terminus"]]
                for train in trains
            ],
            tablefmt="plain"
        )
    )
