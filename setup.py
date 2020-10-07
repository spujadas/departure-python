"""
Setup for departure module
"""

from setuptools import setup, find_packages

setup(
    name="departure",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "departure-client=departure.cli.client:entry_point",
            "departure-server-pygame=departure.cli.server_pygame:entry_point",
            "departure-server-sdl=departure.cli.server_sdl:entry_point",
            "departure-web=departure.cli.web:start"
        ],
    },
    install_requires=[
        "requests",
        "protobuf",
        "grpcio",
        "bdflib",
        "click",
        "uvicorn",
        "aiofiles",
        "zeep",
        "fastapi",
        "tabulate",
        # "rgbmatrix",
        "pygame",
        "PySDL2"
    ],
    include_package_data=True
)
