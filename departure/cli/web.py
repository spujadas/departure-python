import os

import uvicorn
import click


@click.command()
def start():
    uvicorn_reload = "UVICORN_RELOAD" in os.environ
    uvicorn.run("departure.web.api_server:app", reload=uvicorn_reload, host="0.0.0.0")


if __name__ == "__main__":
    start()
