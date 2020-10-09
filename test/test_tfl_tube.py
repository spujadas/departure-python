import json
import pathlib

import departure.provider.tfl_tube.tfl_tube as tfl_tube

# pylint: disable=too-many-lines


class TestIsDepartingFromStationInDirection:
    # {
    #     'naptanId': '940GZZLULGN',
    #     'lineId': 'central',
    #     'platformName': 'Platform 2/3',
    #     'direction': 'inbound',
    #     'vehicleId': '114',
    #     'currentLocation': 'At Platform',
    #     'towards': 'Northolt'
    # }

    def test_no_platform_direction_actual_direction(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLULGN",
            "Westbound",
            "940GZZLUNHT",
            platform_departure_direction=None,
            train_canonical_direction="inbound",
        )

    def test_no_platform_direction_incorrect_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLULGN",
            "Eastbound",
            "940GZZLUNHT",
            platform_departure_direction=None,
            train_canonical_direction="inbound",
        )

    def test_no_platform_direction_equivalent_direction(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLULGN",
            "Outer Rail",
            "940GZZLUNHT",
            platform_departure_direction=None,
            train_canonical_direction="inbound",
        )

    def test_no_platform_direction_equivalent_incorrect_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLULGN",
            "Inner Rail",
            "940GZZLUNHT",
            platform_departure_direction=None,
            train_canonical_direction="inbound",
        )

    def test_hainault_loop_actual_south_of_hlt(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLUFLP",
            "Westbound",
            None,
            platform_departure_direction="Outer Rail",
            train_canonical_direction="inbound",
        )

    def test_hainault_loop_actual_south_of_hlt_no_direction(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLUFLP",
            "Westbound",
            None,
            platform_departure_direction="Outer Rail",
            train_canonical_direction=None,
        )

    def test_hainault_loop_actual_north_of_hlt(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLURVY",
            "Westbound",
            None,
            platform_departure_direction="Outer Rail",
            train_canonical_direction="outbound",
        )

    def test_hainault_loop_actual_north_of_hlt_no_canonical_dir(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "central",
            "940GZZLURVY",
            "Westbound",
            None,
            platform_departure_direction="Outer Rail",
        )

    def test_cannot_determine(self):
        assert (
            tfl_tube.will_arriving_train_depart_from_station_in_direction(
                "district",
                "940GZZLUVIC",
                "Westbound",
                None,
                platform_departure_direction=None,
                train_canonical_direction=None,
            )
            is None
        )

    def test_at_terminating_station_no_departure_in_arrival_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "district",
            "940GZZLUWIM",
            "Westbound",
            None,
            platform_departure_direction="Westbound",
            train_canonical_direction=None,
        )

    def test_at_terminating_station_no_departure_in_departure_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "district",
            "940GZZLUWIM",
            "Westbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction=None,
        )

    def test_at_inline_terminating_station_not_terminating_arr_direction(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Eastbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction=None,
            destination_station_id="940GZZLUSTD",
        )

    def test_at_inline_terminating_station_not_terminating_dep_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Westbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction=None,
            destination_station_id="940GZZLUSTD",
        )

    def test_at_inline_terminating_station_not_terminating_arr_can_dir(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Eastbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction="outbound",
            destination_station_id="940GZZLUSTD",
        )

    def test_at_inline_terminating_station_not_terminating_dep_can_dir(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Westbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction="outbound",
            destination_station_id="940GZZLUSTD",
        )

    def test_at_inline_terminating_station_has_destination_station_id(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Westbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction="outbound",
            destination_station_id="940GZZLUWYP",
        )

    def test_at_inline_terminating_station_has_towards_station_id(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Westbound",
            "940GZZLUWYP",
            platform_departure_direction="Eastbound",
            train_canonical_direction="outbound",
        )

    def test_at_inline_terminating_station_no_destination_dep_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Westbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction="outbound",
        )

    def test_at_inline_terminating_station_no_destination_arr_direction(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "jubilee",
            "940GZZLUWYP",
            "Eastbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction="outbound",
        )

    def test_mismatching_direction_canonical_direction(self, caplog):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "district",
            "940GZZLUEMB",
            "Eastbound",
            None,
            platform_departure_direction="Eastbound",
            train_canonical_direction="inbound",
        )
        assert caplog.text.endswith(
            "incoherent direction at 940GZZLUEMB "
            "(district): towards None / destination None / Eastbound "
            "platform / inbound\n"
        )

    def test_circle_terminating_at_erc_arr_platform_arr_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle",
            "940GZZLUERC",
            "Eastbound",
            "940GZZLUERC",
            platform_departure_direction="Eastbound",
        )

    def test_circle_terminating_at_erc_arr_platform_dep_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle",
            "940GZZLUERC",
            "Westbound",
            "940GZZLUERC",
            platform_departure_direction="Eastbound",
        )

    def test_circle_terminating_at_erc_dep_platform_arr_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle",
            "940GZZLUERC",
            "Eastbound",
            "940GZZLUERC",
            platform_departure_direction="Westbound",
        )

    def test_circle_terminating_at_erc_dep_platform_dep_direction(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle",
            "940GZZLUERC",
            "Westbound",
            "940GZZLUERC",
            platform_departure_direction="Westbound",
        )

    def test_circle_no_platform_south(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle", "940GZZLUWSM", "Westbound", "940GZZLUERC"
        )

    def test_circle_no_platform_north(self):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle", "940GZZLUBST", "Eastbound", "940GZZLUERC"
        )

    def test_circle_towards_erc_at_erc(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle", "940GZZLUERC", "Eastbound", "940GZZLUERC"
        )

    def test_circle_no_platform_no_destination_no_towards_at_erc(self):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle", "940GZZLUERC", "Eastbound", None
        )

    def test_circle_platform_no_destination_no_towards_at_erc_dep_dir(self):
        # not considered to be a terminus
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle",
            "940GZZLUERC",
            "Westbound",
            None,
            platform_departure_direction="Eastbound",
        )

    def test_circle_platform_no_destination_no_towards_at_erc_arr_dir(self):
        # not considered to be a terminus
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "circle",
            "940GZZLUERC",
            "Eastbound",
            None,
            platform_departure_direction="Eastbound",
        )

    def test_wrong_direction_prefer_platform_westbound(self, caplog):
        assert not tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "district",
            "940GZZLUWSM",
            "Westbound",
            "940GZZLUTWH",
            platform_departure_direction="Eastbound",
            train_canonical_direction="inbound",  # incoherent
        )
        assert caplog.text.endswith(
            "incoherent direction at 940GZZLUWSM "
            "(district): towards None / destination 940GZZLUTWH / Eastbound "
            "platform / inbound\n"
        )

    def test_wrong_direction_prefer_platform_eastbound(self, caplog):
        assert tfl_tube.will_arriving_train_depart_from_station_in_direction(
            "district",
            "940GZZLUWSM",
            "Eastbound",
            "940GZZLUTWH",
            platform_departure_direction="Eastbound",
            train_canonical_direction="inbound",  # incoherent
        )
        assert caplog.text.endswith(
            "incoherent direction at 940GZZLUWSM "
            "(district): towards None / destination 940GZZLUTWH / Eastbound "
            "platform / inbound\n"
        )


class TestIsStationTerminusForTrain:
    def test_destination_equals_station(self):
        assert tfl_tube.is_station_terminus_for_train(
            "circle", "940GZZLUERC", destination_station_id="940GZZLUERC"
        )

    def test_towards_equals_station(self):
        assert tfl_tube.is_station_terminus_for_train(
            "circle", "940GZZLUERC", towards_station_id="940GZZLUERC"
        )

    def test_terminus_end_of_line(self):
        assert tfl_tube.is_station_terminus_for_train("district", "940GZZLUWIM")


class TestDirectionFromPlatformName:
    def test_westbound(self):
        assert (
            tfl_tube.departure_direction_from_platform_name("Westbound - Platform 1")
            == "Westbound"
        )

    def test_eastbound(self):
        assert (
            tfl_tube.departure_direction_from_platform_name("Eastbound - Platform 1")
            == "Eastbound"
        )

    def test_northbound(self):
        assert (
            tfl_tube.departure_direction_from_platform_name("Northbound - Platform 1")
            == "Northbound"
        )

    def test_southbound(self):
        assert (
            tfl_tube.departure_direction_from_platform_name("Southbound - Platform 4")
            == "Southbound"
        )

    def test_northbound_fast(self):  # e.g. HOH
        assert (
            tfl_tube.departure_direction_from_platform_name(
                "Northbound Fast - Platform 3"
            )
            == "Northbound"
        )

    def test_southbound_fast(self):  # e.g. HOH
        assert (
            tfl_tube.departure_direction_from_platform_name(
                "Southbound Fast - Platform 6"
            )
            == "Southbound"
        )

    def test_outer(self):  # e.g. FLP
        assert (
            tfl_tube.departure_direction_from_platform_name(
                "Outer Rail - Platform 1",
            )
            == "Outer Rail"
        )

    def test_inner(self):  # e.g. FLP
        assert (
            tfl_tube.departure_direction_from_platform_name(
                "Inner Rail - Platform 2",
            )
            == "Inner Rail"
        )

    def test_westbound_no_dash(self):  # at WLO
        assert (
            tfl_tube.departure_direction_from_platform_name("Westbound Platform 26")
            == "Westbound"
        )

    def test_westbound_upper_b(self):  # at BDS
        assert (
            tfl_tube.departure_direction_from_platform_name("WestBound - Platform 2")
            == "Westbound"
        )

    def test_eastbound_upper_b(self):  # at BDS
        assert (
            tfl_tube.departure_direction_from_platform_name("EastBound - Platform 1")
            == "Eastbound"
        )

    def test_unmatched(self):  # at ASG
        assert (
            tfl_tube.departure_direction_from_platform_name(
                "Eastbound/Westbound - Platform 2/3"
            )
            is None
        )


class TestNumberFromPlatformName:
    def test_single(self):
        assert tfl_tube.number_from_platform_name("Westbound - Platform 1") == "1"

    def test_multiple(self):  # at ASG
        assert (
            tfl_tube.number_from_platform_name("Eastbound/Westbound - Platform 2/3")
            == "2/3"
        )

    def test_unmatched(self):  # at CSM
        assert tfl_tube.number_from_platform_name("North / South") is None


class TestStationIdFromTowards:
    def test_station_id_from_towards_normal(self):
        assert tfl_tube.station_id_from_towards("Hainault", "central") == "940GZZLUHLT"

    def test_station_id_from_towards_alt_name_ampersand(self):
        assert (
            tfl_tube.station_id_from_towards("Elephant and Castle", "bakerloo")
            == "940GZZLUEAC"
        )

    def test_station_id_from_towards_apostrophe(self):
        assert (
            tfl_tube.station_id_from_towards("Queen's Park", "bakerloo")
            == "940GZZLUQPS"
        )

    def test_station_id_from_towards_via_lowercase_v(self):
        assert (
            tfl_tube.station_id_from_towards("Hainault via Newbury Park", "central")
            == "940GZZLUHLT"
        )

    def test_station_id_from_towards_via_uppercase_v(self):
        assert (
            tfl_tube.station_id_from_towards("Woodford Via Hainault", "central")
            == "940GZZLUWOF"
        )

    def test_station_id_from_towards_alt_name_circle(self):
        assert (
            tfl_tube.station_id_from_towards("Edgware Road (Circle)", "circle")
            == "940GZZLUERC"
        )

    def test_station_id_from_towards_alt_name_hr5(self):
        assert (
            tfl_tube.station_id_from_towards("Heathrow T123 + 5", "piccadilly")
            == "940GZZLUHR5"
        )

    def test_station_id_from_towards_alt_name_hr4(self):
        assert (
            tfl_tube.station_id_from_towards("Heathrow via T4 Loop", "piccadilly")
            == "940GZZLUHR4"
        )

    def test_station_id_from_towards_not_a_station(self):
        assert (
            tfl_tube.station_id_from_towards("Check Front of Train", "circle") is None
        )


class TestLocationPlatformFromCurrentLocation:
    # sample data from:
    # jq -c "[.[] | select(.currentLocation | startswith(\"At \")) | \
    #    {currentLocation: .currentLocation, lineId: .lineId}] | unique" \
    #    sample-tube-arrivals-20181230T121143Z.json

    def test_location_platform(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At Arsenal Platform 2"
        )
        assert (location, platform) == ("Arsenal", "2")

    def test_location_platform_two_digit_platform(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At Baker Street Platform 10"
        )
        assert (location, platform) == ("Baker Street", "10")

    def test_location_platform_comma(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At East Finchley, Platform 1"
        )
        assert (location, platform) == ("East Finchley", "1")

    def test_location_platform_typo_plaform(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At London Bridge Plaform 1"
        )
        assert (location, platform) == ("London Bridge", "1")

    def test_location_platform_p_for_platform(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At Kings Cross P7"
        )
        assert (location, platform) == ("Kings Cross", "7")

    def test_location_platform_no_number(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At Angel platform"
        )
        assert (location, platform) == ("Angel", None)

    def test_location_no_platform(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At Mornington Crescent"
        )
        assert (location, platform) == ("Mornington Crescent", None)

    def test_location_not_a_station(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At North Acton Junction"
        )
        assert (location, platform) == ("North Acton Junction", None)

    def test_at_platform(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "At Platform"
        )
        assert (location, platform) == ("<current>", "<current>")

    def test_not_current_location_at(self):
        location, platform = tfl_tube.location_platform_from_current_location(
            "Not At East Finchley, Platform 1"
        )
        assert (location, platform) == (None, None)


class TestCurrentStationPlatformFromCurrentLocation:
    # sample data from:
    # jq "[.[] | select(.currentLocation | startswith(\"At \")) | \
    #     [.currentLocation, .lineId, .naptanId, .platformName]] | unique" \
    #     sample-tube-arrivals-20181230T121143Z.json

    def test_location_platform(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At Arsenal Platform 2",
            "piccadilly",
            "940GZZLULSQ",
            "Westbound - Platform 1",
        )
        assert (station, platform) == ("940GZZLUASL", "2")

    def test_location_platform_two_digit_platform(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At Baker Street Platform 10",
            "jubilee",
            "940GZZLUWHP",
            "Northbound - Platform 1",
        )
        assert (station, platform) == ("940GZZLUBST", "10")

    def test_location_platform_comma(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At East Finchley, Platform 1",
            "northern",
            "940GZZLUWOP",
            "Northbound - Platform 1",
        )
        assert (station, platform) == ("940GZZLUEFY", "1")

    def test_location_platform_no_number(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At Angel platform", "northern", "940GZZLUBTC", "Southbound - Platform 2"
        )
        assert (station, platform) == ("940GZZLUAGL", None)

    def test_location_no_platform(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At Mornington Crescent",
            "northern",
            "940GZZLUWFN",
            "Northbound - Platform 1",
        )
        assert (station, platform) == ("940GZZLUMTC", None)

    def test_location_not_a_station(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At North Acton Junction",
            "central",
            "940GZZLUTCR",
            "Eastbound - Platform 2",
        )
        assert (station, platform) == (None, None)

    def test_at_platform(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "At Platform",
            "piccadilly",
            "940GZZLUASG",
            "Eastbound/Westbound - Platform 2/3",
        )
        assert (station, platform) == ("940GZZLUASG", "2/3")

    def test_not_current_location_at(self):
        (
            station,
            platform,
        ) = tfl_tube.current_station_platform_number_from_current_location(
            "Not At East Finchley, Platform 1",
            "northern",
            "940GZZLUWOP",
            "Northbound - Platform 1",
        )
        assert (station, platform) == (None, None)


class TestStationFromLocation:
    def test_station(self):
        assert (
            tfl_tube.station_from_location("Gants Hill", None, "central")
            == "940GZZLUGTH"
        )

    def test_station_alternative_name(self):
        assert (
            tfl_tube.station_from_location("Elephant and Castle", None, "northern")
            == "940GZZLUEAC"
        )

    def test_not_station_known_location(self):
        assert (
            tfl_tube.station_from_location("North Acton Junction", None, "central")
            is None
        )

    def test_not_station_unknown_location(self, caplog):
        assert tfl_tube.station_from_location("Somewhere", None, "central") is None
        assert caplog.text.endswith("unresolved location Somewhere\n")


class TestCircleLineRailArrivingAtStation:
    def test_platform_westbound_outer_rail(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUVIC", platform_departure_direction="Westbound"
            )
            == "Outer Rail"
        )

    def test_platform_westbound_inner_rail(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUBST", platform_departure_direction="Westbound"
            )
            == "Inner Rail"
        )

    def test_platform_eastbound_outer_rail(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUGPS", platform_departure_direction="Eastbound"
            )
            == "Outer Rail"
        )

    def test_platform_eastbound_outer_rail_erc(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUERC", platform_departure_direction="Eastbound"
            )
            == "Outer Rail"
        )

    def test_platform_eastbound_inner_rail(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUEMB", platform_departure_direction="Eastbound"
            )
            == "Inner Rail"
        )

    def test_terminating_erc(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUMMT", destination_station_id="940GZZLUERC"
            )
            == "Outer Rail"
        )

    def test_terminating_hsc(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUMMT", destination_station_id="940GZZLUHSC"
            )
            == "Inner Rail"
        )

    def test_towards_erc(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUMMT", towards_station_id="940GZZLUERC"
            )
            == "Outer Rail"
        )

    def test_towards_hsc(self):
        assert (
            tfl_tube.circle_line_rail_arriving_at_station(
                "940GZZLUMMT", towards_station_id="940GZZLUHSC"
            )
            == "Inner Rail"
        )

    def test_undefined(self):
        assert tfl_tube.circle_line_rail_arriving_at_station("940GZZLUMMT") is None


class TestFilterTrainsByDirectionOfDeparture:
    def test_bkf_eastbound(self, caplog):
        """
        jq "[.[] | select(.naptanId == \"940GZZLUBKF\")]" \
            sample-line-district_circle-arrivals-20190111.json \
            > line-arrivals-circle_district-BKF.json
        """

        with open(
            pathlib.Path(__file__).parent
            / "data/line-arrivals-circle_district-BKF.json",
            "r",
        ) as file_handler:
            line_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_by_direction_of_departure(
            line_arrivals, "Eastbound"
        )

        assert len(trains) == 13

        assert trains["district-105"] == {
            "line_id": "district",
            "vehicle_id": "105",
            "station_id": "940GZZLUBKF",
            "towards": "Upminster",
            "towards_station_id": "940GZZLUUPM",
            "platform_name": "Eastbound - Platform 2",
            "platform_number": "2",
            "destination_station_id": "940GZZLUUPM",
            "time_to_station": 60,
        }

        assert trains["circle-213"] == {
            "line_id": "circle",
            "vehicle_id": "213",
            "station_id": "940GZZLUBKF",
            "towards": "Hammersmith",
            "towards_station_id": "940GZZLUHSC",
            "platform_name": "Eastbound - Platform 2",
            "platform_number": "2",
            "destination_station_id": "940GZZLUHSC",
            "time_to_station": 361,
        }

        assert trains["district-031"] == {
            "line_id": "district",
            "vehicle_id": "031",
            "station_id": "940GZZLUBKF",
            "towards": "Tower Hill",
            "towards_station_id": "940GZZLUTWH",
            "platform_name": "Eastbound - Platform 2",
            "platform_number": "2",
            "destination_station_id": "940GZZLUTWH",
            "time_to_station": 480,
        }

        assert trains["district-055"]
        assert trains["district-003"]
        assert trains["circle-214"]
        assert trains["district-030"]
        assert trains["district-064"]
        assert trains["district-032"]
        assert trains["district-107"]
        assert trains["district-042"]
        assert trains["district-005"]

        # fake entry with incoherent direction (inbound) vs platform
        # (Eastbound); actual is Eastbound
        assert trains["district-063"]
        assert caplog.text.endswith(
            "incoherent direction at 940GZZLUWSM "
            "(district): towards 940GZZLUTWH / destination 940GZZLUTWH / "
            "Eastbound platform / inbound\n"
        )

    def test_bkf_westbound(self, caplog):
        with open(
            pathlib.Path(__file__).parent
            / "data/line-arrivals-circle_district-BKF.json",
            "r",
        ) as file_handler:
            line_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_by_direction_of_departure(
            line_arrivals, "Westbound"
        )

        assert len(trains) == 12

        assert trains["district-017"] == {
            "line_id": "district",
            "vehicle_id": "017",
            "station_id": "940GZZLUBKF",
            "towards": "Wimbledon",
            "towards_station_id": "940GZZLUWIM",
            "platform_name": "Westbound - Platform 1",
            "platform_number": "1",
            "destination_station_id": "940GZZLUWIM",
            "time_to_station": 91,
        }

        assert trains["district-040"] == {
            "line_id": "district",
            "vehicle_id": "040",
            "station_id": "940GZZLUBKF",
            "towards": "Richmond",
            "towards_station_id": "940GZZLURMD",
            "platform_name": "Westbound - Platform 1",
            "platform_number": "1",
            "destination_station_id": "940GZZLURMD",
            "time_to_station": 211,
        }

        assert trains["district-125"] == {
            "line_id": "district",
            "vehicle_id": "125",
            "station_id": "940GZZLUBKF",
            "towards": "Wimbledon",
            "towards_station_id": "940GZZLUWIM",
            "platform_name": "Westbound - Platform 1",
            "platform_number": "1",
            "destination_station_id": "940GZZLUWIM",
            "time_to_station": 271,
        }

        assert trains["circle-202"] == {
            "line_id": "circle",
            "vehicle_id": "202",
            "station_id": "940GZZLUBKF",
            "towards": "Edgware Road (Circle)",
            "towards_station_id": "940GZZLUERC",
            "platform_name": "Westbound - Platform 1",
            "platform_number": "1",
            "destination_station_id": "940GZZLUERC",
            "time_to_station": 480,
        }

        assert trains["district-014"]
        assert trains["district-016"]
        assert trains["district-126"]
        assert trains["circle-203"]
        assert trains["district-052"]
        assert trains["district-056"]
        assert trains["district-060"]
        assert trains["circle-204"]

        # fake entry with incoherent direction (inbound) vs platform
        # (Eastbound); actual is Eastbound
        assert caplog.text.endswith(
            "incoherent direction at 940GZZLUWSM "
            "(district): towards 940GZZLUTWH / destination 940GZZLUTWH / "
            "Eastbound platform / inbound\n"
        )

    def test_bst_eastbound(self):
        """
        jq "[.[] | select(.naptanId == \"940GZZLUBST\")]" \
            sample-line-district_circle-arrivals-20190111.json \
            > line-arrivals-circle_district-BST.json
        """

        with open(
            pathlib.Path(__file__).parent
            / "data/line-arrivals-circle_district-BST.json",
            "r",
        ) as file_handler:
            line_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_by_direction_of_departure(
            line_arrivals, "Eastbound"
        )

        assert len(trains) == 1

        assert trains["circle-201"] == {
            "line_id": "circle",
            "vehicle_id": "201",
            "station_id": "940GZZLUBST",
            "towards": "Edgware Road (Circle)",
            "towards_station_id": "940GZZLUERC",
            "platform_name": "Eastbound - Platform 5",
            "platform_number": "5",
            "destination_station_id": "940GZZLUERC",
            "time_to_station": 1741,
        }

    def test_bst_westbound(self):
        with open(
            pathlib.Path(__file__).parent
            / "data/line-arrivals-circle_district-BST.json",
            "r",
        ) as file_handler:
            line_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_by_direction_of_departure(
            line_arrivals, "Westbound"
        )

        assert len(trains) == 0


class TestFilterTrainsCurrentlyAtPlatform:
    def test_bkf_circle_district_eastbound(self):
        """
        jq "[.[] | select(\
                (.currentLocation | startswith(\"At Blackfriars\")) or \
                (\
                    (.naptanId == \"940GZZLUBKF\") and \
                    (.currentLocation | startswith(\"At Platform\"))
                )\
            )]" sample-tube-arrivals-20190111.json > tube-arrivals-at_BKF.json
        """

        with open(
            pathlib.Path(__file__).parent / "data/tube-arrivals-at_BKF.json", "r"
        ) as file_handler:
            tube_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_currently_at_platform(
            tube_arrivals,
            line_ids=["district", "circle"],
            requested_station_id="940GZZLUBKF",
            requested_direction="Eastbound",
        )

        assert len(trains) == 1

        assert trains["district-106"] == {
            "line_id": "district",
            "vehicle_id": "106",
            "station_id": "940GZZLUBKF",
            "towards": "Upminster",
            "towards_station_id": "940GZZLUUPM",
            "platform_number": "2",
            "destination_station_id": "940GZZLUUPM",
            "time_to_station": 0,
        }

    def test_bkf_circle_district_westbound(self):
        with open(
            pathlib.Path(__file__).parent / "data/tube-arrivals-at_BKF.json", "r"
        ) as file_handler:
            tube_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_currently_at_platform(
            tube_arrivals,
            line_ids=["district", "circle"],
            requested_station_id="940GZZLUBKF",
            requested_direction="Westbound",
        )

        assert len(trains) == 1

        assert trains["circle-201"] == {
            "line_id": "circle",
            "vehicle_id": "201",
            "station_id": "940GZZLUBKF",
            "towards": "Edgware Road (Circle)",
            "towards_station_id": "940GZZLUERC",
            "platform_number": "1",
            "destination_station_id": "940GZZLUERC",
            "time_to_station": 0,
        }

    def test_bst_circle_district_eastbound(self):
        """
        jq "[.[] | select(\
                (.currentLocation | startswith(\"At Baker Street\")) or \
                (\
                    (.naptanId == \"940GZZLUBST\") and \
                    (.currentLocation | startswith(\"At Platform\"))
                )\
            )]" sample-tube-arrivals-20190111.json > tube-arrivals-at_BST.json
        """

        with open(
            pathlib.Path(__file__).parent / "data/tube-arrivals-at_BST.json", "r"
        ) as file_handler:
            tube_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_currently_at_platform(
            tube_arrivals,
            line_ids=["district", "circle"],
            requested_station_id="940GZZLUBST",
            requested_direction="Eastbound",
        )

        assert len(trains) == 1

        assert trains["circle-204"] == {
            "line_id": "circle",
            "vehicle_id": "204",
            "station_id": "940GZZLUBST",
            "towards": "Edgware Road (Circle)",
            "towards_station_id": "940GZZLUERC",
            "platform_number": "5",
            "destination_station_id": "940GZZLUERC",
            "time_to_station": 0,
        }

    def test_bst_circle_district_westbound(self):
        with open(
            pathlib.Path(__file__).parent / "data/tube-arrivals-at_BST.json", "r"
        ) as file_handler:
            tube_arrivals = json.load(file_handler)

        trains = tfl_tube.filter_trains_currently_at_platform(
            tube_arrivals,
            line_ids=["district", "circle"],
            requested_station_id="940GZZLUBST",
            requested_direction="Westbound",
        )

        assert len(trains) == 0


class TestWillArrivingTrainDepartFromCurrentLocationInDirection:
    def test_arrived_at_terminus_arrival_direction(self):
        assert (
            tfl_tube.will_arriving_train_depart_from_current_location_in_direction(
                "940GZZLUBNK",
                "waterloo-city",
                "940GZZLUBNK",
                "Westbound",
                "940GZZLUBNK",
            )
            == False
        )

    def test_arrived_at_terminus_departure_direction(self):
        assert (
            tfl_tube.will_arriving_train_depart_from_current_location_in_direction(
                "940GZZLUBNK",
                "waterloo-city",
                "940GZZLUBNK",
                "Eastbound",
                "940GZZLUBNK",
            )
            == False
        )

    def test_departing_from_terminus_towards(self):
        assert (
            tfl_tube.will_arriving_train_depart_from_current_location_in_direction(
                "940GZZLUEBY", "central", "940GZZLUEBY", "Eastbound", "940GZZLUHLT"
            )
            == True
        )

    def test_departing_from_terminus_departure_direction(self):
        assert (
            tfl_tube.will_arriving_train_depart_from_current_location_in_direction(
                "940GZZLUEBY", "central", "940GZZLUEBY", "Eastbound", "940GZZLUWCY"
            )
            == True
        )


class TestDirectionOfTrainFromStationTerminatingAt:
    def test_end_of_line(self):
        assert (
            tfl_tube.canonical_direction_of_train_from_station_terminating_at(
                "central", "940GZZLUEBY", "940GZZLUHLT"
            )
            == "outbound"
        )

    def test_inline_single_terminating_direction(self):
        assert (
            tfl_tube.canonical_direction_of_train_from_station_terminating_at(
                "district", "940GZZLUVIC", "940GZZLUTWH"
            )
            == "outbound"
        )

    def test_inline_dual_terminating_directions_normal_service(self):
        assert (
            tfl_tube.canonical_direction_of_train_from_station_terminating_at(
                "central", "940GZZLULYS", "940GZZLUWCY"
            )
            == "inbound"
        )

    def test_inline_dual_terminating_directions_end_of_service(self):
        assert (
            tfl_tube.canonical_direction_of_train_from_station_terminating_at(
                "central", "940GZZLUEBY", "940GZZLUWCY"
            )
            == "outbound"
        )


class TestResolveTrainCanonicalDirection:
    def test_towards_end_of_line(self):
        assert (
            tfl_tube.resolve_train_canonical_direction(
                "central", "940GZZLUOXC", towards_station_id="940GZZLUEBY"
            )
            == "inbound"
        )

    def test_towards_end_of_line_incoherent(self, caplog):
        assert (
            tfl_tube.resolve_train_canonical_direction(
                "central",
                "940GZZLUOXC",
                towards_station_id="940GZZLUEBY",
                destination_station_id="940GZZLUHLT",
            )
            == "inbound"
        )

        assert caplog.text.endswith(
            "incoherent direction at 940GZZLUOXC "
            "(central): towards 940GZZLUHLT / destination 940GZZLUEBY / "
            "None platform / None\n"
        )

    def test_destination_end_of_line(self):
        assert (
            tfl_tube.resolve_train_canonical_direction(
                "central", "940GZZLUOXC", destination_station_id="940GZZLUEBY"
            )
            == "inbound"
        )

    # TODO implement
    """
    def test_inline_single_terminating_direction(self):
        assert False

    def test_inline_single_terminating_direction_incoherent(self, caplog):
        assert False

    def test_inline_dual_term_dir_normal_service(self):
        assert False

    def test_inline_dual_term_dir_normal_service_incoherent(self, caplog):
        assert False

    def test_inline_dual_term_dir_end_of_service(self):
        assert False

    def test_inline_dual_term_dir_end_of_service_incoherent(self, caplog):
        assert False

    def test_from_platform(self):
        assert False

    def test_from_platform_incoherent(self, caplog):
        assert False

    def test_from_canonical_direction(self):
        assert False
    """


class TestInverseCanonicalDirection:
    def test_inbound(self):
        assert tfl_tube.inverse_canonical_direction("inbound") == "outbound"

    def test_outbound(self):
        assert tfl_tube.inverse_canonical_direction("outbound") == "inbound"

    def test_random(self):
        assert tfl_tube.inverse_canonical_direction("random") is None
