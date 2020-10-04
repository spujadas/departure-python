import logging  # for type hinting
import io
from contextlib import redirect_stdout
from typing import Callable, Any


def log_function_stdout_to_debug(
    logger: logging.Logger,
    function: Callable[..., None],
    *argv: Any
):
    stdout_string = io.StringIO()
    with redirect_stdout(stdout_string):
        function(*argv)
    logger.debug(stdout_string.getvalue())
