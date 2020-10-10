import click

from departure.commons.log import init_logging
from departure.provider.ns import cli as ns
from departure.provider.national_rail import cli as national_rail
from departure.provider.ratp import cli as ratp
from departure.provider.sncf import cli as sncf
from departure.provider.tfl_tube import cli as tfl_tube
from departure.provider.transilien import cli as transilien


# initialise logging
init_logging()


# CLI entry point
@click.group()
def entry_point():
    """
    Get station information and departures from public transport operators, and update
    a departure board with departure information for a station.
    """


# add commands
entry_point.add_command(tfl_tube.cli, name="lu")
entry_point.add_command(ns.cli, name="ns")
entry_point.add_command(national_rail.cli, name="national-rail")
entry_point.add_command(ratp.cli, name="ratp")
entry_point.add_command(sncf.cli, name="sncf")
entry_point.add_command(transilien.cli, name="transilien")


if __name__ == "__main__":
    entry_point()
