from rest_framework.authtoken.models import Token
from texas.sio_server import sio_server
from texas_api.models import Game, Player
from texas.logging import log


@sio_server.event
def connect(sid, environ, auth=''):
    try:
        token = Token.objects.get(key=auth['token'])
    except Exception as e:
        # Returning False means the connection was rejected.
        return False

    active_game = Player.objects.get(user=token.user).current_game
    if not active_game:
        return False

    sio_server.save_session(sid, {'username': token.user.username})
    log.error(f'adding {token.user.username} to room {active_game.id}')
    sio_server.enter_room(sid, str(active_game.id))
    sio_server.send(f'{token.user.username} entered the room.', str(active_game.id))
