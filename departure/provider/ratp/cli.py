"""
CLI for RATP
"""

import threading
import time
import logging

import click

from departure.board import board_client

from . import ui, ratp, view_model, data_updater

ONE_DAY_IN_SECONDS = 60 * 60 * 24
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """
    Information and departures for RATP (FR).
    """


@click.command()
@click.argument("query_string")
def search(query_string):
    """Search for stations containing QUERY_STRING."""
    stations = ratp.stations_by_name(query_string)
    ui.list_stations(stations, show_line=True, show_station_id=True)


@click.command(name="lines")
@click.argument("code_query", required=False, default="")
def lines_by_code(code_query):
    """
    Search for lines by number.

    If CODE_QUERY is provided, search line numbers containing the query text.
    Otherwise, list all lines.
    """
    lines_result = ratp.lines_by_code(code_query)
    ui.list_lines(lines_result)


@click.command(name="lines-name")
@click.argument("line_query", required=False, default="")
def lines_by_name(line_query):
    """
    Search for lines by name (termini).

    If LINE_QUERY is provided, search line names containing the query text.
    Otherwise, list all lines.
    """
    lines = ratp.lines_by_name(line_query.lower())
    ui.list_lines(lines)


@click.command()
@click.argument("line_id")
def directions(line_id):
    """
    Get directions for LINE_ID.

    Use line search commands to find the LINE_ID for a line.
    """

    line_directions = ratp.directions(line_id)
    ui.list_directions(line_directions)


@click.command(name="stations-line")
@click.argument("line_id")
def stations_by_line(line_id):
    """
    Get stations on LINE_ID.

    Use line search commands to find the LINE_ID for a line.
    """

    stations = ratp.stations_by_line(line_id)
    ui.list_stations(stations, show_station_id=True)


@click.command(name="next", short_help="Get next departures at station.")
@click.argument("line_id")
@click.argument("line_station_id")
@click.argument("direction")
def next_departures(line_id, line_station_id, direction):
    """
    Get next departures at station LINE_STATION_ID, on line LINE_ID, in direction
    DIRECTION.

    Use the line search commands to find the LINE_ID for a line, the stations-line
    command to find the LINE_STATION_ID for a station on a specific line, and the
    direction command to find the DIRECTIONs for a line.
    """

    departures = ratp.next_departures(line_id, line_station_id, direction)
    ui.list_departures(departures)


@click.command(
    name="board", short_help="Update a departure board with departures at a station."
)
@click.argument("line_id")
@click.argument("line_station_id")
@click.argument("direction_code")
def start_board(line_id, line_station_id, direction_code):
    """Update a departure board with departures at station LINE_STATION_ID, on line
    LINE_ID in direction DIRECTION_CODE.

    Use the line search commands to find the LINE_ID for a line, the stations-line
    command to find the LINE_STATION_ID for a station on a specific line, and the
    direction command to find the DIRECTION_CODEs for a line.
    """

    # start board
    board_client_instance = board_client.BoardClient()

    threading.Thread(
        target=board_client_instance.run,
        args=[
            view_model.ViewModelRatp_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterRatp,
            {
                "line_id": line_id,
                "line_station_id": line_station_id,
                "direction": direction_code,
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
