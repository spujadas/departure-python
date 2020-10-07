import os


class NationalRailException(Exception):
    pass


def check_env_vars():
    if "LDB_TOKEN" not in os.environ:
        raise NationalRailException("missing env var LDB_TOKEN")
