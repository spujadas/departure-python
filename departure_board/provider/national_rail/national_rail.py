from typing import List, Any

from . import data, commons, api


def check_params(station_code: str) -> None:
    stations = data.STATIONS

    if station_code is not None:
        try:
            _ = stations[station_code]
        except Exception:
            raise commons.NationalRailException(
                f"invalid station code {station_code}"
            ) from Exception


def stations_by_string(string):
    string = str(string).lower().strip()
    results = {}
    stations = data.STATIONS

    # iterate over stations
    for station_id in stations:
        # match?
        if string in stations[station_id].lower():
            results[station_id] = stations[station_id]

    return results


def services_from_station_board_with_details(station_board_with_details):
    services = []

    # end here if no services
    if station_board_with_details.trainServices is None:
        return services

    try:
        for station_board_service in station_board_with_details.trainServices.service:
            services.append(
                {
                    "std": station_board_service.std,
                    "etd": station_board_service.etd,
                    "platform": station_board_service.platform,
                    "destination_location_name": station_board_service.destination.location[
                        0
                    ].locationName,
                    "origin_location_name": station_board_service.origin.location[
                        0
                    ].locationName,
                    "operator": station_board_service.operator,
                    "calling_points": [
                        {"location_name": cp.locationName, "st": cp.st, "et": cp.et}
                        for cp in station_board_service.subsequentCallingPoints.callingPointList[
                            0
                        ].callingPoint
                    ],
                }
            )
    except Exception:  # pylint: disable=broad-except
        return []

    return services


def next_services(station_code: str) -> List[Any]:
    # check parameters
    check_params(station_code)

    # get trains departing from station
    station_board_with_details = api.get_departure_board_with_details(station_code)
    services = services_from_station_board_with_details(station_board_with_details)

    return services
