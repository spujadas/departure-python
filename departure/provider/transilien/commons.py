import os


class TransilienException(Exception):
    pass


def check_env_vars():
    missing_vars = []
    for transilien_env_var in ["TRANSILIEN_USER", "TRANSILIEN_PASSWORD"]:
        if transilien_env_var not in os.environ:
            missing_vars.append(transilien_env_var)

    if missing_vars:
        raise TransilienException(f"missing env vars {', '.join(missing_vars)}")
