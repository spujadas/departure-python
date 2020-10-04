from typing import List, Union

import departure.board.departure_pb2 as departure_pb2
import departure.board.board as board
import departure.board.movement as movement


def deserialise_Pixel(pixel: departure_pb2.Pixel):
    return pixel.x, pixel.y, (pixel.r, pixel.g, pixel.b)


def deserialise_BoardSectionContent(
    board_section_content: departure_pb2.BoardSectionContent,
) -> board.BoardSectionContent:
    return board.BoardSectionContent(
        content_pixels=[
            deserialise_Pixel(pixel) for pixel in board_section_content.pixels
        ],
        content_w=board_section_content.content_w,
        content_h=board_section_content.content_h,
        repeat_x=board_section_content.repeat_x,
        repeat_y=board_section_content.repeat_y,
    )


def deserialise_NoMovement(
    no_movement: departure_pb2.NoMovement,
) -> movement.NoMovement:
    return movement.NoMovement(
        x_offset_init=no_movement.x_offset_init, y_offset_init=no_movement.y_offset_init
    )


def deserialise_StaticContent(
    static_content: departure_pb2.StaticContent,
) -> movement.StaticContent:
    return movement.StaticContent(
        total_duration=static_content.total_duration,
        x_offset_init=static_content.x_offset_init,
        y_offset_init=static_content.y_offset_init,
    )


def deserialise_ScrollingContent(
    scrolling_content: departure_pb2.ScrollingContent,
) -> movement.ScrollingContent:
    return movement.ScrollingContent(
        step_duration=scrolling_content.step_duration,
        total_steps=scrolling_content.total_steps,
        delta_x_per_step=scrolling_content.delta_x_per_step,
        delta_y_per_step=scrolling_content.delta_y_per_step,
        x_offset_init=scrolling_content.x_offset_init,
        y_offset_init=scrolling_content.y_offset_init,
    )


def deserialise_Movement(
    single_movement: departure_pb2.Movement,
) -> Union[movement.Movement, None]:
    if single_movement.HasField("no_movement"):
        return deserialise_NoMovement(single_movement.no_movement)

    if single_movement.HasField("static_content"):
        return deserialise_StaticContent(single_movement.static_content)

    if single_movement.HasField("scrolling_content"):
        return deserialise_ScrollingContent(single_movement.scrolling_content)

    return None


def deserialise_RepeatedMovement(
    movement_list: List[departure_pb2.Movement],
) -> Union[None, movement.Movement]:
    # no movement
    if movement_list is None or len(movement_list) == 0:
        return None

    # normal movement
    if len(movement_list) == 1:
        return deserialise_Movement(movement_list[0])

    # movement cycle
    movement_segments = []
    for current_movement in movement_list:
        movement_segment = deserialise_Movement(current_movement)

        # invalid case
        if movement_segment is None:
            return None

        movement_segments.append(movement_segment)

    return movement.MovementCycle(movement_segments)


def serialise_pixels(pixels) -> List[departure_pb2.Pixel]:
    serialised_pixels = []
    for x, y, colour in pixels:
        serialised_pixels.append(
            departure_pb2.Pixel(x=x, y=y, r=colour[0], g=colour[1], b=colour[2])
        )
    return serialised_pixels
