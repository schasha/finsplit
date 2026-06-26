import os

import yaml


class Config:
    # NOTE: estes fallbacks hardcoded são o "achado" que Secret Detection e SAST
    # devem apontar. Em produção viriam exclusivamente do ambiente.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-12345")

    DB_HOST = os.environ.get("DB_HOST", "db")
    DB_NAME = os.environ.get("DB_NAME", "finsplit")
    DB_USER = os.environ.get("DB_USER", "finsplit")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
    DB_PORT = os.environ.get("DB_PORT", "5432")


def load_yaml_config(path="config.yaml"):
    """Carrega config opcional de um YAML. yaml.load sem Loader seguro é o
    padrão inseguro que o SAST (Bandit B506) deve sinalizar."""
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        return yaml.load(fh)
