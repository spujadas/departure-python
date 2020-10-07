import os


class SncfException(Exception):
    pass


def check_env_vars():
    if "SNCF_KEY" not in os.environ:
        raise SncfException("missing env var SNCF_KEY")
