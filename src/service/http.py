import json
from werkzeug.wrappers import Response

from nameko.web.server import WebServer as BaseWebServer
from nameko.web.handlers import HttpRequestHandler as BaseHttpRequestHandler

__all__ = [
    'WebServer',
    'HttpRequestHandler',
    'HttpError',
    'http'
]


class HttpError(Exception):
    """
    General (default HTTP error)
    in JSONAPI format
    """
    def __init__(self, info=None, _id=None, meta=None):

        # Readable information
        if info and info.get('title'):
            self.title = info.get('title')
        if info and info.get('detail'):
            self.detail = info.get('detail')

        # Meta
        self.id = _id
        self.meta = meta

    # Default info
    error_code = 400
    status_code = 400
    title = 'Bad request'
    detail = 'Wrong request format'


class WebServer(BaseWebServer):
    """
    WebServer that sends auth information in
    request context
    """

    def context_data_from_headers(self, request):
        context_data = super().context_data_from_headers(request)

        # Access token
        access_token = request.cookies.get('access_token', None)
        if access_token:
            context_data['access_token'] = access_token

        # Refresh token
        refresh_token = request.cookies.get('refresh_token', None)
        if refresh_token:
            context_data['refresh_token'] = refresh_token

        # CSRF token
        csrf_token = request.cookies.get('csrf_token', None)
        if csrf_token:
            context_data['csrf_token'] = csrf_token

        # CSRF token (header)
        csrf_token_header = request.cookies.get('csrf_token_header', None)
        if csrf_token_header:
            context_data['csrf_token_header'] = csrf_token_header

        # Updated context
        return context_data


class HttpRequestHandler(BaseHttpRequestHandler):
    """
    Http handler that handles custom context data
    and HTTP exceptions
    """

    server = WebServer()

    def response_from_exception(self, exc):
        if isinstance(exc, HttpError):

            # Common information
            error = {
                'status': exc.status_code,
                'code': exc.error_code,
                'title': exc.title,
                'detail': exc.detail
            }

            # Optional information
            for prop in ['id', 'meta']:
                if exc.__getattribute__(prop):
                    error.update({[prop]: exc.__getattribute__(prop)})

            # Convert to JSONAPI Spec
            jsonapi_error = {
                'errors': [error]
            }

            # Respond
            return Response(
                json.dumps(jsonapi_error),
                status=exc.status_code,
                content_type='application/vnd.api+json'
            )

        return HttpRequestHandler.response_from_exception(self, exc)


# http decorator
http = HttpRequestHandler.decorator
