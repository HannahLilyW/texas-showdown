import socketio
from texas.settings import config


sio_server = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[config['django']['hostname']])
