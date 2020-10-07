import threading
import time
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import sncf, commons, view_model, data_updater

logger = logging.getLogger(__name__)

router = APIRouter()


class Station(BaseModel):
    stop_area_id: str


@router.get("/search/{search_string}")
async def search(search_string):
    return sncf.stations_by_string(search_string)


# debugging only
@router.get("/next/{stop_area_id}")
async def next_trains(stop_area_id):
    stop_area_id = stop_area_id.upper()

    try:
        response = sncf.next_trains(stop_area_id)
    except commons.SncfException as e:
        return {"status": "error", "message": str(e)}

    # request next services
    return {"status": "OK", "response": response}


# curl -X POST http://localhost:8000/sncf/start-client -d {\"stop_area_id\":\"87393702\"}
@router.post("/start-client")
async def start_client(station: Station, request: Request):
    # check parameters
    stop_area_id = station.stop_area_id
    try:
        commons.check_env_vars()
        sncf.check_params(stop_area_id)
    except commons.SncfException as e:
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
            view_model.ViewModelSncf_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterSncf,
            {"stop_area_id": stop_area_id},
        ],
    ).start()

    return {"status": "OK"}
