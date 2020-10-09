"""
Setup for departure module
"""

from setuptools import setup, find_namespace_packages

setup(
    name="departure",
    version="1.0",
    packages=find_namespace_packages(include=['departure.*']),
    entry_points={
        "console_scripts": [
            "departure-client=departure.cli.client:entry_point",
            "departure-server=departure.cli.server:entry_point",
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
    ],
    include_package_data=True
)
