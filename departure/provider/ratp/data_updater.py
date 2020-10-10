import time
import threading
import logging

import departure.board.data_updater as data_updater
from departure.commons.log import log_function_stdout_to_debug
from . import view_model, ratp, ui, commons

logger = logging.getLogger(__name__)


class DataUpdaterRatp(data_updater.DataUpdater):
    def __init__(
        self,
        target_view_model: view_model.ViewModelRatp,
        data_refresh_delay_in_s: int,
        end_event: threading.Event,
        line_id: str,
        line_station_id: str,
        direction: str,
    ):
        super().__init__(target_view_model, data_refresh_delay_in_s, end_event)
        self.line_id = line_id
        self.line_station_id = line_station_id
        self.direction = direction
        self.departures = None

    def update(self):
        update_start_time = time.monotonic()
        logger.info("data refresh started at %s", update_start_time)

        try:
            departures = ratp.next_departures(
                self.line_id, self.line_station_id, self.direction
            )
        except commons.RatpException as e:
            logger.warning(
                "%s - line id %s, line station id %s, direction %s",
                str(e),
                self.line_id,
                self.line_station_id,
                self.direction,
            )
            return

        # debugging: capture list of departures to string, then log
        log_function_stdout_to_debug(logger, ui.list_departures, departures)

        # update board only if there were changes
        if departures == self.departures:
            logger.info("no change - no update sent to board")
        else:
            self.view_model.update(departures)
            self.departures = departures

        logger.info("data refresh duration %s", time.monotonic() - update_start_time)
