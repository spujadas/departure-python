from . import data, commons, api


def check_params(station_id: str = None):
    if not any((station_id)):
        return

    stations = data.STATIONS

    if station_id is not None:
        try:
            _ = stations[station_id]
        except Exception as e:
            raise commons.TransilienException(
                f"invalid station code {station_id}"
            ) from e


def stations_by_string(string):
    string = str(string).lower()
    results = {}
    stations = data.STATIONS

    # iterate over stations
    for station_id in stations:
        # match?
        if string in stations[station_id]["nom"].lower():
            results[station_id] = stations[station_id]

    return results


def next_trains(station_id: str):
    # check parameters
    check_params(station_id)

    # get trains departing from station
    departures = api.departures(station_id)

    if departures is None:
        return []

    trains = []

    for train in departures.iter("train"):
        terminus_id = train.find("term").text
        trains.append(
            {
                # extract time from date (formatted as "16/08/2020 20:07")
                "time": train.find("date").text[-5:],
                "mission": train.find("miss").text,
                "terminus_id": terminus_id,
                "terminus": terminus_name(terminus_id),
            }
        )

    return trains


def terminus_name(terminus_id: str) -> str:
    if terminus_id in data.STATIONS:
        return data.STATIONS[terminus_id]["nom"]

    if terminus_id in data.STATIONS_FRANCE:
        return data.STATIONS_FRANCE[terminus_id]["nom"]

    return "???"
