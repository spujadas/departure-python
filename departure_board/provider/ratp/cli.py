"""
CLI for RATP
"""


import threading
import time
import logging

import click

from departure_board.board import board_client

from . import ui, ratp, view_model, data_updater

ONE_DAY_IN_SECONDS = 60 * 60 * 24
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@click.command()
@click.argument("query_string")
def search(query_string):
    stations = ratp.stations_by_name(query_string)
    ui.list_stations(stations, show_line=True)


@click.command(name="lines")
@click.argument("code_query", required=False, default='')
def lines_by_code(code_query):
    lines_result = ratp.lines_by_code(code_query)
    ui.list_lines(lines_result)


@click.command(name="lines-name")
@click.argument("line_query", required=False, default='')
def lines_by_name(line_query):
    lines = ratp.lines_by_name(line_query.lower())
    ui.list_lines(lines)


@click.command()
@click.argument("line_id")
def directions(line_id):
    line_directions = ratp.directions(line_id)
    ui.list_directions(line_directions)


@click.command(name="stations-line")
@click.argument("line_id")
def stations_by_line(line_id):
    stations = ratp.stations_by_line(line_id)
    ui.list_stations(stations, show_station_id=True)


@click.command(name="next", help="e.g. RB 15 A")
@click.argument("line_id")
@click.argument("line_station_id")
@click.argument("direction")
def next_departures(line_id, line_station_id, direction):
    departures = ratp.next_departures(line_id, line_station_id, direction)
    ui.list_departures(departures)


@click.command(name="board")
@click.argument("line_id")
@click.argument("line_station_id")
@click.argument("direction")
def start_board(line_id, line_station_id, direction):
    # start board
    board_client_instance = board_client.BoardClient()

    threading.Thread(
        target=board_client_instance.run,
        args=[
            view_model.ViewModelRatp_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterRatp,
            {
                'line_id': line_id,
                'line_station_id': line_station_id,
                'direction': direction
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
cli.add_command(lines_by_code)
cli.add_command(lines_by_name)
cli.add_command(directions)
cli.add_command(stations_by_line)
cli.add_command(next_departures)
cli.add_command(start_board)

if __name__ == "__main__":
    cli()
