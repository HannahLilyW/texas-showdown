import socketio

from texas.logging import log


sio_server = socketio.Server(async_mode='threading')


@sio_server.event
def connect(sid, environ, auth=''):
    try:
        token = Token.objects.get(auth['token'])
    except Exception as e:
        log.error(f'exception type: {type(e)}')
        log.error(f'exception: {e}')
