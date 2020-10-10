import logging

import grpc

import departure.board.view_model as view_model
import departure.board.contents as contents
import departure.commons.helpers as helpers
import departure.board.departure_pb2 as departure_pb2
import departure.board.protobuf as protobuf

# type hinting
import departure.board.departure_pb2_grpc as departure_pb2_grpc

logger = logging.getLogger(__name__)


# pylint: disable=abstract-method
class ViewModelSncf(view_model.ViewModel):
    pass


# pylint: disable=abstract-method
class ViewModelSncf_192_32(ViewModelSncf):
    def __init__(self):
        self.board_text = contents.BoardText(
            font=contents.read_bdf_font("fonts/6x10_condensed.bdf"),
            colour_map={
                "orange": (255, 204, 0),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "white": (255, 255, 255),
            },
            tabs=[[0, "l"], [19, "l"], [45, "l"], [191, "r"]],
        )

    def text_array_train_overview(self, train, pos: int):
        if train["time"] == train["base_time"]:
            time_colour = "green"
        else:
            time_colour = "red"

        return [
            [helpers.ordinal_fr(pos), "orange"],
            [train["time"], time_colour],
            [train["direction"], "orange", 106],
            [train["headsign"], "white"],
        ]

    def pixels_train_overview(self, train, pos: int):
        return self.board_text.colour_text_tabbed_row_pixels(
            self.text_array_train_overview(train, pos)
        )

    def pixels_train_details(self, train):
        stop_points = []
        index_last_stop_point = len(train["timetable"]) - 1
        index_after_current_stop_point = 0
        before_current_stop_point = True

        for i, stop_point in enumerate(train["timetable"]):
            # ignore stops before current stop
            if stop_point["id"] == train["stop_point_id"]:
                before_current_stop_point = False
                index_after_current_stop_point = i + 1
                continue

            if before_current_stop_point:
                continue

            if i == index_after_current_stop_point:
                pass
            elif i == index_last_stop_point:
                stop_points.append([", et ", "orange"])
            else:
                stop_points.append([", ", "orange"])

            stop_points.append([stop_point["name"] + " ", "orange"])

            if (
                stop_point["amended_departure_time"]
                == stop_point["base_departure_time"]
            ):
                time_colour = "green"
            else:
                time_colour = "red"

            stop_points.append(
                [f'({stop_point["amended_departure_time"]})', time_colour]
            )

        return self.board_text.colour_text_pixels(
            [["Arrêts : ", "orange"]]
            + stop_points
            + [[" (" + train["commercial_mode"] + ")", "orange"]]
        )

    def next_content(self, trains):
        # empty board if called with None
        if trains is None:
            return [], (0, 0), [], (0, 0), [], (0, 0)

        # top section
        if len(trains) == 0:  # "Pas de service" if no service
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.board_text.colour_text_pixels([["Pas de service", "orange"]])
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
            ) = self.pixels_train_details(trains[0])

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
                    self.text_array_train_overview(train, i + 2)
                    for i, train in enumerate(trains[1:])
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


class ViewModelSncf_192_32_3_Rows_To_ProtocolBuffers(ViewModelSncf_192_32):
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

    def update(self, trains):  # pylint: disable=arguments-differ
        requests_data = []

        (
            top_section_content_pixels,
            top_section_content_pixels_size,
            middle_section_content_pixels,
            middle_section_content_pixels_size,
            bottom_section_content_pixels,
            bottom_section_content_pixels_size,
        ) = self.next_content(trains)

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
