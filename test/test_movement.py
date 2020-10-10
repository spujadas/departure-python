import pytest

import departure.board.movement as movement

# pylint: disable=protected-access


class TestStaticContent:
    def test_init(self):
        static_content = movement.StaticContent(50)
        assert static_content.x_offset is None
        assert static_content.y_offset is None
        assert static_content.elapsed_time is None
        assert static_content.total_duration == 50
        assert static_content.extra_time_after_end is None

    def test_update_no_reset(self):
        static_content = movement.StaticContent(0)
        with pytest.raises(movement.MovementException):
            static_content.update(20)

    def test_reset(self):
        static_content = movement.StaticContent(10, 6, 7)
        static_content.set_offset(3, 4)
        static_content.reset()
        assert static_content.x_offset == 6
        assert static_content.y_offset == 7
        assert static_content.total_duration == 10
        assert static_content.elapsed_time == 0
        assert static_content.extra_time_after_end == 0
        assert not static_content.end_of_segment_reached

    def test_forever(self):
        static_content = movement.StaticContent(0, 2, 3)
        static_content.reset()
        assert not static_content.update(13)
        assert not static_content.end_of_segment_reached
        assert static_content.x_offset == 2
        assert static_content.y_offset == 3
        assert static_content.total_duration == 0
        assert static_content.elapsed_time == 0
        assert static_content.extra_time_after_end == 0

    def test_end_not_reached(self):
        static_content = movement.StaticContent(10, 2, 3)
        static_content.reset()
        assert not static_content.update(3)
        assert not static_content.end_of_segment_reached
        assert static_content.x_offset == 2
        assert static_content.y_offset == 3
        assert static_content.total_duration == 10
        assert static_content.elapsed_time == 3
        assert static_content.extra_time_after_end == 0

    def test_end_reached(self):
        static_content = movement.StaticContent(10, 2, 3)
        static_content.reset()
        assert not static_content.update(23)
        assert static_content.end_of_segment_reached
        assert static_content.x_offset == 2
        assert static_content.y_offset == 3
        assert static_content.total_duration == 10
        assert static_content.elapsed_time == 10
        assert static_content.extra_time_after_end == 13

    def test_at_1_before_total_duration_add_1(self):
        static_content = movement.StaticContent(10, 2, 3)
        static_content.reset()
        assert not static_content.update(9)  # 1 before end
        assert not static_content.end_of_segment_reached

        assert not static_content.update(1)  # add 1
        assert static_content.end_of_segment_reached  # this has changed
        assert static_content.extra_time_after_end == 0

        assert not static_content.update(1)  # add 1
        assert static_content.end_of_segment_reached  # still True
        assert static_content.extra_time_after_end == 1

    def test_set_offset(self):
        static_content = movement.StaticContent(10, 2, 3)
        static_content.reset()
        static_content.set_offset(4, 5)
        assert static_content.x_offset == 4
        assert static_content.y_offset == 5


class TestScrollingContent:
    def test_init(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0, 2, 3)
        assert scrolling_content.x_offset_init == 2
        assert scrolling_content.y_offset_init == 3
        assert scrolling_content.x_offset is None
        assert scrolling_content.y_offset is None
        assert scrolling_content.current_step_num is None
        assert scrolling_content.elapsed_time is None
        assert scrolling_content.extra_time_after_end is None
        assert scrolling_content.total_duration == 120
        assert scrolling_content.step_duration == 30
        assert scrolling_content.total_steps == 4
        assert scrolling_content.delta_x_per_step == -1
        assert scrolling_content.delta_y_per_step == 0

    def test_update_no_reset(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0)
        with pytest.raises(movement.MovementException):
            scrolling_content.update(20)

    def test_reset(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0, 2, 3)
        scrolling_content.reset()
        assert scrolling_content.x_offset == 1  # moves at t=0
        assert scrolling_content.y_offset == 3
        assert scrolling_content.current_step_num == 0
        assert scrolling_content.elapsed_time == 0
        assert scrolling_content.extra_time_after_end == 0

    def test_perpetual_scroll(self):
        scrolling_content = movement.ScrollingContent(30, 0, 0, -1, 2, 3)
        scrolling_content.reset()
        assert scrolling_content.update(130)
        assert not scrolling_content.end_of_segment_reached
        assert scrolling_content.x_offset == 2
        assert scrolling_content.y_offset == -2  # moves at t=0, 30, 60, 90, 120
        assert scrolling_content.total_duration == 0
        assert scrolling_content.step_duration == 30
        assert scrolling_content.total_steps == 0
        assert scrolling_content.current_step_num == 0
        assert scrolling_content.elapsed_time == 10
        assert scrolling_content.extra_time_after_end == 0

    def test_within_step_scroll_left(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0, 2, 3)
        scrolling_content.reset()
        assert not scrolling_content.update(20)
        assert not scrolling_content.end_of_segment_reached
        assert scrolling_content.x_offset == 1
        assert scrolling_content.y_offset == 3
        assert scrolling_content.current_step_num == 0
        assert scrolling_content.elapsed_time == 20
        assert scrolling_content.extra_time_after_end == 0

    def test_across_steps_scroll_down(self):
        scrolling_content = movement.ScrollingContent(30, 4, 0, 1, 2, 3)
        scrolling_content.reset()
        assert not scrolling_content.update(20)
        assert not scrolling_content.end_of_segment_reached
        assert scrolling_content.update(50)
        assert not scrolling_content.end_of_segment_reached
        assert scrolling_content.x_offset == 2
        assert scrolling_content.y_offset == 6
        assert scrolling_content.current_step_num == 2
        assert scrolling_content.elapsed_time == 70
        assert scrolling_content.extra_time_after_end == 0

    def test_end_reached_scroll_left(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0, 2, 3)
        scrolling_content.reset()
        scrolling_content.update(80)
        assert scrolling_content.update(70)
        assert scrolling_content.end_of_segment_reached
        assert scrolling_content.x_offset == -2
        assert scrolling_content.y_offset == 3
        assert scrolling_content.current_step_num == 3
        assert scrolling_content.elapsed_time == 120
        assert scrolling_content.extra_time_after_end == 30

    def test_at_1_before_total_duration_add_1(self):
        scrolling_content = movement.ScrollingContent(30, 4, 0, 1, 2, 3)
        scrolling_content.reset()
        # total duration == 120
        assert scrolling_content.update(119)  # 1 before end
        assert not scrolling_content.end_of_segment_reached
        assert scrolling_content.x_offset == 2
        assert scrolling_content.y_offset == 7
        assert scrolling_content.current_step_num == 3

        # add 1
        assert not scrolling_content.update(1)  # no changed as end reached
        assert scrolling_content.end_of_segment_reached  # this has changed
        assert scrolling_content.x_offset == 2
        assert scrolling_content.y_offset == 7  # but not this
        assert scrolling_content.current_step_num == 3  # nor this
        assert scrolling_content.elapsed_time == 120
        assert scrolling_content.extra_time_after_end == 0

        # add 1
        assert not scrolling_content.update(1)
        assert scrolling_content.end_of_segment_reached  # no change
        assert scrolling_content.x_offset == 2
        assert scrolling_content.y_offset == 7  # no change
        assert scrolling_content.current_step_num == 3  # no change
        assert scrolling_content.elapsed_time == 120
        assert scrolling_content.extra_time_after_end == 1  # change

    def test_reset_scroll(self):
        scrolling_content = movement.ScrollingContent(30, 4, 0, -1, 2, 3)
        scrolling_content.reset()
        scrolling_content.update(80)
        scrolling_content.update(70)
        # (assume other movements happen, then loop back to this movement)
        scrolling_content.reset()
        scrolling_content.set_offset(8, 9)
        assert not scrolling_content.end_of_segment_reached
        assert scrolling_content.x_offset == 8
        assert scrolling_content.y_offset == 9
        assert scrolling_content.current_step_num == 0
        assert scrolling_content.elapsed_time == 0
        assert scrolling_content.extra_time_after_end == 0

    def test_set_offset(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0, 2, 3)
        scrolling_content.reset()
        scrolling_content.update(40)  # at t==40
        assert scrolling_content.x_offset == 0
        assert scrolling_content.y_offset == 3

        scrolling_content.set_offset(6, 8)
        scrolling_content.update(60)  # at t==100
        assert scrolling_content.x_offset == 4
        assert scrolling_content.y_offset == 8

    def test_set_offset_after_end(self):
        scrolling_content = movement.ScrollingContent(30, 4, -1, 0, 2, 3)
        scrolling_content.reset()
        scrolling_content.update(150)
        assert scrolling_content.x_offset == -2
        assert scrolling_content.y_offset == 3
        scrolling_content.set_offset(6, 8)
        scrolling_content.update(60)
        # no further movement
        assert scrolling_content.x_offset == 6
        assert scrolling_content.y_offset == 8


class TestMovementCycle:  # pylint: disable=attribute-defined-outside-init
    def setup_method(self):
        self.tracker = movement.MovementCycle(
            [movement.StaticContent(200), movement.ScrollingContent(15, 4, -1, 0)]
        )

    def test_init(self):
        assert len(self.tracker.anim_sequence) == 2
        assert isinstance(self.tracker.anim_sequence[0], movement.StaticContent)
        assert isinstance(self.tracker.anim_sequence[1], movement.ScrollingContent)
        assert not self.tracker._started

        assert self.tracker.cur_segment is None
        assert self.tracker.anim_sequence[0].x_offset is None
        assert self.tracker.anim_sequence[0].y_offset is None
        assert self.tracker.anim_sequence[0].extra_time_after_end is None
        assert self.tracker.anim_sequence[0].elapsed_time is None
        assert self.tracker.anim_sequence[1].x_offset is None
        assert self.tracker.anim_sequence[1].y_offset is None
        assert self.tracker.anim_sequence[1].extra_time_after_end is None
        assert self.tracker.anim_sequence[1].elapsed_time is None
        assert self.tracker.x_offset is None
        assert self.tracker.y_offset is None

    def test_reset(self):
        self.tracker.reset()
        self.tracker.set_offset(2, 3)
        assert self.tracker._started
        assert self.tracker.cur_segment == 0
        assert self.tracker.anim_sequence[0].x_offset == 2
        assert self.tracker.anim_sequence[0].y_offset == 3
        assert self.tracker.anim_sequence[0].extra_time_after_end == 0
        assert self.tracker.anim_sequence[0].elapsed_time == 0
        assert self.tracker.x_offset == 2
        assert self.tracker.y_offset == 3

    def test_within_segment(self):
        self.tracker.reset()
        self.tracker.set_offset(2, 3)
        self.tracker.update(180)
        assert self.tracker.cur_segment == 0
        assert self.tracker.anim_sequence[0].x_offset == 2
        assert self.tracker.anim_sequence[0].y_offset == 3
        assert self.tracker.anim_sequence[0].extra_time_after_end == 0
        assert self.tracker.anim_sequence[0].elapsed_time == 180
        assert not self.tracker.anim_sequence[0].end_of_segment_reached
        assert self.tracker.x_offset == 2
        assert self.tracker.y_offset == 3

    def test_across_segments(self):
        self.tracker.reset()
        self.tracker.set_offset(2, 3)
        self.tracker.update(235)
        assert self.tracker.cur_segment == 1
        assert self.tracker.anim_sequence[0].extra_time_after_end == 35
        assert self.tracker.anim_sequence[0].elapsed_time == 200
        assert self.tracker.anim_sequence[0].end_of_segment_reached
        assert self.tracker.anim_sequence[0].x_offset == 2
        assert self.tracker.anim_sequence[0].y_offset == 3
        assert self.tracker.anim_sequence[1].x_offset == -1
        assert self.tracker.anim_sequence[1].y_offset == 3
        assert self.tracker.anim_sequence[1].extra_time_after_end == 0
        assert self.tracker.anim_sequence[1].elapsed_time == 35
        assert self.tracker.anim_sequence[1].current_step_num == 2
        assert not self.tracker.anim_sequence[1].end_of_segment_reached
        assert self.tracker.x_offset == -1
        assert self.tracker.y_offset == 3

    def test_full_cycle(self):
        self.tracker.reset()
        self.tracker.set_offset(2, 3)
        self.tracker.update(500)
        assert self.tracker.cur_segment == 1
        assert self.tracker.anim_sequence[0].extra_time_after_end == 40
        assert self.tracker.anim_sequence[0].elapsed_time == 200
        assert self.tracker.anim_sequence[0].end_of_segment_reached
        assert self.tracker.anim_sequence[1].x_offset == -5
        assert self.tracker.anim_sequence[1].y_offset == 3
        assert self.tracker.anim_sequence[1].extra_time_after_end == 0
        assert self.tracker.anim_sequence[1].elapsed_time == 40
        assert self.tracker.anim_sequence[1].current_step_num == 2
        assert not self.tracker.anim_sequence[1].end_of_segment_reached
        assert self.tracker.x_offset == -5
        assert self.tracker.y_offset == 3

    def test_set_offset(self):
        self.tracker.reset()
        self.tracker.set_offset(2, 3)
        self.tracker.update(500)  # init with output of previous test
        assert self.tracker.x_offset == -5
        assert self.tracker.y_offset == 3
        self.tracker.set_offset(8, 2)
        assert self.tracker.x_offset == 8
        assert self.tracker.y_offset == 2
        self.tracker.update(15)
        assert self.tracker.cur_segment == 1
        assert self.tracker.anim_sequence[1].x_offset == 7
        assert self.tracker.anim_sequence[1].y_offset == 2
        assert self.tracker.anim_sequence[1].elapsed_time == 55
        assert self.tracker.anim_sequence[1].current_step_num == 3
