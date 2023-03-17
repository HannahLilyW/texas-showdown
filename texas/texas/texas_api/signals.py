from django.db.models.signals import post_save
from django.dispatch import receiver
from texas_api.models import Game
from texas.sio_server import sio_server


@receiver(post_save, sender=Game)
def update_game(sender, instance, **kwargs):
    sio_server.emit('myevent', {'data': 'foobar'})
