import threading
import time

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import ns, commons, view_model, data_updater


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
    # check parameters
    station_code = station_code.upper()
    params_status = check_params(station_code)
    if params_status:
        return params_status

    # request next services
    return {
        "status": "OK",
        "response": ns.departures_with_schedule(station_code),
    }


# curl -X POST http://localhost:8000/ns/start-client -d {\"code\":\"gvc\"}
@router.post("/start-client")
async def start_client(station: Station, request: Request):
    # check parameters
    station_code = station.code.upper()
    params_status = check_params(station_code)
    if params_status:
        return params_status

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
