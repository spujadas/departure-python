import threading
import time
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import ns, commons, view_model, data_updater

logger = logging.getLogger(__name__)

router = APIRouter()


class Station(BaseModel):
    code: str


def check_params(station_code):
    try:
        ns.check_params(station_code)
    except commons.NSException:
        return {"status": "error", "message": "invalid station code"}
    return {}


@router.get("/search/{search_string}")
async def search(search_string):
    return ns.search(search_string)


# debugging only
@router.get("/next/{station_code}")
async def next_departures(station_code):
    # request next departures
    station_code = station_code.upper()

    try:
        response = ns.departures_with_schedule(station_code)
    except commons.NSException as e:
        logger.warning(str(e))
        return {"status": "error", "message": str(e)}

    # request next services
    return {
        "status": "OK",
        "response": response,
    }


# curl -X POST http://localhost:8000/ns/start-client -d {\"code\":\"gvc\"}
@router.post("/start-client")
async def start_client(station: Station, request: Request):
    # check parameters
    station_code = station.code.upper()
    try:
        ns.check_params(station_code)
        commons.check_env_vars()
    except commons.NSException as e:
        logger.warning(str(e))
        return {"status": "error", "message": str(e)}

    # stop board client if already running
    if request.app.board_client.running:
        request.app.board_client.running = False
        time.sleep(1)

    # start board
    threading.Thread(
        target=request.app.board_client.run,
        args=[
            view_model.ViewModelNS192x32x3ToProtocolBuffers,
            data_updater.DataUpdaterNS,
            {"station_code": station_code},
        ],
    ).start()

    return {"status": "OK"}
