import threading
import os
import logging

import grpc

import departure.board.departure_pb2_grpc as departure_pb2_grpc

from . import data_updater, view_model

logger = logging.getLogger(__name__)


class BoardClient:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.running = False

    def run(
        self,
        view_model_class: view_model.ViewModel,
        data_updater_class: data_updater.DataUpdater,
        data_updater_extra_arguments: dict,
    ) -> None:

        end_event = threading.Event()

        # set departure board server
        if "DEPARTURE_BOARD_SERVER" in os.environ:
            departure_board_server = os.environ["DEPARTURE_BOARD_SERVER"]
            server_info_str = "DEPARTURE_BOARD_SERVER env var set - "
        else:
            server_info_str = "DEPARTURE_BOARD_SERVER env var not set - "
            departure_board_server = "127.0.0.1"
        logger.info("%s using %s as server", server_info_str, departure_board_server)

        # open channel to board server
        channel = grpc.insecure_channel(f"{departure_board_server}:50051")

        # set up client parameters
        board_manager_stub = departure_pb2_grpc.BoardManagerStub(channel)
        target_view_model = view_model_class(board_manager_stub)

        # init and run updater thread
        data_updater_thread = data_updater_class(
            target_view_model=target_view_model,
            data_refresh_delay_in_s=15,
            end_event=end_event,
            **data_updater_extra_arguments,
        )

        data_updater_thread.start()

        self.running = True

        # run until self.running is set to false
        while self.running:
            end_event.wait(0.5)

        # clean and exit
        logger.info("stopping")
        end_event.set()
        data_updater_thread.join()
        target_view_model.update(None)
