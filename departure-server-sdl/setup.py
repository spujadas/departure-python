"""
Setup for departure server with SDL2 back end module
"""

from setuptools import setup, find_namespace_packages

setup(
    name="departure-server-sdl",
    version="1.0",
    packages=find_namespace_packages(include=['departure.renderer.*']),
    install_requires=[
        "departure",
        "PySDL2",
    ]
)
