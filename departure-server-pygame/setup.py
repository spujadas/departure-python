"""
Setup for departure server with pygame backend module
"""

from setuptools import setup, find_namespace_packages

setup(
    name="departure-server-pygame",
    version="1.0",
    packages=find_namespace_packages(include=['departure.renderer.*']),
    install_requires=[
        "departure",
        "pygame",
    ],
)
