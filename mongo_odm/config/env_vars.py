import configparser
import os

from reljicd_utils.config import get_env
from str2bool import str2bool

config_file_path = os.getenv('CONFIG_FILE')
if config_file_path:
    config = configparser.ConfigParser()
    config.read(config_file_path)
else:
    config = None

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
    default='')
MONGO_USE_SSL: bool = str2bool(get_env(
    key='MONGO_USE_SSL',
    default='False'))
MONGO_CERT_PATH: str = get_env(
    key='MONGO_CERT_PATH',
    default='')
MONGO_USE_REPLICA_SET: bool = str2bool(get_env(
    key='MONGO_USE_REPLICA_SET',
    default='False'))
