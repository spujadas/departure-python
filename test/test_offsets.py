import departure.board.board as board
import departure.board.movement as movement

# pylint: disable=protected-access


class TestRepeatedOffsets:
    # x_offset, y_offset, display_w, display_h, content_w, content_h

    def test_no_wrap_right_no_repeat(self):
        assert board.repeated_offsets(20, 3, 60, 20, 20, 10) == (
            [20],
            [3],
        )  # right of display_w
        assert board.repeated_offsets(2, 3, 60, 20, 20, 10) == (
            [2],
            [3],
        )  # between 0 and display_w (visible)
        assert board.repeated_offsets(0, 3, 60, 20, 20, 10) == (
            [0],
            [3],
        )  # at limit of visible (visible)
        assert board.repeated_offsets(-1, 3, 60, 20, 20, 10) == (
            [-1],
            [3],
        )  # at limit of visible (non-visible)
        assert board.repeated_offsets(-40, 3, 60, 20, 20, 10) == (
            [-40],
            [3],
        )  # at limit of repeat (non-repeat)

    def test_repeat_right(self):
        assert board.repeated_offsets(-41, 3, 60, 20, 20, 10) == (
            [-41, 19],
            [3],
        )  # at limit of repeat (repeat)
        assert board.repeated_offsets(-59, 3, 60, 20, 20, 10) == (
            [-59, 1],
            [3],
        )  # at limit of wrap (non-wrap)

    def test_no_wrap_down_no_repeat(self):
        assert board.repeated_offsets(2, 20, 60, 20, 20, 10) == (
            [2],
            [20],
        )  # below display_h
        assert board.repeated_offsets(2, 2, 60, 20, 20, 10) == (
            [2],
            [2],
        )  # between 0 and display_h (visible)
        assert board.repeated_offsets(2, 0, 60, 20, 20, 10) == (
            [2],
            [0],
        )  # at limit of visible (visible)
        assert board.repeated_offsets(2, -1, 60, 20, 20, 10) == (
            [2],
            [-1],
        )  # at limit of visible (non-visible)
        assert board.repeated_offsets(2, -10, 60, 20, 20, 10) == (
            [2],
            [-10],
        )  # at limit of repeat (non-repeat)

    def test_repeat_down(self):
        assert board.repeated_offsets(2, -11, 60, 20, 20, 10) == (
            [2],
            [-11, 9],
        )  # at limit of repeat (repeat)
        assert board.repeated_offsets(2, -19, 60, 20, 20, 10) == (
            [2],
            [-19, 1],
        )  # at limit of wrap (non-wrap)


class TestWrapOffset:
    def test_wrap_right(self):
        content = board.BoardSectionContent([], 60, 20)
        move = movement.NoMovement(20, 10)
        section = board.BoardSection(0, 0, 0, 0, content=content, movement=move)

        # at limit of wrap (wrap)
        section._movement.set_offset(-60, 3)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (0, 3)

        # between
        section._movement.set_offset(-61, 3)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (-1, 3)

        # resolves (wrap) to limit of repeat (non-repeat)
        section._movement.set_offset(-100, 3)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (-40, 3)

        # resolves (wrap) to limit of repeat (repeat)
        section._movement.set_offset(-101, 3)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (-41, 3)

    def test_wrap_down(self):
        content = board.BoardSectionContent([], 60, 20)
        move = movement.NoMovement(20, 10)
        section = board.BoardSection(0, 0, 0, 0, content=content, movement=move)

        # at limit of wrap (wrap)
        section._movement.set_offset(2, -20)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (2, 0)

        # between
        section._movement.set_offset(2, -21)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (2, -1)

        # resolves (wrap) to limit of repeat (non-repeat)
        section._movement.set_offset(2, -30)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (2, -10)

        # resolves (wrap) to limit of repeat (repeat)
        section._movement.set_offset(2, -31)
        section._wrap_offset()
        assert (section._movement.x_offset, section._movement.y_offset) == (2, -11)


class TestVisiblePixelsMultipleOffsets:
    # remains marked as not covered by tests due to continue
    # see https://bitbucket.org/ned/coveragepy/issues/198/continue-marked-as-not-covered
    # leaving in case bug gets fixed
    def test_invisible_repetitions(self):
        output_pixels = board.visible_pixels_multiple_offsets(
            [(0, 0, (255, 255, 255))], [0, 8], [0, 8], 8, 8, 8, 8
        )

        assert output_pixels == [(0, 0, (255, 255, 255))]
