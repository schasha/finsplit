import os

import yaml


class Config:
    # CORRIGIDO: sem fallback hardcoded. As variáveis sensíveis são obrigatórias
    # e vêm exclusivamente do ambiente; ausência derruba a app (fail-closed).
    SECRET_KEY = os.environ["SECRET_KEY"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]

    DB_HOST = os.environ.get("DB_HOST", "db")
    DB_NAME = os.environ.get("DB_NAME", "finsplit")
    DB_USER = os.environ.get("DB_USER", "finsplit")
    DB_PORT = os.environ.get("DB_PORT", "5432")


def load_yaml_config(path="config.yaml"):
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        # CORRIGIDO: safe_load não instancia objetos arbitrários (sem RCE).
        return yaml.safe_load(fh)
