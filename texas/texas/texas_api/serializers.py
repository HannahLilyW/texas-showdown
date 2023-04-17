from rest_framework import serializers
from texas_api.models import Game, Player, TurnHistory
from django.contrib.auth.models import User


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['created_by', 'num_players', 'betting']
    
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
            'position': value.position,
            'is_turn': value.is_turn,
            'waiting_for_continue': value.waiting_for_continue,
            'tricks': value.tricks,
            'score': value.score
        }


class TurnHistoryListField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'turn': value.turn,
            'hand': value.hand,
            'player': value.player.user.username,
            'card': value.card.number
        }


class WinnerListField(serializers.RelatedField):
    def to_representation(self, value):
        return value.username


class GameSerializer(serializers.ModelSerializer):
    player_set = PlayerNameListField(many=True, read_only=True)
    turnhistory_set = TurnHistoryListField(many=True, read_only=True)
    winners = WinnerListField(many=True, read_only=True)

    class Meta:
        model = Game
        fields = '__all__'
    
    def to_representation(self, instance):
        # Return usernames rather than user ids
        ret = super().to_representation(instance)
        ret['created_by'] = User.objects.get(id=ret['created_by']).username
        ret['owner'] = User.objects.get(id=ret['owner']).username
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
