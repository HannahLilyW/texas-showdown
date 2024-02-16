import random

from rest_framework import serializers
from texas_api.models import Game, Player, TurnHistory
from django.contrib.auth.models import User


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['created_by', 'num_players', 'betting', 'is_private']
    
    def validate(self, data):
        super().validate(data)

        # Ensure there are between 3 and 6 players
        if data['num_players'] > 6 or data['num_players'] < 3:
            raise serializers.ValidationError('num_players must be between 3 and 6')

        # Ensure the user that would create the game doen't already have an active game.
        player = Player.objects.get(user=self.context['request'].user)
        if player.current_game:
            raise serializers.ValidationError('User already has a current game')

        # request.user is inserted by Django Rest Framework based on the provided token,
        # so we don't need to do any extra validation here.
        data['created_by'] = self.context['request'].user
        data['owner'] = self.context['request'].user
        return data
    
    def create(self, validated_data):
        game = super().create(validated_data)
        # Set the player's current_game to this one.
        player = Player.objects.get(user=self.context['request'].user)
        player.current_game = game
        player.position = 0
        player.save()
        if game.is_private:
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            room_code = ''
            for i in range(4):
                room_code += random.choice(alphabet)
            game.room_code = room_code
            game.save()
        return game

    def to_representation(self, instance):
        # Return usernames rather than user ids
        ret = super().to_representation(instance)
        ret['created_by'] = User.objects.get(id=ret['created_by']).username
        return ret


class PlayerNameListField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'username': value.user.username,
            'name': value.user.first_name,
            'background_color': value.background_color.lower(),
            'shirt_color': value.shirt_color.lower(),
            'skin_color': value.skin_color.lower(),
            'hat_color': value.hat_color.lower(),
            'position': value.position,
            'is_turn': value.is_turn,
            'choose_turn': value.choose_turn,
            'waiting_for_continue': value.waiting_for_continue,
            'tricks': value.tricks,
            'score': value.score,
            'money': value.money,
            'bet': value.bet,
            'fold': value.fold
        }


class TurnHistoryListField(serializers.RelatedField):
    def to_representation(self, value):
        card_number = None
        if value.card:
            card_number = value.card.number
        return {
            'turn': value.turn,
            'hand': value.hand,
            'player': value.player.user.username,
            'card': card_number,
            'end_game': value.end_game
        }


class BetTurnHistoryListField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'bet_turn': value.bet_turn,
            'hand': value.hand,
            'player': value.player.user.username,
            'bet_action': value.bet_action,
            'bet_amount': value.bet_amount,
            'player_money': value.player_money
        }


class UsernameListField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'username': value.username,
            'name': value.first_name
        }


class GameSerializer(serializers.ModelSerializer):
    player_set = PlayerNameListField(many=True, read_only=True)
    turnhistory_set = TurnHistoryListField(many=True, read_only=True)
    betturnhistory_set = BetTurnHistoryListField(many=True, read_only=True)
    winners = UsernameListField(many=True, read_only=True)
    losers = UsernameListField(many=True, read_only=True)

    class Meta:
        model = Game
        exclude = ('room_code', )

    def to_representation(self, instance):
        # Return usernames rather than user ids
        ret = super().to_representation(instance)
        ret['created_by'] = User.objects.get(id=ret['created_by']).username
        owner = User.objects.get(id=ret['owner'])
        ret['owner'] = owner.username
        ret['owner_name'] = owner.first_name
        return ret


class FinishedGameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'owner', 'created']
    
    def to_representation(self, instance):
        # Return usernames rather than ids
        ret = super().to_representation(instance)
        ret['owner'] = User.objects.get(id=ret['owner']).username
        return ret


class PlayerStatisticSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    wins = serializers.SerializerMethodField()
    losses = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['username', 'wins', 'losses']
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_wins(self, obj):
        return obj.user.winner.count()

    def get_losses(self, obj):
        return obj.user.loser.count()


class AdminGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
