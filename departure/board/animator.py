import time
import threading
import logging

from departure.board.board import Board
from departure.board.renderer import Renderer

logger = logging.getLogger(__name__)


class BoardAnimator(threading.Thread):
    def __init__(
        self,
        board: Board,
        renderer: Renderer,
        time_step_in_s: float,
        board_lock: threading.RLock,
        end_event: threading.Event,
    ):
        super().__init__()
        self.board = board
        self.renderer = renderer
        self.time_step_in_s = time_step_in_s
        self.board_lock = board_lock
        self.end_event = end_event

    def update(self, delta_time: int):
        self.board.update(delta_time)
        self.renderer.render_frame(self.board.pixels())

    def run(self):
        self.board.reset()

        # start the clock
        last_loop_start_time = time.monotonic()
        next_loop_start_time = time.monotonic() + self.time_step_in_s

        # code for non-drifting loop from
        # https://raspberrypi.stackexchange.com/a/34245

        while not self.end_event.is_set():
            this_loop_start_time = time.monotonic()

            # pylint: disable=pointless-string-statement
            """
            # display drift (debugging)
            logger.debug('drift {:.02f} ms'.format(
                1000 * (this_loop_start_time - next_loop_start_time
                    + self.time_step_in_s)
                ))
            """

            with self.board_lock:
                self.update(int(1000 * (time.monotonic() - last_loop_start_time)))

            delay = -self.time_step_in_s
            missed = 0

            while delay < 0.0:
                delay = next_loop_start_time - time.monotonic()
                next_loop_start_time += self.time_step_in_s
                missed += 1

            if missed > 1:
                logger.warning(
                    "exceeded animation loop step duration %s time(s)", missed - 1
                )

            self.end_event.wait(delay)
            last_loop_start_time = this_loop_start_time

        logger.info("board animator stopped running")
