import threading
import time
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from . import ratp, commons, view_model, data_updater

logger = logging.getLogger(__name__)

router = APIRouter()


class StationDirection(BaseModel):
    line_id: str
    line_station_id: str
    direction: str


@router.get("/stations/{station_name_query}")
async def search_stations(station_name_query: str):
    return ratp.stations_by_name(station_name_query)


@router.get("/stations-line/{line_id}")
async def stations_line(line_id: str):
    return ratp.stations_by_line(line_id)


@router.get("/lines/{line_name_query}")
async def search_lines(line_name_query: str):
    return ratp.lines_by_name(line_name_query)


@router.get("/lines-by-code/{code_query}")
async def search_lines_by_code(code_query: str):
    return ratp.lines_by_code(code_query)


@router.get("/directions/{line_id}")
async def directions(line_id: str):
    return ratp.directions(line_id)


# debugging only
@router.get("/next/{line_id}/{line_station_id}/{direction}")
async def next_departures(line_id: str, line_station_id: str, direction: str):
    try:
        departures = ratp.next_departures(line_id, line_station_id, direction)
    except commons.RatpException as e:
        logger.warning(str(e))
        return {"status": "error", "message": str(e)}

    return {"status": "OK", "response": departures}


# curl -X POST http://localhost:8000/ratp/start-client \
#   -d {\"line_id\":\"RB\", \"line_station_id\":\"15\", \"direction\":\"A\"}
@router.post("/start-client")
async def start_client(station_direction: StationDirection, request: Request):
    # check params
    try:
        ratp.check_params(
            station_direction.line_id,
            station_direction.line_station_id,
            station_direction.direction,
        )
    except commons.RatpException as e:
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
            view_model.ViewModelRatp_192_32_3_Rows_To_ProtocolBuffers,
            data_updater.DataUpdaterRatp,
            {
                "line_id": station_direction.line_id,
                "line_station_id": station_direction.line_station_id,
                "direction": station_direction.direction,
            },
        ],
    ).start()

    return {"status": "OK"}
