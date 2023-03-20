from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import F, Count
from rest_framework import views, viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from texas.logging import log
from texas_api.models import Game, Player
from texas_api.serializers import CreateGameSerializer, GameSerializer
import json
import re


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
        if len(username) > 150:
            return Response('Username must be 150 characters or fewer', status=status.HTTP_400_BAD_REQUEST)
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
    
    @action(detail=False, methods=['post'])
    def join_game(self, request):
        # Verify user is not already in a game
        player = Player.objects.get(user=request.user)
        if player.current_game:
            return Response('You are already in a game', status=status.HTTP_400_BAD_REQUEST)

        # Verify user supplied game id is valid
        game_id = request.data.get('id', None)
        if not game_id:
            return Response('Game id required', status=HTTP_400_BAD_REQUEST)
        if type(game_id) is not int:
            return Response('Invalid game id', status=HTTP_400_BAD_REQUEST)
        try:
            game = Game.objects.get(id=game_id)
        except Exception as e:
            return Response('Invalid game id', status=HTTP_400_BAD_REQUEST)
        if game.is_started:
            return Response('Game already started', status=HTTP_400_BAD_REQUEST)
        if len(game.player_set.all()) == game.num_players:
            return Response('Game is full', status=HTTP_400_BAD_REQUEST)

        player.position = len(game.player_set.all())
        player.current_game = game
        player.save()
        return Response('ok')
    
    @action(detail=False, methods=['post'])
    def leave_game(self, request):
        player = Player.objects.get(user=request.user)
        game = player.current_game
        if not game:
            return Response('You are not in a game', status=HTTP_400_BAD_REQUEST)
        if game.owner == request.user:
            if len(game.player_set) > 1:
                # Change the owner to another player.
                for other in game.player_set:
                    if other != player:
                        game.owner = other
                        game.save()
        player.current_game = None
        player.position = None
        player.save()
        game = player.current_game
        if not len(game.player_set) and not game.is_started:
            game.delete()
        return Response('ok')
