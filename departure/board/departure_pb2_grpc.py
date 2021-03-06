# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from departure.board import departure_pb2 as departure_dot_board_dot_departure__pb2


class BoardManagerStub(object):
    """service"""

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.BoardSectionsUpdate = channel.unary_unary(
            "/departure.proto.BoardManager/BoardSectionsUpdate",
            request_serializer=departure_dot_board_dot_departure__pb2.BoardSectionsUpdateRequest.SerializeToString,
            response_deserializer=departure_dot_board_dot_departure__pb2.BoardSectionsUpdateResponse.FromString,
        )


class BoardManagerServicer(object):
    """service"""

    def BoardSectionsUpdate(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_BoardManagerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "BoardSectionsUpdate": grpc.unary_unary_rpc_method_handler(
            servicer.BoardSectionsUpdate,
            request_deserializer=departure_dot_board_dot_departure__pb2.BoardSectionsUpdateRequest.FromString,
            response_serializer=departure_dot_board_dot_departure__pb2.BoardSectionsUpdateResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "departure.proto.BoardManager", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
