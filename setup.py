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
            'departure-client=departure.cli.client:entry_point',
            'departure-server=departure.cli.server:entry_point',
            'departure-web=departure.cli.web:start'
        ],
    }
)
