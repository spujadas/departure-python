import logging

import click

from departure.provider.ns import cli as ns
from departure.provider.national_rail import cli as national_rail
from departure.provider.ratp import cli as ratp
from departure.provider.sncf import cli as sncf
from departure.provider.tfl_tube import cli as tfl_tube
from departure.provider.transilien import cli as transilien

# initialise logging
logger = logging.getLogger('departure')
logger.setLevel(level=logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# CLI entry point
@click.group()
def entry_point():
    pass

# add commands
entry_point.add_command(ns.cli, name="ns")
entry_point.add_command(national_rail.cli, name="national-rail")
entry_point.add_command(ratp.cli, name="ratp")
entry_point.add_command(sncf.cli, name="sncf")
entry_point.add_command(tfl_tube.cli, name="tfl-tube")
entry_point.add_command(transilien.cli, name="transilien")

if __name__ == "__main__":
    entry_point()
