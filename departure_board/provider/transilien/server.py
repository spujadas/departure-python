import threading
import time

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import transilien, commons, view_model, data_updater


class Station(BaseModel):
    station_id: str


router = APIRouter()


def check_params(station_id):
    try:
        transilien.check_params(station_id)
    except commons.TransilienException as e:
        return {"status": "error", "message": str(e)}
    return {}


@router.get("/search/{search_string}")
async def search(search_string):
    return transilien.stations_by_string(search_string)


# debugging only
@router.get("/next/{station_id}")
async def next_trains(station_id):
    # check parameters
    station_id = station_id.upper()
    params_status = check_params(station_id)
    if params_status:
        return params_status

    # request next services
    return {"status": "OK", "response": transilien.next_trains(station_id)}


# curl -X POST http://localhost:8000/transilien/start-client -d {\"station_id\":\"87384008\"}
@router.post("/start-client")
async def start_client(station: Station, request: Request):
    # check parameters
    station_id = station.station_id
    params_status = check_params(station_id)
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
            view_model.ViewModelTransilien_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterTransilien,
            {"station_id": station_id},
        ],
    ).start()

    return {"status": "OK"}
