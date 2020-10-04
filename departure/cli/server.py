import logging
import os

import click

# suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# pylint: disable=wrong-import-position
from departure.renderer.pygame import cli as pygame
from departure.renderer.sdl import cli as sdl
from departure.renderer.sdl_ext import cli as sdl_ext


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
entry_point.add_command(pygame.run)
entry_point.add_command(sdl.run)
entry_point.add_command(sdl_ext.run)
