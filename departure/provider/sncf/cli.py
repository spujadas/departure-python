"""
CLI for SNCF
"""


import threading
import time
import logging

import click

from departure.board import board_client

from . import ui, sncf, commons, view_model, data_updater

ONE_DAY_IN_SECONDS = 60 * 60 * 24
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@click.command()
@click.argument("query_string")
def search(query_string):
    stations = sncf.stations_by_string(query_string)
    ui.list_stations(stations)


@click.command(name="next")
@click.argument("stop_area_id")
@click.option("--full", "timetable_for_all_trains", is_flag=True)
def next_departures(stop_area_id, timetable_for_all_trains):
    trains = sncf.next_trains(stop_area_id, timetable_for_all_trains)
    ui.list_trains(trains)


@click.command(name="board")
@click.argument("stop_area_id")
def start_board(stop_area_id):
    try:
        sncf.check_params(stop_area_id)
    except commons.SncfException as e:
        logger.error("error: %s", str(e))

    # start board
    board_client_instance = board_client.BoardClient()

    threading.Thread(
        target=board_client_instance.run,
        args=[
            view_model.ViewModelSncf_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterSncf,
            {
                "stop_area_id": stop_area_id,
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
cli.add_command(next_departures)
cli.add_command(start_board)

if __name__ == "__main__":
    cli()
