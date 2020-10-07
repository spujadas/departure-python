import os

import departure.commons as commons


# suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# pylint: disable=wrong-import-position
from departure.renderer.pygame import cli as pygame

# initialise logging
commons.init_logging()

# CLI entry point
def entry_point():
    pygame.run()
