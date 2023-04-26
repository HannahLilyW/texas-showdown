import socketio


# sio_server = socketio.Server(async_mode='threading')
sio_server = socketio.AsyncServer(async_mode='asgi')