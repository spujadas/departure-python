import threading

import departure.board.board as board
import departure.board.movement as movement
import departure.board.departure_pb2 as departure_pb2
import departure.board.protobuf as protobuf


class BoardUpdater:
    def __init__(self, target_board: board.Board, board_lock: threading.RLock):
        self.board = target_board
        self.board_lock = board_lock

    def update(self):
        raise NotImplementedError()


class BoardUpdater_192_32_3_Rows(BoardUpdater):
    def __init__(self, target_board: board.Board, board_lock: threading.RLock):
        super().__init__(target_board, board_lock)

        self.board.sections = [
            board.BoardSection(0, 0, 192, 10, board.BoardSectionContent([], 0, 0)),
            board.BoardSection(0, 11, 192, 10, board.BoardSectionContent([], 0, 0)),
            board.BoardSection(0, 22, 192, 10, board.BoardSectionContent([], 0, 0)),
        ]

    def update_section(
        self,
        number: int,
        section_content: board.BoardSectionContent,
        section_movement: movement.Movement,
        section_continue_movement: bool,
    ):
        change_movement = True

        if section_content is not None:
            # if continuous movement is requested, do not change movement
            # if new content size is identical to old one
            if (
                section_continue_movement
                and section_content.content_w
                == self.board.sections[number]._content.content_w
                and section_content.content_h
                == self.board.sections[number]._content.content_h
            ):
                change_movement = False

            self.board.sections[number].update_content(section_content)

        if section_movement is not None and change_movement:
            self.board.sections[number].update_movement(section_movement)
            self.board.sections[number].reset()

    def update_sections(
        self,
        top_section_content: board.BoardSectionContent = None,
        top_section_movement: movement.Movement = None,
        top_section_continue_movement: bool = False,
        middle_section_content: board.BoardSectionContent = None,
        middle_section_movement: movement.Movement = None,
        middle_section_continue_movement: bool = False,
        bottom_section_content: board.BoardSectionContent = None,
        bottom_section_movement: movement.Movement = None,
        bottom_section_continue_movement: bool = False,
    ):

        with self.board_lock:
            self.update_section(
                0,
                top_section_content,
                top_section_movement,
                top_section_continue_movement,
            )

            self.update_section(
                1,
                middle_section_content,
                middle_section_movement,
                middle_section_continue_movement,
            )

            self.update_section(
                2,
                bottom_section_content,
                bottom_section_movement,
                bottom_section_continue_movement,
            )

    def update(self):
        raise NotImplementedError()


class BoardUpdater_192_32_3_Rows_Native(BoardUpdater_192_32_3_Rows):
    def update(
        self,
        top_section_content: board.BoardSectionContent = None,
        top_section_movement: movement.Movement = None,
        top_section_continue_movement: bool = False,
        middle_section_content: board.BoardSectionContent = None,
        middle_section_movement: movement.Movement = None,
        middle_section_continue_movement: bool = False,
        bottom_section_content: board.BoardSectionContent = None,
        bottom_section_movement: movement.Movement = None,
        bottom_section_continue_movement: bool = False,
    ):
        self.update_sections(
            top_section_content,
            top_section_movement,
            top_section_continue_movement,
            middle_section_content,
            middle_section_movement,
            middle_section_continue_movement,
            bottom_section_content,
            bottom_section_movement,
            bottom_section_continue_movement,
        )


class BoardUpdater_192_32_3_Rows_From_ProtocolBuffers(BoardUpdater_192_32_3_Rows):
    def update(
        self,
        board_sections_update_request: departure_pb2.BoardSectionsUpdateRequest,
    ) -> departure_pb2.BoardSectionsUpdateResponse:

        sections_update_data = {}
        sections_update_response = []

        for req in board_sections_update_request.requests:
            if req.section_index == 0:
                section_prefix = "top_section_"
            elif req.section_index == 1:
                section_prefix = "middle_section_"
            elif req.section_index == 2:
                section_prefix = "bottom_section_"
            else:  # invalid section
                sections_update_response.append(
                    # pylint: disable=E1101
                    departure_pb2.BoardSectionOperationStatus(
                        section_index=req.section_index,
                        status=departure_pb2.BoardSectionOperationStatus.SECTION_NOEXISTS,
                    )
                )
                continue

            # content
            sections_update_data[
                section_prefix + "content"
            ] = protobuf.deserialise_BoardSectionContent(req.content)

            # movement
            section_movement = protobuf.deserialise_RepeatedMovement(req.movement)
            if section_movement is not None:
                sections_update_data[section_prefix + "movement"] = section_movement

            # continue movement
            sections_update_data[
                section_prefix + "continue_movement"
            ] = req.continue_movement

            # response
            # pylint: disable=E1101
            sections_update_response.append(
                departure_pb2.BoardSectionOperationStatus(
                    section_index=req.section_index,
                    status=departure_pb2.BoardSectionOperationStatus.OK,
                )
            )

        self.update_sections(**sections_update_data)

        return departure_pb2.BoardSectionsUpdateResponse(
            status=sections_update_response
        )
