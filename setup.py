"""
Setup for departure_board module
"""

from setuptools import setup, find_packages

setup(
    name="departure-board",
    version="1.0",
    packages=find_packages(),
    entry_points={"console_scripts": "db=departure_board.cli:entry_point"},
)
