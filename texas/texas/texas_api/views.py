from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import F, Count
from rest_framework import views, viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from texas.logging import log
from texas_api.models import Game, Player, Card, TurnHistory, BetTurnHistory
from texas_api.serializers import CreateGameSerializer, GameSerializer, FinishedGameListSerializer, PlayerStatisticSerializer
from texas.sio_events import sio_leave_room, sio_update_game
import json
import re
import secrets  # Cryptographically secure randomness
import math
from threading import Timer


TIMEOUT_SECONDS = 600


# Timers for each game to track when to end them due to inactivity
timers = {}


def timeout(game_id):
    game = Game.objects.get(id=game_id)
    if not game.is_finished:
        # Check if there are any players we are waiting on to click continue.
        # If there are, all those players lose,
        # and the remaining ones win.
        players_waiting_for_continue = []
        for player in game.player_set.all():
            if player.waiting_for_continue:
                players_waiting_for_continue.append(player)
                game.losers.add(player.user)
                game.save()
                TurnHistory.objects.create(
                    game=game,
                    turn=game.turn,
                    hand=game.hand,
                    player=player,
                    end_game=True
                )
        if len(players_waiting_for_continue):
            game.is_finished = True
            game.save()
            for other_player in game.player_set.all():
                if other_player not in players_waiting_for_continue:
                    game.winners.add(other_player.user)
                    game.save()
        else:
            # Else, whoever's turn it currently is is the loser.
            player = Player.objects.filter(current_game=game, is_turn=True).first()

            TurnHistory.objects.create(
                game=game,
                turn=game.turn,
                hand=game.hand,
                player=player,
                end_game=True
            )
            game.is_finished = True

            # This player should lose, and all other players should win.
            game.losers.add(player.user)
            game.save()
            for other_player in game.player_set.all():
                if other_player != player:
                    game.winners.add(other_player.user)
                    game.save()
        sio_update_game(game.id)


class CreateAccountView(views.APIView):
    # Endpoint for creating new accounts.

    # This endpoint is available to anyone, including unauthenticated users.
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        if request.content_type != 'application/json':
            return Response('Content-Type must be application/json', status=status.HTTP_400_BAD_REQUEST)

        # If we get here, then Django REST Framework has already validated that request.data is valid json and has parsed it into a dict.

        username = request.data.get('username', None)
        password = request.data.get('password', None)

        # Validation
        if not isinstance(username, str):
            return Response('Username must be a string', status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(password, str):
            return Response('Password must be a string', status=status.HTTP_400_BAD_REQUEST)
        if len(username) > 32:
            return Response('Username must be 32 characters or fewer', status=status.HTTP_400_BAD_REQUEST)
        if len(password) > 150:
            return Response('Password must be 150 characters or fewer', status=status.HTTP_400_BAD_REQUEST)
        if len(username) < 1:
            return Response('Username must be at least 1 character', status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 8:
            return Response('Password must be at least 8 characters', status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return Response('Username may only contain letters, digits, and underscores', status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^[A-Za-z0-9_!@#$%^&*()]+$', password):
            return Response('Password may only contain letters, digits, and the following characters: _ ! @ # $ % ^ & * ( )', status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).first() is not None:
            return Response('There is already a user with that username. Please choose another.', status=status.HTTP_400_BAD_REQUEST)
        try:
            # Run the password through the validators configured in AUTH_PASSWORD_VALIDATORS in settings.py
            validate_password(password)
        except ValidationError as e:
            # If the exception has type ValidationError, we know the error will have safe error messages from the built-in Django password validators.
            # Pass these back to the client so they know what to change about the password.
            return Response(f'Invalid password: {e}', status=status.HTTP_400_BAD_REQUEST)

        # Validation complete.

        try:
            user = User.objects.create_user(username=username, password=password)
            player = Player.objects.create(user=user)
        except Exception as e:
            log.error(f'Error creating account: Unexpected error creating user object: {e}')
            return Response('Error creating account', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token = Token.objects.create(user=user)

        return Response({
            'token': token.key,
            'username': user.username
        })


class LogOutView(views.APIView):
    # Endpoint for logging out
    def post(self, request, format=None):
        Token.objects.get(user=request.user).delete()
        return Response('ok')


class GameViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    # Endpoints for creating/updating/retrieving games
    queryset = Game.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateGameSerializer
        else:
            return GameSerializer

    @action(detail=False, methods=['get'])
    def get_current_game(self, request):
        player = Player.objects.get(user=request.user)
        if player.current_game:
            serializer = GameSerializer(player.current_game)
            return Response(serializer.data)
        else:
            return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_existing_games(self, request):
        # Get games that have not started yet and still need players.
        games = Game.objects.annotate(Count('player')).filter(
            num_players__gt=F('player__count'),
            is_started=False
        )
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_finished_games(self, request):
        games = Game.objects.filter(is_finished=True)
        serializer = FinishedGameListSerializer(games, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def get_finished_game(self, request, pk=None):
        game = Game.objects.get(id=pk)
        if not game.is_finished:
            return Response('Game is not finished', status=status.HTTP_400_BAD_REQUEST)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def join_game(self, request):
        # Verify user is not already in a game
        player = Player.objects.get(user=request.user)
        if player.current_game:
            return Response('You are already in a game', status=status.HTTP_400_BAD_REQUEST)

        # Verify user supplied game id is valid
        game_id = request.data.get('id', None)
        if not game_id:
            return Response('Game id required', status=status.HTTP_400_BAD_REQUEST)
        if type(game_id) is not int:
            return Response('Invalid game id', status=status.HTTP_400_BAD_REQUEST)
        try:
            game = Game.objects.get(id=game_id)
        except Exception as e:
            return Response('Invalid game id', status=status.HTTP_400_BAD_REQUEST)
        if game.is_started:
            return Response('Game already started', status=status.HTTP_400_BAD_REQUEST)
        if len(game.player_set.all()) == game.num_players:
            return Response('Game is full', status=status.HTTP_400_BAD_REQUEST)

        player.position = len(game.player_set.all())
        player.current_game = game
        player.save()

        sio_update_game(game.id)

        return Response('ok')
    
    @action(detail=False, methods=['post'])
    def leave_game(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        game_id = game.id

        if not game.is_started:
            if len(game.player_set.all()) == 1:
                game.delete()
            else:
                if game.owner == request.user:
                    # Change the owner to another player.
                    for other in game.player_set.all():
                        if other != player:
                            game.owner = other.user
                            game.save()
                # Get the other players in the game that have a higher position than this player,
                # and move them each down one position.
                other_players = game.player_set.filter(position__gt=player.position).all()
                for other_player in other_players:
                    other_player.position -= 1
                    other_player.save()
        elif not game.is_finished:
            # The player is ending the game by leaving.
            # Add a special TurnHistory to show this in the game log.
            TurnHistory.objects.create(
                game=game,
                turn=game.turn,
                hand=game.hand,
                player=player,
                end_game=True
            )
            game.is_finished = True

            # This player should lose, and all other players should win.
            game.losers.add(player.user)
            game.save()
            for other_player in game.player_set.all():
                if other_player != player:
                    game.winners.add(other_player.user)
                    game.save()
        # Else, the game is already finished and nothing more needs to be done to the game state.

        player.current_game = None
        player.position = None
        player.is_turn = False
        player.waiting_for_continue = False
        player.tricks = 0
        player.score = 0
        player.money = 0
        player.bet = 0
        player.fold = False
        for card in player.card_set.all():
            card.player = None
            card.save()
        player.save()

        sio_leave_room(player.user.id, game_id)
        sio_update_game(game_id)

        return Response('ok')

    @action(detail=False, methods=['post'])
    def start_game(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.owner != request.user:
            return Response('Only the game owner can start the game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_started:
            return Response('Game already started', status=status.HTTP_400_BAD_REQUEST)
        if game.num_players != len(game.player_set.all()):
            return Response('Not enough players to start the game', status=status.HTTP_400_BAD_REQUEST)

        if game.betting:
            game.is_betting_round = True
            game.save()
            for other_player in game.player_set.all():
                other_player.money = 100
                other_player.save()

        deck = [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29,
            31, 32, 33, 34, 35, 36, 37, 38,
            41, 42, 43, 44, 45, 46, 47,
            51, 52, 53, 54, 55, 56,
            61, 62, 63, 64, 65,
            71, 72, 73, 74
        ]
        shuffled_deck = []

        for i in range(len(deck)):
            card_num = secrets.choice(deck)
            deck.remove(card_num)
            shuffled_deck.append(card_num)
            player_receiving_card = game.player_set.get(position=i % game.num_players)
            card = Card.objects.create(number=card_num, game=game, player=player_receiving_card)
            card.save()
            if (card_num == 0):
                player_receiving_card.is_turn = True
                player_receiving_card.save()

        game.is_started = True
        game.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')
    
    @action(detail=False, methods=['post'])
    def continue_game(self, request):
        player = Player.objects.get(user=request.user)
        if not player.waiting_for_continue:
            return Response('No need to click continue now', status=status.HTTP_400_BAD_REQUEST)
        player.waiting_for_continue = False
        player.save()

        if player.current_game:
            sio_update_game(player.current_game.id)

            global timers
            timers[f'game{player.current_game.id}'].cancel()
            timers[f'game{player.current_game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [player.current_game.id])
            timers[f'game{player.current_game.id}'].start()

        return Response('ok')

    @action(detail=False, methods=['post'])
    def check(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_finished:
            return Response('Game is finished', status=status.HTTP_400_BAD_REQUEST)
        if not game.is_betting_round:
            return Response('It is not a betting round', status=status.HTTP_400_BAD_REQUEST)
        if not player.is_turn:
            return Response('It is not your turn', status=status.HTTP_400_BAD_REQUEST)
        for other_player in game.player_set.all():
            if other_player.bet > 0:
                return Response('You cannot check', status=status.HTTP_400_BAD_REQUEST)
        
        BetTurnHistory.objects.create(
            game=game,
            bet_turn=game.bet_turn,
            hand=game.hand,
            player=player,
            bet_action='CHECK'
        )
        game.bet_turn += 1
        game.save()

        player.is_turn = False
        player.save()

        # Check if betting round should end
        if (player.position + 1) == game.num_players:
            # Transfer bets into the pot
            for other_player in game.player_set.all():
                game.pot += other_player.bet
                game.save()
                other_player.bet = 0
                other_player.save()

            game.is_betting_round = False
            game.save()

            # The next player is the one with the 0
            for other_player in game.player_set.all():
                if other_player.card_set.filter(number=0).count() == 1:
                    other_player.is_turn = True
                    other_player.save()
                    break
        else:
            # The next player is the one with position (current_player.position + 1) % num_players
            next_player = game.player_set.get(position=(player.position + 1) % game.num_players)
            next_player.is_turn = True
            next_player.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'].cancel()
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')

    @action(detail=False, methods=['post'])
    def open_betting(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_finished:
            return Response('Game is finished', status=status.HTTP_400_BAD_REQUEST)
        if not game.is_betting_round:
            return Response('It is not a betting round', status=status.HTTP_400_BAD_REQUEST)
        if not player.is_turn:
            return Response('It is not your turn', status=status.HTTP_400_BAD_REQUEST)
        for other_player in game.player_set.all():
            if other_player.bet > 0:
                return Response('You cannot open', status=status.HTTP_400_BAD_REQUEST)

        unvalidated_bet = request.data.get('bet')
        if (type(unvalidated_bet) is not int) or (unvalidated_bet <= 0) or (unvalidated_bet > player.money):
            return Response('Invalid bet', status=status.HTTP_400_BAD_REQUEST)
        validated_bet = unvalidated_bet

        BetTurnHistory.objects.create(
            game=game,
            bet_turn=game.bet_turn,
            hand=game.hand,
            player=player,
            bet_action='OPEN',
            bet_amount=validated_bet
        )
        game.bet_turn += 1
        game.save()

        player.money = player.money - validated_bet
        player.bet = validated_bet
        player.save()

        # Make it the next player's turn
        player.is_turn = False
        player.save()

        # The next player is the one with position (current_player.position + 1) % num_players
        next_player = game.player_set.get(position=(player.position + 1) % game.num_players)
        next_player.is_turn = True
        next_player.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'].cancel()
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')

    @action(detail=False, methods=['post'])
    def fold(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_finished:
            return Response('Game is finished', status=status.HTTP_400_BAD_REQUEST)
        if not game.is_betting_round:
            return Response('It is not a betting round', status=status.HTTP_400_BAD_REQUEST)
        if not player.is_turn:
            return Response('It is not your turn', status=status.HTTP_400_BAD_REQUEST)
        bets = False
        for other_player in game.player_set.all():
            if other_player.bet > 0:
                bets = True
        if not bets:
            return Response('You cannot fold', status=status.HTTP_400_BAD_REQUEST)

        BetTurnHistory.objects.create(
            game=game,
            bet_turn=game.bet_turn,
            hand=game.hand,
            player=player,
            bet_action='FOLD'
        )
        game.bet_turn += 1
        game.save()

        player.fold = True
        player.save()

        player.is_turn = False
        player.save()

        # Check if betting round should end
        highest_bet = game.player_set.order_by('-bet').first().bet
        num_players_with_highest_bet = game.player_set.filter(bet=highest_bet, fold=False).count()
        num_players_not_folded = game.player_set.filter(fold=False).count()
        if num_players_with_highest_bet == num_players_not_folded:
            # Transfer bets into the pot
            for other_player in game.player_set.all():
                game.pot += other_player.bet
                game.save()
                other_player.bet = 0
                other_player.save()

            game.is_betting_round = False
            game.save()
        else:
            # The next player is the one with position (current_player.position + 1) % num_players
            next_player = game.player_set.get(position=(player.position + 1) % game.num_players)
            next_player.is_turn = True
            next_player.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'].cancel()
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')

    @action(detail=False, methods=['post'])
    def call(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_finished:
            return Response('Game is finished', status=status.HTTP_400_BAD_REQUEST)
        if not game.is_betting_round:
            return Response('It is not a betting round', status=status.HTTP_400_BAD_REQUEST)
        if not player.is_turn:
            return Response('It is not your turn', status=status.HTTP_400_BAD_REQUEST)
        bets = False
        for other_player in game.player_set.all():
            if other_player.bet > 0:
                bets = True
        if not bets:
            return Response('You cannot call', status=status.HTTP_400_BAD_REQUEST)
        if player.fold:
            return Response('You have folded', status=status.HTTP_400_BAD_REQUEST)

        BetTurnHistory.objects.create(
            game=game,
            bet_turn=game.bet_turn,
            hand=game.hand,
            player=player,
            bet_action='CALL'
        )
        game.bet_turn += 1
        game.save()

        # Make this player's bet match the current highest bet
        highest_bet = game.player_set.order_by('-bet').first().bet
        player.money = (player.money + player.bet) - highest_bet
        player.bet = highest_bet
        player.save()

        player.is_turn = False
        player.save()

        # Check if the betting round should end
        num_players_with_highest_bet = game.player_set.filter(bet=highest_bet, fold=False).count()
        num_players_not_folded = game.player_set.filter(fold=False).count()
        if num_players_with_highest_bet == num_players_not_folded:
            # Transfer bets into the pot
            for other_player in game.player_set.all():
                game.pot += other_player.bet
                game.save()
                other_player.bet = 0
                other_player.save()

            game.is_betting_round = False
            game.save()
        else:
            # The next player is the one with position (current_player.position + 1) % num_players
            next_player = game.player_set.get(position=(player.position + 1) % game.num_players)
            next_player.is_turn = True
            next_player.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')

    @action(detail=False, methods=['post'])
    def raise_bet(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_finished:
            return Response('Game is finished', status=status.HTTP_400_BAD_REQUEST)
        if not game.is_betting_round:
            return Response('It is not a betting round', status=status.HTTP_400_BAD_REQUEST)
        if not player.is_turn:
            return Response('It is not your turn', status=status.HTTP_400_BAD_REQUEST)
        bets = False
        for other_player in game.player_set.all():
            if other_player.bet > 0:
                bets = True
        if not bets:
            return Response('You cannot raise', status=status.HTTP_400_BAD_REQUEST)
        if player.fold:
            return Response('You have folded', status=status.HTTP_400_BAD_REQUEST)
        
        unvalidated_bet = request.data.get('bet')
        if (type(unvalidated_bet) is not int) or (unvalidated_bet <= 0) or (unvalidated_bet > (player.money + player.bet)):
            return Response('Invalid bet', status=status.HTTP_400_BAD_REQUEST)
        validated_bet = unvalidated_bet
        
        highest_bet = game.player_set.order_by('-bet').first().bet
        if validated_bet <= highest_bet:
            return Response('You must raise to higher than the current highest bet', status=status.HTTP_400_BAD_REQUEST)
        
        BetTurnHistory.objects.create(
            game=game,
            bet_turn=game.bet_turn,
            hand=game.hand,
            player=player,
            bet_action='RAISE',
            bet_amount=validated_bet
        )
        game.bet_turn += 1
        game.save()
        
        player.money = (player.money + player.bet) - validated_bet
        player.bet = validated_bet
        player.save()

        # Make it the next player's turn
        player.is_turn = False
        player.save()

        # The next player is the one with position (current_player.position + 1) % num_players
        next_player = game.player_set.get(position=(player.position + 1) % game.num_players)
        next_player.is_turn = True
        next_player.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')


class PlayerViewSet(
    viewsets.GenericViewSet
):
    queryset = Player.objects.none()

    @action(detail=False, methods=['get'])
    def hand(self, request):
        player = Player.objects.get(user=request.user)
        hand = [h.number for h in player.card_set.all()]
        return Response(hand)
    
    @action(detail=False, methods=['get'])
    def view_player_statistics(self, request):
        players = Player.objects.all()
        serializer = PlayerStatisticSerializer(players, many=True)
        return Response(serializer.data)


class CardViewSet(
    viewsets.GenericViewSet
):
    queryset = Card.objects.none()

    @action(detail=False, methods=['post'])
    def play(self, request, **kwargs):
        black = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        red = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        blue = [21, 22, 23, 24, 25, 26, 27, 28, 29]
        brown = [31, 32, 33, 34, 35, 36, 37, 38]
        green = [41, 42, 43, 44, 45, 46, 47]
        yellow = [51, 52, 53, 54, 55, 56]
        purple = [61, 62, 63, 64, 65]
        gray = [71, 72, 73, 74]

        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=status.HTTP_400_BAD_REQUEST)
        if game.is_finished:
            return Response('Game is finished', status=status.HTTP_400_BAD_REQUEST)
        if game.is_betting_round:
            return Response('In a betting round', status=status.HTTP_400_BAD_REQUEST)
        if not player.is_turn:
            return Response('It is not your turn', status=status.HTTP_400_BAD_REQUEST)

        # Ensure we are not waiting for any players to click "continue"
        for other_player in game.player_set.all():
            if other_player.waiting_for_continue:
                return Response('Cannot play now, waiting for at least 1 player to click continue', status=status.HTTP_400_BAD_REQUEST)

        unvalidated_number = request.data.get('number')
        if (type(unvalidated_number) is not int) or (unvalidated_number < 0) or (unvalidated_number > 74):
            return Response('Invalid card number', status=status.HTTP_400_BAD_REQUEST)
        validated_number = unvalidated_number

        card = player.card_set.filter(number=validated_number).first()
        if not card:
            return Response('You do not have that card', status=status.HTTP_400_BAD_REQUEST)

        first_turn_of_trick = math.floor(game.turn / game.num_players) * game.num_players
        is_first_turn_of_trick = first_turn_of_trick == game.turn

        # Ensure this card is a valid card to play at this point in the game
        if game.turn == 0:
            # This is the first turn of the hand.
            # The only valid card to play is the 0.
            if validated_number != 0:
                return Response('You must play the 0', status=status.HTTP_400_BAD_REQUEST)
        elif is_first_turn_of_trick:
            # This is the first turn of the trick, but not the first turn of the hand.
            # The player can play anything in their hand.
            pass
        else:
            # This is not the first turn of the trick.
            # If the player has any cards with colors that have already been played in the trick,
            # they must play one of those cards.
            # Otherwise, they can play anything.

            # Get the cards that have already been played in the trick
            turn_histories_in_trick = game.turnhistory_set.filter(hand=game.hand, turn__gte=first_turn_of_trick)

            # Get the colors which have already been played
            played_colors = []
            for turn_history in turn_histories_in_trick:
                for color in [black, red, blue, brown, green, yellow, purple, gray]:
                    if turn_history.card.number in color:
                        played_colors += color
            
            # Check if the user has any cards in colors which have already been played
            can_play_anything = True
            for hand_card in player.card_set.all():
                if hand_card.number in played_colors:
                    can_play_anything = False
                    break

            if not can_play_anything:
                if card.number not in played_colors:
                    return Response('You must play one of your cards which is a color that has already been played', status=status.HTTP_400_BAD_REQUEST)

        # Create the TurnHistory
        turn_history = TurnHistory.objects.create(
            game=game,
            turn=game.turn,
            hand=game.hand,
            player=player,
            card=card
        )

        # Update the game state
        if game.turn < 59:
            game.turn += 1
        else:
            game.turn = 0
            game.hand += 1
        game.save()

        # Remove the card from this player's hand
        card.player = None
        card.save()

        # Make it the next player's turn
        player.is_turn = False
        player.save()

        first_turn_of_trick = math.floor(game.turn / game.num_players) * game.num_players
        is_first_turn_of_trick = first_turn_of_trick == game.turn
        if game.turn == 0:
            # The next turn is the first turn of the hand.

            # Transfer the tricks taken this round to each player's score.
            # Determine if the game is finished (if a player has >= 10 points).
            for other_player in game.player_set.all():
                other_player.score += other_player.tricks
                other_player.tricks = 0
                other_player.save()
                if other_player.score >= 10:
                    game.is_finished = True
                    game.save()

            if game.is_finished:
                # Figure out the winner(s) of the game

                # Find the lowest score
                lowest_score = game.player_set.order_by('score')[0].score

                # Get all players with the lowest score. These players are the winners.
                for other_player in game.player_set.filter(score=lowest_score):
                    game.winners.add(other_player.user)
                    game.save()
                
                # The remaining players (the ones with higher scores) are the losers.
                for other_player in game.player_set.filter(score__gt=lowest_score):
                    game.losers.add(other_player.user)
                    game.save()

                # Don't give players new cards if game is finished.
                sio_update_game(game.id)
                return Response('ok')

            # Shuffle the deck and give players their cards.
            # The next player is the one who gets the 0.
            deck = [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 23, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 34, 35, 36, 37, 38,
                41, 42, 43, 44, 45, 46, 47,
                51, 52, 53, 54, 55, 56,
                61, 62, 63, 64, 65,
                71, 72, 73, 74
            ]
            shuffled_deck = []

            for i in range(len(deck)):
                card_num = secrets.choice(deck)
                deck.remove(card_num)
                shuffled_deck.append(card_num)
                player_receiving_card = game.player_set.get(position=i % game.num_players)
                card = Card.objects.create(number=card_num, game=game, player=player_receiving_card)
                card.save()
                if (card_num == 0):
                    player_receiving_card.is_turn = True
                    player_receiving_card.save()
            
            # If betting is enabled, start a new betting round.
            if game.betting:
                game.is_betting_round = True
                game.save()

            # Wait for all players to click continue, to ensure everyone sees the results of the trick that just finished.
            for player in game.player_set.all():
                player.waiting_for_continue = True
                player.save()
        elif is_first_turn_of_trick:
            # The next turn is the first turn of the trick, but not the first turn of the hand.
            # Analyze the last trick to figure out who goes first in this trick.
            first_turn_of_last_trick = first_turn_of_trick - game.num_players
            turn_histories_in_last_trick = game.turnhistory_set.filter(hand=game.hand, turn__lt=first_turn_of_trick, turn__gte=first_turn_of_last_trick)

            # Figure out which color(s) occured the most times
            color_frequencies = [0, 0, 0, 0, 0, 0, 0, 0]
            colors = [black, red, blue, brown, green, yellow, purple, gray]
            for turn_history in turn_histories_in_last_trick:
                for index, color in enumerate(colors):
                    if turn_history.card.number in color:
                        color_frequencies[index] += 1
            max_colors = []
            for index in range(len(color_frequencies)):
                if color_frequencies[index] == max(color_frequencies):
                    max_colors += colors[index]

            # For cards played in that (those) color(s), figure out which card had the highest number
            max_number = 0
            for turn_history in turn_histories_in_last_trick:
                if (turn_history.card.number in max_colors) and (turn_history.card.number > max_number):
                    max_number = turn_history.card.number

            player_taking_trick = turn_histories_in_last_trick.get(card__number=max_number).player
            player_taking_trick.is_turn = True
            player_taking_trick.tricks += 1
            player_taking_trick.save()

            # Wait for all players to click continue, to ensure everyone sees the results of the trick that just finished.
            for player in game.player_set.all():
                player.waiting_for_continue = True
                player.save()
        else:
            # The next turn is not the first turn of the trick.
            # The next player is the one with position (current_player.position + 1) % num_players
            next_player = game.player_set.get(position=(player.position + 1) % game.num_players)
            next_player.is_turn = True
            next_player.save()

        sio_update_game(game.id)

        global timers
        timers[f'game{game.id}'].cancel()
        timers[f'game{game.id}'] = Timer(TIMEOUT_SECONDS, timeout, [game.id])
        timers[f'game{game.id}'].start()

        return Response('ok')
