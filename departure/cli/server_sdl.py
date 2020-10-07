import click

import departure.commons as commons
from departure.renderer.sdl import cli as sdl
from departure.renderer.sdl_ext import cli as sdl_ext


# initialise logging
commons.init_logging()

# CLI entry point
@click.group()
def entry_point():
    pass

# add commands
entry_point.add_command(sdl.run)
entry_point.add_command(sdl_ext.run)
