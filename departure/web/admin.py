import os
import json
import logging

import requests


logger = logging.getLogger(__name__)


class AdminException(Exception):
    pass


def board_server_url() -> str:
    # check for DEPARTURE_BOARD_HTTP_PORT env var
    if "DEPARTURE_BOARD_HTTP_PORT" not in os.environ:
        raise AdminException("missing DEPARTURE_BOARD_HTTP_PORT env var")

    # check for DEPARTURE_BOARD_SERVER env var
    departure_board_host = os.environ.get(
        "DEPARTURE_BOARD_SERVER",
        # default: not 'localhost' on Win: https://stackoverflow.com/q/43096253/2654646
        "127.0.0.1",
    )

    return f"http://{departure_board_host}:{os.environ['DEPARTURE_BOARD_HTTP_PORT']}"


def shutdown_board_server() -> dict:
    try:
        url = board_server_url()
    except AdminException as e:
        return {"status": "error", "message": str(e)}

    if "DEPARTURE_BOARD_RSHUTDOWN_TOKEN" not in os.environ:
        return {
            "status": "error",
            "message": "missing DEPARTURE_BOARD_RSHUTDOWN_TOKEN env var",
        }

    # send shutdown request
    try:
        response = requests.post(
            url, json={"token": os.environ["DEPARTURE_BOARD_RSHUTDOWN_TOKEN"]}
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Error shutting down board server: %s", str(e))
        return {"status": "error", "message": str(e)}

    # return status
    if response.status_code == 200:
        response_json = json.loads(response.content.decode("utf-8"))
        if response_json["status"] == 0:
            return {"status": "OK"}
        return {"status": "error", "message": "invalid token"}

    logger.warning(
        "Error shutting down board server, HTTP response: %s", response.status_code
    )
    return {"status": "error", "message": response.status_code}


def is_board_server_up() -> dict:
    try:
        url = board_server_url()
    except AdminException as e:
        return {"status": "error", "message": str(e)}

    try:
        response = requests.get(url)
    except Exception as e:  # pylint: disable=broad-except
        return {"status": "OK", "server_up": False}

    # return status
    if response.status_code == 200:
        return {"status": "OK", "server_up": True}

    return {"status": "error", "message": response.status_code}


def shutdown_web_server():
    os.system("sudo shutdown -h now")
