from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owner')
    num_players = models.IntegerField()
    is_private = models.BooleanField(default=False)
    room_code = models.CharField(max_length=8, null=True)
    is_started = models.BooleanField(default=False)
    pot = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    turn = models.IntegerField(default=0)  # Turn during actual gameplay
    hand = models.IntegerField(default=1)
    winners = models.ManyToManyField(User, blank=True, related_name='winner')
    losers = models.ManyToManyField(User, blank=True, related_name='loser')
    last_timer_reset = models.DateTimeField(auto_now_add=True)
    buy_in = models.IntegerField(default=0)


color_choices = [
    ('BLACK', 'black'),
    ('RED', 'red'),
    ('BLUE', 'blue'),
    ('BROWN', 'brown'),
    ('GREEN', 'green'),
    ('YELLOW', 'yellow'),
    ('PURPLE', 'purple'),
    ('GRAY', 'gray'),
    ('WHITE', 'white'),
    ('SKIN1', 'skin1'),
    ('SKIN2', 'skin2'),
    ('SKIN3', 'skin3'),
    ('SKIN4', 'skin4'),
    ('BLANK', 'blank')
]


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_guest = models.BooleanField(default=False)
    current_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField(null=True) # used to determine turn order
    is_turn = models.BooleanField(default=False)
    choose_turn = models.BooleanField(default=False)
    waiting_for_continue = models.BooleanField(default=False)
    tricks = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    money = models.IntegerField(default=100)

    last_gift = models.DateTimeField(auto_now_add=True)

    background_color = models.CharField(max_length=10, choices=color_choices, default='BLANK')
    shirt_color = models.CharField(max_length=10, choices=color_choices, default='BLACK')
    skin_color = models.CharField(max_length=10, choices=color_choices, default='BLACK')
    hat_color = models.CharField(max_length=10, choices=color_choices, default='BLACK')

    class Meta:
        ordering = ['position', 'pk']


class Card(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    number = models.IntegerField()


class TurnHistory(models.Model):
    """
    Represents a turn that has taken place during actual gameplay,
    or a game-ending event.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    turn = models.IntegerField()
    hand = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    end_game = models.BooleanField(default=False)
