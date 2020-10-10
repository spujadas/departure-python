import logging  # for type hinting
import io
from contextlib import redirect_stdout
from typing import Callable, Any


def log_function_stdout_to_debug(
    logger: logging.Logger, function: Callable[..., None], *argv: Any
):
    stdout_string = io.StringIO()
    with redirect_stdout(stdout_string):
        function(*argv)
    logger.debug(stdout_string.getvalue())


def init_logging(logger_level=logging.DEBUG, handler_level=logging.DEBUG):
    logger = logging.getLogger("departure")
    logger.setLevel(level=logger_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(handler_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
