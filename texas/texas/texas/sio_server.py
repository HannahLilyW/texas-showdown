import socketio


sio_server = socketio.Server(async_mode='threading')


@sio_server.event
def connect(sid, environ, auth=''):
    print('connect ', sid, auth)