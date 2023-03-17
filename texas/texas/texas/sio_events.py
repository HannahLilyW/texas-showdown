from rest_framework.authtoken.models import Token
from texas import sio_server


@sio_server.event
def connect(sid, environ, auth=''):
    try:
        token = Token.objects.get(auth['token'])
    except Exception as e:
        log.error(f'exception type: {type(e)}')
        log.error(f'exception: {e}')
