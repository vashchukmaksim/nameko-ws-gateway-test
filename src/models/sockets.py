from sqlalchemy import Column, DateTime, String
from sqlalchemy_utils import UUIDType

from ..conf import DeclarativeBase

__all__ = [
    'SocketsModel'
]


class SocketsModel(DeclarativeBase):

    __tablename__ = 'sockets'
    __table_args__ = {
        'extend_existing': True,
        'schema': DeclarativeBase.metadata.schema
    }

    socket_id = Column(String(256), nullable=False, unique=True, primary_key=True)
    expire = Column(DateTime, nullable=False)
    user_uuid = Column(UUIDType(binary=False), nullable=False)
    channel = Column(String(256), nullable=False)

    def __repr__(self):
        return '{}_{}'.format(self.user_uuid, self.socket_id)
