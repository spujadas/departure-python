"""
CLI for Nederlandse Spoorwegen
"""

import threading
import time
import logging

import click

from departure.board import board_client

from . import ui, ns, commons, view_model, data_updater

ONE_DAY_IN_SECONDS = 60 * 60 * 24
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """
    Information and departures for Nederlandse Spoorwegen (NL).

    Note - Your NS API key must be assigned to the NS_API_KEY environment variable.
    """


@click.command()
@click.argument("query_string")
def search(query_string):
    """Search for stations containing QUERY_STRING."""
    stations = ns.search(query_string)
    ui.list_stations(stations)


@click.command(name="next")
@click.argument("ns_code")
@click.option(
    "--full",
    "timetable_for_all_trains",
    is_flag=True,
    help="displays timetable for all trains, instead of just first one",
)
def next_departures(ns_code, timetable_for_all_trains):
    """
    Get next departures at station NS_CODE.

    Use search to find the NS_CODE for a station.
    """

    ns_code = ns_code.upper()
    try:
        trains = ns.departures_with_schedule(ns_code, timetable_for_all_trains)
    except commons.NSException as e:
        print(f"error: {str(e)}")
        return

    ui.list_departures_with_schedule(trains, ns_code)


@click.command(name="board")
@click.argument("ns_code")
def start_board(ns_code):
    """Update a departure board with departures at station NS_CODE.

    Use search to find the NS_CODE for a station."""

    ns_code = ns_code.upper()

    try:
        ns.check_params(ns_code)
    except commons.NSException as e:
        logger.error("error: %s", str(e))
        return

    # start board
    board_client_instance = board_client.BoardClient()

    threading.Thread(
        target=board_client_instance.run,
        args=[
            view_model.ViewModelNS192x32x3ToProtocolBuffers,
            data_updater.DataUpdaterNS,
            {
                "station_code": ns_code,
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
