import logging

import grpc

import departure.board.view_model as view_model
import departure.board.contents as contents
import departure.commons.helpers as helpers
import departure.board.departure_pb2 as departure_pb2
import departure.board.departure_pb2_grpc as departure_pb2_grpc  # for type hinting
import departure.board.protobuf as protobuf


logger = logging.getLogger(__name__)


class ViewModelNationalRail(view_model.ViewModel):  # pylint: disable=abstract-method
    pass


# pylint: disable=abstract-method
class ViewModelNationalRail_192_32(ViewModelNationalRail):
    def __init__(self):
        self.board_text = contents.BoardText(
            font=contents.read_bdf_font("fonts/6x10_condensed.bdf"),
            colour_map={
                "orange": (255, 204, 0),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "white": (255, 255, 255),
            },
            tabs=[[0, "l"], [20, "l"], [56, "r"], [60, "l"], [191, "r"]],
        )

    def text_array_service_overview(self, service, pos: int):
        if service["platform"] is None:
            platform = ""
        else:
            platform = service["platform"]

        if service["etd"] == "On time":
            etd_colour = "green"
        else:
            etd_colour = "red"

        return [
            [helpers.ordinal_en(pos), "orange"],
            [service["std"], "orange"],
            [platform, "white"],
            [service["destination_location_name"], "orange", 95],
            [service["etd"], etd_colour],
        ]

    def pixels_service_overview(self, service, pos: int):
        return self.board_text.colour_text_tabbed_row_pixels(
            self.text_array_service_overview(service, pos)
        )

    def pixels_service_details(self, service):
        calling_points = []
        index_last_calling_point = len(service["calling_points"]) - 1
        for i, calling_point in enumerate(service["calling_points"]):
            if i == 0:
                pass
            elif i == index_last_calling_point:
                calling_points.append([", and ", "orange"])
            else:
                calling_points.append([", ", "orange"])

            calling_points.append([calling_point["location_name"] + " ", "orange"])

            time_display = calling_point["st"]
            if calling_point["et"] == "On time":
                time_colour = "green"
            else:
                time_colour = "red"

            calling_points.append(["(" + time_display + ")", time_colour])

        return self.board_text.colour_text_pixels(
            [["Calling at: ", "orange"]]
            + calling_points
            + [[" (" + service["operator"] + ")", "orange"]]
        )

    def next_content(self, services):
        # empty board if called with None
        if services is None:
            return [], (0, 0), [], (0, 0), [], (0, 0)

        # top section
        if len(services) == 0:  # "No service" if no service
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.board_text.colour_text_pixels([["No service", "orange"]])
        else:  # otherwise: 1st train
            (
                top_section_content_pixels,
                top_section_content_pixels_size,
            ) = self.pixels_service_overview(services[0], 1)

        # middle section:
        if len(services) == 0:  # nothing if no service
            middle_section_content_pixels = []
            middle_section_content_pixels_size = (0, 0)
        else:  # otherwise: calling points of 1st train
            (
                middle_section_content_pixels,
                middle_section_content_pixels_size,
            ) = self.pixels_service_details(services[0])

        # bottom section
        if len(services) < 2:  # nothing if fewer than 2 trains
            bottom_section_content_pixels = []
            bottom_section_content_pixels_size = (0, 0)

        elif len(services) == 2:  # 2nd train (if only 2 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.pixels_service_overview(services[1], 2)

        else:  # 2nd train onwards (if more than 2 trains)
            (
                bottom_section_content_pixels,
                bottom_section_content_pixels_size,
            ) = self.board_text.colour_text_tabbed_rows_pixels(
                [
                    self.text_array_service_overview(service, i + 2)
                    for i, service in enumerate(services[1:])
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


class ViewModelNationalRail_192_32_3_Rows_To_ProtocolBuffers(
    ViewModelNationalRail_192_32
):
    def __init__(self, board_manager_stub: departure_pb2_grpc.BoardManagerStub):
        super().__init__()
        self.board_manager_stub = board_manager_stub

        self.next_service_tracker = [
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
    def update(self, services):
        requests_data = []

        (
            top_section_content_pixels,
            top_section_content_pixels_size,
            middle_section_content_pixels,
            middle_section_content_pixels_size,
            bottom_section_content_pixels,
            bottom_section_content_pixels_size,
        ) = self.next_content(services)

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
        if services is None or len(services) <= 2:  # no v-scroll if up to 2 trains
            next_movement = self.no_movement
        else:  # v-scroll if more than 2 trains
            next_movement = self.next_service_tracker

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
