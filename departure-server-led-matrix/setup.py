"""
Setup for departure server with LED matrix backend module
"""

from setuptools import setup, find_namespace_packages

setup(
    name="departure-server-led-matrix",
    version="1.0",
    packages=find_namespace_packages(include=['departure.renderer.*']),
    install_requires=[
        "departure",
    ],
)
