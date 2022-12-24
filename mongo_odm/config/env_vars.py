import configparser
import os

from str2bool import str2bool

config_file_path = os.getenv('CONFIG_FILE')
if config_file_path:
    config = configparser.ConfigParser()
    config.read(config_file_path)
else:
    config = None


def get_env(key: str, default: str) -> str:
    """ Returns default even if env var is empty string """
    env = os.getenv(key)
    if env:
        return env

    if config and key in config['DEFAULT'] and config['DEFAULT'][key]:
        return config['DEFAULT'][key]

    return default


MONGO_HOST: str = get_env(
    key='MONGO_HOST',
    default='localhost')
MONGO_PORT: int = int(get_env(
    key='MONGO_PORT',
    default='27017'))
MONGO_USERNAME: str = get_env(
    key='MONGO_USERNAME',
    default='')
MONGO_PASSWORD: str = get_env(
    key='MONGO_PASSWORD',
    default='')
DB_CONFIGS: str = get_env(
    key='DB_CONFIGS',
    default='mongo_odm/config/db_configs')
MONGO_USE_SSL: bool = str2bool(get_env(
    key='MONGO_USE_SSL',
    default='False'))
MONGO_CERT_PATH: str = get_env(
    key='MONGO_CERT_PATH',
    default='al_mongo/config/rds-combined-ca-bundle.pem')
MONGO_USE_REPLICA_SET: bool = str2bool(get_env(
    key='MONGO_USE_REPLICA_SET',
    default='False'))
