"""
Setup for departure module
"""

from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="departure",
    version="1.0.1",
    author="Sébastien Pujadas",
    author_email="sebastien@pujadas.net",
    description="Get station information and departures from public transport "
        "operators, and control virtual or physical departure boards.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spujadas/departure-python",
    packages=find_namespace_packages(include=["departure.*"]),
    entry_points={
        "console_scripts": [
            "departure=departure.cli.client:entry_point",
            "departure-server=departure.cli.server:entry_point",
            "departure-web=departure.cli.web:start",
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
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
