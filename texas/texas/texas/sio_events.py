from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from texas.sio_server import sio_server
from texas.logging import log
from texas_api.models import Game, Player
from texas_api.serializers import GameSerializer
from asgiref.sync import sync_to_async


@sio_server.event
async def connect(sid, environ, auth=''):
    try:
        get_token = sync_to_async(Token.objects.get)
        token = await get_token(key=auth['token'])
    except Exception as e:
        # Returning False means the connection was rejected.
        log.error(f'rejected connection for user because of invalid token. error: {e}')
        return False
    
    def sync_get_user(token):
        return token.user
    
    get_user = sync_to_async(sync_get_user)
    user = await get_user(token)

    get_player = sync_to_async(Player.objects.get)
    player = await get_player(user=user)

    def sync_get_active_game(player):
        return player.current_game

    get_active_game = sync_to_async(sync_get_active_game)
    active_game = await get_active_game(player)
    if not active_game:
        log.error('rejected connection for user because no active game')
        return False

    sio_server.save_session(sid, {'username': user.username})
    log.error(f'adding {user.username} to room {active_game.id}')
    sio_server.enter_room(sid, str(active_game.id))
    await sio_server.emit('enter_room', {'data': 'foo'})


def sio_update_game(game_id):
    log.error(f'sio_update_game {game_id}')
    try:
        game = Game.objects.get(id=int(game_id))
    except ObjectDoesNotExist as e:
        log.error(f'object does not exist: {e}')
        sio_server.emit('update_game', {'data': 'foobar'}, room='21')
        # sio_server.emit('update_game', None)
        return
    serializer = GameSerializer(game)
    log.error(f'emitting update_game: {serializer.data}')
    sio_server.emit('update_game', {'data': 'foobar'}, room=str(game_id))
    # sio_server.emit('update_game', serializer.data)
