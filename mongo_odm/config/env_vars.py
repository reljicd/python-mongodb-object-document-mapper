import os

from str2bool import str2bool

MONGO_HOST: str = os.getenv(
    key='MONGO_HOST',
    default='localhost')
MONGO_PORT: int = int(os.getenv(
    key='MONGO_PORT',
    default='27017'))
MONGO_USERNAME: str = os.getenv(
    key='MONGO_USERNAME',
    default='')
MONGO_PASSWORD: str = os.getenv(
    key='MONGO_PASSWORD',
    default='')
DB_CONFIGS: str = os.getenv(
    key='DB_CONFIGS',
    default='')
MONGO_USE_SSL: bool = str2bool(os.getenv(
    key='MONGO_USE_SSL',
    default='False'))
MONGO_CERT_PATH: str = os.getenv(
    key='MONGO_CERT_PATH',
    default='')
MONGO_USE_REPLICA_SET: bool = str2bool(os.getenv(
    key='MONGO_USE_REPLICA_SET',
    default='False'))
