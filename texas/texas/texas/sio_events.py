from rest_framework.authtoken.models import Token
from texas.sio_server import sio_server
from texas.logging import log


@sio_server.event
def connect(sid, environ, auth=''):
    try:
        token = Token.objects.get(key=auth['token'])
    except Exception as e:
        return False

    log.error(f'user: {token.user}')
    log.error(f'user type: {type(token.user)}')
    sio_server.save_session(sid, {'user': token.user})
