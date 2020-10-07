import os


class NSException(Exception):
    pass


def check_env_vars():
    if "NS_API_KEY" not in os.environ:
        raise NSException("missing NS_API_KEY env var")
