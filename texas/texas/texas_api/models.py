from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owner')
    num_players = models.IntegerField()
    betting = models.BooleanField()
    is_started = models.BooleanField(default=False)
    is_betting_round = models.BooleanField(default=False)
    pot = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    turn = models.IntegerField(default=0)
    hand = models.IntegerField(default=1)
    winners = models.ManyToManyField(User, blank=True, related_name='winner')
    losers = models.ManyToManyField(User, blank=True, related_name='loser')


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    current_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField(null=True) # used to determine turn order
    is_turn = models.BooleanField(default=False)
    waiting_for_continue = models.BooleanField(default=False)
    tricks = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    money = models.IntegerField(default=0)
    bet = models.IntegerField(default=0)

    class Meta:
        ordering = ['position', 'pk']


class Card(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    number = models.IntegerField()


class TurnHistory(models.Model):
    """
    Represents a turn that has taken place.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    turn = models.IntegerField()
    hand = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    end_game = models.BooleanField(default=False)
