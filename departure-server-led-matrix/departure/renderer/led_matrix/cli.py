from concurrent import futures

import threading
import logging

import grpc
import click

import departure.board.animator as animator
import departure.board.board_updater as board_updater
import departure.board.board as board
import departure.board.departure_pb2_grpc as departure_pb2_grpc

from . import renderer

COMMAND='led'

logger = logging.getLogger(__name__)


class BoardManagerServicer(departure_pb2_grpc.BoardManagerServicer):
    def __init__(
        self,
        target_board_updater: board_updater.BoardUpdater_192_32_3_Rows_From_ProtocolBuffers,
    ):
        self.target_board_updater = target_board_updater

    def BoardSectionsUpdate(self, request, context):
        return self.target_board_updater.update(request)

@click.command(name='led')
def run():
    target_board = board.Board(192, 32)

    target_renderer = renderer.Renderer()

    target_renderer.initialise()

    board_lock = threading.RLock()
    end_event = threading.Event()

    # initialise board animator
    animator_thread = animator.BoardAnimator(
        board=target_board,
        renderer=target_renderer,
        time_step_in_s=0.05,
        board_lock=board_lock,
        end_event=end_event,
    )

    # initialise board updater (also initialises board with 3 rows)
    target_board_updater = (
        board_updater.BoardUpdater_192_32_3_Rows_From_ProtocolBuffers(
            target_board=target_board, board_lock=board_lock
        )
    )

    # initialise gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    departure_pb2_grpc.add_BoardManagerServicer_to_server(
        BoardManagerServicer(target_board_updater), server
    )
    server.add_insecure_port("[::]:50051")

    # start gRPC server and board animator
    animator_thread.start()
    server.start()

    try:
        while not end_event.is_set():
            end_event.wait(0.5)
    except KeyboardInterrupt:
        logger.info("received keyboard interrupt")

    end_event.set()
    server.stop(0)
    animator_thread.join()

    target_renderer.terminate()


if __name__ == "__main__":
    run()
