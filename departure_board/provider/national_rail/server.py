import threading
import time

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import api, national_rail, commons, view_model, data_updater


router = APIRouter()


class Station(BaseModel):
    code: str


def check_params(station_code):
    try:
        national_rail.check_params(station_code)
    except commons.NationalRailException:
        return {"status": "error", "message": "invalid station code"}
    return {}


@router.get("/search/{search_string}")
async def search(search_string):
    return national_rail.stations_by_string(search_string)


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
        "response": national_rail.next_services(station_code),
    }


# curl -X POST http://localhost:8000/national-rail/start-client -d {\"code\":\"vic\"}
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
            view_model.ViewModelNationalRail_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterNationalRail,
            {"station_id": station_code},
        ],
    ).start()

    return {"status": "OK"}
