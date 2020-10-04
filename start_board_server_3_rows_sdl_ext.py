from concurrent import futures

import threading

import sdl2.ext
import grpc

import departure.board.animator as animator
import departure.board.board_updater as board_updater
import departure.board.board as board
import departure.renderer.local_sdl_ext as local_sdl_ext
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
    sdl_renderer = local_sdl_ext.SdlExtRendererLarge()
    # sdl_renderer = local_sdl_ext.SdlExtRendererActualSize()
    sdl_renderer.initialise((192, 32))

    board_lock = threading.RLock()
    end_event = threading.Event()

    # initialise board animator
    animator_thread = animator.BoardAnimator(
        board=tfl_board,
        renderer=sdl_renderer,
        time_step_in_s=0.05,
        board_lock=board_lock,
        end_event=end_event,
    )

    # initilaise board updater (also initialises board with 3 rows)
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

    running = True
    try:
        while running:
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    print("received SDL QUIT event")  # debugging
                    running = False
                    break
            end_event.wait(0.5)
    except KeyboardInterrupt:
        print("received keyboard interrupt")  # debugging

    end_event.set()
    server.stop(0)
    animator_thread.join()

    sdl_renderer.terminate()


if __name__ == "__main__":
    run()
