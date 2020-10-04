# run with:
# python start-board-3-rows-server-pygame.py
# stop with Ctrl-C on **QWERTY** keyboard

from concurrent import futures
import threading

import pygame
import grpc

import departure.board.animator as animator
import departure.board.board_updater as board_updater
import departure.board.board as board
import departure.renderer.local_pygame as local_pygame
import departure.board.departure_pb2_grpc as departure_pb2_grpc


class BoardManagerServicer(departure_pb2_grpc.BoardManagerServicer):
    def __init__(
        self,
        target_board_updater: board_updater.BoardUpdater_192_32_3_Rows_From_ProtocolBuffers,
    ):
        self.target_board_updater = target_board_updater

    def BoardSectionsUpdate(self, request, context):
        return self.target_board_updater.update(request)


def run():
    tfl_board = board.Board(192, 32)

    # initialise renderer
    pygame_renderer = local_pygame.PygameRendererLarge()
    pygame_renderer.initialise((192, 32))

    board_lock = threading.RLock()
    end_event = threading.Event()

    # initialise board animator
    animator_thread = animator.BoardAnimator(
        board=tfl_board,
        renderer=pygame_renderer,
        time_step_in_s=0.05,
        board_lock=board_lock,
        end_event=end_event,
    )

    # initialise board updater (also initialises board with 3 rows)
    target_board_updater = (
        board_updater.BoardUpdater_192_32_3_Rows_From_ProtocolBuffers(
            target_board=tfl_board, board_lock=board_lock
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

    while not end_event.is_set():
        # note: this isn't good, but it's required by pygame :(
        for event in pygame.event.get():
            if (
                event.type == pygame.KEYUP
                and event.key == pygame.K_c
                and event.mod & pygame.KMOD_CTRL
            ):
                print("received interrupt")  # debugging
                end_event.set()
                server.stop(0)
                animator_thread.join()
        end_event.wait(0.5)

    pygame_renderer.terminate()


if __name__ == "__main__":
    run()
