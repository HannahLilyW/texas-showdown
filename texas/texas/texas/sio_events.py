from rest_framework.authtoken.models import Token
from texas.sio_server import sio_server
from texas.logging import log


@sio_server.event
def connect(sid, environ, auth=''):
    try:
        token = Token.objects.get(auth['token'])
    except Exception as e:
        log.error(f'exception type: {type(e)}')
        log.error(f'exception: {e}')
        log.error(f'auth: {auth}')
        log.error(f'auth type: {type(auth)}')
        log.error(f'auth token: {auth["token"]}')
        log.error(f'auth token type: {type(auth["token"])}')
