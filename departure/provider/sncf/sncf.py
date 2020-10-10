from . import data, commons, api


def check_params(stop_area_id: str = None):
    if not any((stop_area_id)):
        return

    stations = data.STATIONS

    if stop_area_id is not None:
        try:
            _ = stations[stop_area_id]
        except Exception as e:
            raise commons.SncfException(f"invalid stop area id {stop_area_id}") from e


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


def timetable_from_disruptions(disruptions):
    timetable = []

    impacted_stops = disruptions["disruptions"][0]["impacted_objects"][0][
        "impacted_stops"
    ]

    for impacted_stop in impacted_stops:
        # rewrite times from '162300' to '16:23'
        base_departure_time = impacted_stop["base_departure_time"]
        base_departure_time = f"{base_departure_time[:2]}:{base_departure_time[2:4]}"

        # determine (and rewrite) amended departure time
        if (impacted_stop["departure_status"] == "delayed") or (
            impacted_stop["departure_status"] == "unchanged"
        ):
            amended_departure_time = impacted_stop["amended_departure_time"]
            amended_departure_time = (
                f"{amended_departure_time[:2]}:{amended_departure_time[2:4]}"
            )
        elif impacted_stop["departure_status"] == "deleted":
            amended_departure_time = "--:--"
        else:  # 'added' - FIXME? may crash as never seen before
            amended_departure_time = "??:??"

        timetable.append(
            {
                "id": impacted_stop["stop_point"]["id"],
                "name": impacted_stop["stop_point"]["name"],
                "base_departure_time": base_departure_time,
                "amended_departure_time": amended_departure_time,
            }
        )

    return timetable


def timetable_from_vehicle_journeys(vehicle_journeys):
    timetable = []

    stop_times = vehicle_journeys["vehicle_journeys"][0]["stop_times"]

    for stop_time in stop_times:
        # rewrite time from '162300' to '16:23'
        departure_time = stop_time["departure_time"]
        departure_time = f"{departure_time[:2]}:{departure_time[2:4]}"

        timetable.append(
            {
                "id": stop_time["stop_point"]["id"],
                "name": stop_time["stop_point"]["name"],
                "base_departure_time": departure_time,
                "amended_departure_time": departure_time,
            }
        )

    return timetable


def timetable_from_departure(current_departure):
    timetable = []

    # schedule if disruption
    has_disruption = False
    for link in current_departure["display_informations"]["links"]:
        if link["type"] != "disruption":
            continue

        has_disruption = True
        disruptions = api.disruptions(link["id"])
        timetable = timetable_from_disruptions(disruptions)

        break

    if has_disruption and timetable != []:
        return timetable

    # schedule if normal traffic or disrupted schedule unresolved
    for link in current_departure["links"]:
        if link["type"] != "vehicle_journey":
            continue

        vehicle_journeys = api.vehicle_journeys(link["id"])
        timetable = timetable_from_vehicle_journeys(vehicle_journeys)

    return timetable


def next_trains(stop_area_id: str, timetable_for_all_trains: bool = False):
    # check parameters
    check_params(stop_area_id)

    # get trains departing from station
    departures = api.departures(stop_area_id)
    if departures is None:
        return []

    trains = []

    # extract data for each depature
    for i, current_departure in enumerate(departures["departures"]):
        # extract time for later rewrite (see below)
        departure_date_time = current_departure["stop_date_time"]["departure_date_time"]
        base_departure_date_time = current_departure["stop_date_time"][
            "base_departure_date_time"
        ]

        # remove city from direction, e.g. "Lyon-Part-Dieu (Lyon)" => "Lyon-Part-Dieu"
        direction = current_departure["display_informations"]["direction"]
        index_of_last_open_paren = direction.rfind("(")
        if index_of_last_open_paren != -1:
            direction = direction[: index_of_last_open_paren - 1]

        train_data = {
            "stop_point_id": current_departure["stop_point"]["id"],
            "direction": direction,
            "headsign": current_departure["display_informations"]["headsign"],
            # extract times from date (formatted as "20200822T203600")
            "base_time": f"{base_departure_date_time[-6:-4]}:{base_departure_date_time[-4:-2]}",
            "time": f"{departure_date_time[-6:-4]}:{departure_date_time[-4:-2]}",
            "commercial_mode": current_departure["display_informations"][
                "commercial_mode"
            ],
        }

        # get timetables for 2nd and following trains if requested
        if i == 0 or timetable_for_all_trains:
            train_data["timetable"] = timetable_from_departure(current_departure)

        trains.append(train_data)

    return trains
