import time
import threading
import logging

import departure.board.data_updater as data_updater
from departure.commons.log import log_function_stdout_to_debug
from . import view_model, tfl_tube, ui

logger = logging.getLogger(__name__)


class DataUpdaterTflTube(data_updater.DataUpdater):
    def __init__(
        self,
        target_view_model: view_model.ViewModelTflTube,
        data_refresh_delay_in_s: int,
        end_event: threading.Event,
        line_id: str,
        station_id: str,
        direction: str,
    ):
        super().__init__(target_view_model, data_refresh_delay_in_s, end_event)
        self.line_id = line_id
        self.station_id = station_id
        self.direction = direction
        self.trains = None

    def update(self):
        update_start_time = time.monotonic()
        logger.info("data refresh started at %s", update_start_time)

        trains = tfl_tube.next_trains(self.line_id, self.station_id, self.direction)

        # debugging: capture list of trains to string, then log
        log_function_stdout_to_debug(logger, ui.list_trains_single_station, trains)

        # update board only if there were changes
        if trains == self.trains:
            logger.info("no change - no update sent to board")
        else:
            self.view_model.update(trains)
            self.trains = trains

        logger.info("data refresh duration %s", time.monotonic() - update_start_time)
