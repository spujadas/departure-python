import threading
import time
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import national_rail, commons, view_model, data_updater

logger = logging.getLogger(__name__)

router = APIRouter()


class Station(BaseModel):
    code: str


@router.get("/search/{search_string}")
async def search(search_string):
    return national_rail.stations_by_string(search_string)


# debugging only
@router.get("/next/{station_code}")
async def next_departures(station_code):
    # request next services
    station_code = station_code.upper()
    try:
        response = national_rail.next_services(station_code)
    except commons.NationalRailException as e:
        logger.warning(str(e))
        return {"status": "error", "message": str(e)}

    # return next services
    return {
        "status": "OK",
        "response": response,
    }


# curl -X POST http://localhost:8000/national-rail/start-client -d {\"code\":\"vic\"}
@router.post("/start-client")
async def start_client(station: Station, request: Request):
    # check parameters
    station_code = station.code.upper()
    try:
        commons.check_env_vars()
        national_rail.check_params(station_code)
    except commons.NationalRailException as e:
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
            view_model.ViewModelNationalRail_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterNationalRail,
            {"station_id": station_code},
        ],
    ).start()

    return {"status": "OK"}
