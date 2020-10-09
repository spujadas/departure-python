"""
CLI for Pygame 3-row renderer
"""

from concurrent import futures
import threading
import logging
import os

import click
import grpc

# suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# pylint: disable=wrong-import-position
import pygame

import departure.board.animator as animator
import departure.board.board_updater as board_updater
import departure.board.board as board
import departure.board.departure_pb2_grpc as departure_pb2_grpc

from . import renderer

COMMAND='pygame'

logger = logging.getLogger(__name__)


class BoardManagerServicer(departure_pb2_grpc.BoardManagerServicer):
    def __init__(
        self,
        target_board_updater: board_updater.BoardUpdater_192_32_3_Rows_From_ProtocolBuffers,
    ):
        self.target_board_updater = target_board_updater

    def BoardSectionsUpdate(self, request, context):
        return self.target_board_updater.update(request)

@click.command(name='pygame')
def run():
    target_board = board.Board(192, 32)

    # initialise renderer
    target_renderer = renderer.PygameRendererLarge()
    target_renderer.initialise((192, 32))

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

    print("stop with Ctrl-C on *QWERTY* keyboard\n")

    while not end_event.is_set():
        # note: this isn't good, but it's required by pygame :(
        for event in pygame.event.get():
            if (
                event.type == pygame.KEYUP
                and event.key == pygame.K_c
                and event.mod & pygame.KMOD_CTRL
            ):
                logger.info("received interrupt")
                end_event.set()
                server.stop(0)
                animator_thread.join()
        end_event.wait(0.5)

    target_renderer.terminate()


if __name__ == "__main__":
    run()
