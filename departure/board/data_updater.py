import time
import threading
import logging

import departure.board.view_model as view_model

logger = logging.getLogger(__name__)


class DataUpdater(threading.Thread):
    def __init__(
        self,
        target_view_model: view_model.ViewModel,
        data_refresh_delay_in_s: int,
        end_event: threading.Event,
    ):
        super().__init__()
        self.view_model = target_view_model
        self.data_refresh_delay_in_s = data_refresh_delay_in_s
        self.end_event = end_event

    def run(self):
        while not self.end_event.is_set():
            loop_start_time = time.monotonic()
            next_loop_start_time = loop_start_time + self.data_refresh_delay_in_s

            self.update()

            if next_loop_start_time > time.monotonic():
                self.end_event.wait(next_loop_start_time - time.monotonic())
            else:
                logger.warning("exceeded data update refresh delay")

        logger.info("data updater stopped running")

    def update(self):
        raise NotImplementedError()
