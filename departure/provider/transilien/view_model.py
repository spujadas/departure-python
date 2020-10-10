import logging

import grpc

import departure.board.view_model as view_model
import departure.board.contents as contents
import departure.commons.helpers as helpers
import departure.board.departure_pb2 as departure_pb2
import departure.board.departure_pb2_grpc as departure_pb2_grpc  # for type hinting
import departure.board.protobuf as protobuf

logger = logging.getLogger(__name__)


# pylint: disable=abstract-method
class ViewModelTransilien(view_model.ViewModel):
    pass


# pylint: disable=abstract-method
class ViewModelTransilien_192_32(ViewModelTransilien):
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
        return [
            [helpers.ordinal_fr(pos), "orange"],
            [train["time"], "orange"],
            [train["terminus"], "orange", 106],
            [train["mission"], "white"],
        ]

    def pixels_train_overview(self, train, pos: int):
        return self.board_text.colour_text_tabbed_row_pixels(
            self.text_array_train_overview(train, pos)
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
        if len(trains) < 2:  # nothing if fewer than 2 trains
            middle_section_content_pixels = []
            middle_section_content_pixels_size = (0, 0)
        else:  # otherwise: calling points of 1st train
            (
                middle_section_content_pixels,
                middle_section_content_pixels_size,
            ) = self.pixels_train_overview(trains[1], 2)

        # bottom section
        if len(trains) < 3:  # nothing if fewer than 3 trains
            bottom_section_content_pixels = []
            bottom_section_content_pixels_size = (0, 0)

        elif len(trains) == 2:  # 3rd train (if only 3 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.pixels_train_overview(trains[2], 3)

        else:  # 3rd train onwards (if more than 2 trains) - limit 10
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.board_text.colour_text_tabbed_rows_pixels(
                [
                    self.text_array_train_overview(train, i + 3)
                    for i, train in enumerate(trains[2:10])
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


class ViewModelTransilien_192_32_3_Rows_To_ProtocolBuffers(ViewModelTransilien_192_32):
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
                    content_w=middle_section_content_pixels_size[0],
                    content_h=middle_section_content_pixels_size[1],
                    repeat_x=False,
                    repeat_y=False,
                ),
                movement=self.no_movement,
                continue_movement=False,
            )
        )

        # bottom section: 3rd train onwards
        if trains is None or len(trains) <= 3:  # no v-scroll if up to 3 trains
            next_movement = self.no_movement
        else:  # v-scroll if more than 3 trains
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
