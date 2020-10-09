import departure.board.board as board
import departure.board.movement as movement

# pylint: disable=attribute-defined-outside-init,protected-access


class TestContentUpdateWithMovement:
    def setup_method(self):
        self.content_pixels = [
            [0, 0, (255, 0, 0)],
            [0, 7, (0, 255, 0)],
            [0, 15, (0, 0, 255)],
        ]

        self.next_content_pixels = [
            [0, 0, (255, 0, 0)],
            [1, 0, (255, 0, 0)],
            [0, 7, (0, 255, 0)],
            [1, 7, (0, 255, 0)],
            [0, 15, (0, 0, 255)],
            [1, 15, (0, 0, 255)],
        ]

        self.board = board.Board(
            board_w=8,
            board_h=8,
            sections=[
                board.BoardSection(
                    output_x=0,
                    output_y=0,
                    output_w=8,
                    output_h=8,
                    content=board.BoardSectionContent(
                        content_pixels=self.content_pixels,
                        content_w=16,
                        content_h=16,
                    ),
                    movement=movement.ScrollingContent(30, 0, 0, -1),
                )
            ],
        )

        self.next_content = board.BoardSectionContent(
            content_pixels=self.next_content_pixels, content_w=16, content_h=16
        )

    def test_init(self):
        self.board.reset()  # includes first move

        # has scrolled up by 1px
        assert self.board.pixels() == [
            [0, 6, (0, 255, 0)],
        ]

    def test_30_ms(self):
        self.board.reset()
        self.board.update(30)

        # has scrolled up by 2px
        assert self.board.pixels() == [
            [0, 5, (0, 255, 0)],
        ]

    def test_30_ms_update_content(self):
        self.board.reset()
        self.board.update(30)

        self.board.sections[0].update_content(self.next_content)
        assert self.board.pixels() == [
            [0, 5, (0, 255, 0)],
            [1, 5, (0, 255, 0)],
        ]


class TestBoardSection:
    def test_update_movement(self):
        movement1 = movement.NoMovement()
        movement2 = movement.StaticContent(0)
        board_section = board.BoardSection(
            0,
            0,
            8,
            8,
            board.BoardSectionContent([(0, 0, (255, 255, 255))], 8, 8),
            movement=movement1,
        )

        board_section.reset()
        _ = board_section.pixels()

        assert board_section._movement == movement1
        assert not board_section._has_changed

        board_section.update_movement(movement2)

        assert board_section._movement == movement2
        assert board_section._has_changed
