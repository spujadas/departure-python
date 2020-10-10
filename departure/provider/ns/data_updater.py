import time
import threading
import logging

import departure.board.data_updater as data_updater
from departure.commons.log import log_function_stdout_to_debug
from . import view_model, ns, ui, commons

logger = logging.getLogger(__name__)


class DataUpdaterNS(data_updater.DataUpdater):
    def __init__(
        self,
        target_view_model: view_model.ViewModelNS,
        data_refresh_delay_in_s: int,
        end_event: threading.Event,
        station_code: str,
    ):
        super().__init__(target_view_model, data_refresh_delay_in_s, end_event)
        self.station_code = station_code
        self.departures = None

    def update(self):
        update_start_time = time.monotonic()
        logger.info("data refresh started at %s", update_start_time)

        try:
            departures = ns.departures_with_schedule(self.station_code)
        except commons.NSException as e:
            logger.warning("%s - station code %s", str(e), self.station_code)
            return

        # debugging: capture list of services to string, then log
        log_function_stdout_to_debug(
            logger, ui.list_departures_with_schedule, departures, self.station_code
        )

        # update board only if there were changes
        if departures == self.departures:
            logger.info("no change - no update sent to board")
        else:
            self.view_model.update(departures, self.station_code)
            self.departures = departures

        logger.info("data refresh duration %s", time.monotonic() - update_start_time)
