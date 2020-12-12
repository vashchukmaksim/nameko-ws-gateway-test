import json
from datetime import datetime, timedelta

from nameko.rpc import rpc
from nameko.web.handlers import http
from nameko.extensions import DependencyProvider
from nameko.dependency_providers import Config
from nameko.web.websocket import WebSocketHubProvider, rpc as rpc_ws

from nameko_sentry import SentryReporter
from nameko_sqlalchemy import DatabaseSession

from .logger import WorkerLogger
from .http import http

from ..models import SocketsModel
from ..conf import DeclarativeBase

__all__ = [
    'WebSocketsGatewayService'
]


AVAILABLE_CHANNELS = [
    'scheduler'
]


class ContainerIdentifier(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return id(self.container)


class WebSocketsGatewayService():

    # Service name
    name = 'service_ws_gateway'

    # Dependencies
    config = Config()
    db = DatabaseSession(DeclarativeBase, engine_options={'pool_pre_ping': True, 'pool_recycle': 3600})
    container_id = ContainerIdentifier()
    websocket_hub = WebSocketHubProvider()
    log = WorkerLogger('service_ws_gateway')
    sentry = SentryReporter()

    @http('GET', '/healthz')
    def healthz(self, request):
        return 200, json.dumps({'message': 'Healthy service'})

    @http('GET', '/readyz')
    def readyz(self, request):
        return 200, json.dumps({'message': 'Ready service'})

    @rpc_ws
    def unsubscribe(self, socket_id, channel):
        if channel in AVAILABLE_CHANNELS:
            try:
                self.websocket_hub.unsubscribe(socket_id, channel)
            except Exception as e:
                self.log.logger.error(e)
                return 'can not unsubscribe from a channel {}, unexpected error'.format(channel)

        # Result message
        return 'unsubscribed from {}'.format(channel)

    @rpc_ws
    def subscribe(self, socket_id, channel):

        # Check if channel that user wants to be subscribed to
        # is available
        if channel in AVAILABLE_CHANNELS:

            # Validate token and get user UUID
            # user_uuid = None

            # Subscribe to channel
            try:
                self.websocket_hub.subscribe(socket_id, channel)
            except Exception as e:
                self.log.logger.error(e)
                return 'can not subscribe to a channel {}, unexpected error'.format(channel)

            # Write user_uuid and socket_id to the db
            socket_data = {
                'channel': channel,
                'user_uuid': '04c623ca-90f9-4f4c-bfaa-f1838adb84dc', # user_uuid,
                'socket_id': socket_id,
                'expire': datetime.utcnow() + timedelta(hours=4)
            }

            socket = SocketsModel(**socket_data)
            self.db.add(socket)
            self.db.commit()

        # Result message
        return 'subscribed to {}'.format(channel)

    @rpc
    # @rpc_errors(log.logger)
    def send(self, user_uuid, channel, event, data):

        # Find all the sockets for the given user with a given channel
        # to send a message to
        sockets = self.db.query(SocketsModel).\
            filter(SocketsModel.user_uuid == user_uuid).\
            filter(SocketsModel.channel == channel).\
            filter(SocketsModel.expire > datetime.utcnow()).\
            all()

        # If list is not empty send a message
        # to each of them
        failed = []
        for socket in sockets:
            try:
                self.websocket_hub.unicast(socket.socket_id, event, {
                    **data,
                    'channel': channel
                })
            except Exception as e:
                failed.append(socket.socket_id)

        # Some messages were not delivered
        if len(sockets) == 0 or len(failed) == len(sockets):
            return {
                'status': 404,
                'user_uuid': user_uuid,
                'channel': channel,
                'message': 'No sockets available for user and channel'
            }

        # RPC response
        return {
            'status': 200,
            'message': 'Message was sent to a socket'
        }
