import time
import threading
import logging

import departure.board.data_updater as data_updater
from departure.commons.log import log_function_stdout_to_debug
from . import view_model, sncf, ui

logger = logging.getLogger(__name__)


class DataUpdaterSncf(data_updater.DataUpdater):
    def __init__(
        self,
        target_view_model: view_model.ViewModelSncf,
        data_refresh_delay_in_s: int,
        end_event: threading.Event,
        stop_area_id: str,
    ):
        super().__init__(target_view_model, data_refresh_delay_in_s, end_event)
        self.stop_area_id = stop_area_id
        self.trains = None

    def update(self):
        update_start_time = time.monotonic()
        logger.info("data refresh started at %s", update_start_time)

        trains = sncf.next_trains(self.stop_area_id)

        # debugging: capture list of trains to string, then log
        log_function_stdout_to_debug(logger, ui.list_trains, trains)

        # update board only if there were changes
        if trains == self.trains:
            logger.info("no change - no update sent to board")
        else:
            self.view_model.update(trains)
            self.trains = trains

        logger.info("data refresh duration %s", time.monotonic() - update_start_time)
