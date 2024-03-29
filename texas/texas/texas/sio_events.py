from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Count
from rest_framework.authtoken.models import Token
from texas.sio_server import sio_server
from texas.logging import log
from texas_api.models import Game, Player
from texas_api.serializers import GameSerializer
from asgiref.sync import sync_to_async, async_to_sync


userids_to_sids = {}


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

    global userids_to_sids
    userids_to_sids[f'user{user.id}'] = sid

    sio_server.save_session(sid, {'username': user.username})

    if active_game:
        sio_server.enter_room(sid, f'room{active_game.id}')
    else:
        sio_server.enter_room(sid, 'join_existing_game')


async def async_sio_leave_room(user_id, game_id):
    global userids_to_sids
    try:
        sio_server.leave_room(userids_to_sids[f'user{user_id}'], f'room{game_id}')
    except Exception as e:
        log.error(f'error leaving socketio room: {repr(e)}')


async def async_sio_update_game(game_id):
    try:
        get_game = sync_to_async(Game.objects.get)
        game = await get_game(id=int(game_id))
    except ObjectDoesNotExist as e:
        log.error(f'object does not exist: {e}')
        return
    serializer = GameSerializer(game)
    
    def sync_get_data(serializer):
        return serializer.data

    get_data = sync_to_async(sync_get_data)
    data = await get_data(serializer)

    await sio_server.emit('update_game', serializer.data, room=f'room{game_id}')


async def async_sio_update_existing_games():
    def sync_get_existing_games():
        games = Game.objects.annotate(Count('player')).filter(
            num_players__gt=F('player__count'),
            is_started=False,
            is_private=False
        )
        serializer = GameSerializer(games, many=True)
        return serializer.data
    
    get_existing_games = sync_to_async(sync_get_existing_games)
    existing_games = await get_existing_games()

    await sio_server.emit('update_existing_games', existing_games, room='join_existing_game')


async def async_sio_chat(game_id, username, chat):
    def sync_get_game():
        return Game.objects.get(id=int(game_id))
    get_game = sync_to_async(sync_get_game)
    try:
        await get_game()
    except ObjectDoesNotExist as e:
        log.error(f'object does not exist: {e}')
        return
    await sio_server.emit(
        'chat',
        {
            'username': username,
            'chat': chat
        },
        room=f'room{game_id}'
    )


sio_leave_room = async_to_sync(async_sio_leave_room, force_new_loop=True)
sio_update_game = async_to_sync(async_sio_update_game, force_new_loop=True)
sio_update_existing_games = async_to_sync(async_sio_update_existing_games, force_new_loop=True)
sio_chat = async_to_sync(async_sio_chat, force_new_loop=True)