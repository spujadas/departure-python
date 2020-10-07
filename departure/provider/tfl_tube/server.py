import threading
import time
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import tfl_tube, commons, view_model, data_updater

logger = logging.getLogger(__name__)

router = APIRouter()


class StationDirection(BaseModel):
    line_id: str
    station_id: str
    direction: str


@router.get("/stations/{station_string_query}")
async def search_stations(station_string_query: str):
    return tfl_tube.stations_by_string(station_string_query)


@router.get("/lines")
async def lines():
    return tfl_tube.lines()


@router.get("/stations-line/{line_id}")
async def stations_line(line_id: str):
    return tfl_tube.stations_by_line(line_id)


@router.get("/directions/{line_id}")
async def directions(line_id: str):
    return tfl_tube.directions(line_id)


# debugging only
@router.get("/next/{line_id}/{station_id}/{direction}")
async def next_trains(line_id: str, station_id: str, direction: str):
    try:
        departures = tfl_tube.next_trains(line_id, station_id, direction)
    except commons.TflTubeException as e:
        logger.warning(str(e))
        return {"status": "error", "message": str(e)}

    return {"status": "OK", "response": departures}


# curl -X POST http://localhost:8000/tfl-tube/start-client \
#   -d {\"line_id\":\"district\", \"station_id\":\"940GZZLUVIC\", \"direction\":\"Westbound\"}
@router.post("/start-client")
async def start_client(station_direction: StationDirection, request: Request):
    # check params
    try:
        tfl_tube.check_params(
            [station_direction.line_id],
            station_direction.station_id,
            station_direction.direction,
        )
        commons.check_env_vars()
    except commons.TflTubeException as e:
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
            view_model.ViewModelTflTube_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterTflTube,
            {
                "line_id": station_direction.line_id,
                "station_id": station_direction.station_id,
                "direction": station_direction.direction,
            },
        ],
    ).start()

    return {"status": "OK"}
