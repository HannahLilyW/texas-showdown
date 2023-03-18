from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owner')
    num_players = models.IntegerField()
    betting = models.BooleanField()
    is_started = models.BooleanField(default=False)


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    current_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
