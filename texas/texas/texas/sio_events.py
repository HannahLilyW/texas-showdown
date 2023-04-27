from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from texas.sio_server import sio_server
from texas.logging import log
from texas_api.models import Game, Player
from texas_api.serializers import GameSerializer


@sio_server.event
async def connect(sid, environ, auth=''):
    try:
        token = Token.objects.get(key=auth['token'])
    except Exception as e:
        # Returning False means the connection was rejected.
        log.error('rejected connection for user because of invalid token')
        return False

    active_game = Player.objects.get(user=token.user).current_game
    if not active_game:
        log.error('rejected connection for user because no active game')
        return False

    sio_server.save_session(sid, {'username': token.user.username})
    log.error(f'adding {token.user.username} to room {active_game.id}')
    sio_server.enter_room(sid, str(active_game.id))


def sio_update_game(game_id):
    log.error(f'sio_update_game {game_id}')
    try:
        game = Game.objects.get(id=int(game_id))
    except ObjectDoesNotExist as e:
        sio_server.send(None)
        return
    serializer = GameSerializer(game)
    log.error(f'emitting update_game: {serializer.data}')
    sio_server.send(serializer.data)
