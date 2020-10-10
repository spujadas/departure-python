import logging

import grpc

import departure.board.view_model as view_model
import departure.board.contents as contents
import departure.commons.helpers as helpers
import departure.board.departure_pb2 as departure_pb2
import departure.board.departure_pb2_grpc as departure_pb2_grpc  # for type hinting
import departure.board.protobuf as board_protobuf

logger = logging.getLogger(__name__)


class ViewModelRatp(view_model.ViewModel):  # pylint: disable=abstract-method
    pass


class ViewModelRatp_192_32(ViewModelRatp):  # pylint: disable=abstract-method
    def __init__(self):
        self.board_text = contents.BoardText(
            font=contents.read_bdf_font("fonts/6x10_condensed.bdf"),
            colour_map={
                "orange": (255, 204, 0),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "white": (255, 255, 255),
            },
            tabs=[[0, "l"], [18, "l"], [42, "l"], [191, "r"]],
        )

    def text_array_service_overview(self, mission, pos: int):
        if mission["code"] is None:  # metro, bus
            return [
                [helpers.ordinal_fr(pos), "orange"],
                # [mission['message'] + ' - ' + mission['destinationName'], 'orange'],
                [mission["destinationName"], "orange"],
                ["", "orange"],
                [mission["message"], "white"],
            ]
        else:  # RER
            return [
                [helpers.ordinal_fr(pos), "orange"],
                [mission["code"], "white"],
                [mission["message"] + " - " + mission["destinationName"], "orange"]
                # [mission['destinationName'], 'orange']
            ]

    def pixels_mission_overview(self, mission, pos: str):
        return self.board_text.colour_text_tabbed_row_pixels(
            self.text_array_service_overview(mission, pos)
        )

    def next_content(self, departures):
        # empty board if called with None
        if departures is None:
            return [], (0, 0), [], (0, 0), [], (0, 0)

        # top section
        if len(departures["missions"]) == 0:  # "Pas de service" if no service
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.board_text.colour_text_pixels([["Pas de service", "orange"]])
        else:  # otherwise: 1st mission
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.pixels_mission_overview(departures["missions"][0], 1)

        # middle section
        if len(departures["missions"]) < 2:  # nothing if fewer than 2 trains
            middle_section_content_pixels = []
            middle_section_content_pixels_size = (0, 0)
        else:  # otherwise: 2nd mission
            (
                middle_section_content_pixels,
                middle_section_content_pixels_size,
            ) = self.pixels_mission_overview(departures["missions"][1], 2)

        # bottom section
        if departures["perturbations"]:  # disruptions if any
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.board_text.colour_text_pixels(
                [[departures["perturbations"], "red"]]
            )
            # adjust space before repeating
            bottom_section_content_pixels_size = (
                bottom_section_content_pixels_size[0] + 192,
                bottom_section_content_pixels_size[1],
            )

        elif len(departures["missions"]) < 3:  # nothing if fewer than 3 trains
            bottom_section_content_pixels = []
            bottom_section_content_pixels_size = (0, 0)

        elif len(departures["missions"]) == 3:  # 3rd train (if only 3 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.pixels_mission_overview(departures["missions"][2], 3)

        else:  # 3rd train onwards (if more than 3 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.board_text.colour_text_tabbed_rows_pixels(
                [
                    self.text_array_service_overview(mission, i + 3)
                    for i, mission in enumerate(departures["missions"][2:])
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


class ViewModelRatp_192_32_3_Rows_To_ProtocolBuffers(ViewModelRatp_192_32):
    def __init__(self, board_manager_stub: departure_pb2_grpc.BoardManagerStub):
        super().__init__()
        self.board_manager_stub = board_manager_stub

        self.next_mission_tracker = [
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

        self.horizontal_scroll = [
            departure_pb2.Movement(
                scrolling_content=departure_pb2.ScrollingContent(
                    step_duration=50,
                    total_steps=0,
                    delta_x_per_step=-1,
                    delta_y_per_step=0,
                )
            )
        ]

        self.no_movement = [
            departure_pb2.Movement(no_movement=departure_pb2.NoMovement())
        ]

    def update(self, departures):  # pylint: disable=arguments-differ
        requests_data = []

        (
            top_section_content_pixels,
            top_section_content_pixels_size,
            middle_section_content_pixels,
            middle_section_content_pixels_size,
            bottom_section_content_pixels,
            bottom_section_content_pixels_size,
        ) = self.next_content(departures)

        # top section: 1st train
        requests_data.append(
            departure_pb2.BoardSectionUpdateRequest(
                section_index=0,
                content=departure_pb2.BoardSectionContent(
                    pixels=board_protobuf.serialise_pixels(top_section_content_pixels),
                    content_w=top_section_content_pixels_size[0],
                    content_h=top_section_content_pixels_size[1],
                    repeat_x=False,
                    repeat_y=False,
                ),
                movement=self.no_movement,
                continue_movement=False,
            )
        )

        # middle section: 2nd train
        requests_data.append(
            departure_pb2.BoardSectionUpdateRequest(
                section_index=1,
                content=departure_pb2.BoardSectionContent(
                    pixels=board_protobuf.serialise_pixels(
                        middle_section_content_pixels
                    ),
                    content_w=middle_section_content_pixels_size[0],
                    content_h=middle_section_content_pixels_size[1],
                    repeat_x=False,
                    repeat_y=False,
                ),
                movement=self.no_movement,
                continue_movement=False,
            )
        )

        # bottom section: 3rd train onwards or disruptions
        repeat_x = False
        repeat_y = False

        if departures is None:
            next_movement = self.no_movement
        elif departures["perturbations"]:  # h-scroll if disruptions
            next_movement = self.horizontal_scroll
            repeat_x = True
        elif len(departures["missions"]) <= 3:  # no v-scroll if up to 3 trains
            next_movement = self.no_movement
        else:  # v-scroll if more than 3 trains
            next_movement = self.next_mission_tracker
            repeat_y = True

        requests_data.append(
            departure_pb2.BoardSectionUpdateRequest(
                section_index=2,
                content=departure_pb2.BoardSectionContent(
                    pixels=board_protobuf.serialise_pixels(
                        bottom_section_content_pixels
                    ),
                    content_w=bottom_section_content_pixels_size[0],
                    content_h=bottom_section_content_pixels_size[1],
                    repeat_x=repeat_x,
                    repeat_y=repeat_y,
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
