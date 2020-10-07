import os


class TflTubeException(Exception):
    pass


def check_env_vars():
    if "TFL_APP_KEY" not in os.environ:
        raise TflTubeException("missing env var TFL_APP_KEY")
