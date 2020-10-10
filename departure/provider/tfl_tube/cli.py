"""
CLI for London Underground (TfL Tube)
"""

import threading
import time
import logging
import cProfile
import pstats

import click

from departure.board import board_client

from . import ui, tfl_tube, commons, view_model, data_updater
from . import api

ONE_DAY_IN_SECONDS = 60 * 60 * 24
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """
    Information and departures for London Underground (UK).

    Note - Your TfL application key must be assigned to the TFL_APP_KEY environment
    variable.
    """


@click.command(name="search")
@click.argument("query_string", required=False, default="")
def search(query_string):
    """Search for stations."""
    if query_string:
        stations_result = tfl_tube.stations_by_string(query_string)
        ui.list_stations(stations_result)
    else:
        ui.list_stations()


@click.command()
def lines():
    """List lines and directions."""
    ui.list_lines()


@click.command(name="next", short_help="Get next services at station.")
@click.argument("line_id")
@click.argument("station_id")
@click.argument("direction")
@click.option(
    "--profiling", is_flag=True, help="(debugging) performance profiling"
)
def next_departures(line_id, station_id, direction, profiling):
    """
    Get next departures at station STATION_ID, on line LINE_ID, in direction
    DIRECTION.

    Use the lines command to find the LINE_ID and possible DIRECTIONs for a line,
    and the search command to find the STATION_ID and LINE_ID for a station.

    Note - This command accepts short versions of its argument values: the line's
    initial (or first two characters for the Central and Circle lines), the last three
    characters of the station, and the direction's initial.
    For example you can use 'next ce oxc w' to find the next Westbound departures on
    the Central line at Oxford Circus.
    """

    try:
        if profiling:
            prof = cProfile.Profile()
            prof.enable()

        trains = tfl_tube.next_trains(
            ui.expanded_line_id(line_id),
            ui.expanded_station_id(station_id),
            ui.expanded_direction(direction),
        )
        ui.list_trains_single_station(trains)

        if profiling:
            prof.disable()
            prof_stats = pstats.Stats(prof)
            prof_stats.strip_dirs()
            prof_stats.sort_stats("cumulative")
            prof_stats.print_stats("tfl_tube")

    except commons.TflTubeException as e:
        print(f"error: {str(e)}")


@click.command(name="at-station", help="(debugging) list arrivals")
@click.option("--line_ids", help="LINE_ID[,LINE_ID]*")
@click.option("--station_id", help="STATION_ID")
@click.option("--direction", help="DIRECTION")
def at_station(line_ids=None, station_id=None, direction=None):
    if line_ids is not None:
        line_ids = line_ids.split(",")
        line_ids = [ui.expanded_line_id(l) for l in line_ids]

    if station_id is not None:
        station_id = ui.expanded_station_id(station_id)

    if direction is not None:
        direction = ui.expanded_direction(direction)

    try:
        arrivals = api.tube_arrivals(count=-1)

        if arrivals is None:
            print("no arrivals")
            return

        trains = tfl_tube.filter_trains_currently_at_platform(
            arrivals, line_ids, station_id, direction
        )
        ui.list_trains_multiple_stations(trains)
    except commons.TflTubeException as e:
        print(f"error: {str(e)}")


@click.command(name="board")
@click.argument("line_id")
@click.argument("station_id")
@click.argument("direction_id")
def start_board(line_id, station_id, direction_id):
    """Update a departure board with departures at station STATION_ID, on line
    LINE_ID in direction DIRECTION_CODE.

    Use the lines command to find the LINE_ID and possible DIRECTIONs for a line,
    and the search command to find the STATION_ID and LINE_ID for a station.

    Note - This command accepts short versions of its argument values: the line's
    initial (or first two characters for the Central and Circle lines), the last three
    characters of the station, and the direction's initial.
    For example you can use 'next ce oxc w' to find the next Westbound departures on
    the Central line at Oxford Circus.
    """

    line_id = ui.expanded_line_id(line_id)
    station_id = ui.expanded_station_id(station_id)
    direction = ui.expanded_direction(direction_id)

    try:
        tfl_tube.check_params([line_id], station_id, direction)
    except commons.TflTubeException as e:
        logger.error(str(e))
        return

    # start board
    board_client_instance = board_client.BoardClient()

    threading.Thread(
        target=board_client_instance.run,
        args=[
            view_model.ViewModelTflTube_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterTflTube,
            {"line_id": line_id, "station_id": station_id, "direction": direction},
        ],
    ).start()

    # run until interrupt
    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info("received interrupt")  # debugging
        board_client_instance.running = False


cli.add_command(search)
cli.add_command(lines)
cli.add_command(next_departures)
cli.add_command(at_station)
cli.add_command(start_board)

if __name__ == "__main__":
    cli()
