import logging

import grpc

import departure.board.view_model as view_model
import departure.board.contents as contents
import departure.commons.helpers as helpers
import departure.board.departure_pb2 as departure_pb2
import departure.board.protobuf as protobuf

# type hinting
import departure.board.departure_pb2_grpc as departure_pb2_grpc

from . import data

logger = logging.getLogger(__name__)


def text_array_train_overview(train, pos: int):
    if train["actual_time"] == train["planned_time"]:
        time_colour = "green"
    else:
        time_colour = "red"

    return [
        [helpers.ordinal_en(pos), "orange"],
        [train["actual_time"], time_colour],
        [train["track"], "white"],
        [train["direction"], "orange", 106],
        [train["train_number"], "white"],
    ]


# for type hinting
# pylint: disable=abstract-method,too-few-public-methods
class ViewModelNS(view_model.ViewModel):
    pass


class ViewModelNS192x32x3(ViewModelNS):  # pylint: disable=abstract-method
    def __init__(self):
        self.board_text = contents.BoardText(
            font=contents.read_bdf_font("fonts/6x10_condensed.bdf"),
            colour_map={
                "orange": (255, 204, 0),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "white": (255, 255, 255),
            },
            tabs=[[0, "l"], [20, "l"], [58, "r"], [62, "l"], [191, "r"]],
        )

    def pixels_train_overview(self, train, pos: int):
        return self.board_text.colour_text_tabbed_row_pixels(
            text_array_train_overview(train, pos)
        )

    def pixels_train_details(self, train: dict, current_station_ns_code: str):
        stops = []
        index_last_station = len(train["schedule"]) - 1

        stations_by_uic = data.STATIONS_BY_UIC
        current_station_uic = data.STATIONS_BY_NS_CODE[current_station_ns_code]["uic"]
        before_current_station = True
        index_after_current_station = 0

        for i, stop in enumerate(train["schedule"]):
            # ignore stops before current stop
            if stop["stop_uic"] == current_station_uic:
                before_current_station = False
                index_after_current_station = i + 1
                continue

            if before_current_station:
                continue

            # display schedule after current station

            ## list formatting (e.g. Oxford comma)
            if i == index_after_current_station:
                pass
            elif i == index_last_station:
                stops.append([", and ", "orange"])
            else:
                stops.append([", ", "orange"])

            ## resolve name
            if stop["stop_uic"] in stations_by_uic:
                stop_name = stations_by_uic[stop["stop_uic"]]["name_medium"]
            else:  # don't attempt to resolve using UIC if stop is outside NL
                stop_name = f"{stop['stop_name']}"
            stops.append([f"{stop_name} ", "orange"])

            if stop["actual_time"] == stop["planned_time"]:
                time_colour = "green"
            else:
                time_colour = "red"

            stops.append([f'({stop["actual_time"]})', time_colour])

        return self.board_text.colour_text_pixels(
            [["Calling at: ", "orange"]]
            + stops
            + [[" (" + train["train_category"] + ")", "orange"]]
        )

    def next_content(self, trains: list, current_station_ns_code: str):
        # empty board if called with None
        if trains is None:
            return [], (0, 0), [], (0, 0), [], (0, 0)

        # top section
        if len(trains) == 0:  # "No service" if no service
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.board_text.colour_text_pixels([["No service", "orange"]])
        else:  # otherwise: 1st train
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.pixels_train_overview(trains[0], 1)

        # middle section
        if len(trains) == 0:  # nothing if no service
            middle_section_content_pixels = []
            middle_section_content_pixels_size = (0, 0)
        else:  # otherwise: calling points of 1st train
            (
                middle_section_content_pixels,
                middle_section_content_pixels_size,
            ) = self.pixels_train_details(trains[0], current_station_ns_code)

        # bottom section
        if len(trains) < 2:  # nothing if fewer than 2 trains
            bottom_section_content_pixels = []
            bottom_section_content_pixels_size = (0, 0)

        elif len(trains) == 2:  # 2nd train (if only 2 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.pixels_train_overview(trains[1], 2)

        else:  # 2nd train onwards (if more than 2 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.board_text.colour_text_tabbed_rows_pixels(
                [
                    text_array_train_overview(train, i + 2)
                    for i, train in enumerate(trains[1:10])
                ],
                row_height=11,
            )

        return (
            top_section_content_pixels,
            top_section_content_pixels_size,
            middle_section_content_pixels,
            middle_section_content_pixels_size,
            bottom_section_content_pixels,
            bottom_section_content_pixels_size,
        )


class ViewModelNS192x32x3ToProtocolBuffers(ViewModelNS192x32x3):
    def __init__(self, board_manager_stub: departure_pb2_grpc.BoardManagerStub):
        super().__init__()
        self.board_manager_stub = board_manager_stub

        self.next_train_tracker = [
            departure_pb2.Movement(
                static_content=departure_pb2.StaticContent(total_duration=2000)
            ),
            departure_pb2.Movement(
                scrolling_content=departure_pb2.ScrollingContent(
                    step_duration=100,
                    total_steps=11,
                    delta_x_per_step=0,
                    delta_y_per_step=-1,
                )
            ),
        ]

        self.no_movement = [
            departure_pb2.Movement(no_movement=departure_pb2.NoMovement())
        ]

    # pylint: disable=arguments-differ
    def update(self, trains: list, current_station_ns_code: str = ""):
        requests_data = []

        (
            top_section_content_pixels,
            top_section_content_pixels_size,
            middle_section_content_pixels,
            middle_section_content_pixels_size,
            bottom_section_content_pixels,
            bottom_section_content_pixels_size,
        ) = self.next_content(trains, current_station_ns_code)

        # top section: 1st train
        requests_data.append(
            departure_pb2.BoardSectionUpdateRequest(
                section_index=0,
                content=departure_pb2.BoardSectionContent(
                    pixels=protobuf.serialise_pixels(top_section_content_pixels),
                    content_w=top_section_content_pixels_size[0],
                    content_h=top_section_content_pixels_size[1],
                    repeat_x=False,
                    repeat_y=False,
                ),
                movement=self.no_movement,
                continue_movement=False,
            )
        )

        # middle section: calling points of 1st train
        requests_data.append(
            departure_pb2.BoardSectionUpdateRequest(
                section_index=1,
                content=departure_pb2.BoardSectionContent(
                    pixels=protobuf.serialise_pixels(middle_section_content_pixels),
                    content_w=middle_section_content_pixels_size[0] + 192,
                    content_h=middle_section_content_pixels_size[1],
                    repeat_x=True,
                    repeat_y=False,
                ),
                movement=[
                    departure_pb2.Movement(
                        scrolling_content=departure_pb2.ScrollingContent(
                            step_duration=50,
                            total_steps=0,
                            delta_x_per_step=-1,
                            delta_y_per_step=0,
                        )
                    )
                ],
                continue_movement=True,
            )
        )

        # bottom section: 2nd train onwards
        if trains is None or len(trains) <= 2:  # no v-scroll if up to 2 trains
            next_movement = self.no_movement
        else:  # v-scroll if more than 2 trains
            next_movement = self.next_train_tracker

        requests_data.append(
            departure_pb2.BoardSectionUpdateRequest(
                section_index=2,
                content=departure_pb2.BoardSectionContent(
                    pixels=protobuf.serialise_pixels(bottom_section_content_pixels),
                    content_w=bottom_section_content_pixels_size[0],
                    content_h=bottom_section_content_pixels_size[1],
                    repeat_x=True,
                    repeat_y=True,
                ),
                movement=next_movement,
                continue_movement=True,
            )
        )

        # send gRPC message
        try:
            self.board_manager_stub.BoardSectionsUpdate(
                departure_pb2.BoardSectionsUpdateRequest(requests=requests_data)
            )
        # pylint: disable=protected-access
        except (grpc._channel._Rendezvous, grpc._channel._InactiveRpcError):
            logger.warning("connection to board failed")
