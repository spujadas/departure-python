from typing import List


class MovementException(Exception):
    pass


class Movement:
    def __init__(self, x_offset_init=0, y_offset_init=0):
        self.x_offset_init = x_offset_init
        self.y_offset_init = y_offset_init
        self.x_offset = None
        self.y_offset = None
        self._started = False

    def reset(self):
        # next line removed to avoid complications with inheritance
        # self.set_offset(x_offset, y_offset)
        self.x_offset = self.x_offset_init
        self.y_offset = self.y_offset_init
        self._started = True

    def update(self, delta_time):
        # raise Exception if update() is called before reset()
        if not self._started:
            raise MovementException(f"movement not started for object {type(self)}")
        return False  # have offsets changed?

    def set_offset(self, x_offset, y_offset):
        # e.g. used to update movement offset if it has wrapped
        self.x_offset = x_offset
        self.y_offset = y_offset


class NoMovement(Movement):
    pass


class MovementSegment(Movement):
    # abstract parent class for Movement segments (i.e. Movements that
    # can have a limited duration, designed to be combined with other
    # Movements)
    def __init__(self, x_offset_init=0, y_offset_init=0):
        super().__init__(x_offset_init, y_offset_init)
        self.elapsed_time = None
        self.extra_time_after_end = None
        self.end_of_segment_reached = None

    def reset(self):
        super().reset()
        # used at beginning of segment and after cycling back to segment
        self.elapsed_time = 0
        self.extra_time_after_end = 0
        self.end_of_segment_reached = False

    def update(self, delta_time):
        return super().update(delta_time)


class StaticContent(MovementSegment):
    def __init__(self, total_duration, x_offset_init=0, y_offset_init=0):
        super().__init__(x_offset_init, y_offset_init)
        self.total_duration = total_duration  # 0: forever

    def update(self, delta_time):
        super().update(delta_time)

        # no update if unlimited duration
        if self.total_duration == 0:
            return False

        self.elapsed_time += delta_time

        # if end of segment reached, also calculate remaining time beyond end
        if self.elapsed_time >= self.total_duration:
            self.end_of_segment_reached = True
            self.extra_time_after_end = self.elapsed_time - self.total_duration
            self.elapsed_time = self.total_duration

        return False


class ScrollingContent(MovementSegment):
    def __init__(
        self,
        step_duration: int,
        total_steps: int,  # 0: forever
        delta_x_per_step: int,
        delta_y_per_step: int,
        x_offset_init: int = 0,
        y_offset_init: int = 0,
    ):
        super().__init__(x_offset_init, y_offset_init)
        self.step_duration = step_duration
        self.total_steps = total_steps
        self.total_duration = total_steps * step_duration  # helper
        self.delta_x_per_step = delta_x_per_step
        self.delta_y_per_step = delta_y_per_step
        self.current_step_num = None

    def reset(self):
        super().reset()
        self.current_step_num = 0

        # first scroll at t==0 (will not scroll at t==total_duration)
        self.x_offset += self.delta_x_per_step
        self.y_offset += self.delta_y_per_step

    def update(self, delta_time):
        super().update(delta_time)
        new_elapsed_time = self.elapsed_time + delta_time

        # if perpetual scroll
        if self.total_duration == 0:
            # advance...
            new_step_num = new_elapsed_time // self.step_duration
            delta_step_num = new_step_num - self.current_step_num
            self.x_offset += delta_step_num * self.delta_x_per_step
            self.y_offset += delta_step_num * self.delta_y_per_step

            # ... and reset to step 0 (avoids risk of overflow)
            self.current_step_num = 0
            self.elapsed_time = new_elapsed_time % self.step_duration
            return delta_step_num > 0

        # if end of segment reached
        # note - '>=': do *not* scroll at t==total_duration (scrolled at t==0)
        if new_elapsed_time >= self.total_duration:
            self.end_of_segment_reached = True

            # advance
            delta_step_num = (self.total_steps - 1) - self.current_step_num
            self.x_offset += delta_step_num * self.delta_x_per_step
            self.y_offset += delta_step_num * self.delta_y_per_step

            # set current position at end of segment
            self.current_step_num = self.total_steps - 1
            self.elapsed_time = self.total_duration

            # and calculate remaining time beyond end
            self.extra_time_after_end = new_elapsed_time - self.total_duration

            return delta_step_num > 0

        # if within (bounded) segment
        new_step_num = new_elapsed_time // self.step_duration
        delta_step_num = new_step_num - self.current_step_num
        self.x_offset += delta_step_num * self.delta_x_per_step
        self.y_offset += delta_step_num * self.delta_y_per_step
        self.current_step_num = new_step_num
        self.elapsed_time = new_elapsed_time

        return delta_step_num > 0


class MovementCycle(Movement):
    def __init__(self, anim_sequence: List[MovementSegment]):
        super().__init__()
        self.anim_sequence = anim_sequence
        self.cur_segment = None
        self._started = False

    def reset(self):
        super().reset()
        self.cur_segment = 0
        self.anim_sequence[0].reset()

        # get initial offset (content may move after reset)
        self.x_offset = self.anim_sequence[0].x_offset
        self.y_offset = self.anim_sequence[0].y_offset

        self._started = True

    def update(self, delta_time):
        super().update(delta_time)

        while True:
            # update current segment by delta_time
            self.anim_sequence[self.cur_segment].update(delta_time)
            end_of_segment_reached = self.anim_sequence[
                self.cur_segment
            ].end_of_segment_reached
            new_x_offset = self.anim_sequence[self.cur_segment].x_offset
            new_y_offset = self.anim_sequence[self.cur_segment].y_offset

            # stop if end of current segment not reached
            if not end_of_segment_reached:
                break

            # otherwise retrieve amount of remaining time...
            delta_time = self.anim_sequence[self.cur_segment].extra_time_after_end

            # ... and move on to next segment
            self.cur_segment = (self.cur_segment + 1) % len(self.anim_sequence)
            self.anim_sequence[self.cur_segment].x_offset_init = new_x_offset
            self.anim_sequence[self.cur_segment].y_offset_init = new_y_offset
            self.anim_sequence[self.cur_segment].reset()

        if new_x_offset == self.x_offset and new_y_offset == self.y_offset:
            return False

        self.set_offset(new_x_offset, new_y_offset)
        return True

    def set_offset(self, x_offset, y_offset):
        super().set_offset(x_offset, y_offset)
        self.anim_sequence[self.cur_segment].set_offset(x_offset, y_offset)
