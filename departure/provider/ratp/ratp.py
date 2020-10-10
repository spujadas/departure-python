from . import api, commons


def check_params(line_id: str, station_id: str, direction_sens: str):
    response = api.get_missions_next(line_id, station_id, direction_sens)

    # invalid station
    if response.ambiguityMessage is not None:
        raise commons.RatpException(
            "invalid line code and/or station code and/or direction"
        )


def lines_by_name(name_query: str = ""):
    results = []

    # get all lines
    lines = api.get_lines_realtime_realm()

    # filter by name
    for line in sorted(lines, key=lambda k: k["code"]):
        # ignore lines that do not contain query string
        if name_query not in line.name.lower():
            continue

        results.append(simplified_line_data(line))
    return results


def lines_by_code(code_query):
    results = []

    lines = api.get_lines_by_code(code_query)

    for line in sorted(lines, key=lambda k: k["code"]):
        # stop if no results
        if line["id"] is None:
            break

        results.append(simplified_line_data(line))

    return results


def simplified_line_data(line):
    if line.image is None:
        # image = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
        image = ""
    else:
        image = f"http://opendata-tr.ratp.fr/wsiv/static/line/{line.image}"

    return {
        "id": line.id,
        "reseau": line.reseau.name,
        "code": line.code,
        "name": line.name,
        "image": image,
    }


def simplified_station_data(station: dict) -> dict:
    return {
        "name": station.name,
        "line_station_id": station.id,
        "line": simplified_line_data(station.line),
    }


def directions(line_id: str) -> dict:
    response = api.get_directions(line_id)

    results = {}
    for direction in response.directions:
        results[direction.sens] = direction.name

    return results


def stations_by_line(line_id: str) -> list:
    stations = api.get_stations_by_line(line_id)

    results = []
    for station in stations:
        results.append(simplified_station_data(station))

    return results


def stations_by_name(name_query: str) -> list:
    response = api.get_stations_by_name(name_query)

    results = []
    for station in response.stations:
        results.append(simplified_station_data(station))

    return results


def next_departures(line_id: str, station_id: str, direction_sens: str) -> dict:
    response = api.get_missions_next(line_id, station_id, direction_sens)

    # invalid station
    if response.ambiguityMessage is not None:
        raise commons.RatpException("invalid station code and/or direction")

    missions = []
    for mission in response.missions:
        # handle case where service has ended
        if len(mission.stations) > 1:
            destination_name = mission.stations[1].name
        else:
            destination_name = "---"

        if len(mission.stationsDates) > 0:
            stations_date = mission.stationsDates[0]
        else:
            stations_date = "------------"

        missions.append(
            {
                "code": mission.code,
                "destinationName": destination_name,
                "datetime": stations_date,
                # 'platform': mission.stationsPlatforms[0],  # only for RER
                "message": mission.stationsMessages[0],
            }
        )

    if len(response.perturbations) > 0:
        perturbations = response.perturbations[0].message.text
    else:
        perturbations = ""

    return {"missions": missions, "perturbations": perturbations}
