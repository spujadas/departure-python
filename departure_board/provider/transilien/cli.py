"""
CLI for Transilien
"""

import threading
import time
import logging

import click

from departure_board.board import board_client

from . import ui, transilien, commons, view_model, data_updater

ONE_DAY_IN_SECONDS = 60 * 60 * 24
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@click.command()
@click.argument("query_string")
def search(query_string):
    stations = transilien.stations_by_string(query_string)
    ui.list_stations(stations)

@click.command(name="next")
@click.argument("station_id")
def next_trains(station_id):
    try:
        trains = transilien.next_trains(station_id)
    except commons.TransilienException as e:
        print(f"error: {str(e)}")
        return

    ui.list_trains(trains)


@click.command(name="board")
@click.argument("station_id")
def start_board(station_id):
    try:
        transilien.check_params(station_id)
    except commons.TransilienException as e:
        print(f"error: {str(e)}")
        return

    # start board
    board_client_instance = board_client.BoardClient()

    threading.Thread(
        target=board_client_instance.run,
        args=[
            view_model.ViewModelTransilien_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterTransilien,
            {
                "station_id": station_id,
            },
        ],
    ).start()

    # run until interrupt
    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info("received interrupt")
        board_client_instance.running = False


cli.add_command(search)
cli.add_command(next_trains)
cli.add_command(start_board)

if __name__ == "__main__":
    cli()
