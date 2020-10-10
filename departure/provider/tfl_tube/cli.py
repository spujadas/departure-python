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
    pass


@click.command(name="search")
@click.argument("query_string")
def search(query_string):
    stations_result = tfl_tube.stations_by_string(query_string)
    ui.list_stations(stations_result)


@click.command()
def lines():
    ui.list_lines()


@click.command()
def stations():
    ui.list_stations()


@click.command(name="next")
@click.argument("line_code")
@click.argument("station_code")
@click.argument("direction")
@click.option("--profiling", is_flag=True)
def next_departures(line_code, station_code, direction, profiling):
    try:
        if profiling:
            prof = cProfile.Profile()
            prof.enable()

        trains = tfl_tube.next_trains(
            ui.expanded_line_id(line_code),
            ui.expanded_station_id(station_code),
            ui.expanded_direction(direction),
        )
        ui.list_trains_single_station(trains)

        if profiling:
            prof.disable()
            prof_stats = pstats.Stats(prof)
            prof_stats.strip_dirs()
            prof_stats.sort_stats("cumulative")
            prof_stats.print_stats("tfl")

    except commons.TflTubeException as e:
        print(f"error: {str(e)}")


@click.command(name="at-station", help="debugging only")
@click.option("--line_codes", help="<line-id[,line-id]*>")
@click.option("--station_code", help="<station-id>")
@click.option("--direction", help="<direction>")
def at_station(line_codes=None, station_code=None, direction=None):
    if line_codes is not None:
        line_codes = line_codes.split(",")
        line_codes = [ui.expanded_line_id(l) for l in line_codes]

    if station_code is not None:
        station_code = ui.expanded_station_id(station_code)

    if direction is not None:
        direction = ui.expanded_direction(direction)

    try:
        arrivals = api.tube_arrivals(count=-1)

        if arrivals is None:
            print("no arrivals")
            return

        trains = tfl_tube.filter_trains_currently_at_platform(
            arrivals, line_codes, station_code, direction
        )
        print(trains)  # debug
        ui.list_trains_multiple_stations(trains)
    except commons.TflTubeException as e:
        print(f"error: {str(e)}")


@click.command(name="board")
@click.argument("line_code")
@click.argument("station_code")
@click.argument("direction_code")
def start_board(line_code, station_code, direction_code):
    line_id = ui.expanded_line_id(line_code)
    station_id = ui.expanded_station_id(station_code)
    direction = ui.expanded_direction(direction_code)

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
cli.add_command(stations)
cli.add_command(next_departures)
cli.add_command(at_station)
cli.add_command(start_board)

if __name__ == "__main__":
    cli()
