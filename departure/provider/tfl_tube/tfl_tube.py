import logging
from typing import List, Any
import re

from . import data, api, commons

logger = logging.getLogger(__name__)


def check_params(line_ids: List[str] = None, station_id=None, direction=None):
    if not any((line_ids, station_id, direction)):
        return

    stations = data.STATIONS

    if station_id is not None:
        try:
            station = stations[station_id]
        except Exception as e:
            raise commons.TflTubeException(f"invalid station id {station_id}") from e

    if line_ids is not None:
        for line_id in line_ids:
            if line_id not in data.lines:
                raise commons.TflTubeException(f"invalid line id {line_id}")
            if (station_id is not None) and (line_id not in station["lines"]):
                raise commons.TflTubeException(
                    f"station/line mismatch for {station_id}/{line_id}"
                )

    if direction is not None:
        for line_id in line_ids:
            if direction not in data.lines[line_id]["canonical_directions"]:
                raise commons.TflTubeException(
                    f"invalid direction {direction} for {line_id}"
                )


def stations_by_string(string: str) -> dict:
    string = str(string).lower()
    results = {}
    stations = data.STATIONS

    # iterate over stations
    for station_id in stations:
        # match?
        if string in stations[station_id]["name"].lower():
            results[station_id] = stations[station_id]

    return results


def lines() -> list:
    return {line_id: data.lines[line_id]["name"] for line_id in data.lines}


def stations_by_line(line_id: str) -> dict:
    results = {}
    stations = data.STATIONS
    stoppoints = data.stoppoints_by_line(line_id)

    for stoppoint in stoppoints:
        results[stoppoint["naptanId"]] = stations[stoppoint["naptanId"]]

    return results


def directions(line_id: str) -> dict:
    return list(data.lines[line_id]["canonical_directions"].keys())


def location_platform_from_current_location(current_location: str):
    """Parses currentLocation: "At ..." -> (location, platform_number)"""

    # ignore if not *at* a location
    if not current_location.startswith("At "):
        return None, None

    # discard initial 'At '
    current_location = current_location[3:]

    # at current station/platform (i.e. "[At ]Platform")
    if current_location == "Platform":
        return "<current>", "<current>"  # special values

    # with station and platform, supporting the following alternatives
    # - "Manor House Platform 1" (normal)
    # - "East Finchley, Platform 1" (extra comma)
    # - "London Bridge Plaform 1" (typo)
    # - "Kings Cross P7" (abbreviation)
    station_platform = re.match(r"^(.*?),? P(?:lat?form )?(\d+)$", current_location)

    if station_platform is not None:
        return station_platform.group(1), station_platform.group(2)

    # without platform number (e.g. "[At ]Angel platform")
    if current_location.endswith(" platform"):
        return current_location[: -len(" platform")], None

    # no mention of platform
    if "Platform" not in current_location:
        return current_location, None

    return None, None


def station_from_location(location_name: str, current_station_id: str, line_id: str):
    if location_name is None:
        return None

    # actual stations
    if location_name in data.STATION_ID_BY_NAME:
        return data.STATION_ID_BY_NAME[location_name]

    if location_name == "<current>":
        return current_station_id

    # alternative stations names
    if location_name in data.alternative_station_names:
        return data.alternative_station_names[location_name]

    # ambiguous alternative stations names (resolve through line)
    if location_name in data.alternative_station_names_ambiguous:
        return data.alternative_station_names_ambiguous[location_name][line_id]

    # known non-stations
    if location_name in data.non_station_locations:
        return None

    logger.warning("unresolved location %s", location_name)
    return None


def filter_trains_by_direction_of_departure(
    arrivals: List[Any],
    requested_direction: str,
    conservative: bool = False,  # also match uncertain directions
):
    trains = {}

    for arrival in arrivals:
        # extract train id
        line_id = arrival["lineId"]
        vehicle_id = arrival["vehicleId"]

        # ignore duplicate trains
        train_id = f"{line_id}-{vehicle_id}"
        if train_id in trains:
            continue

        # extract train data
        station_id = arrival["naptanId"]
        towards_station_id = station_id_from_towards(arrival["towards"], line_id)
        platform_departure_direction = departure_direction_from_platform_name(
            arrival["platformName"]
        )
        train_canonical_direction = arrival.get("direction", None)
        destination_station_id = arrival.get("destinationNaptanId", None)

        # check if will depart in requested direction
        will_depart_in_requested_direction = (
            will_arriving_train_depart_from_station_in_direction(
                line_id,
                station_id,
                requested_direction,
                towards_station_id,
                platform_departure_direction=platform_departure_direction,
                train_canonical_direction=train_canonical_direction,
                destination_station_id=destination_station_id,
            )
        )

        # ignore if not departing in requested direction
        if not will_depart_in_requested_direction:
            continue

        # ignore if can't determine departing direction and conservative
        if will_depart_in_requested_direction is None and conservative:
            continue

        train = {
            "line_id": line_id,
            "vehicle_id": vehicle_id,
            "station_id": station_id,
            "towards": arrival["towards"],
            "towards_station_id": towards_station_id,
            "platform_name": arrival["platformName"],
            "platform_number": number_from_platform_name(arrival["platformName"]),
            "destination_station_id": destination_station_id,
            "time_to_station": arrival["timeToStation"],
        }

        trains[train_id] = train

    return trains


def current_station_platform_number_from_current_location(
    current_location: str, line_id: str, station_id: str, platform_name: str
):
    at_location, at_platform_number = location_platform_from_current_location(
        current_location
    )

    if at_platform_number == "<current>":
        at_platform_number = number_from_platform_name(platform_name)

    at_station_id = station_from_location(at_location, station_id, line_id)

    return at_station_id, at_platform_number


def filter_trains_currently_at_platform(
    arrivals: List[Any],
    line_ids: List[str] = None,
    requested_station_id: str = None,
    requested_direction: str = None,
):
    trains = {}
    processed_trains = set()

    for arrival in arrivals:
        # extract train id
        line_id = arrival["lineId"]
        vehicle_id = arrival["vehicleId"]

        # ignore duplicate trains
        train_id = f"{line_id}-{vehicle_id}"
        if train_id in processed_trains:
            continue
        else:
            processed_trains.add(train_id)

        # extract train data
        line_id = arrival["lineId"]
        station_id = arrival["naptanId"]
        platform_departure_direction = departure_direction_from_platform_name(
            arrival["platformName"]
        )
        train_canonical_direction = arrival.get("direction", None)
        destination_station_id = arrival.get("destinationNaptanId", None)
        towards_station_id = station_id_from_towards(arrival["towards"], line_id)

        # get current station id
        (
            current_station_id,
            current_platform,
        ) = current_station_platform_number_from_current_location(
            arrival["currentLocation"], line_id, station_id, arrival["platformName"]
        )

        # ignore if train not at a station
        if current_station_id is None:
            continue

        # ignore if train is not on one of the requested lines
        if line_ids is not None and line_id not in line_ids:
            continue

        # ignore if train is not at requested station
        if (
            requested_station_id is not None
            and current_station_id != requested_station_id
        ):
            continue

        # ignore if train not in requested direction
        if (
            requested_direction is not None
            and not will_arriving_train_depart_from_current_location_in_direction(
                current_station_id,
                line_id,
                station_id,
                requested_direction,
                towards_station_id,
                platform_departure_direction,
                train_canonical_direction,
                destination_station_id,
            )
        ):
            continue

        # create item for train at platform
        train = {
            "line_id": line_id,
            "vehicle_id": vehicle_id,
            "station_id": current_station_id,
            "towards": arrival["towards"],
            "towards_station_id": towards_station_id,
            "platform_number": current_platform,
            "destination_station_id": destination_station_id,
            "time_to_station": 0,
        }

        trains[train_id] = train

    return trains


def next_trains(line_id: str, station_id: str, requested_direction: str = None):
    # check parameters
    check_params([line_id], station_id, requested_direction)

    # include merged lines
    line_ids = [line_id] + data.lines[line_id].get("merged_lines", [])

    # get trains arriving at station
    arrivals = api.line_arrivals(line_ids, station_id=station_id)
    if arrivals is None:
        return {}

    # filter by direction if requested
    if requested_direction is not None:
        trains = filter_trains_by_direction_of_departure(arrivals, requested_direction)

    # get all trains including those at station of interest
    arrivals = api.tube_arrivals(count=2)  # use -1 for debugging
    if arrivals is None:
        return trains

    # filter by current station (and direction of departure if requested)
    trains_currently_at_platform = filter_trains_currently_at_platform(
        arrivals, line_ids, station_id, requested_direction
    )

    # merge next and current (will overwrite next)
    trains.update(trains_currently_at_platform)

    return trains


def number_from_platform_name(platform_name: str):
    if "Platform " in platform_name:
        return platform_name.split("Platform ")[1]
    return None


def departure_direction_from_platform_name(platform_name: str):
    # platform name contains both direction and platform number
    for prefix in data.platform_name_prefix_direction:
        if platform_name.startswith(prefix):
            return data.platform_name_prefix_direction[prefix]

    # otherwise need to figure out things differently
    return None


def canonical_direction_from_platform_direction(line_id, direction):
    if line_id not in data.lines or line_id == "circle":
        return None

    try:
        return data.lines[line_id]["canonical_directions"][direction]
    except Exception:  # pylint: disable=broad-except
        pass  # passthrough to default

    return None


def circle_line_rail_arriving_at_station(
    station_id: str,
    platform_departure_direction: str = None,
    destination_station_id: str = None,
    towards_station_id: str = None,
):
    # if destination is known
    if destination_station_id is not None:
        try:
            return data.lines["circle"]["termini"][destination_station_id][
                "arrival_rail"
            ]
        except Exception:  # pylint: disable=broad-except
            pass

    # if towards is known
    if towards_station_id is not None:
        try:
            return data.lines["circle"]["termini"][towards_station_id]["arrival_rail"]
        except Exception:  # pylint: disable=broad-except
            pass

    # if direction is known from platform name (should cover remaining cases)
    if platform_departure_direction == "Westbound":
        if station_id in data.circle_line_outer_rail_westbound_stations:
            return "Outer Rail"
        else:
            return "Inner Rail"
    elif platform_departure_direction == "Eastbound":
        if station_id in data.circle_line_outer_rail_westbound_stations:
            return "Inner Rail"
        else:
            return "Outer Rail"

    # should never happen
    return None


def inverse_canonical_direction(canonical_direction):
    return {"inbound": "outbound", "outbound": "inbound"}.get(canonical_direction, None)


def canonical_direction_of_train_from_station_terminating_at(
    line_id, station_id, terminus_station_id
):
    # normal terminating direction
    try:
        terminating_canonical_direction = data.lines[line_id]["canonical_directions"][
            data.lines[line_id]["termini"][terminus_station_id]["arrival"]
        ]
    except Exception:  # pylint: disable=broad-except
        return None  # not a terminus

    # handle stations with inverse terminating directions at inline stations,
    # e.g. trains from EBY/central at end of service, terminating at WYC
    # (normally a Westbound inline terminus)
    try:
        if (
            data.lines[line_id]["termini"][terminus_station_id]["is_inline"]
            and station_id
            in data.lines[line_id]["termini"][terminus_station_id][
                "stations_inverse_terminating_direction"
            ]
        ):
            terminating_canonical_direction = inverse_canonical_direction(
                terminating_canonical_direction
            )
    except Exception:  # pylint: disable=broad-except
        pass

    return terminating_canonical_direction


def resolve_train_canonical_direction(
    line_id: str,
    station_id: str,
    towards_station_id: str = None,
    destination_station_id: str = None,
    platform_direction: str = None,
    train_canonical_direction: str = None,
):
    """
    not at terminus: arrival == departure
    """

    current_canonical_direction = None
    are_canonical_directions_coherent = True

    # resolve from towards
    if towards_station_id is not None:
        towards_canonical_direction = (
            canonical_direction_of_train_from_station_terminating_at(
                line_id, station_id, towards_station_id
            )
        )
        if towards_canonical_direction is not None:
            # update resolved direction
            current_canonical_direction = towards_canonical_direction

    # resolve from destination
    if destination_station_id is not None:
        destination_canonical_direction = (
            canonical_direction_of_train_from_station_terminating_at(
                line_id, station_id, destination_station_id
            )
        )

        if destination_canonical_direction is not None:
            # update resolved direction and coherence check
            if current_canonical_direction is None:
                current_canonical_direction = destination_canonical_direction
            else:
                are_canonical_directions_coherent &= (
                    current_canonical_direction == destination_canonical_direction
                )

    # resolve from platform
    if platform_direction is not None:
        platform_canonical_direction = canonical_direction_from_platform_direction(
            line_id, platform_direction
        )

        # update resolved direction and coherence check
        if current_canonical_direction is None:
            current_canonical_direction = platform_canonical_direction
        else:
            are_canonical_directions_coherent &= (
                current_canonical_direction == platform_canonical_direction
            )

    # use declared canonical direction otherwise
    # e.g. at LGN central inbound 'Platform 2/3'
    #      or WCY central outbound 'Platform 2/3'
    if train_canonical_direction is not None:
        # inverse declared canonical direction if north of HLT on HLT loop
        # (see data)
        if station_id in data.hainault_loop_outer_rail_outbound_stations:
            train_canonical_direction = inverse_canonical_direction(
                train_canonical_direction
            )

        if current_canonical_direction is None:
            current_canonical_direction = train_canonical_direction
        else:
            are_canonical_directions_coherent &= (
                current_canonical_direction == train_canonical_direction
            )

    if not are_canonical_directions_coherent:
        logger.warning(
            "incoherent direction at %s (%s): "
            "towards %s / destination %s / %s platform / %s",
            station_id,
            line_id,
            destination_station_id,
            towards_station_id,
            platform_direction,
            train_canonical_direction,
        )

    return current_canonical_direction


def will_arriving_train_depart_from_station_in_direction(
    line_id: str,
    station_id: str,
    requested_direction: str,
    towards_station_id: str,
    platform_departure_direction: str = None,
    train_canonical_direction: str = None,
    destination_station_id: str = None,
):
    # 1) check if current station is terminus
    is_station_terminus = is_station_terminus_for_train(
        line_id, station_id, destination_station_id, towards_station_id
    )

    # general case: won't depart if current station is terminus
    if is_station_terminus:
        return False

    # special case: if station *could* be a terminus but can't tell due to
    # missing information, consider that the station isn't a terminus
    if is_station_terminus is None:
        pass  # replace with return None (can't tell) or False (no) as needed

    # 2) on Circle Line (which only has one canonical direction for
    # all directions), resolve via inner/outer rail
    if line_id == "circle":
        # departure direction == arrival direction as not a terminus
        station_rail = circle_line_rail_arriving_at_station(
            station_id,
            platform_departure_direction=platform_departure_direction,
            destination_station_id=destination_station_id,
            towards_station_id=towards_station_id,
        )
        # can't determine
        if station_rail is None:
            return None

        requested_rail = circle_line_rail_arriving_at_station(
            station_id, platform_departure_direction=requested_direction
        )

        return station_rail == requested_rail

    # 3) general case: resolve via canonical direction
    requested_canonical_direction = canonical_direction_from_platform_direction(
        line_id, requested_direction
    )

    # get actual train canonical direction
    actual_train_canonical_direction = resolve_train_canonical_direction(
        line_id,
        station_id,
        towards_station_id=towards_station_id,
        destination_station_id=destination_station_id,
        platform_direction=platform_departure_direction,
        train_canonical_direction=train_canonical_direction,
    )

    if actual_train_canonical_direction is not None:
        return requested_canonical_direction == actual_train_canonical_direction

    # can't determine direction
    return None


def will_arriving_train_depart_from_current_location_in_direction(
    current_station_id: str,
    line_id: str,
    station_id: str,
    requested_direction: str,
    towards_station_id: str,
    platform_departure_direction: str = None,
    train_canonical_direction: str = None,
    destination_station_id: str = None,
):
    # 1) check if current station is terminus in arriving direction
    # test cases:
    # - depart from EBY towards HLT ~> will depart
    # - depart from EBY towards WCY ~> should depart (WTT id 110 p. 125)
    #   >> incoherent direction at 940GZZLUEBY (central):
    #      destination 940GZZLUWCY / towards 940GZZLUWCY / Eastbound platform
    #      / outbound
    is_current_station_terminus = is_station_terminus_for_train(
        line_id, current_station_id, destination_station_id, towards_station_id
    )

    # general case: won't depart if current station is terminus
    if is_current_station_terminus:
        return False

    # special case: if current station *could* be a terminus but can't tell
    # due to missing information, consider that the current station isn't a
    # terminus
    if is_current_station_terminus is None:
        pass  # replace with return None (can't tell) or False (no) as needed

    # 2) determine platform arrival direction
    is_station_terminus = is_station_terminus_for_train(
        line_id, station_id, destination_station_id, towards_station_id
    )

    # if train terminates at station, get arrival direction from terminus data
    if is_station_terminus:
        try:
            platform_arrival_direction = data.lines[line_id]["termini"][station_id][
                "arrival"
            ]
        except Exception:  # pylint: disable=broad-except
            return False
    # otherwise arrival direction and departure direction are identical
    else:
        platform_arrival_direction = platform_departure_direction

    # special case: if station *could* be a terminus but can't tell due to
    # missing information, consider that the station isn't a terminus
    if is_station_terminus is None:
        pass  # replace with return None (can't tell) or add as and to
        # previous if statement (consider as terminus)

    # 3) on Circle Line (which only has one canonical direction for all
    # directions), resolve directions via inner/outer rail
    if line_id == "circle":
        # departure direction == arrival direction as not a terminus
        station_rail = circle_line_rail_arriving_at_station(
            station_id,
            platform_departure_direction=platform_arrival_direction,
            destination_station_id=destination_station_id,
            towards_station_id=towards_station_id,
        )
        # can't determine
        if station_rail is None:
            return None

        requested_rail = circle_line_rail_arriving_at_station(
            current_station_id,
            platform_departure_direction=requested_direction,
        )
        return station_rail == requested_rail

    # 4) general case: resolve via canonical direction
    requested_canonical_direction = canonical_direction_from_platform_direction(
        line_id, requested_direction
    )

    # get actual train canonical direction
    actual_train_canonical_direction = resolve_train_canonical_direction(
        line_id,
        station_id,
        towards_station_id=towards_station_id,
        destination_station_id=destination_station_id,
        platform_direction=platform_arrival_direction,
        train_canonical_direction=train_canonical_direction,
    )

    if actual_train_canonical_direction is not None:
        return requested_canonical_direction == actual_train_canonical_direction

    # 5) can't determine direction
    return None


def station_id_from_station_name(station_name: str, line_id: str):
    try:
        return data.STATION_ID_BY_NAME[station_name]
    except Exception:  # pylint: disable=broad-except
        pass

    try:
        return data.alternative_station_names[station_name]
    except Exception:  # pylint: disable=broad-except
        pass

    try:
        return data.alternative_station_names_ambiguous[station_name][line_id]
    except Exception:  # pylint: disable=broad-except
        pass

    return None


def station_id_from_towards(towards: str, line_id: str):
    if towards == "Check Front of Train":
        return None

    try:
        return data.alternative_terminus_names[towards]
    except Exception:  # pylint: disable=broad-except
        pass

    if " via " in towards:
        station_name = towards.split(" via ")[0]
    elif " Via " in towards:
        station_name = towards.split(" Via ")[0]
    else:
        station_name = towards

    return station_id_from_station_name(station_name, line_id)


def is_station_terminus_for_train(
    line_id,
    station_id,
    destination_station_id: str = None,
    towards_station_id: str = None,
):
    # if destination is known and same as station
    if destination_station_id is not None:
        return station_id == destination_station_id

    # if towards (e.g. "Edgware via CX") resolves to requested station
    if towards_station_id is not None:
        return station_id == towards_station_id

    # if station is a terminus
    if station_id in data.lines[line_id]["termini"]:
        # can't tell if inline (e.g. BKG/HLT), no destinationNaptanId,
        # towards="Check Front of Train"
        if data.lines[line_id]["termini"][station_id]["is_inline"]:
            return None
        # non-inline (e.g. WIM)
        return True

    # default: not a terminus (caveat: false negative if abnormal service
    # with no information on destination)
    return False
