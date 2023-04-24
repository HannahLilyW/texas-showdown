import socketio


sio_server = socketio.Server(async_mode='threading', logger=True, engineio_logger=True)


def sio_update_game(game_id):
    from texas.logging import log
    from texas_api.models import Game
    from django.core.exceptions import ObjectDoesNotExist
    from texas_api.serializers import GameSerializer
    log.error(f'sio_update_game {game_id}')
    try:
        game = Game.objects.get(id=int(game_id))
    except ObjectDoesNotExist as e:
        sio_server.emit('update_game', None, room=str(game_id))
        return
    serializer = GameSerializer(game)
    log.error(f'emitting update_game: {serializer.data}')
    sio_server.emit('update_game', serializer.data, room=str(game_id))