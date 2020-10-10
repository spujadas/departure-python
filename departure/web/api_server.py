# 1) set provider environment variables
# 2) set IP address of board in environment variable DEPARTURE_BOARD_SERVER
# 3) uvicorn api_server:app --reload --host 0.0.0.0

import time
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

import departure.provider.national_rail.server as national_rail_server
import departure.provider.ratp.server as ratp_server
import departure.provider.sncf.server as sncf_server
import departure.provider.tfl_tube.server as tfl_tube_server
import departure.provider.transilien.server as transilien_server
import departure.provider.ns.server as ns_server
from departure.board import board_client
from departure.commons.log import init_logging
from . import admin


# initialise logging
init_logging()

# initialise app
app = FastAPI()

# initialise shared board client
app.board_client = board_client.BoardClient()

### API routes first
app.include_router(national_rail_server.router, prefix="/national-rail")
app.include_router(ratp_server.router, prefix="/ratp")
app.include_router(sncf_server.router, prefix="/sncf")
app.include_router(tfl_tube_server.router, prefix="/tfl-tube")
app.include_router(transilien_server.router, prefix="/transilien")
app.include_router(ns_server.router, prefix="/ns")


@app.post("/stop-client")
async def stop_client():
    # stop board client if running
    if app.board_client.running:
        app.board_client.running = False
        time.sleep(1)

    return {"status": "OK"}


@app.get("/client-status")
async def client_status():
    if app.board_client.running:
        return {"client_status": "running"}
    return {"client_status": "stopped"}


@app.get("/board-server-status")
async def board_server_status():
    return admin.is_board_server_up()


@app.post("/shutdown-board-server")
async def shutdown_board_server():
    await stop_client()
    return admin.shutdown_board_server()


@app.post("/shutdown-web-server")
async def shutdown_web_server():
    admin.shutdown_web_server()
    return {"status": "OK"}


### static files second (https://github.com/tiangolo/fastapi/issues/130) if root set
if "DEPARTURE_STATIC_WEBROOT" in os.environ:
    # index
    @app.get("/")
    async def read_index():
        return FileResponse(f"{os.environ['DEPARTURE_STATIC_WEBROOT']}/index.html")

    # other static files
    app.mount(
        "/",
        StaticFiles(directory=os.environ["DEPARTURE_STATIC_WEBROOT"]),
        name="static",
    )
