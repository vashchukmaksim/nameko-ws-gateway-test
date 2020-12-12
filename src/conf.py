import os

from raven import Client

from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base

__all__ = [
    'DeclarativeBase',
    'db_session',
    'sentry'
]


# Sentry
sentry = Client(os.environ.get('SENTRY_DSN', None))

# Setup remote (container debugger)
# if os.environ.get('DEBUG_ENV', False) == 'development':
#     import pydevd_pycharm
#     pydevd_pycharm.settrace('docker.for.mac.localhost', port=5758, stdoutToServer=True, stderrToServer=True)


# Declarative base
class Base(object):
    pass


# Setup DB
DeclarativeBase = declarative_base(Base, metadata=MetaData(schema='websockets'))

# DB URI
uri = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ.get('POSTGRES_DB_USERNAME', 'dev_user'),
    os.environ.get('POSTGRES_DB_PASSWORD', '0000'),
    os.environ.get('POSTGRES_DB_HOST', 'postgres'),
    os.environ.get('POSTGRES_DB_PORT', '5432'),
    os.environ.get('POSTGRES_DB_NAME', 'tg')
)

# DB session object to use outside of service context
engine = create_engine(uri, pool_pre_ping=True, pool_recycle=3600)
Session = sessionmaker(bind=engine)
db_session = Session()
