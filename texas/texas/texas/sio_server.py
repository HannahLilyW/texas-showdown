import socketio

from texas.logging import log


sio_server = socketio.Server(async_mode='threading')


@sio_server.event
def connect(sid, environ, auth=''):
    log.error(f'sid: {sid} environ: {environ} auth: {auth}')
